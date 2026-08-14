"""Mertens HDR Exposure Fusion: Deterministic multi-exposure blending without tonemapping halos."""

from typing import List
import numpy as np
import cv2
from PIL import Image


def merge_mertens_hdr(
    images: List[Image.Image],
    contrast_weight: float = 1.0,
    saturation_weight: float = 1.0,
    exposedness_weight: float = 1.0,
) -> Image.Image:
    """Fuses multiple bracketed exposures (e.g. underexposed, normal, overexposed) using OpenCV's Mertens Exposure Fusion algorithm.
    Produces high dynamic range images with crisp shadow detail and highlight preservation with zero halo artifacts.
    """
    if not images:
        raise ValueError("No images provided for HDR fusion")
    if len(images) == 1:
        return images[0]

    # Convert all PIL Images to BGR NumPy uint8 arrays
    cv_imgs = [cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR) for img in images]

    # Initialize Mertens Merge Processor
    merge_mertens = cv2.createMergeMertens(
        contrast_weight=contrast_weight,
        saturation_weight=saturation_weight,
        exposure_weight=exposedness_weight
    )

    # Perform multi-scale Laplacian pyramid fusion
    fusion_32f = merge_mertens.process(cv_imgs)

    # Map [0.0, 1.0] float to [0, 255] 8-bit image
    fusion_8u = np.clip(fusion_32f * 255.0, 0, 255).astype(np.uint8)
    fusion_rgb = cv2.cvtColor(fusion_8u, cv2.COLOR_BGR2RGB)

    return Image.fromarray(fusion_rgb, mode="RGB")
