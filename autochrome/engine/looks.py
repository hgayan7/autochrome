"""Snapseed Aesthetic Styles & Looks Presets."""

from typing import Dict, Any
from PIL import Image
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.details import apply_details
from autochrome.engine.curves import apply_curves, PRESET_CURVES
from autochrome.types import TuneParams, DetailsParams, CurveParams


PRESET_LOOKS: Dict[str, Dict[str, Any]] = {
    "linkedin_pro": {
        "description": "Clean, crisp, trustworthy corporate portrait styling with natural skin pop",
        "tune": TuneParams(brightness=5, contrast=10, ambiance=15, highlights=-10, shadows=12, warmth=4, saturation=6),
        "details": DetailsParams(structure=15, sharpening=25),
    },
    "drama": {
        "description": "Snapseed Drama: intense dynamic contrast, rich shadows, and textured highlights",
        "tune": TuneParams(brightness=-2, contrast=30, ambiance=45, highlights=-25, shadows=15, warmth=-5, saturation=12),
        "details": DetailsParams(structure=40, sharpening=30),
    },
    "vintage_film": {
        "description": "Warm nostalgic film look with lifted matte shadows and golden highlights",
        "tune": TuneParams(brightness=4, contrast=-10, ambiance=20, highlights=-15, shadows=25, warmth=22, saturation=-8),
        "details": DetailsParams(structure=-5, sharpening=10),
        "curve_preset": "matte_vintage",
    },
    "noir_bw": {
        "description": "Dramatic high-contrast monochrome with deep velvety blacks and crisp whites",
        "tune": TuneParams(brightness=2, contrast=35, ambiance=25, highlights=10, shadows=-15, saturation=-100),
        "details": DetailsParams(structure=30, sharpening=35),
    },
    "glamour_glow": {
        "description": "Dreamy, luminous soft-focus glow with warm highlights",
        "tune": TuneParams(brightness=8, contrast=-5, ambiance=30, highlights=15, shadows=10, warmth=10, saturation=10),
        "details": DetailsParams(structure=-15, sharpening=15),
    },
    "crisp_editorial": {
        "description": "Modern studio magazine grade: razor sharp micro-contrast and true-to-life colors",
        "tune": TuneParams(brightness=3, contrast=18, ambiance=20, highlights=-8, shadows=8, warmth=0, saturation=8),
        "details": DetailsParams(structure=25, sharpening=40),
    },
    "cyberpunk": {
        "description": "Futuristic neon aesthetic with cyan shadows and hot magenta highlights",
        "tune": TuneParams(brightness=0, contrast=25, ambiance=30, highlights=15, shadows=-10, warmth=-30, saturation=35),
        "details": DetailsParams(structure=30, sharpening=30),
    },
}


def apply_look(image: Image.Image, look_name: str) -> Image.Image:
    """Applies a curated Snapseed look preset to an image."""
    name_clean = look_name.lower().strip().replace(" ", "_")
    look = PRESET_LOOKS.get(name_clean, PRESET_LOOKS["linkedin_pro"])

    img = image.copy()
    if "tune" in look:
        img = apply_tune_image(img, look["tune"])
    if "curve_preset" in look:
        pts = PRESET_CURVES.get(look["curve_preset"], [])
        if pts:
            img = apply_curves(img, CurveParams(channel="rgb", points=pts))
    if "details" in look:
        img = apply_details(img, look["details"])

    return img
