"""Adaptive Photographic Intelligence: Dynamic Scene-Aware Color Grading and Lighting Compensation."""

from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image

from autochrome.vision.analyze import analyze_photographic_scene
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.hsl import apply_hsl_mixer
from autochrome.engine.color_grade import apply_color_wheels_grading
from autochrome.engine.details import apply_details
from autochrome.types import TuneParams, DetailsParams


def compute_adaptive_grade_recipe(image: Image.Image, desired_mood: str = "photographic") -> Dict[str, Any]:
    """Analyzes the image's specific histogram, color cast, and lighting to compute a tailored dynamic editing recipe."""
    scene = analyze_photographic_scene(image)
    lighting = scene["lighting_scenario"]
    color_sci = scene["color_science"]
    depth_eval = scene["optical_depth_evaluation"]

    mean_lum = lighting["mean_luminance"]
    contrast_std = lighting["dynamic_contrast_std"]
    shadow_pct = lighting["shadow_clipped_pct"]
    highlight_pct = lighting["highlight_blown_pct"]
    color_cast = color_sci["color_cast"]
    tint_bias = color_sci["tint_bias"]

    # 1. Dynamic Zone System Exposure & Tone Adjustments
    # Compute dynamic compensation tailored to THIS specific photo
    target_lum = 128.0
    lum_gap = target_lum - mean_lum
    
    # Brightness adjustment proportional to exposure deficit
    dynamic_brightness = float(np.clip(lum_gap * 0.15, -20.0, 20.0))

    # Contrast adjustment: if low contrast (flat overcast), boost contrast; if harsh sun, soften
    if contrast_std < 40:
        dynamic_contrast = float(np.clip((45.0 - contrast_std) * 0.8 + 8.0, 6.0, 22.0))
        dynamic_ambiance = float(np.clip((45.0 - contrast_std) * 1.1 + 15.0, 15.0, 35.0))
    elif contrast_std > 65:
        dynamic_contrast = -8.0 # soften harsh light
        dynamic_ambiance = 12.0
    else:
        dynamic_contrast = 10.0
        dynamic_ambiance = 20.0

    # Highlights: compress if blown out
    if highlight_pct > 3.0:
        dynamic_highlights = float(np.clip(-highlight_pct * 3.5, -35.0, -10.0))
    else:
        dynamic_highlights = -8.0

    # Shadows: lift if crushed or deep
    if shadow_pct > 5.0 or mean_lum < 110:
        dynamic_shadows = float(np.clip(shadow_pct * 2.0 + 10.0, 8.0, 25.0))
    else:
        dynamic_shadows = 6.0

    # Color Temperature / Warmth compensation:
    # If photo is cool blue overcast -> warm it up. If already warm tungsten -> do NOT add warmth!
    if color_cast == "cool_blue":
        dynamic_warmth = 8.0
    elif color_cast == "warm":
        dynamic_warmth = -2.0 # Neutralize excessive orange/yellow
    else:
        dynamic_warmth = 3.5

    # Tint compensation:
    if tint_bias == "green":
        dynamic_tint = -4.0 # Add magenta
    elif tint_bias == "magenta":
        dynamic_tint = 4.0  # Add green
    else:
        dynamic_tint = 0.0

    # 2. Dynamic HSL Selective Separation
    # If skin is dull, boost Orange luminance. If eyes are green/hazel, boost green/yellow saturation
    dynamic_hsl = {
        "hue_shifts": {"orange": 2.0},
        "saturation_shifts": {
            "orange": 6.0,
            "yellow": 8.0 if dynamic_warmth > 0 else 0.0,
            "green": 18.0, # enhance natural iris pigment
            "red": 8.0,    # healthy lip tone
        },
        "luminance_shifts": {
            "orange": float(np.clip(12.0 + (target_lum - mean_lum) * 0.08, 6.0, 20.0)),
            "green": 10.0,
            "yellow": 8.0,
        }
    }

    # 3. Dynamic 3-Way Color Wheels
    if desired_mood == "cinematic":
        dynamic_wheels = {
            "shadows": {"hue": 215.0, "saturation": 12.0, "luminance": -3.0},
            "midtones": {"hue": 38.0, "saturation": 8.0, "luminance": 0.0},
            "highlights": {"hue": 45.0, "saturation": 12.0, "luminance": 2.0},
        }
    elif desired_mood == "kodak_portra":
        dynamic_wheels = {
            "shadows": {"hue": 35.0, "saturation": 6.0, "luminance": -2.0},
            "midtones": {"hue": 40.0, "saturation": 8.0, "luminance": 0.0},
            "highlights": {"hue": 48.0, "saturation": 12.0, "luminance": 2.0},
        }
    else: # pure natural photographic
        dynamic_wheels = {
            "shadows": {"hue": 210.0, "saturation": 6.0, "luminance": -2.0},
            "midtones": {"hue": 35.0, "saturation": 4.0, "luminance": 0.0},
            "highlights": {"hue": 45.0, "saturation": 8.0, "luminance": 1.0},
        }

    return {
        "diagnosis": {
            "lighting_scenario": lighting["type"],
            "description": lighting["description"],
            "mean_luminance": mean_lum,
            "contrast_std": contrast_std,
            "color_cast": color_cast,
            "natural_depth_detected": depth_eval["has_natural_depth_of_field"],
        },
        "computed_recipe": {
            "tune": TuneParams(
                brightness=round(dynamic_brightness, 1),
                contrast=round(dynamic_contrast, 1),
                ambiance=round(dynamic_ambiance, 1),
                highlights=round(dynamic_highlights, 1),
                shadows=round(dynamic_shadows, 1),
                warmth=round(dynamic_warmth, 1),
                tint=round(dynamic_tint, 1),
                saturation=5.0,
            ),
            "hsl": dynamic_hsl,
            "color_wheels": dynamic_wheels,
            "details": DetailsParams(structure=10.0, sharpening=24.0),
        }
    }


def apply_adaptive_photographic_grade(image: Image.Image, mood: str = "photographic") -> Tuple[Image.Image, Dict[str, Any]]:
    """Automatically analyzes image metrics and applies a completely tailored, scene-aware photographic grade."""
    plan = compute_adaptive_grade_recipe(image, desired_mood=mood)
    recipe = plan["computed_recipe"]

    img = image.copy()

    # 1. Dynamic Tune
    img = apply_tune_image(img, recipe["tune"])

    # 2. Dynamic HSL
    hsl_cfg = recipe["hsl"]
    img = apply_hsl_mixer(
        img,
        hue_shifts=hsl_cfg.get("hue_shifts"),
        saturation_shifts=hsl_cfg.get("saturation_shifts"),
        luminance_shifts=hsl_cfg.get("luminance_shifts"),
    )

    # 3. Dynamic Color Wheels
    cw_cfg = recipe["color_wheels"]
    img = apply_color_wheels_grading(
        img,
        shadows=cw_cfg.get("shadows"),
        midtones=cw_cfg.get("midtones"),
        highlights=cw_cfg.get("highlights"),
    )

    # 4. Details / Micro-contrast
    img = apply_details(img, recipe["details"])

    return img, plan
