"""Unit tests for the 16 FilterLibrary photo filters."""

import pytest
from PIL import Image
import numpy as np

from autochrome.core.canvas import Canvas
from autochrome.mcp.tools import set_active_canvas
from autochrome.mcp import tools
from autochrome.engine.filter_library import apply_filter_by_name, FilterType, list_available_filters


@pytest.fixture
def sample_image():
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[:50, :50] = [200, 50, 50]
    arr[:50, 50:] = [50, 200, 50]
    arr[50:, :50] = [50, 50, 200]
    arr[50:, 50:] = [220, 220, 180]
    return Image.fromarray(arr, mode="RGB")


def test_all_16_filters(sample_image):
    for f in FilterType:
        out = apply_filter_by_name(sample_image, f.value)
        assert out.size == sample_image.size
        assert out.mode == "RGB"


def test_mcp_filter_tools(sample_image):
    canvas = Canvas.from_image(sample_image)
    set_active_canvas(canvas)

    res_list = tools.tool_list_filters()
    assert res_list["status"] == "success"
    assert len(res_list["filters"]) == 16

    res_apply = tools.tool_apply_filter(filter_name="polaroid_70s")
    assert res_apply["status"] == "success"
    assert res_apply["filter"] == "polaroid_70s"
