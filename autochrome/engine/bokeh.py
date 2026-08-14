"""Snapseed-grade Lens Blur / Bokeh Engine: Elliptical depth-of-field, transition blur, and lens vignette."""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from autochrome.types import BokehParams


def apply_lens_blur(image: Image.Image, params: BokehParams) -> Image.Image:
    """Applies realistic optical depth-of-field blur with smooth elliptical transition and vignette."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.width, img_rgba.height
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    cx = params.center_x if params.center_x is not None else w // 2
    cy = params.center_y if params.center_y is not None else h // 2

    # 1. Compute realistic multi-pass bokeh blur on entire image
    blur_sigma = max(1.0, (params.blur_strength / 100.0) * 28.0)
    
    # Optical bokeh highlight boost
    blurred_rgb = gaussian_filter(rgb, sigma=(blur_sigma, blur_sigma, 0))
    if params.bokeh_boost > 0:
        highlight_mask = np.clip((rgb - 0.7) / 0.3, 0.0, 1.0)
        boost_arr = gaussian_filter(highlight_mask, sigma=(blur_sigma * 0.7, blur_sigma * 0.7, 0))
        blurred_rgb = np.clip(blurred_rgb + (params.bokeh_boost / 100.0) * boost_arr * 0.5, 0.0, 1.0)

    # 2. Build Elliptical / Circular Transition Blur Mask
    y_grid, x_grid = np.mgrid[0:h, 0:w]
    
    # Coordinate shift relative to center
    dx = x_grid - cx
    dy = y_grid - cy

    if params.rotation_deg != 0.0:
        rad = np.radians(params.rotation_deg)
        cos_r, sin_r = np.cos(rad), np.sin(rad)
        dx_rot = dx * cos_r - dy * sin_r
        dy_rot = dx * sin_r + dy * cos_r
    else:
        dx_rot, dy_rot = dx, dy

    # Shape aspect ratio
    aspect = 1.35 if params.shape == "ellipse" else 1.0
    norm_dist = np.sqrt((dx_rot / 1.0) ** 2 + (dy_rot * aspect) ** 2)

    r_in = float(params.inner_radius)
    r_out = float(max(r_in + 10, params.outer_radius))

    # Mask: 0 inside inner radius (sharp), 1 outside outer radius (full blur)
    blur_amount = np.clip((norm_dist - r_in) / (r_out - r_in), 0.0, 1.0)
    # Smooth cubic S-curve falloff
    blur_amount_smooth = (blur_amount * blur_amount * (3.0 - 2.0 * blur_amount))[..., np.newaxis]

    # Composite sharp subject with blurred background
    out_rgb = rgb * (1.0 - blur_amount_smooth) + blurred_rgb * blur_amount_smooth

    # 3. Optional Vignette
    if params.vignette > 0:
        max_dim = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
        corner_dist = np.sqrt(dx ** 2 + dy ** 2) / max_dim
        vignette_mask = np.clip(1.0 - ((params.vignette / 100.0) * 0.8 * (corner_dist ** 1.8)), 0.0, 1.0)[..., np.newaxis]
        out_rgb = out_rgb * vignette_mask

    out_arr = np.concatenate([np.clip(out_rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
