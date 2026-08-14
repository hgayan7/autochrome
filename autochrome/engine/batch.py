"""Batch Shoot Matcher & Color Transfer Engine: Matches exposure, white balance, and color grade across an entire photo shoot to a hero reference."""

import os
from typing import List, Dict, Any, Optional
import numpy as np
import cv2
from PIL import Image


def match_color_to_reference(source: Image.Image, reference: Image.Image, strength: float = 0.85) -> Image.Image:
    """Applies Reinhard Color Transfer in CIELAB color space to match the color tone and exposure of a source image to a hero reference photo."""
    src_rgb = np.array(source.convert("RGB"))
    ref_rgb = np.array(reference.convert("RGB"))

    # Convert to CIELAB space
    src_lab = cv2.cvtColor(src_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    ref_lab = cv2.cvtColor(ref_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

    # Compute mean and standard deviation for each channel
    src_mean, src_std = np.mean(src_lab, axis=(0, 1)), np.std(src_lab, axis=(0, 1))
    ref_mean, ref_std = np.mean(ref_lab, axis=(0, 1)), np.std(ref_lab, axis=(0, 1))

    # Guard against zero std dev
    src_std = np.where(src_std < 1e-5, 1.0, src_std)

    # Transfer statistics: result = ((src - src_mean) * (ref_std / src_std)) + ref_mean
    matched_lab = np.zeros_like(src_lab)
    for c in range(3):
        matched_channel = (src_lab[..., c] - src_mean[c]) * (ref_std[c] / src_std[c]) + ref_mean[c]
        # Blend with original based on strength
        matched_lab[..., c] = src_lab[..., c] * (1.0 - strength) + matched_channel * strength

    matched_lab = np.clip(matched_lab, 0, 255).astype(np.uint8)
    matched_rgb = cv2.cvtColor(matched_lab, cv2.COLOR_LAB2RGB)

    return Image.fromarray(matched_rgb, mode="RGB")


def process_batch_shoot(
    input_dir: str,
    output_dir: str,
    reference_path: Optional[str] = None,
    strength: float = 0.85,
) -> Dict[str, Any]:
    """Batch develops an entire folder of photos to match a hero reference shot."""
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory does not exist: {input_dir}")

    os.makedirs(output_dir, exist_ok=True)
    supported_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    ref_img = None
    if reference_path and os.path.exists(reference_path):
        ref_img = Image.open(reference_path)

    processed_files = []
    for fname in sorted(os.listdir(input_dir)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in supported_exts:
            src_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            
            src_img = Image.open(src_path)
            if ref_img is not None:
                developed = match_color_to_reference(src_img, ref_img, strength=strength)
            else:
                from autochrome.engine.master_critic import develop_to_master
                developed = develop_to_master(src_img)

            developed.save(out_path, quality=95)
            processed_files.append(fname)

    return {
        "status": "success",
        "processed_count": len(processed_files),
        "output_directory": output_dir,
        "files": processed_files
    }
