"""Snapseed-grade Portrait Retouch Engine: Face spotlight, skin smoothing, eye clarity."""

from typing import Optional, Tuple
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from autochrome.types import PortraitParams


def apply_portrait_retouch(
    image: Image.Image,
    params: PortraitParams,
    face_box: Optional[Tuple[int, int, int, int]] = None,
) -> Image.Image:
    """Retouches portrait with face spotlight, skin texture smoothing, and eye clarity."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.width, img_rgba.height
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    if face_box is not None:
        fx, fy, fw, fh = face_box
        fcx, fcy = fx + fw // 2, fy + fh // 2
        fradius = int(max(fw, fh) * 0.75)
    else:
        # Default center upper third
        fcx, fcy = w // 2, int(h * 0.4)
        fradius = int(min(w, h) * 0.35)

    y_grid, x_grid = np.mgrid[0:h, 0:w]
    face_dist = np.sqrt((x_grid - fcx) ** 2 + ((y_grid - fcy) * 1.2) ** 2)
    face_mask = np.clip(1.0 - (face_dist / float(fradius)), 0.0, 1.0)
    face_mask_smooth = (face_mask * face_mask * (3.0 - 2.0 * face_mask))[..., np.newaxis]

    # 1. Face Spotlight (gentle illumination boost in face region)
    if params.face_spotlight > 0:
        spot_factor = (params.face_spotlight / 100.0) * 0.35
        spot_boost = spot_factor * face_mask_smooth * (1.0 - rgb)
        rgb = np.clip(rgb + spot_boost, 0.0, 1.0)

    # 2. Skin Smoothing (Surface blur preserving facial contours)
    if params.skin_smoothing > 0:
        smooth_factor = (params.skin_smoothing / 100.0)
        # Guided bilateral approximation: smooth low frequency while preserving edges
        blur_fine = gaussian_filter(rgb, sigma=(3.0, 3.0, 0))
        # Edge mask
        diff = np.abs(rgb - blur_fine)
        edge_weight = np.clip(1.0 - (diff * 4.0), 0.0, 1.0)
        smoothed = rgb * (1.0 - edge_weight) + blur_fine * edge_weight
        
        # Apply smoothing predominantly in face region
        rgb = rgb * (1.0 - face_mask_smooth * smooth_factor * 0.75) + smoothed * (face_mask_smooth * smooth_factor * 0.75)

    # 3. Eye Clarity (Eye level micro-contrast boost)
    if params.eye_clarity > 0:
        eye_factor = (params.eye_clarity / 100.0) * 0.5
        # Eye region is approximately top 30-50% of the face box
        eye_cy = fcy - int(fradius * 0.2)
        eye_dist = np.sqrt((x_grid - fcx) ** 2 + ((y_grid - eye_cy) * 2.5) ** 2)
        eye_mask = np.clip(1.0 - (eye_dist / float(fradius * 0.5)), 0.0, 1.0)
        eye_mask_smooth = (eye_mask * eye_mask * (3.0 - 2.0 * eye_mask))[..., np.newaxis]

        # High-pass pop for eyes
        blur_eye = gaussian_filter(rgb, sigma=(1.5, 1.5, 0))
        eye_highpass = rgb - blur_eye
        rgb = np.clip(rgb + eye_highpass * eye_factor * eye_mask_smooth * 2.0, 0.0, 1.0)

    # 4. Skin Tone Warmth
    if params.skin_tone_warmth != 0:
        w_factor = (params.skin_tone_warmth / 100.0) * 0.08
        rgb[..., 0] = np.clip(rgb[..., 0] + w_factor * face_mask_smooth[..., 0], 0.0, 1.0)
        rgb[..., 2] = np.clip(rgb[..., 2] - (w_factor * 0.7) * face_mask_smooth[..., 0], 0.0, 1.0)

    out_arr = np.concatenate([np.clip(rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
