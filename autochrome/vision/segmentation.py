"""Deterministic Computer Vision Semantic Segmentation & GrabCut Alpha Matting."""

from typing import Tuple, Optional, Union
import numpy as np
import cv2
from PIL import Image
from scipy.ndimage import gaussian_filter

from autochrome.vision.face import detect_primary_face


def extract_subject_mask(
    image: Image.Image,
    iter_count: int = 5,
) -> np.ndarray:
    """Extracts a high-precision binary/soft alpha mask of the primary subject
    using deterministic OpenCV GrabCut graph cuts and edge matting.
    Returns float32 mask of shape (H, W) in range [0.0, 1.0].
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    h, w, _ = arr.shape

    # 1. Detect primary face to anchor foreground bounding box
    face = detect_primary_face(img_rgb)
    if face:
        fx, fy, fw, fh = face
        # Expand face box to include body and head
        rect_x = max(0, int(fx - fw * 0.8))
        rect_y = max(0, int(fy - fh * 0.4))
        rect_w = min(w - rect_x, int(fw * 2.6))
        rect_h = min(h - rect_y, int(h - rect_y))
    else:
        # Fallback centered rectangle
        rect_x = int(w * 0.10)
        rect_y = int(h * 0.05)
        rect_w = int(w * 0.80)
        rect_h = int(h * 0.90)

    # 2. Execute OpenCV GrabCut
    mask = np.zeros((h, w), dtype=np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    rect = (rect_x, rect_y, rect_w, rect_h)
    cv2.grabCut(arr, mask, rect, bgd_model, fgd_model, iter_count, cv2.GC_INIT_WITH_RECT)

    # Convert GrabCut output (0=BGD, 1=FGD, 2=PR_BGD, 3=PR_FGD) to binary
    binary_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1.0, 0.0).astype(np.float32)

    # 3. Refine edges with bilateral and Gaussian smoothing
    smooth_mask = gaussian_filter(binary_mask, sigma=1.0)
    smooth_mask = np.clip((smooth_mask - 0.2) / 0.6, 0.0, 1.0)
    smooth_mask = smooth_mask * smooth_mask * (3.0 - 2.0 * smooth_mask)

    return smooth_mask


def replace_background_deterministic(
    image: Image.Image,
    target_bg: Union[str, Tuple[int, int, int]] = "studio_light_grey",
    edge_feather: float = 1.0,
) -> Image.Image:
    """Deterministic Background Replacement using OpenCV GrabCut + Alpha Matting."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    h, w, _ = arr.shape

    alpha = extract_subject_mask(image)
    if edge_feather > 0:
        alpha = gaussian_filter(alpha, sigma=edge_feather)
        alpha = np.clip(alpha, 0.0, 1.0)

    # Generate target background
    Y, X = np.ogrid[:h, :w]
    cx, cy = w // 2, int(h * 0.45)
    rad = np.sqrt(((X - cx) / (w * 0.65)) ** 2 + ((Y - cy) / (h * 0.65)) ** 2)
    rad = np.clip(rad, 0.0, 1.0)

    if isinstance(target_bg, tuple):
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array(target_bg, dtype=np.float32)
    elif target_bg == "clean_white":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * 248.0
    elif target_bg == "solid_red":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([220, 38, 38], dtype=np.float32)
    elif target_bg == "studio_red" or target_bg == "crimson_red":
        c_center = np.array([225, 29, 72], dtype=np.float32)
        c_edge = np.array([120, 15, 40], dtype=np.float32)
        new_bg = (1.0 - rad[..., np.newaxis] ** 1.2) * c_center + (rad[..., np.newaxis] ** 1.2) * c_edge
    elif target_bg == "solid_yellow":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([250, 204, 21], dtype=np.float32)
    elif target_bg == "studio_yellow" or target_bg == "yellow":
        c_center = np.array([254, 215, 60], dtype=np.float32)
        c_edge = np.array([215, 140, 15], dtype=np.float32)
        new_bg = (1.0 - rad[..., np.newaxis] ** 1.2) * c_center + (rad[..., np.newaxis] ** 1.2) * c_edge
    elif target_bg == "studio_blue":
        new_bg = np.ones((h, w, 3), dtype=np.float32) * np.array([215, 230, 245], dtype=np.float32)
    else: # "studio_light_grey"
        c_center = np.array([242, 244, 247], dtype=np.float32)
        c_edge = np.array([210, 215, 222], dtype=np.float32)
        new_bg = (1.0 - rad[..., np.newaxis]) * c_center + rad[..., np.newaxis] * c_edge

    alpha_3d = alpha[..., np.newaxis]
    composite = arr * alpha_3d + new_bg * (1.0 - alpha_3d)

    out_arr = np.clip(composite, 0, 255).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")
