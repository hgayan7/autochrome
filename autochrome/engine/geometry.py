"""Deterministic Computer Vision Geometry, Lens Distortion & Perspective Homography Suite."""

from typing import Tuple, List, Optional
import numpy as np
import cv2
from PIL import Image


def apply_keystone_correction(
    image: Image.Image,
    pitch: float = 0.0, # Vertical tilt (-30.0 to +30.0 deg)
    yaw: float = 0.0,   # Horizontal angle (-30.0 to +30.0 deg)
    roll: float = 0.0,  # In-plane rotation (-45.0 to +45.0 deg)
) -> Image.Image:
    """Corrects perspective keystoning (vertical/horizontal converging lines)
    using deterministic 4-point homography and OpenCV warpPerspective.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    h, w, _ = arr.shape

    # Source corners
    src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

    # Calculate perspective distortion offsets based on pitch and yaw
    pitch_offset = (pitch / 100.0) * (w * 0.25)
    yaw_offset = (yaw / 100.0) * (h * 0.25)

    dst_pts = np.float32([
        [max(0.0, pitch_offset), max(0.0, yaw_offset)],
        [min(float(w), float(w) - pitch_offset), max(0.0, -yaw_offset)],
        [min(float(w), float(w) + pitch_offset), min(float(h), float(h) - yaw_offset)],
        [max(0.0, -pitch_offset), min(float(h), float(h) + yaw_offset)]
    ])

    # Compute 3x3 Homography Matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(arr, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

    if roll != 0.0:
        rot_M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), roll, 1.0)
        warped = cv2.warpAffine(warped, rot_M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

    return Image.fromarray(warped, mode="RGB")


def apply_lens_distortion_correction(
    image: Image.Image,
    k1: float = -0.04, # Barrel (< 0) or Pincushion (> 0) coefficient
    k2: float = 0.0,
) -> Image.Image:
    """Corrects radial camera lens distortion (barrel / pincushion) using camera calibration matrix."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    h, w, _ = arr.shape

    # Intrinsic camera matrix estimate
    focal_length = w
    cam_matrix = np.array([
        [focal_length, 0, w / 2.0],
        [0, focal_length, h / 2.0],
        [0, 0, 1.0]
    ], dtype=np.float32)

    dist_coeffs = np.array([k1, k2, 0.0, 0.0], dtype=np.float32)
    undistorted = cv2.undistort(arr, cam_matrix, dist_coeffs)

    return Image.fromarray(undistorted, mode="RGB")
