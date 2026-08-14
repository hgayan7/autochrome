"""Unit tests for Annotations, Redactions, and Screenshots."""

from PIL import Image
from autochrome.types import ArrowParams, CalloutParams, LoupeParams, BadgeParams, MockupParams
from autochrome.engine.annotation import draw_arrow, draw_callout_box, draw_highlighter, add_numbered_badge, add_magnifier_loupe
from autochrome.engine.privacy import blur_region, pixelate_region, blackout_region
from autochrome.engine.mockup import beautify_screenshot


def create_test_image() -> Image.Image:
    return Image.new("RGBA", (300, 300), (40, 40, 40, 255))


def test_annotations():
    img = create_test_image()
    # Arrow
    arrow_params = ArrowParams(start_x=50, start_y=50, end_x=200, end_y=200, curvature=0.2)
    out = draw_arrow(img, arrow_params)
    assert out.size == (300, 300)

    # Callout
    callout_params = CalloutParams(x=60, y=60, width=120, height=80, label="Test")
    out = draw_callout_box(img, callout_params)
    assert out.size == (300, 300)

    # Highlighter
    out = draw_highlighter(img, 40, 40, 100, 30)
    assert out.size == (300, 300)

    # Badge
    badge_params = BadgeParams(x=100, y=100, number=1)
    out = add_numbered_badge(img, badge_params)
    assert out.size == (300, 300)

    # Loupe
    loupe_params = LoupeParams(target_x=100, target_y=100, loupe_x=200, loupe_y=200)
    out = add_magnifier_loupe(img, loupe_params)
    assert out.size == (300, 300)


def test_redactions():
    img = create_test_image()
    # Blur
    out = blur_region(img, 50, 50, 100, 50, radius=10)
    assert out.size == (300, 300)

    # Pixelate
    out = pixelate_region(img, 50, 50, 100, 50, block_size=8)
    assert out.size == (300, 300)

    # Blackout
    out = blackout_region(img, 50, 50, 100, 50)
    assert out.size == (300, 300)


def test_mockup():
    img = create_test_image()
    params = MockupParams(frame_type="macos_dark", backdrop="mesh_sunset", padding=40)
    out = beautify_screenshot(img, params)
    assert out.width > 300
    assert out.height > 300
