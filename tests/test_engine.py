"""Unit tests for photographic editing engines."""

from PIL import Image
import numpy as np
from autochrome.types import TuneParams, DetailsParams, CurveParams, CurvePoint, BokehParams, PortraitParams, SelectivePoint
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.details import apply_details
from autochrome.engine.curves import apply_curves
from autochrome.engine.bokeh import apply_lens_blur
from autochrome.engine.portrait import apply_portrait_retouch
from autochrome.engine.selective import apply_selective_adjust
from autochrome.engine.healing import apply_healing_patch
from autochrome.engine.looks import apply_look


def create_test_image() -> Image.Image:
    img = Image.new("RGBA", (150, 150), (128, 128, 128, 255))
    return img


def test_tune_image():
    img = create_test_image()
    params = TuneParams(brightness=20, contrast=15, ambiance=10, warmth=5)
    out = apply_tune_image(img, params)
    assert out.size == (150, 150)
    arr = np.array(out)
    assert np.mean(arr[..., :3]) > 128


def test_details():
    img = create_test_image()
    params = DetailsParams(structure=20, sharpening=30)
    out = apply_details(img, params)
    assert out.size == (150, 150)


def test_curves():
    img = create_test_image()
    pts = [CurvePoint(in_val=0, out_val=0), CurvePoint(in_val=128, out_val=180), CurvePoint(in_val=255, out_val=255)]
    out = apply_curves(img, CurveParams(channel="rgb", points=pts))
    arr = np.array(out)
    assert np.mean(arr[..., :3]) > 128


def test_lens_blur():
    img = create_test_image()
    params = BokehParams(center_x=75, center_y=75, inner_radius=30, outer_radius=60, blur_strength=20)
    out = apply_lens_blur(img, params)
    assert out.size == (150, 150)


def test_portrait_retouch():
    img = create_test_image()
    params = PortraitParams(face_spotlight=25, skin_smoothing=30, eye_clarity=30)
    out = apply_portrait_retouch(img, params, face_box=(40, 40, 70, 70))
    assert out.size == (150, 150)


def test_selective():
    img = create_test_image()
    pt = SelectivePoint(x=75, y=75, radius=40, brightness=50)
    out = apply_selective_adjust(img, [pt])
    arr = np.array(out)
    assert arr[75, 75, 0] > 128


def test_healing():
    img = create_test_image()
    out = apply_healing_patch(img, 75, 75, radius=15)
    assert out.size == (150, 150)


def test_looks():
    img = create_test_image()
    for look in ["linkedin_pro", "drama", "vintage_film", "noir_bw", "glamour_glow", "crisp_editorial"]:
        out = apply_look(img, look)
        assert out.size == (150, 150)
