"""Unit tests for 3D Cube LUT Engine."""

import pytest
import numpy as np
from PIL import Image

from autochrome.engine.lut_cube import parse_cube_lut, apply_3d_lut, export_canvas_to_cube_lut
from autochrome.mcp.tools import set_active_canvas, tool_apply_3d_cube_lut
from autochrome.core.canvas import Canvas


SAMPLE_CUBE_TEXT = """
# Sample Identity 2x2x2 LUT
TITLE "Identity Test"
LUT_3D_SIZE 2
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""


def test_cube_parsing_and_apply():
    grid, size = parse_cube_lut(SAMPLE_CUBE_TEXT)
    assert size == 2
    assert grid.shape == (2, 2, 2, 3)

    img = Image.new("RGB", (50, 50), (128, 64, 200))
    out = apply_3d_lut(img, grid, size)
    assert out.size == img.size


def test_cube_export():
    cube_str = export_canvas_to_cube_lut(lambda x: x, lut_size=4, title="Export Test")
    assert "LUT_3D_SIZE 4" in cube_str
    assert len(cube_str.strip().splitlines()) >= 64
