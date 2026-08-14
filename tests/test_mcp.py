"""Unit tests for MCP tool dispatchers."""

import os
from PIL import Image
from autochrome.mcp import tools


def test_mcp_tools():
    # Create temp image
    temp_path = "/tmp/test_mcp_image.png"
    img = Image.new("RGBA", (200, 200), (80, 100, 120, 255))
    img.save(temp_path)

    # 1. Open
    res = tools.tool_open_image(temp_path)
    assert res["status"] == "success"

    # 2. Inspect
    metrics = tools.tool_inspect_image()
    assert "lighting_scenario" in metrics
    assert "optical_depth_evaluation" in metrics

    # 3. Adaptive Color Grade
    res = tools.tool_adaptive_color_grade(mood="photographic")
    assert res["status"] == "success"

    # 4. HSL Mixer
    res = tools.tool_hsl_color_mixer(hue_shifts={"orange": 2.0}, saturation_shifts={"green": 10.0})
    assert res["status"] == "success"

    # 5. Film Profile
    res = tools.tool_apply_film_profile("kodak_portra_400")
    assert res["status"] == "success"

    # 6. Tune
    res = tools.tool_tune_image(brightness=10, contrast=5, ambiance=15)
    assert res["status"] == "success"

    # 7. Details
    res = tools.tool_adjust_details(structure=20, sharpening=15)
    assert res["status"] == "success"

    # 8. Annotations
    res = tools.tool_draw_arrow(20, 20, 100, 100)
    assert res["status"] == "success"

    # 9. Undo / Redo
    res = tools.tool_undo()
    assert res["status"] == "success"
    res = tools.tool_redo()
    assert res["status"] == "success"

    # 10. Export
    out_path = "/tmp/test_mcp_out.png"
    res = tools.tool_export_image(out_path)
    assert res["status"] == "success"
    assert os.path.exists(out_path)
