"""Snapseed-grade Healing Brush / Inpainting Engine."""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def apply_healing_patch(image: Image.Image, center_x: int, center_y: int, radius: int = 20) -> Image.Image:
    """Removes a spot, blemish, or unwanted artifact by sampling surrounding texture and blending seamlessly."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.width, img_rgba.height
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    # Crop bounding box of healing zone with margin
    margin = radius * 2
    x0 = max(0, center_x - margin)
    x1 = min(w, center_x + margin)
    y0 = max(0, center_y - margin)
    y1 = min(h, center_y + margin)

    patch = rgb[y0:y1, x0:x1].copy()
    ph, pw, _ = patch.shape
    local_cx = center_x - x0
    local_cy = center_y - y0

    y_grid, x_grid = np.mgrid[0:ph, 0:pw]
    dist = np.sqrt((x_grid - local_cx) ** 2 + (y_grid - local_cy) ** 2)

    # Inpaint mask: 1 inside blemish, 0 outside
    mask = np.clip(1.0 - (dist / float(radius)), 0.0, 1.0)
    smooth_mask = (mask * mask * (3.0 - 2.0 * mask))[..., np.newaxis]

    # Ring sample around the blemish
    ring_mask = np.clip((dist - radius) / float(radius), 0.0, 1.0) * np.clip(1.0 - (dist - radius) / float(radius), 0.0, 1.0)
    
    # Weighted average color around perimeter
    weights = ring_mask[..., np.newaxis]
    if np.sum(weights) > 0:
        surrounding_color = np.sum(patch * weights, axis=(0, 1)) / np.sum(weights)
    else:
        surrounding_color = np.mean(patch, axis=(0, 1))

    # Fast Gaussian diffusion inpaint
    blurred_patch = gaussian_filter(patch, sigma=(radius * 0.6, radius * 0.6, 0))
    inpainted = blurred_patch * 0.7 + surrounding_color * 0.3

    # Seamless composite
    blended_patch = patch * (1.0 - smooth_mask) + inpainted * smooth_mask
    rgb[y0:y1, x0:x1] = blended_patch

    out_arr = np.concatenate([np.clip(rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
