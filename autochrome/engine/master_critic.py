"""Photographic Quality Scoring, Aesthetic Critic & Autonomous Master Development Engine."""

from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from autochrome.engine.tune import apply_tune_image
from autochrome.engine.hsl import apply_hsl_mixer, rgb_to_hsl
from autochrome.engine.color_grade import apply_color_wheels_grading
from autochrome.engine.details import apply_details
from autochrome.engine.portrait import apply_portrait_retouch
from autochrome.vision.face import detect_primary_face
from autochrome.types import TuneParams, DetailsParams, PortraitParams


def score_photographic_quality(image: Image.Image) -> Dict[str, Any]:
    """Critiques and scores an image across fundamental professional photography dimensions (0 - 100)."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    h, w, _ = arr.shape

    # Rec.709 Luminance
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    mean_lum = float(np.mean(lum))
    std_lum = float(np.std(lum))

    # 1. Exposure & Dynamic Balance Score (Ideal mean ~ 118-135, low clipping)
    crushed_shadows = float(np.mean(lum < 25))
    blown_highlights = float(np.mean(lum > 235))
    
    lum_penalty = abs(mean_lum - 126.0) / 126.0 # 0 to 1
    clip_penalty = (crushed_shadows * 1.5 + blown_highlights * 2.0)
    exposure_score = float(np.clip(100.0 - (lum_penalty * 45.0 + clip_penalty * 100.0), 10.0, 99.0))

    # 2. Tonal Contrast & Dimension Score (Standard deviation & midtone distribution)
    # Muddy flat images have std < 35. High dynamic portraits have std 48-65.
    if std_lum < 32:
        contrast_score = float(np.clip(std_lum * 2.0, 15.0, 65.0))
    elif 45 <= std_lum <= 68:
        contrast_score = float(np.clip(88.0 + (std_lum - 45.0) * 0.4, 85.0, 98.0))
    else:
        contrast_score = float(np.clip(95.0 - (std_lum - 68.0) * 0.8, 40.0, 95.0))

    # 3. Color Science & Skin Tone Health Score
    rgb_norm = arr / 255.0
    h_arr, s_arr, l_arr = rgb_to_hsl(rgb_norm)

    # Detect human skin region (Hue ~ 10° to 45°, Saturation 0.15 to 0.65, Lum 0.2 to 0.8)
    skin_mask = (h_arr >= 8.0) & (h_arr <= 46.0) & (s_arr >= 0.12) & (s_arr <= 0.70) & (l_arr >= 0.18) & (l_arr <= 0.85)
    
    if np.sum(skin_mask) > (w * h * 0.03):
        skin_l = float(np.mean(l_arr[skin_mask]))
        skin_s = float(np.mean(s_arr[skin_mask]))
        
        # Ideal skin tone luminance is 0.48 - 0.68, saturation 0.28 - 0.48
        skin_lum_deficit = abs(skin_l - 0.58)
        skin_sat_deficit = abs(skin_s - 0.38)
        skin_score = float(np.clip(100.0 - (skin_lum_deficit * 90.0 + skin_sat_deficit * 70.0), 20.0, 99.0))
    else:
        skin_score = 80.0 # No prominent skin detected

    # 4. Micro-Contrast & Perceptual Sharpness Score
    blur_map = gaussian_filter(lum, sigma=1.5)
    high_freq = np.abs(lum - blur_map)
    sharpness_metric = float(np.mean(high_freq))
    # Typical sharp portrait has mean high-freq between 3.5 and 7.0
    if sharpness_metric < 2.0:
        sharpness_score = float(np.clip(sharpness_metric * 30.0, 20.0, 60.0))
    elif 3.5 <= sharpness_metric <= 8.5:
        sharpness_score = float(np.clip(85.0 + (sharpness_metric - 3.5) * 2.5, 85.0, 98.0))
    else:
        sharpness_score = float(np.clip(95.0 - (sharpness_metric - 8.5) * 2.0, 60.0, 95.0))

    # Overall Photographic Aesthetic Index (Weighted aggregate)
    overall_index = float(
        exposure_score * 0.30 +
        contrast_score * 0.25 +
        skin_score * 0.25 +
        sharpness_score * 0.20
    )

    grade = "Master Studio Quality" if overall_index >= 88 else (
        "Good Photographic Standard" if overall_index >= 75 else (
            "Mediocre / Needs Tone Work" if overall_index >= 60 else "Poor / Underexposed or Muddy"
        )
    )

    return {
        "overall_aesthetic_index": round(overall_index, 1),
        "quality_tier": grade,
        "metrics": {
            "exposure_score": round(exposure_score, 1),
            "tonal_contrast_score": round(contrast_score, 1),
            "skin_tone_radiance_score": round(skin_score, 1),
            "sharpness_clarity_score": round(sharpness_score, 1),
        },
        "diagnosis": {
            "mean_luminance": round(mean_lum, 1),
            "contrast_std": round(std_lum, 1),
            "crushed_shadows_pct": round(crushed_shadows * 100, 1),
            "blown_highlights_pct": round(blown_highlights * 100, 1),
        }
    }


def auto_master_develop(image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
    """Autonomous Master Development Loop:
    Evaluates the image, critiques defects, and dynamically optimizes all photographic parameters
    to achieve the maximum possible Photographic Aesthetic Index.
    """
    initial_critique = score_photographic_quality(image)
    diag = initial_critique["diagnosis"]
    mean_lum = diag["mean_luminance"]
    contrast_std = diag["contrast_std"]
    shadow_clip = diag["crushed_shadows_pct"]
    highlight_clip = diag["blown_highlights_pct"]

    # --- Phase 1: Zone System Exposure Compensation ---
    # Target optimum luminance 128
    lum_gap = 128.0 - mean_lum
    adj_brightness = float(np.clip(lum_gap * 0.20, -15.0, 22.0))

    # Contrast & Ambiance
    if contrast_std < 42:
        adj_contrast = float(np.clip((46.0 - contrast_std) * 0.75 + 8.0, 8.0, 20.0))
        adj_ambiance = float(np.clip((46.0 - contrast_std) * 1.1 + 18.0, 18.0, 36.0))
    elif contrast_std > 66:
        adj_contrast = -6.0
        adj_ambiance = 12.0
    else:
        adj_contrast = 10.0
        adj_ambiance = 22.0

    # Shadows & Highlights
    adj_shadows = float(np.clip(shadow_clip * 1.8 + (15.0 if mean_lum < 115 else 8.0), 6.0, 26.0))
    adj_highlights = float(np.clip(-highlight_clip * 3.0 - 10.0, -30.0, -8.0))

    # Channel Balances (Auto White Balance / Temperature)
    arr = np.array(image.convert("RGB"), dtype=np.float32)
    avg_r, avg_g, avg_b = float(np.mean(arr[..., 0])), float(np.mean(arr[..., 1])), float(np.mean(arr[..., 2]))
    r_b_diff = avg_r - avg_b

    if r_b_diff < -8: # Cool blue cast -> warm up
        adj_warmth = float(np.clip(abs(r_b_diff) * 0.5 + 3.0, 4.0, 12.0))
    elif r_b_diff > 25: # Too warm/yellow -> cool down
        adj_warmth = float(np.clip(-abs(r_b_diff) * 0.25, -10.0, -2.0))
    else:
        adj_warmth = 4.5

    tune_params = TuneParams(
        brightness=round(adj_brightness, 1),
        contrast=round(adj_contrast, 1),
        ambiance=round(adj_ambiance, 1),
        highlights=round(adj_highlights, 1),
        shadows=round(adj_shadows, 1),
        warmth=round(adj_warmth, 1),
        saturation=5.5,
    )

    stage1 = apply_tune_image(image, tune_params)

    # --- Phase 2: 8-Channel HSL Color Science & Skin Tone Vector ---
    # Target skin radiance & eye iris pop
    hsl_shifts = {
        "hue_shifts": {"orange": 2.0},
        "saturation_shifts": {"orange": 6.0, "yellow": 8.0, "red": 8.0, "green": 16.0},
        "luminance_shifts": {
            "orange": float(np.clip(14.0 + (128.0 - mean_lum) * 0.08, 8.0, 22.0)),
            "yellow": 8.0,
            "green": 12.0,
            "red": 5.0,
        }
    }
    stage2 = apply_hsl_mixer(
        stage1,
        hue_shifts=hsl_shifts["hue_shifts"],
        saturation_shifts=hsl_shifts["saturation_shifts"],
        luminance_shifts=hsl_shifts["luminance_shifts"],
    )

    # --- Phase 3: 3-Way Color Wheels Harmonic Separation ---
    stage3 = apply_color_wheels_grading(
        stage2,
        shadows={"hue": 218.0, "saturation": 8.0, "luminance": -2.0},
        midtones={"hue": 36.0, "saturation": 6.0, "luminance": 0.0},
        highlights={"hue": 45.0, "saturation": 10.0, "luminance": 2.0},
    )

    # --- Phase 4: Face Key Spotlight & Catchlight Enhancement ---
    face_box = detect_primary_face(stage3)
    portrait_params = PortraitParams(
        face_spotlight=24.0 if mean_lum < 120 else 16.0,
        skin_smoothing=12.0,
        eye_clarity=38.0,
        skin_tone_warmth=3.0,
    )
    stage4 = apply_portrait_retouch(stage3, portrait_params, face_box)

    # --- Phase 5: High-Pass Micro-Contrast & Texture Refinement ---
    details_params = DetailsParams(structure=10.0, sharpening=24.0)
    final_image = apply_details(stage4, details_params)

    # Final Quality Score
    final_critique = score_photographic_quality(final_image)

    report = {
        "before_critique": initial_critique,
        "after_critique": final_critique,
        "score_improvement": round(final_critique["overall_aesthetic_index"] - initial_critique["overall_aesthetic_index"], 1),
        "applied_adjustments": {
            "tune": tune_params.model_dump(),
            "hsl": hsl_shifts,
            "portrait": portrait_params.model_dump(),
            "details": details_params.model_dump(),
        }
    }

    return final_image, report
