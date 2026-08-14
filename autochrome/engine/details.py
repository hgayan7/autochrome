"""Snapseed-grade Details Engine: Structure (Texture & Micro-Contrast) and Sharpening."""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from autochrome.types import DetailsParams


def apply_details(image: Image.Image, params: DetailsParams) -> Image.Image:
    """Applies Structure (fine texture popping) and high-pass edge sharpening."""
    if params.structure == 0.0 and params.sharpening == 0.0:
        return image

    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    # Structure: Band-pass texture frequency enhancement
    if params.structure != 0.0:
        struct_factor = params.structure / 100.0
        # Multi-scale Gaussian separation
        blur_fine = gaussian_filter(rgb, sigma=(2.0, 2.0, 0))
        blur_med = gaussian_filter(rgb, sigma=(6.0, 6.0, 0))
        # High-frequency texture band
        texture = blur_fine - blur_med
        # Soft sign-preserving boost
        rgb = np.clip(rgb + struct_factor * texture * 1.5, 0.0, 1.0)

    # Sharpening: Unsharp mask high-pass
    if params.sharpening > 0.0:
        sharp_factor = (params.sharpening / 100.0) * 1.2
        blur_sharp = gaussian_filter(rgb, sigma=(1.2, 1.2, 0))
        high_pass = rgb - blur_sharp
        rgb = np.clip(rgb + sharp_factor * high_pass, 0.0, 1.0)

    out_arr = np.concatenate([rgb * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
