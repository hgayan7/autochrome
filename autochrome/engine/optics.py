"""Optics & Defringe Engine: Chromatic Aberration Removal and Lens Vignetting Compensation."""

import numpy as np
import cv2
from PIL import Image
from autochrome.engine.hsl import rgb_to_hsl, hsl_to_rgb


def remove_chromatic_aberration(
    image: Image.Image,
    purple_amount: float = 0.85,
    green_amount: float = 0.85,
    radius: int = 3,
) -> Image.Image:
    """Detects and desaturates lateral chromatic aberration (purple and green fringing) along high-contrast backlit edges."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    norm = arr / 255.0

    # 1. Compute image luminance & gradient edges (Sobel)
    gray = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
    
    # Edge mask (high contrast boundaries)
    edge_mask = (magnitude > 30.0).astype(np.float32)
    dilated_edges = cv2.dilate(edge_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (radius * 2 + 1, radius * 2 + 1)))

    # 2. Extract HSL
    h_arr, s_arr, l_arr = rgb_to_hsl(norm)

    # 3. Identify Purple Fringing: Hue 275-335 deg, Saturation > 0.20
    is_purple = (h_arr >= 275.0) & (h_arr <= 335.0) & (s_arr > 0.20) & (dilated_edges > 0.5)

    # 4. Identify Green Fringing: Hue 90-165 deg, Saturation > 0.20
    is_green = (h_arr >= 90.0) & (h_arr <= 165.0) & (s_arr > 0.20) & (dilated_edges > 0.5)

    # 5. Desaturate fringes selectively
    new_s = s_arr.copy()
    new_s = np.where(is_purple, new_s * (1.0 - purple_amount), new_s)
    new_s = np.where(is_green, new_s * (1.0 - green_amount), new_s)

    out_rgb = hsl_to_rgb(h_arr, new_s, l_arr) * 255.0
    return Image.fromarray(np.clip(out_rgb, 0, 255).astype(np.uint8), mode="RGB")


def correct_lens_vignetting(
    image: Image.Image,
    amount: float = 35.0,
    midpoint: float = 50.0,
) -> Image.Image:
    """Compensates for optical lens light falloff (vignetting) towards image corners using cos^4(theta) radial gain."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    h, w, _ = arr.shape

    # Generate radial distance map normalized [0, 1]
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    max_radius = np.sqrt(cx ** 2 + cy ** 2)
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_radius

    # Gain curve: inverse falloff
    mp_norm = midpoint / 100.0
    gain_curve = np.clip((r - mp_norm) / (1.0 - mp_norm + 1e-5), 0.0, 1.0)
    falloff_multiplier = 1.0 + (amount / 100.0) * (gain_curve ** 2)

    corrected = arr * falloff_multiplier[..., np.newaxis]
    return Image.fromarray(np.clip(corrected, 0, 255).astype(np.uint8), mode="RGB")
