"""Deterministic Computer Vision Portrait Retouching Suite: Frequency Separation."""

from typing import Tuple, Optional
import numpy as np
import cv2
from PIL import Image
from scipy.ndimage import gaussian_filter

from autochrome.engine.hsl import rgb_to_hsl


def apply_frequency_separation(
    image: Image.Image,
    blur_radius: float = 3.5,
    smoothing_strength: float = 0.55,
) -> Image.Image:
    """Authentic Studio Frequency Separation:
    1. Low-Frequency Layer: Contains tones, color gradations, and blotchiness.
    2. High-Frequency Layer: Contains skin pore textures, fine lines, and hair strands.
    Strictly masks smoothing to facial skin so clothing, beard hair, and background are 100% untouched.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    rgb_norm = arr / 255.0

    # Extract Skin Mask (Hue 10-48 deg, Sat 0.14-0.65, Lum 0.25-0.85)
    h_arr, s_arr, l_arr = rgb_to_hsl(rgb_norm)
    is_skin = (h_arr >= 10.0) & (h_arr <= 48.0) & (s_arr >= 0.14) & (s_arr <= 0.65) & (l_arr >= 0.25) & (l_arr <= 0.85)

    skin_alpha = gaussian_filter(is_skin.astype(np.float32), sigma=1.0)
    skin_alpha = np.clip(skin_alpha, 0.0, 1.0)

    # 1. Low-Frequency (LF) Base Layer
    lf_base = cv2.bilateralFilter(arr.astype(np.uint8), d=9, sigmaColor=75, sigmaSpace=75).astype(np.float32)

    # 2. High-Frequency (HF) Texture Layer: HF = Image - LF + 128.0
    hf_texture = arr - lf_base + 128.0

    # 3. Smooth Low-Frequency Layer selectively on skin
    lf_smoothed = gaussian_filter(lf_base, sigma=blur_radius)
    lf_blended = lf_base * (1.0 - smoothing_strength) + lf_smoothed * smoothing_strength

    # 4. Recomposite: Output = LF_smoothed + HF - 128.0
    reconstructed = lf_blended + hf_texture - 128.0
    
    # 5. Apply only to skin mask
    sa_3d = skin_alpha[..., np.newaxis]
    final_arr = reconstructed * sa_3d + arr * (1.0 - sa_3d)

    out_arr = np.clip(final_arr, 0, 255).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")
