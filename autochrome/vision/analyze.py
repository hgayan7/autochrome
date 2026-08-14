"""Photographic Scene Intelligence, Modality Detection, Vectorscope & Depth Evaluation."""

from typing import Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, sobel


def detect_content_modality(arr_rgb: np.ndarray, lum: np.ndarray) -> Tuple[str, Dict[str, Any]]:
    """Detects whether an image is a natural photograph, UI screenshot, document scan, or digital graphic.
    
    Uses gradient sparsity, flat surface ratios, and color quantization entropy.
    """
    # 1. Flat area ratio (gradient magnitude < 1.5)
    gx = sobel(lum, axis=1)
    gy = sobel(lum, axis=0)
    grad_mag = np.hypot(gx, gy)
    flat_ratio = float(np.mean(grad_mag < 2.0))

    # 2. Histogram sparsity & top color dominance
    # Quantize to 64 colors
    quant = (arr_rgb // 32) * 32
    quant_flat = quant.reshape(-1, 3)
    _, counts = np.unique(quant_flat, axis=0, return_counts=True)
    top_color_dominance = float(np.max(counts) / len(quant_flat))

    # 3. Orthogonal edge alignment (UI windows have 90-degree straight lines)
    horiz_edges = float(np.mean(np.abs(gy) > 20))
    vert_edges = float(np.mean(np.abs(gx) > 20))
    diag_diff = abs(horiz_edges - vert_edges)

    # Classification heuristics
    mean_lum = float(np.mean(lum))
    
    if flat_ratio > 0.30 or top_color_dominance > 0.35:
        # It is a digital UI, screenshot, document, or graphic
        if mean_lum > 220 and flat_ratio > 0.50:
            modality = "document_or_light_ui"
        elif mean_lum < 50 and flat_ratio > 0.40:
            modality = "dark_ui_screenshot"
        else:
            modality = "ui_screenshot"
            
        theme = "light_mode" if mean_lum > 130 else "dark_mode"
        return modality, {
            "is_photograph": False,
            "theme": theme,
            "flat_surface_ratio": round(flat_ratio, 3),
            "top_color_dominance": round(top_color_dominance, 3),
            "recommended_tools": ["beautify_screenshot", "draw_callout", "draw_arrow_with_label", "blur_region", "add_magnifier_loupe"]
        }
    
    return "photograph", {
        "is_photograph": True,
        "flat_surface_ratio": round(flat_ratio, 3),
        "top_color_dominance": round(top_color_dominance, 3),
        "recommended_tools": ["master_develop", "tone_curve", "hsl_color_mixer", "color_wheels_grade", "portrait_retouch", "adjust_details"]
    }


def analyze_photographic_scene(image: Image.Image) -> Dict[str, Any]:
    """Performs scale-invariant scene intelligence and modality-aware image evaluation."""
    img_rgb = image.convert("RGB")
    orig_w, orig_h = image.size

    # SCALE-INVARIANCE: Normalize to canonical analysis resolution (max 800px)
    max_dim = 800
    scale = min(1.0, max_dim / max(orig_w, orig_h))
    analysis_size = (max(64, int(orig_w * scale)), max(64, int(orig_h * scale)))
    scaled_img = img_rgb.resize(analysis_size, Image.Resampling.BILINEAR)
    
    arr = np.array(scaled_img, dtype=np.float32)
    w, h = analysis_size

    # Rec.709 Luminance map
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    mean_lum = float(np.mean(lum))
    std_lum = float(np.std(lum))

    # Detect Content Modality (Photo vs Screenshot/Graphic)
    modality, mod_meta = detect_content_modality(arr, lum)

    # Dominant Color Palette (from scaled image)
    small_arr = arr.reshape(-1, 3)
    quantized = ((small_arr // 32) * 32).astype(np.int32)
    unique, counts = np.unique(quantized, axis=0, return_counts=True)
    top_indices = np.argsort(counts)[::-1][:5]
    palette = [f"#{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}" for c in unique[top_indices]]

    avg_r = float(np.mean(arr[..., 0]))
    avg_g = float(np.mean(arr[..., 1]))
    avg_b = float(np.mean(arr[..., 2]))

    color_temp_diff = avg_r - avg_b
    tint_diff = avg_g - (avg_r + avg_b) / 2.0

    # IF NON-PHOTOGRAPHIC (UI Screenshot, Graphic, Document)
    if not mod_meta["is_photograph"]:
        return {
            "content_modality": modality,
            "is_photograph": False,
            "dimensions": {"width": orig_w, "height": orig_h, "aspect_ratio": round(orig_w / float(orig_h), 3)},
            "ui_analysis": {
                "theme": mod_meta["theme"],
                "background_color": palette[0] if palette else "#FFFFFF",
                "dominant_palette": palette,
                "recommended_workflow": "Screenshot Annotation & Presentation Studio (beautify_screenshot, draw_arrow, blur_region)",
            },
            "lighting_scenario": {
                "type": "synthetic_digital_ui",
                "description": f"Digital User Interface / Screenshot ({mod_meta['theme']})",
                "mean_luminance": round(mean_lum, 1),
                "dynamic_contrast_std": round(std_lum, 1),
                "shadow_clipped_pct": 0.0,
                "highlight_blown_pct": 0.0,
            },
            "color_science": {
                "color_cast": "warm" if color_temp_diff > 12 else ("cool_blue" if color_temp_diff < -10 else "neutral"),
                "tint_bias": "magenta" if tint_diff < -6 else ("green" if tint_diff > 6 else "balanced"),
                "dominant_palette": palette,
            },
            "optical_depth_evaluation": {
                "has_natural_depth_of_field": False,
                "subject_sharpness": 0.0,
                "background_sharpness": 0.0,
                "blur_recommendation": "DO NOT apply lens blur to UI screenshots. Use beautify_screenshot or blur_region for sensitive data redaction.",
            }
        }

    # FOR NATURAL PHOTOGRAPHS: Scale-invariant photographic color science
    shadow_ratio = float(np.mean(lum < 35))
    highlight_ratio = float(np.mean(lum > 225))
    
    avg_r = float(np.mean(arr[..., 0]))
    avg_g = float(np.mean(arr[..., 1]))
    avg_b = float(np.mean(arr[..., 2]))

    color_temp_diff = avg_r - avg_b
    tint_diff = avg_g - (avg_r + avg_b) / 2.0

    # Scale-invariant Lighting Classification
    if std_lum < 36 and 85 <= mean_lum <= 165:
        lighting_type = "overcast_diffused"
        lighting_description = "Flat diffused daylight (soft shadows, muted contrast, overcast sky)"
    elif std_lum > 65 and highlight_ratio > 0.08 and shadow_ratio > 0.08:
        lighting_type = "harsh_direct_sun"
        lighting_description = "Direct harsh sunlight with high dynamic contrast"
    elif color_temp_diff > 25:
        lighting_type = "warm_golden_or_tungsten"
        lighting_description = "Warm golden hour or tungsten ambient"
    elif mean_lum < 65:
        lighting_type = "low_light_underexposed"
        lighting_description = "Low light environment, shadows need lifting"
    else:
        lighting_type = "balanced_natural"
        lighting_description = "Balanced natural lighting"

    # Scale-Invariant Depth-of-Field Evaluation (canonical sigma = 2.0 on 800px scale)
    blur_map = gaussian_filter(lum, sigma=2.0)
    highpass = np.abs(lum - blur_map)
    
    cy_min, cy_max = int(h * 0.25), int(h * 0.75)
    cx_min, cx_max = int(w * 0.25), int(w * 0.75)

    center_sharpness = float(np.mean(highpass[cy_min:cy_max, cx_min:cx_max]))
    perimeter_pixels = (w * h) - ((cy_max - cy_min) * (cx_max - cx_min))
    perimeter_sharpness = float((np.sum(highpass) - np.sum(highpass[cy_min:cy_max, cx_min:cx_max])) / max(1, perimeter_pixels))

    has_natural_depth = (perimeter_sharpness < center_sharpness * 0.65) or (perimeter_sharpness < 2.2)

    return {
        "content_modality": "photograph",
        "is_photograph": True,
        "dimensions": {"width": orig_w, "height": orig_h, "aspect_ratio": round(orig_w / float(orig_h), 3)},
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

