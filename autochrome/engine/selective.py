"""Snapseed-grade Selective Adjust Engine: Targeted radial control points."""

from typing import List
import numpy as np
from PIL import Image
from autochrome.types import SelectivePoint
from autochrome.engine.details import apply_details
from autochrome.types import DetailsParams


def apply_selective_adjust(image: Image.Image, points: List[SelectivePoint]) -> Image.Image:
    """Applies Snapseed-style localized radial adjustments."""
    if not points:
        return image

    img_rgba = image.convert("RGBA")
    w, h = img_rgba.width, img_rgba.height
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    y_coords, x_coords = np.mgrid[0:h, 0:w]

    for pt in points:
        # Distance map
        dist = np.sqrt((x_coords - pt.x) ** 2 + (y_coords - pt.y) ** 2)
        # Cosine smooth falloff mask [0, 1]
        mask = np.clip(1.0 - (dist / float(pt.radius)), 0.0, 1.0)
        # Smooth hermite interpolation
        smooth_mask = (mask * mask * (3.0 - 2.0 * mask))[..., np.newaxis]

        if np.max(smooth_mask) <= 0:
            continue

        pt_rgb = rgb.copy()

        # Local Brightness
        if pt.brightness != 0.0:
            b_factor = (pt.brightness / 100.0) * 0.5
            pt_rgb = np.where(b_factor > 0, pt_rgb + b_factor * (1.0 - pt_rgb), pt_rgb + b_factor * pt_rgb)

        # Local Contrast
        if pt.contrast != 0.0:
            c_factor = (pt.contrast / 100.0) * 0.5
            pt_rgb = (pt_rgb - 0.5) * (1.0 + c_factor * 1.5) + 0.5

        # Local Saturation
        if pt.saturation != 0.0:
            sat_factor = 1.0 + (pt.saturation / 100.0)
            lum = (0.299 * pt_rgb[..., 0] + 0.587 * pt_rgb[..., 1] + 0.114 * pt_rgb[..., 2])[..., np.newaxis]
            pt_rgb = lum + (pt_rgb - lum) * sat_factor

        pt_rgb = np.clip(pt_rgb, 0.0, 1.0)
        # Blend with smooth falloff
        rgb = rgb * (1.0 - smooth_mask) + pt_rgb * smooth_mask

    out_arr = np.concatenate([np.clip(rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
