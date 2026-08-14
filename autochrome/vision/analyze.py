"""Photographic Scene Intelligence, Lighting Analysis, Vectorscope Skin Tone & Depth Evaluation."""

from typing import Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def analyze_photographic_scene(image: Image.Image) -> Dict[str, Any]:
    """Performs deep photographic and colorimetric scene evaluation to guide intelligent editing."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    w, h = image.size

    # Luminance map (Rec.709 standard coefficients)
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    mean_lum = float(np.mean(lum))
    std_lum = float(np.std(lum))

    # Zone System Exposure Distribution
    # Zone 0-II (Shadows < 40), Zone III-VII (Midtones 40-200), Zone VIII-X (Highlights > 200)
    shadow_ratio = float(np.mean(lum < 40))
    highlight_ratio = float(np.mean(lum > 215))
    midtone_ratio = 1.0 - (shadow_ratio + highlight_ratio)

    # Average Channel Balances
    avg_r = float(np.mean(arr[..., 0]))
    avg_g = float(np.mean(arr[..., 1]))
    avg_b = float(np.mean(arr[..., 2]))

    # Color Temperature & Tint Metrics
    color_temp_diff = avg_r - avg_b
    tint_diff = avg_g - (avg_r + avg_b) / 2.0

    # Lighting Scenario Classification
    if std_lum < 38 and 85 <= mean_lum <= 165:
        lighting_type = "overcast_diffused"
        lighting_description = "Flat diffused daylight (soft shadows, muted contrast, overcast sky)"
    elif std_lum > 65 and highlight_ratio > 0.08:
        lighting_type = "harsh_direct_sun"
        lighting_description = "Direct harsh sunlight with high dynamic contrast"
    elif color_temp_diff > 30:
        lighting_type = "warm_golden_or_tungsten"
        lighting_description = "Warm golden hour or tungsten indoor ambient"
    elif mean_lum < 70:
        lighting_type = "low_light_underexposed"
        lighting_description = "Low light environment, shadows need lifting"
    else:
        lighting_type = "balanced_natural"
        lighting_description = "Balanced natural lighting"

    # Natural Depth-of-Field & Blur Analysis
    # Compare high-frequency texture gradient in center (subject) vs perimeter (background)
    blur_map = gaussian_filter(lum, sigma=2.0)
    highpass = np.abs(lum - blur_map)
    
    # Margin vs Center texture power
    cy_min, cy_max = int(h * 0.25), int(h * 0.75)
    cx_min, cx_max = int(w * 0.25), int(w * 0.75)

    center_sharpness = float(np.mean(highpass[cy_min:cy_max, cx_min:cx_max]))
    perimeter_sharpness = float((np.sum(highpass) - np.sum(highpass[cy_min:cy_max, cx_min:cx_max])) / (w * h - (cy_max - cy_min) * (cx_max - cx_min)))

    has_natural_depth = (perimeter_sharpness < center_sharpness * 0.65) or (perimeter_sharpness < 2.5)

    # Dominant Color Palette
    small_arr = np.array(img_rgb.resize((64, 64), Image.Resampling.BOX)).reshape(-1, 3)
    quantized = (small_arr // 32) * 32
    unique, counts = np.unique(quantized, axis=0, return_counts=True)
    top_indices = np.argsort(counts)[::-1][:5]
    palette = [f"#{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}" for c in unique[top_indices]]

    return {
        "dimensions": {"width": w, "height": h, "aspect_ratio": round(w / float(h), 3)},
        "lighting_scenario": {
            "type": lighting_type,
            "description": lighting_description,
            "mean_luminance": round(mean_lum, 1),
            "dynamic_contrast_std": round(std_lum, 1),
            "shadow_clipped_pct": round(shadow_ratio * 100, 1),
            "highlight_blown_pct": round(highlight_ratio * 100, 1),
        },
        "color_science": {
            "color_cast": "warm" if color_temp_diff > 12 else ("cool_blue" if color_temp_diff < -10 else "neutral"),
            "tint_bias": "magenta" if tint_diff < -6 else ("green" if tint_diff > 6 else "balanced"),
            "dominant_palette": palette,
        },
        "optical_depth_evaluation": {
            "has_natural_depth_of_field": has_natural_depth,
            "subject_sharpness": round(center_sharpness, 2),
            "background_sharpness": round(perimeter_sharpness, 2),
            "blur_recommendation": "DO NOT apply artificial lens blur - natural depth already present or background details are integral" if has_natural_depth else "Consider subtle background blur only if background is distracting",
        }
    }
