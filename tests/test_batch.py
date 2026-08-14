"""Unit tests for Batch Shoot Color Matcher."""

import os
import pytest
import numpy as np
from PIL import Image

from autochrome.engine.batch import match_color_to_reference, process_batch_shoot


def test_color_transfer_to_reference():
    src = Image.new("RGB", (100, 100), (200, 100, 50))  # Warm orange
    ref = Image.new("RGB", (100, 100), (50, 120, 220))  # Cool blue

    matched = match_color_to_reference(src, ref, strength=0.9)
    assert matched.size == (100, 100)
    arr = np.array(matched)
    # Blue channel should increase significantly
    assert arr[50, 50, 2] > 100


def test_batch_shoot_processing(tmp_path):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()

    for i in range(3):
        img = Image.new("RGB", (50, 50), (100 + i * 20, 120, 140))
        img.save(in_dir / f"shot_{i}.jpg")

    ref_path = str(in_dir / "shot_0.jpg")
    res = process_batch_shoot(str(in_dir), str(out_dir), reference_path=ref_path)
    assert res["status"] == "success"
    assert res["processed_count"] == 3
