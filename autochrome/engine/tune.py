"""Snapseed-grade Tune Image Engine: Brightness, Contrast, Saturation, Ambiance, Highlights, Shadows, Warmth, Tint."""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from autochrome.types import TuneParams


def apply_tune_image(image: Image.Image, params: TuneParams) -> Image.Image:
    """Applies comprehensive Snapseed-style tone adjustments to an image."""
    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    # 1. Brightness (-100 to +100) -> gentle non-linear exposure curve
    if params.brightness != 0.0:
        b_factor = params.brightness / 100.0
        if b_factor > 0:
            rgb = rgb + b_factor * (1.0 - rgb) * 0.75
        else:
            rgb = rgb + b_factor * rgb * 0.75

    # 2. Contrast (-100 to +100) -> S-curve around mid-grey (0.5)
    if params.contrast != 0.0:
        c_factor = (params.contrast / 100.0) * 0.5
        # Soft sigmoid contrast
        rgb = np.clip((rgb - 0.5) * (1.0 + c_factor * 1.5) + 0.5, 0.0, 1.0)

    # 3. Ambiance (-100 to +100) -> Snapseed's signature local contrast and dynamic balance
    # Ambiance balances shadows and highlights while adding a subtle saturation pop to midtones
    if params.ambiance != 0.0:
        amb_factor = params.ambiance / 100.0
        # Compute luminance map
        lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
        # Low-pass luminance
        lum_blur = gaussian_filter(lum, sigma=min(rgb.shape[0], rgb.shape[1]) * 0.05)
        # Difference map for local dynamic enhancement
        diff = lum - lum_blur
        for c in range(3):
            rgb[..., c] = np.clip(rgb[..., c] + amb_factor * diff * 0.6 + amb_factor * (0.5 - lum_blur) * 0.25, 0.0, 1.0)

    # 4. Highlights (-100 to +100) -> Selective highlight compression/boost
    if params.highlights != 0.0:
        h_factor = params.highlights / 100.0
        lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
        # Highlight mask (dominant in upper luminance range > 0.5)
        h_mask = np.clip((lum - 0.4) / 0.6, 0.0, 1.0) ** 2
        for c in range(3):
            if h_factor < 0:
                # Recover highlights (darken bright spots)
                rgb[..., c] = rgb[..., c] + h_factor * h_mask * (rgb[..., c] * 0.5)
            else:
                rgb[..., c] = rgb[..., c] + h_factor * h_mask * (1.0 - rgb[..., c]) * 0.6

    # 5. Shadows (-100 to +100) -> Selective shadow lift or crush
    if params.shadows != 0.0:
        s_factor = params.shadows / 100.0
        lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
        # Shadow mask (dominant in lower luminance range < 0.6)
        s_mask = np.clip((0.6 - lum) / 0.6, 0.0, 1.0) ** 2
        for c in range(3):
            if s_factor > 0:
                # Lift shadows
                rgb[..., c] = rgb[..., c] + s_factor * s_mask * (1.0 - rgb[..., c]) * 0.5
            else:
                rgb[..., c] = rgb[..., c] + s_factor * s_mask * (rgb[..., c] * 0.6)

    # 6. Warmth / Temperature (-100 to +100) -> Amber / Cyan shift
    if params.warmth != 0.0:
        w_factor = (params.warmth / 100.0) * 0.15
        rgb[..., 0] = np.clip(rgb[..., 0] + w_factor, 0.0, 1.0)  # Red boost
        rgb[..., 2] = np.clip(rgb[..., 2] - w_factor, 0.0, 1.0)  # Blue reduce

    # 7. Tint (-100 to +100) -> Green / Magenta shift
    if params.tint != 0.0:
        t_factor = (params.tint / 100.0) * 0.12
        rgb[..., 1] = np.clip(rgb[..., 1] - t_factor, 0.0, 1.0)  # Green decrease -> Magenta increase

    # 8. Saturation (-100 to +100)
    if params.saturation != 0.0:
        sat_factor = 1.0 + (params.saturation / 100.0)
        lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])[..., np.newaxis]
        rgb = np.clip(lum + (rgb - lum) * sat_factor, 0.0, 1.0)

    out_rgb = np.clip(rgb, 0.0, 1.0) * 255.0
    out_arr = np.concatenate([out_rgb, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
