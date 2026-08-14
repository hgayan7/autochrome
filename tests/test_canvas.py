"""Unit tests for Canvas Engine and Layers."""

import os
import pytest
from PIL import Image
from autochrome.core.canvas import Canvas
from autochrome.core.layer import ImageLayer


def test_canvas_creation():
    img = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
    canvas = Canvas.from_image(img)
    assert canvas.width == 200
    assert canvas.height == 200
    assert len(canvas.layers) == 1
    assert canvas.original_image is not None


def test_canvas_render():
    img = Image.new("RGBA", (100, 100), (100, 100, 100, 255))
    canvas = Canvas.from_image(img)
    top_img = Image.new("RGBA", (100, 100), (255, 255, 255, 128))
    canvas.add_layer(ImageLayer("Top", top_img, opacity=0.5))
    rendered = canvas.render()
    assert rendered.size == (100, 100)
    assert rendered.mode == "RGBA"


def test_canvas_undo_redo():
    img1 = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    canvas = Canvas.from_image(img1)
    
    img2 = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    canvas.replace_base_image(img2, "edit_1", "Made white")
    assert len(canvas.history.undo_stack) == 2

    # Undo
    assert canvas.undo() is True
    assert canvas.history.undo_stack[-1].action.tool_name == "init_canvas"

    # Redo
    assert canvas.redo() is True
    assert canvas.history.undo_stack[-1].action.tool_name == "edit_1"
