"""Authentic Film Emulation & Master Photographic Color Grading Profiles."""

from typing import Dict, Any
from PIL import Image
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.curves import apply_curves, PRESET_CURVES
from autochrome.engine.hsl import apply_hsl_mixer
from autochrome.engine.color_grade import apply_color_wheels_grading, apply_split_toning
from autochrome.engine.details import apply_details
from autochrome.types import TuneParams, DetailsParams, CurveParams


FILM_PROFILES: Dict[str, Dict[str, Any]] = {
    "kodak_portra_400": {
        "name": "Kodak Portra 400",
        "description": "Legendary portrait film: warm radiant skin tones, soft creamy highlights, and rich golden warmth",
        "tune": TuneParams(brightness=4.0, contrast=10.0, ambiance=24.0, highlights=-15.0, shadows=12.0, warmth=6.0, saturation=5.0),
        "hsl": {
            "hue_shifts": {"orange": 2.0, "yellow": -3.0},
            "saturation_shifts": {"orange": 8.0, "yellow": 10.0, "red": 8.0, "blue": -10.0},
            "luminance_shifts": {"orange": 15.0, "yellow": 8.0, "red": 4.0},
        },
        "color_wheels": {
            "shadows": {"hue": 35.0, "saturation": 6.0, "luminance": -2.0},
            "midtones": {"hue": 40.0, "saturation": 8.0, "luminance": 0.0},
            "highlights": {"hue": 48.0, "saturation": 12.0, "luminance": 2.0},
        },
        "details": DetailsParams(structure=8.0, sharpening=20.0),
    },
    "fuji_pro_400h": {
        "name": "Fuji Pro 400H",
        "description": "Fine-art pastel look: cool emerald/cyan shadows, neutral creamy skin tones, and bright airy highlights",
        "tune": TuneParams(brightness=5.0, contrast=8.0, ambiance=20.0, highlights=-12.0, shadows=15.0, warmth=-3.0, tint=-4.0, saturation=3.0),
        "hsl": {
            "hue_shifts": {"green": -8.0, "aqua": 5.0, "orange": -2.0},
            "saturation_shifts": {"green": 18.0, "aqua": 15.0, "orange": 4.0, "red": 4.0},
            "luminance_shifts": {"green": 10.0, "aqua": 12.0, "orange": 12.0},
        },
        "color_wheels": {
            "shadows": {"hue": 195.0, "saturation": 12.0, "luminance": 0.0},
            "midtones": {"hue": 30.0, "saturation": 5.0, "luminance": 0.0},
            "highlights": {"hue": 160.0, "saturation": 8.0, "luminance": 3.0},
        },
        "details": DetailsParams(structure=6.0, sharpening=18.0),
    },
    "cinematic_teal_orange": {
        "name": "Cinematic Teal & Orange",
        "description": "Hollywood complementary color harmony: deep rich teal shadows with radiant amber skin tones",
        "tune": TuneParams(brightness=3.0, contrast=16.0, ambiance=26.0, highlights=-18.0, shadows=10.0, warmth=5.0, saturation=8.0),
        "hsl": {
            "hue_shifts": {"orange": 3.0, "blue": -10.0, "aqua": -5.0},
            "saturation_shifts": {"orange": 12.0, "blue": 18.0, "aqua": 16.0, "yellow": 10.0},
            "luminance_shifts": {"orange": 16.0, "blue": -8.0, "aqua": -4.0},
        },
        "color_wheels": {
            "shadows": {"hue": 215.0, "saturation": 18.0, "luminance": -4.0},
            "midtones": {"hue": 35.0, "saturation": 10.0, "luminance": 0.0},
            "highlights": {"hue": 42.0, "saturation": 16.0, "luminance": 2.0},
        },
        "details": DetailsParams(structure=12.0, sharpening=25.0),
    },
    "moody_nordic": {
        "name": "Moody Nordic Editorial",
        "description": "Atmospheric Scandinavian editorial: desaturated surroundings, deep slate shadows, and luminous skin isolation",
        "tune": TuneParams(brightness=2.0, contrast=14.0, ambiance=22.0, highlights=-20.0, shadows=6.0, warmth=-5.0, saturation=-15.0),
        "hsl": {
            "hue_shifts": {"orange": 2.0},
            "saturation_shifts": {"orange": 12.0, "yellow": -25.0, "green": -35.0, "blue": -20.0, "magenta": -40.0},
            "luminance_shifts": {"orange": 18.0, "yellow": -5.0, "blue": -8.0},
        },
        "color_wheels": {
            "shadows": {"hue": 220.0, "saturation": 10.0, "luminance": -5.0},
            "midtones": {"hue": 35.0, "saturation": 6.0, "luminance": -1.0},
            "highlights": {"hue": 200.0, "saturation": 6.0, "luminance": 1.0},
        },
        "details": DetailsParams(structure=14.0, sharpening=26.0),
    },
}


def apply_film_profile(image: Image.Image, profile_key: str) -> Image.Image:
    """Applies a professional analog film profile / color grading recipe."""
    profile = FILM_PROFILES.get(profile_key.lower().strip(), FILM_PROFILES["kodak_portra_400"])
    img = image.copy()

    # 1. Tone tuning
    if "tune" in profile:
        img = apply_tune_image(img, profile["tune"])

    # 2. 8-channel HSL
    if "hsl" in profile:
        hsl_cfg = profile["hsl"]
        img = apply_hsl_mixer(
            img,
            hue_shifts=hsl_cfg.get("hue_shifts"),
            saturation_shifts=hsl_cfg.get("saturation_shifts"),
            luminance_shifts=hsl_cfg.get("luminance_shifts"),
        )

    # 3. 3-Way Color Wheels
    if "color_wheels" in profile:
        cw_cfg = profile["color_wheels"]
        img = apply_color_wheels_grading(
            img,
            shadows=cw_cfg.get("shadows"),
            midtones=cw_cfg.get("midtones"),
            highlights=cw_cfg.get("highlights"),
        )

    # 4. Details / Micro-contrast
    if "details" in profile:
        img = apply_details(img, profile["details"])

    return img
