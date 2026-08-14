"""Unit tests for deterministic OpenCV computer vision tools."""

import pytest
from PIL import Image
import numpy as np

from autochrome.core.canvas import Canvas
from autochrome.mcp.tools import set_active_canvas, get_active_canvas
from autochrome.mcp import tools
from autochrome.engine.retouch import apply_frequency_separation
from autochrome.engine.geometry import apply_keystone_correction, apply_lens_distortion_correction
from autochrome.engine.lut import apply_zone_system_calibration


@pytest.fixture
def sample_test_image():
    arr = np.zeros((200, 200, 3), dtype=np.uint8)
    arr[:, :] = [40, 80, 220]
    arr[40:160, 50:150] = [210, 160, 120]
    arr[30:70, 50:150] = [30, 25, 20]
    arr[80:95, 70:85] = [20, 20, 20]
    arr[80:95, 115:130] = [20, 20, 20]
    arr[125:140, 85:115] = [230, 210, 170]
    return Image.fromarray(arr, mode="RGB")


def test_frequency_separation(sample_test_image):
    out = apply_frequency_separation(sample_test_image, blur_radius=2.0, smoothing_strength=0.5)
    assert out.size == sample_test_image.size
    assert out.mode == "RGB"


def test_keystone_correction(sample_test_image):
    out = apply_keystone_correction(sample_test_image, pitch=5.0, yaw=-5.0, roll=2.0)
    assert out.size == sample_test_image.size


def test_lens_distortion(sample_test_image):
    out = apply_lens_distortion_correction(sample_test_image, k1=-0.03, k2=0.0)
    assert out.size == sample_test_image.size


def test_zone_system_calibration(sample_test_image):
    out = apply_zone_system_calibration(sample_test_image, {3: 0.2, 7: -0.1})
    assert out.size == sample_test_image.size


def test_mcp_cv_tools_execution(sample_test_image):
    canvas = Canvas.from_image(sample_test_image)
    set_active_canvas(canvas)

    res_fs = tools.tool_frequency_separation(blur_radius=2.0)
    assert res_fs["status"] == "success"

    res_ks = tools.tool_keystone_correction(pitch=2.0)
    assert res_ks["status"] == "success"

    res_ld = tools.tool_lens_distortion_correction(k1=-0.02)
    assert res_ld["status"] == "success"

    res_zs = tools.tool_zone_system_calibration()
    assert res_zs["status"] == "success"
