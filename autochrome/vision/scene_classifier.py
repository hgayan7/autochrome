"""Photographic Scene Intelligence, Content Classification & Semantic Region Analysis."""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from PIL import Image
import cv2

from autochrome.vision.analyze import analyze_photographic_scene, detect_content_modality
from autochrome.vision.face import detect_primary_face


def estimate_kelvin_temperature(arr_rgb: np.ndarray) -> int:
    """Estimates the baseline color temperature in Kelvin from RGB channel ratios."""
    r_mean = float(np.mean(arr_rgb[..., 0]))
    g_mean = float(np.mean(arr_rgb[..., 1]))
    b_mean = float(np.mean(arr_rgb[..., 2]))

    if b_mean < 1.0:
        b_mean = 1.0
    rg_ratio = r_mean / max(1.0, g_mean)
    rb_ratio = r_mean / max(1.0, b_mean)

    # Approximate blackbody curve fit (2500K - 9500K)
    # Higher red/blue ratio -> lower Kelvin (warmer/candle/tungsten)
    # Higher blue/red ratio -> higher Kelvin (cooler/overcast/shade)
    if rb_ratio > 1.8:
        kelvin = int(2800 + (2.5 - min(2.5, rb_ratio)) * 800)
    elif rb_ratio > 1.2:
        kelvin = int(3800 + (1.8 - rb_ratio) * 2000)
    elif rb_ratio > 0.85:
        kelvin = int(5200 + (1.2 - rb_ratio) * 3500)
    else:
        kelvin = int(7200 + min(2300, (0.85 - rb_ratio) * 4000))

    return max(2200, min(11000, kelvin))


def segment_semantic_regions(arr_rgb: np.ndarray) -> Dict[str, Any]:
    """Segments skin, foliage, sky, and specular highlights using colorimetry and HSV color space."""
    # Convert to HSV
    hsv = cv2.cvtColor(arr_rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)
    h = hsv[..., 0]  # 0-179 in OpenCV (0-360 mapped)
    s = hsv[..., 1]  # 0-255
    v = hsv[..., 2]  # 0-255
    total_pixels = float(hsv.shape[0] * hsv.shape[1])

    # 1. Skin mask (Hue 0-25 -> 0-50° in 360 scale, Saturation 30-180, Value 50-250)
    # Human skin falls precisely on vectorscope 120° I-Line (Hue ~10-20 in OpenCV 0-179)
    skin_mask = ((h >= 3) & (h <= 24) & (s >= 35) & (s <= 190) & (v >= 45) & (v <= 250)).astype(np.uint8)
    skin_ratio = float(np.sum(skin_mask) / total_pixels)

    # 2. Foliage / Flora mask (Green/Yellow hue: Hue 30-85 in OpenCV -> 60-170° in 360, Saturation > 35)
    foliage_mask = ((h >= 28) & (h <= 85) & (s >= 35) & (v >= 30)).astype(np.uint8)
    foliage_ratio = float(np.sum(foliage_mask) / total_pixels)

    # 3. Sky mask (Top half of image, Blue/Cyan hue: Hue 90-135, or low saturation bright overcast)
    top_half_height = hsv.shape[0] // 2
    sky_blue = ((h[:top_half_height, :] >= 90) & (h[:top_half_height, :] <= 135) & 
                (s[:top_half_height, :] >= 20) & (v[:top_half_height, :] >= 80))
    sky_overcast = ((s[:top_half_height, :] < 25) & (v[:top_half_height, :] >= 190))
    sky_pixels = np.sum(sky_blue | sky_overcast)
    sky_ratio = float(sky_pixels / total_pixels)

    # 4. Specular highlights (High luminance, low saturation, extreme brightness > 230)
    specular_mask = ((v >= 235) & (s <= 80)).astype(np.uint8)
    specular_ratio = float(np.sum(specular_mask) / total_pixels)

    return {
        "skin": {"ratio": round(skin_ratio, 3), "detected": skin_ratio > 0.03, "mask": skin_mask},
        "foliage": {"ratio": round(foliage_ratio, 3), "detected": foliage_ratio > 0.05, "mask": foliage_mask},
        "sky": {"ratio": round(sky_ratio, 3), "detected": sky_ratio > 0.06, "mask": sky_blue | sky_overcast},
        "specular_highlights": {"ratio": round(specular_ratio, 4), "detected": specular_ratio > 0.002, "mask": specular_mask},
    }


def classify_scene_content(image: Image.Image) -> Dict[str, Any]:
    """Performs comprehensive scene understanding, content classification, and adaptive recommendations."""
    img_rgb = image.convert("RGB")
    orig_w, orig_h = image.size

    # 1. Base Scene Analysis & Modality
    scene_metrics = analyze_photographic_scene(img_rgb)
    if not scene_metrics.get("is_photograph", True):
        return {
            "scene_genre": "ui_screenshot",
            "is_photograph": False,
            "confidence": 0.98,
            "scene_metrics": scene_metrics,
            "subject_profile": {"has_human_subject": False, "has_faces": False},
            "recommendations": {
                "primary_workflow": "screenshot_studio",
                "film_stock_suitable": False,
                "recommended_tools": ["beautify_screenshot", "draw_callout", "blur_region"]
            }
        }

    # Normalize scale for fast analysis
    max_dim = 800
    scale = min(1.0, max_dim / max(orig_w, orig_h))
    analysis_size = (max(64, int(orig_w * scale)), max(64, int(orig_h * scale)))
    scaled_img = img_rgb.resize(analysis_size, Image.Resampling.BILINEAR)
    arr = np.array(scaled_img, dtype=np.float32)

    # 2. Semantic Region Segmentation
    regions = segment_semantic_regions(arr)
    
    # 3. Face Detection
    face_box = detect_primary_face(scaled_img)
    has_faces = face_box is not None

    # 4. Color Temperature (Kelvin)
    kelvin = estimate_kelvin_temperature(arr)

    # 5. Scene Genre Classification
    skin_detected = (regions["skin"]["ratio"] > 0.05) or has_faces
    foliage_detected = regions["foliage"]["detected"]
    sky_detected = regions["sky"]["detected"]
    specular_detected = regions["specular_highlights"]["detected"]
    mean_lum = scene_metrics["lighting_scenario"]["mean_luminance"]
    std_lum = scene_metrics["lighting_scenario"]["dynamic_contrast_std"]

    skin_ratio = regions["skin"]["ratio"]
    nature_ratio = regions["foliage"]["ratio"] + regions["sky"]["ratio"]

    if has_faces or (skin_ratio > 0.12 and skin_ratio > nature_ratio):
        genre = "portrait"
        genre_desc = "Human portrait or editorial figure photography"
        recommended_stocks = ["kodak_portra_400", "kodak_portra_160", "fuji_provia_100f", "kodak_trix_400"]
        optical_rec = ["portrait_retouch", "frequency_separation", "orton_effect"]
    elif (foliage_detected or sky_detected) and (nature_ratio > 0.15):
        genre = "landscape_nature"
        genre_desc = "Outdoor natural landscape, foliage, or scenic environment"
        recommended_stocks = ["fuji_velvia_50", "kodachrome_64", "fuji_classic_chrome", "agfa_vista_200"]
        optical_rec = ["dehaze_image", "orton_effect", "add_photographic_grain"]
    elif mean_lum < 80 and (specular_detected or std_lum > 50):
        genre = "street_night"
        genre_desc = "Night street photography, tungsten neon lights, or urban ambiance"
        recommended_stocks = ["cinestill_800t", "kodak_trix_400", "fuji_classic_chrome", "technicolor_2strip"]
        optical_rec = ["apply_film_halation", "add_photographic_grain", "apply_bleach_bypass"]
    elif std_lum < 38 and not skin_detected:
        genre = "architecture_interior"
        genre_desc = "Architectural, interior, or structured geometric scene"
        recommended_stocks = ["fuji_classic_chrome", "kodak_portra_160", "polaroid_sx70", "ilford_hp5"]
        optical_rec = ["keystone_correction", "correct_lens_vignetting"]
    else:
        genre = "general_editorial"
        genre_desc = "General photography with balanced lighting"
        recommended_stocks = ["kodak_portra_400", "fuji_classic_chrome", "kodachrome_64", "cinestill_800t"]
        optical_rec = ["adaptive_color_grade", "add_photographic_grain"]

    return {
        "scene_genre": genre,
        "description": genre_desc,
        "is_photograph": True,
        "estimated_kelvin": kelvin,
        "subject_profile": {
            "has_human_subject": skin_detected,
            "has_faces": has_faces,
            "skin_tone_ratio_pct": round(regions["skin"]["ratio"] * 100, 1),
            "face_box": face_box,
        },
        "environment": {
            "has_sky": sky_detected,
            "sky_ratio_pct": round(regions["sky"]["ratio"] * 100, 1),
            "has_foliage": foliage_detected,
            "foliage_ratio_pct": round(regions["foliage"]["ratio"] * 100, 1),
            "has_specular_highlights": specular_detected,
            "specular_ratio_pct": round(regions["specular_highlights"]["ratio"] * 100, 2),
        },
        "scene_metrics": scene_metrics,
        "adaptive_recommendations": {
            "ideal_film_stocks": recommended_stocks,
            "ideal_optical_fx": optical_rec,
            "skin_protection_required": skin_detected,
            "halation_candidate": specular_detected and (genre in ["street_night", "portrait"]),
            "dehaze_candidate": sky_detected and scene_metrics["lighting_scenario"]["type"] == "overcast_diffused",
        }
    }
