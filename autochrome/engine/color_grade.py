"""Professional 3-Way Color Wheels & Split Toning Engine (DaVinci Resolve / Lightroom standard)."""

from typing import Optional, Tuple, Dict, Any
import numpy as np
from PIL import Image


def apply_split_toning(
    image: Image.Image,
    shadow_hue: float = 210.0,      # Degrees (e.g. 210 for deep teal/navy)
    shadow_sat: float = 0.0,        # 0 to 100
    highlight_hue: float = 40.0,    # Degrees (e.g. 40 for warm champagne/gold)
    highlight_sat: float = 0.0,     # 0 to 100
    balance: float = 0.0,           # -100 (more shadows) to +100 (more highlights)
) -> Image.Image:
    """Applies classic photographic Split Toning (shadows vs highlights tinting)."""
    if shadow_sat == 0.0 and highlight_sat == 0.0:
        return image

    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    # Luminance map
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    # Balance threshold midpoint [0.1, 0.9]
    midpoint = 0.5 + (balance / 100.0) * 0.3

    # Shadow & highlight weight masks
    shadow_weight = np.clip((midpoint - lum) / midpoint, 0.0, 1.0) ** 1.5
    highlight_weight = np.clip((lum - midpoint) / (1.0 - midpoint), 0.0, 1.0) ** 1.5

    # Helper: Convert hue degree to unit RGB vector
    def hue_to_rgb_vector(h_deg: float) -> np.ndarray:
        rad = np.radians(h_deg)
        # Saturated color at hue
        r = (np.cos(rad) + 1.0) / 2.0
        g = (np.cos(rad - 2.094) + 1.0) / 2.0
        b = (np.cos(rad + 2.094) + 1.0) / 2.0
        vec = np.array([r, g, b], dtype=np.float32)
        return vec / (np.max(vec) + 1e-6)

    if shadow_sat > 0:
        s_rgb = hue_to_rgb_vector(shadow_hue)
        s_amt = (shadow_sat / 100.0) * 0.35
        for c in range(3):
            rgb[..., c] = np.clip(rgb[..., c] + shadow_weight * s_amt * (s_rgb[c] - 0.5), 0.0, 1.0)

    if highlight_sat > 0:
        h_rgb = hue_to_rgb_vector(highlight_hue)
        h_amt = (highlight_sat / 100.0) * 0.35
        for c in range(3):
            rgb[..., c] = np.clip(rgb[..., c] + highlight_weight * h_amt * (h_rgb[c] - 0.5), 0.0, 1.0)

    out_arr = np.concatenate([np.clip(rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")


def apply_color_wheels_grading(
    image: Image.Image,
    shadows: Optional[Dict[str, float]] = None,     # {"hue": float, "saturation": float, "luminance": float}
    midtones: Optional[Dict[str, float]] = None,    # {"hue": float, "saturation": float, "luminance": float}
    highlights: Optional[Dict[str, float]] = None,  # {"hue": float, "saturation": float, "luminance": float}
) -> Image.Image:
    """Applies DaVinci Resolve-style 3-Way Color Wheels grading (Lift, Gamma, Gain)."""
    shadows = shadows or {}
    midtones = midtones or {}
    highlights = highlights or {}

    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    # 3-way zone masks
    mask_sh = np.clip((0.45 - lum) / 0.45, 0.0, 1.0) ** 1.8
    mask_hl = np.clip((lum - 0.55) / 0.45, 0.0, 1.0) ** 1.8
    mask_mid = np.clip(1.0 - (mask_sh + mask_hl), 0.0, 1.0)

    def apply_wheel(rgb_in: np.ndarray, mask: np.ndarray, wheel_params: Dict[str, float]) -> np.ndarray:
        hue = wheel_params.get("hue", 0.0)
        sat = wheel_params.get("saturation", 0.0)
        lum_shift = wheel_params.get("luminance", 0.0)

        rad = np.radians(hue)
        r_c = (np.cos(rad) + 1.0) / 2.0
        g_c = (np.cos(rad - 2.094) + 1.0) / 2.0
        b_c = (np.cos(rad + 2.094) + 1.0) / 2.0
        c_vec = np.array([r_c, g_c, b_c], dtype=np.float32)

        # Tint shift
        if sat > 0:
            tint_amt = (sat / 100.0) * 0.3
            for c in range(3):
                rgb_in[..., c] += mask * tint_amt * (c_vec[c] - 0.5)

        # Luminance offset
        if lum_shift != 0:
            l_amt = (lum_shift / 100.0) * 0.25
            rgb_in += mask[..., np.newaxis] * l_amt

        return rgb_in

    if shadows:
        rgb = apply_wheel(rgb, mask_sh, shadows)
    if midtones:
        rgb = apply_wheel(rgb, mask_mid, midtones)
    if highlights:
        rgb = apply_wheel(rgb, mask_hl, highlights)

    out_arr = np.concatenate([np.clip(rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
