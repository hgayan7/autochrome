"""Precision Chroma Key, Edge Despill & Studio Background Replacement Engine."""

from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_erosion, binary_dilation


def replace_background_color(
    image: Image.Image,
    target_bg: Union[str, Tuple[int, int, int]] = "studio_yellow",
    key_color: Optional[Tuple[int, int, int]] = None,
    tolerance: float = 0.22,
    smoothness: float = 0.10,
) -> Image.Image:
    """Detects and cleanly isolates background (e.g. blue screen / solid backdrop)
    and composites the subject onto a new background without any background color leaking into the subject.
    """
    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    h, w, _ = arr.shape
    rgb = arr[..., :3] / 255.0

    # 1. Detect background key color (sample 4 corners and borders)
    if key_color is None:
        corners = np.concatenate([
            rgb[:15, :15].reshape(-1, 3),
            rgb[:15, -15:].reshape(-1, 3),
            rgb[-15:, :15].reshape(-1, 3),
            rgb[-15:, -15:].reshape(-1, 3),
            rgb[:10, :].reshape(-1, 3),
        ], axis=0)
        median_key = np.median(corners, axis=0)
    else:
        median_key = np.array(key_color, dtype=np.float32) / 255.0

    # Check if blue screen
    is_blue_screen = (median_key[2] > median_key[0] * 1.3) and (median_key[2] > median_key[1] * 1.3)
    
    if is_blue_screen:
        # Blue screen keying: difference between blue and the max of red/green
        max_rg = np.maximum(rgb[..., 0], rgb[..., 1])
        blue_dominance = rgb[..., 2] - max_rg
        
        # Pure background when blue exceeds max(r, g) by > 0.08
        # Pure subject when blue <= max(r, g)
        bg_weight = np.clip((blue_dominance - 0.01) / 0.08, 0.0, 1.0)
        
        # Subject alpha: 1.0 on subject, 0.0 on background
        subject_alpha = 1.0 - bg_weight
        
        # Ensure subject core is 100% solid (no background leakage into skin or shirt)
        subject_core = subject_alpha > 0.95
        subject_core_expanded = binary_dilation(subject_core, iterations=2)
        subject_alpha = np.where(subject_core_expanded, 1.0, subject_alpha)
        
        # Smooth only the outer 1-pixel boundary
        subject_alpha = gaussian_filter(subject_alpha, sigma=0.5)
        subject_alpha = np.clip(subject_alpha, 0.0, 1.0)
        
        # Edge Despill: on the boundary edge, remove residual blue bounce
        edge_zone = (subject_alpha > 0.05) & (subject_alpha < 0.98)
        clean_rgb = rgb.copy()
        clean_rgb[..., 2] = np.where(
            edge_zone,
            np.minimum(rgb[..., 2], max_rg * 1.05),
            rgb[..., 2]
        )
    else:
        diff = rgb - median_key
        dist = np.sqrt(np.sum(diff ** 2, axis=-1))
        bg_weight = np.clip((tolerance + smoothness - dist) / (smoothness + 1e-6), 0.0, 1.0)
        subject_alpha = 1.0 - bg_weight
        clean_rgb = rgb

    # 2. Generate New Target Background
    Y, X = np.ogrid[:h, :w]
    cx, cy = w // 2, int(h * 0.45)
    rad = np.sqrt(((X - cx) / (w * 0.65)) ** 2 + ((Y - cy) / (h * 0.65)) ** 2)
    rad = np.clip(rad, 0.0, 1.0)

    if isinstance(target_bg, tuple):
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array(target_bg, dtype=np.float32)
    elif target_bg == "solid_yellow":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([250, 204, 21], dtype=np.float32) # Clean Solid Yellow #FACC15
    elif target_bg == "studio_yellow" or target_bg == "yellow":
        # Clean Studio Amber-Yellow with soft radial glow
        c_center = np.array([254, 215, 60], dtype=np.float32)
        c_edge = np.array([215, 140, 15], dtype=np.float32)
        new_bg = (1.0 - rad[..., np.newaxis] ** 1.2) * c_center + (rad[..., np.newaxis] ** 1.2) * c_edge
    elif target_bg == "solid_red":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([220, 38, 38], dtype=np.float32)
    elif target_bg == "crimson_red" or target_bg == "studio_red" or target_bg == "red":
        c_center = np.array([225, 29, 72], dtype=np.float32)
        c_edge = np.array([120, 15, 40], dtype=np.float32)
        new_bg = (1.0 - rad[..., np.newaxis] ** 1.2) * c_center + (rad[..., np.newaxis] ** 1.2) * c_edge
    else:
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([250, 204, 21], dtype=np.float32)

    # 3. Composite subject over new background with zero foreground color leakage
    alpha_3d = subject_alpha[..., np.newaxis]
    composite_rgb = (clean_rgb * 255.0) * alpha_3d + new_bg * (1.0 - alpha_3d)

    out_arr = np.concatenate([
        np.clip(composite_rgb, 0, 255).astype(np.uint8),
        np.ones((h, w, 1), dtype=np.uint8) * 255
    ], axis=-1)

    return Image.fromarray(out_arr, mode="RGBA")
