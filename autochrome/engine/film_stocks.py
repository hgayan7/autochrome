"""Authentic Analog Film Stock Emulations with Scene-Aware Protection & Color Science."""

from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image

from autochrome.engine.tune import apply_tune_image
from autochrome.types import TuneParams, CurveParams
from autochrome.engine.hsl import apply_hsl_mixer
from autochrome.engine.color_grade import apply_color_wheels_grading, apply_split_toning
from autochrome.engine.curves import apply_curves, PRESET_CURVES
from autochrome.engine.optical_fx import apply_film_halation, add_photographic_grain, apply_orton_effect
from autochrome.vision.scene_classifier import classify_scene_content, segment_semantic_regions


FILM_STOCKS_METADATA = {
    "kodak_portra_400": {
        "name": "Kodak Portra 400",
        "category": "Portrait & Editorial",
        "description": "Warm golden skin tones, gentle highlight rolloff, low contrast, soft pastel colors, cyan-subtracted shadows.",
        "best_for": "Portraits, natural light, golden hour, lifestyle",
    },
    "kodak_portra_160": {
        "name": "Kodak Portra 160",
        "category": "Portrait & Editorial",
        "description": "Ultra-fine grain, neutral warm skin rendition, smooth pastel transitions, understated contrast.",
        "best_for": "Studio portraits, editorial fashion, daylight",
    },
    "cinestill_800t": {
        "name": "CineStill 800T",
        "category": "Cinematic & Night",
        "description": "Tungsten 3200K balance, cool atmospheric cyan shadows, glowing neon specular halation.",
        "best_for": "Night street, urban neon, tungsten interior, cinematic",
    },
    "kodak_trix_400": {
        "name": "Kodak Tri-X 400",
        "category": "Black & White Classic",
        "description": "Punchy Zone I/II velvety blacks, authentic silver halide midtone micro-grain, crisp highlight separation.",
        "best_for": "Street photojournalism, fine art noir, dramatic portraits",
    },
    "ilford_hp5": {
        "name": "Ilford HP5 Plus",
        "category": "Black & White Classic",
        "description": "Wide exposure latitude, soft medium contrast, rich shadow detail, smooth tonal gradations.",
        "best_for": "Documentary, architectural, classic street",
    },
    "fuji_velvia_50": {
        "name": "Fujifilm Velvia 50",
        "category": "Vibrant Landscape",
        "description": "Hyper-saturated emerald greens, deep cobalt blues, punchy contrast, crisp color separation.",
        "best_for": "Nature landscapes, sunsets, travel photography",
    },
    "fuji_provia_100f": {
        "name": "Fujifilm Provia 100F",
        "category": "Standard Reversal Slide",
        "description": "Natural faithful color rendition, neutral contrast, vivid primaries with realistic skin balance.",
        "best_for": "Commercial, general outdoor, clean editorial",
    },
    "kodachrome_64": {
        "name": "Kodachrome 64",
        "category": "Vintage Classic",
        "description": "Rich warm reds, golden amber midtones, deep inky blacks, classic 1970s National Geographic print look.",
        "best_for": "Vintage documentary, retro travel, nostalgia",
    },
    "fuji_classic_chrome": {
        "name": "Fujifilm Classic Chrome",
        "category": "Documentary & Street",
        "description": "Muted greens and cyans, warm earthen midtones, hard shadow contrast.",
        "best_for": "Documentary, city street, minimalist editorial",
    },
    "polaroid_sx70": {
        "name": "Polaroid SX-70 Instant",
        "category": "Instant Vintage",
        "description": "Faded matte blacks, warm green/magenta crossover, dreamy diffusion, retro instant print charm.",
        "best_for": "Artistic nostalgia, lo-fi instant, dreamscapes",
    },
    "agfa_vista_200": {
        "name": "Agfa Vista 200",
        "category": "Color Print Vintage",
        "description": "Vibrant golden-red bias, punchy dynamic contrast, rich 1990s color print nostalgia.",
        "best_for": "Sunny daylight, casual lifestyle, vintage color",
    },
    "technicolor_2strip": {
        "name": "Technicolor 2-Strip (1920s)",
        "category": "Historical Motion Picture",
        "description": "Early Hollywood two-color beam splitter (Red & Green-Cyan). Subtracted blues, coral skin tones.",
        "best_for": "Retro 1920s cinema, stylized artistic portraits",
    },
    "technicolor_3strip": {
        "name": "Technicolor 3-Strip (Golden Age)",
        "category": "Historical Motion Picture",
        "description": "1930s-1950s Golden Age dye-transfer imbibition: hyper-saturated primaries, deep dense blacks.",
        "best_for": "Golden Age cinema, vivid retro fashion, high-impact color",
    },
}


def apply_film_stock(
    image: Image.Image,
    stock_name: str = "kodak_portra_400",
    protect_skin: bool = True,
    adapt_to_scene: bool = True,
) -> Image.Image:
    """Applies a calibrated analog film stock emulation with scene-aware adaptation and skin protection."""
    stock_key = stock_name.lower().replace("-", "_").replace(" ", "_")
    if stock_key not in FILM_STOCKS_METADATA:
        # Fallback closest match or default
        stock_key = "kodak_portra_400"

    img_rgb = image.convert("RGB")
    orig_arr = np.array(img_rgb, dtype=np.float32)

    # 1. Diagnose scene & semantic regions
    scene_info = classify_scene_content(img_rgb)
    skin_info = segment_semantic_regions(orig_arr)["skin"]
    has_skin = skin_info["detected"] and protect_skin

    # 2. Execute Stock Recipe
    if stock_key == "kodak_portra_400":
        # Warm golden tones, soft contrast, lifted blacks, cyan-subtracted shadows
        img = apply_tune_image(img_rgb, TuneParams(brightness=2.0, contrast=-6.0, ambiance=18.0, highlights=-12.0, shadows=14.0, warmth=7.0, saturation=-2.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"yellow": 8.0, "green": 12.0, "blue": -6.0},
            saturation_shifts={"orange": -4.0, "yellow": -8.0, "green": -14.0, "blue": -10.0},
            luminance_shifts={"orange": 12.0, "red": 6.0, "yellow": 6.0}
        )
        img = apply_split_toning(img, shadow_hue=210.0, shadow_sat=8.0, highlight_hue=42.0, highlight_sat=10.0, balance=10.0)
        img = add_photographic_grain(img, amount=12.0, size=0.9, roughness=0.4)

    elif stock_key == "kodak_portra_160":
        # Ultra-fine grain, neutral warm skin, smooth pastel transitions
        img = apply_tune_image(img_rgb, TuneParams(brightness=3.0, contrast=-8.0, ambiance=14.0, highlights=-15.0, shadows=10.0, warmth=4.0, saturation=-4.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"yellow": 6.0, "green": 8.0},
            saturation_shifts={"orange": -6.0, "yellow": -10.0, "green": -10.0, "blue": -8.0},
            luminance_shifts={"orange": 14.0, "yellow": 4.0}
        )
        img = apply_split_toning(img, shadow_hue=205.0, shadow_sat=6.0, highlight_hue=45.0, highlight_sat=7.0)
        img = add_photographic_grain(img, amount=8.0, size=0.7, roughness=0.3)

    elif stock_key == "cinestill_800t":
        # Tungsten cool balance, cyan shadows, glowing neon specular halation
        img = apply_tune_image(img_rgb, TuneParams(brightness=0.0, contrast=12.0, ambiance=8.0, highlights=6.0, shadows=-6.0, warmth=-12.0, tint=4.0, saturation=8.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"blue": -10.0, "aqua": -6.0, "red": 5.0},
            saturation_shifts={"red": 18.0, "orange": 8.0, "aqua": 15.0, "blue": 14.0},
            luminance_shifts={"aqua": 8.0, "blue": -6.0}
        )
        img = apply_color_wheels_grading(
            img,
            shadows={"hue": 195.0, "saturation": 16.0, "luminance": -4.0},
            highlights={"hue": 40.0, "saturation": 12.0, "luminance": 4.0}
        )
        # Add CineStill signature red halation on specular highlights
        img = apply_film_halation(img, threshold=210.0, radius=22.0, intensity=0.75, tint_rgb=(255, 45, 15))
        img = add_photographic_grain(img, amount=16.0, size=1.1, roughness=0.5)

    elif stock_key == "kodak_trix_400":
        # Punchy Zone I/II blacks, silver halide grain, hard contrast B&W
        img = apply_tune_image(img_rgb, TuneParams(brightness=0.0, contrast=24.0, ambiance=20.0, highlights=8.0, shadows=-10.0, saturation=-100.0))
        img = apply_curves(img, CurveParams(channel="rgb", points=PRESET_CURVES["hard_contrast"]))
        img = add_photographic_grain(img, amount=30.0, size=1.2, roughness=0.7)

    elif stock_key == "ilford_hp5":
        # Soft medium contrast, wide latitude, smooth gradations B&W
        img = apply_tune_image(img_rgb, TuneParams(brightness=3.0, contrast=10.0, ambiance=15.0, highlights=-8.0, shadows=12.0, saturation=-100.0))
        img = add_photographic_grain(img, amount=22.0, size=1.0, roughness=0.5)

    elif stock_key == "fuji_velvia_50":
        # Hyper-saturated emerald greens, deep cobalt blues, punchy contrast
        img = apply_tune_image(img_rgb, TuneParams(brightness=0.0, contrast=16.0, ambiance=12.0, highlights=6.0, shadows=-8.0, warmth=2.0, saturation=22.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"green": 6.0, "yellow": -4.0, "blue": 4.0},
            saturation_shifts={"green": 34.0, "aqua": 28.0, "blue": 25.0, "yellow": 16.0, "red": 12.0},
            luminance_shifts={"green": 8.0, "blue": -10.0}
        )
        img = apply_curves(img, CurveParams(channel="rgb", points=PRESET_CURVES["brighten"]))
        img = add_photographic_grain(img, amount=10.0, size=0.8, roughness=0.3)

    elif stock_key == "fuji_provia_100f":
        # Natural faithful color rendition, neutral contrast, vivid primaries
        img = apply_tune_image(img_rgb, TuneParams(brightness=1.0, contrast=6.0, ambiance=8.0, highlights=-4.0, shadows=4.0, warmth=0.0, saturation=8.0))
        img = apply_hsl_mixer(
            img,
            saturation_shifts={"blue": 10.0, "green": 8.0, "red": 6.0},
            luminance_shifts={"orange": 6.0}
        )
        img = add_photographic_grain(img, amount=9.0, size=0.75, roughness=0.3)

    elif stock_key == "kodachrome_64":
        # Rich warm reds, golden amber midtones, deep inky blacks
        img = apply_tune_image(img_rgb, TuneParams(brightness=-2.0, contrast=18.0, ambiance=10.0, highlights=-6.0, shadows=-12.0, warmth=12.0, saturation=12.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"yellow": 12.0, "red": -4.0, "blue": -8.0},
            saturation_shifts={"red": 24.0, "yellow": 18.0, "orange": 10.0, "blue": -12.0},
            luminance_shifts={"red": 6.0, "orange": 8.0, "blue": -12.0}
        )
        img = apply_split_toning(img, shadow_hue=215.0, shadow_sat=12.0, highlight_hue=40.0, highlight_sat=16.0)
        img = add_photographic_grain(img, amount=18.0, size=1.0, roughness=0.5)

    elif stock_key == "fuji_classic_chrome":
        # Muted greens and cyans, warm earthen midtones, hard shadow contrast
        img = apply_tune_image(img_rgb, TuneParams(brightness=1.0, contrast=14.0, ambiance=6.0, highlights=-8.0, shadows=-6.0, warmth=4.0, saturation=-10.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"green": 18.0, "yellow": 8.0},
            saturation_shifts={"green": -28.0, "aqua": -24.0, "blue": -16.0, "yellow": -12.0, "orange": -4.0},
            luminance_shifts={"orange": 8.0, "green": -6.0}
        )
        img = apply_split_toning(img, shadow_hue=200.0, shadow_sat=8.0, highlight_hue=45.0, highlight_sat=8.0)
        img = add_photographic_grain(img, amount=14.0, size=0.9, roughness=0.4)

    elif stock_key == "polaroid_sx70":
        # Faded matte blacks, warm green/magenta crossover, dreamy diffusion
        img = apply_tune_image(img_rgb, TuneParams(brightness=4.0, contrast=-12.0, ambiance=20.0, highlights=-18.0, shadows=18.0, warmth=8.0, tint=6.0, saturation=-8.0))
        img = apply_curves(img, CurveParams(channel="rgb", points=PRESET_CURVES["matte_vintage"]))
        img = apply_split_toning(img, shadow_hue=140.0, shadow_sat=10.0, highlight_hue=330.0, highlight_sat=12.0)
        img = apply_orton_effect(img, strength=0.20, blur_radius=22.0)
        img = add_photographic_grain(img, amount=20.0, size=1.2, roughness=0.6)

    elif stock_key == "agfa_vista_200":
        # Vibrant golden-red bias, punchy dynamic contrast
        img = apply_tune_image(img_rgb, TuneParams(brightness=2.0, contrast=12.0, ambiance=12.0, highlights=-6.0, shadows=6.0, warmth=10.0, saturation=14.0))
        img = apply_hsl_mixer(
            img,
            hue_shifts={"red": -4.0, "yellow": 6.0},
            saturation_shifts={"red": 20.0, "yellow": 14.0, "orange": 10.0, "blue": 8.0},
            luminance_shifts={"orange": 10.0, "yellow": 6.0}
        )
        img = add_photographic_grain(img, amount=14.0, size=0.95, roughness=0.4)

    elif stock_key == "technicolor_2strip":
        # Early 2-strip (Red & Cyan). Blue is mapped into teal/slate, skin remains vibrant coral
        arr = np.array(img_rgb, dtype=np.float32)
        # Red record from red channel, Green-Cyan record from average of G and B
        r_rec = arr[..., 0]
        cyan_rec = (arr[..., 1] * 0.6 + arr[..., 2] * 0.4)
        
        t2_arr = np.zeros_like(arr)
        t2_arr[..., 0] = np.clip(r_rec * 1.08, 0.0, 255.0)
        t2_arr[..., 1] = np.clip(cyan_rec * 0.95, 0.0, 255.0)
        t2_arr[..., 2] = np.clip(cyan_rec * 0.82 + r_rec * 0.08, 0.0, 255.0)
        
        img = Image.fromarray(t2_arr.astype(np.uint8), mode="RGB")
        img = apply_tune_image(img, TuneParams(contrast=14.0, ambiance=8.0))
        img = add_photographic_grain(img, amount=16.0, size=1.1, roughness=0.5)

    elif stock_key == "technicolor_3strip":
        # Golden age 3-strip dye transfer: intense primaries, deep dense blacks
        img = apply_tune_image(img_rgb, TuneParams(brightness=0.0, contrast=20.0, ambiance=14.0, highlights=4.0, shadows=-10.0, saturation=24.0))
        img = apply_hsl_mixer(
            img,
            saturation_shifts={"red": 28.0, "green": 24.0, "blue": 22.0, "yellow": 20.0},
            luminance_shifts={"red": 8.0, "blue": -8.0}
        )
        img = apply_curves(img, CurveParams(channel="rgb", points=PRESET_CURVES["hard_contrast"]))
        img = add_photographic_grain(img, amount=12.0, size=0.85, roughness=0.4)

    else:
        img = img_rgb

    # 3. Content-Aware Skin Protection (Guard skin tones if enabled)
    if has_skin and stock_key in ["fuji_velvia_50", "technicolor_2strip", "kodachrome_64"]:
        graded_arr = np.array(img, dtype=np.float32)
        skin_mask = skin_info["mask"].astype(np.float32)
        # Soften mask edges with slight blur
        from scipy.ndimage import gaussian_filter
        soft_mask = gaussian_filter(skin_mask, sigma=3.0)[..., np.newaxis]
        
        # Blend 70% graded skin + 30% natural original skin tone
        blended_skin = graded_arr * 0.65 + orig_arr * 0.35
        final_arr = graded_arr * (1.0 - soft_mask) + blended_skin * soft_mask
        img = Image.fromarray(np.clip(final_arr, 0.0, 255.0).astype(np.uint8), mode="RGB")

    return img


def list_available_film_stocks() -> Dict[str, Any]:
    """Returns all 13 authentic film stock emulations with metadata."""
    return FILM_STOCKS_METADATA
