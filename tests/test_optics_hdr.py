"""Unit tests for Optics Defringe, Vignetting, and Mertens HDR Fusion."""

import pytest
import numpy as np
from PIL import Image

from autochrome.engine.optics import remove_chromatic_aberration, correct_lens_vignetting
from autochrome.engine.hdr import merge_mertens_hdr


def test_chromatic_aberration_defringe():
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[:, :50] = [255, 255, 255]
    arr[:, 50:] = [0, 0, 0]
    # Inject purple fringe
    arr[:, 48:52] = [200, 50, 220]
    img = Image.fromarray(arr, mode="RGB")

    defringed = remove_chromatic_aberration(img, purple_amount=0.9)
    assert defringed.size == img.size


def test_lens_vignetting_correction():
    img = Image.new("RGB", (100, 100), (120, 120, 120))
    corrected = correct_lens_vignetting(img, amount=40.0)
    assert corrected.size == img.size


def test_mertens_hdr_fusion():
    img1 = Image.new("RGB", (60, 60), (40, 40, 40))
    img2 = Image.new("RGB", (60, 60), (128, 128, 128))
    img3 = Image.new("RGB", (60, 60), (220, 220, 220))

    fused = merge_mertens_hdr([img1, img2, img3])
    assert fused.size == (60, 60)
