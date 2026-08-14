"""Comprehensive unit tests for scene classification, 13 film stocks, and optical physics."""

import pytest
import numpy as np
from PIL import Image

from autochrome.vision.scene_classifier import classify_scene_content, estimate_kelvin_temperature
from autochrome.engine.film_stocks import apply_film_stock, list_available_film_stocks, FILM_STOCKS_METADATA
from autochrome.engine.optical_fx import (
    apply_film_halation, apply_orton_effect, apply_bleach_bypass,
    dehaze_image, set_color_temperature_kelvin, add_photographic_grain
)
from autochrome.engine.smart_develop import smart_develop
from autochrome.core.canvas import Canvas
from autochrome.mcp.tools import set_active_canvas
from autochrome.mcp import tools


@pytest.fixture
def portrait_image():
    # 300x400 synthetic portrait with skin tone face & shoulders + natural lighting gradient
    np.random.seed(42)
    y, x = np.mgrid[0:400, 0:300]
    grad = (y / 400.0) * 30.0
    noise = np.random.normal(0, 3, (400, 300, 3))
    
    arr = np.zeros((400, 300, 3), dtype=np.float32)
    # Background slate gradient
    arr[:, :, 0] = 45 + grad
    arr[:, :, 1] = 55 + grad
    arr[:, :, 2] = 75 + grad
    # Shoulders
    arr[200:400, 50:250] = [35, 45, 55]
    # Face (warm skin tone: R:225, G:165, B:135 on vectorscope I-line)
    arr[80:240, 90:210] = [225, 165, 135]
    # Hair
    arr[60:120, 80:220] = [35, 25, 20]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def landscape_image():
    # 400x300 landscape with sky top and green foliage bottom
    np.random.seed(42)
    y, x = np.mgrid[0:300, 0:400]
    noise = np.random.normal(0, 3, (300, 400, 3))
    arr = np.zeros((300, 400, 3), dtype=np.float32)
    # Sky (blue gradient top)
    arr[0:150, :, 0] = 100 + (y[0:150, :] / 150.0) * 40
    arr[0:150, :, 1] = 150 + (y[0:150, :] / 150.0) * 30
    arr[0:150, :, 2] = 230
    # Foliage (green gradient bottom)
    arr[150:300, :, 0] = 40 + (y[150:300, :] / 150.0) * 20
    arr[150:300, :, 1] = 130 + (y[150:300, :] / 150.0) * 30
    arr[150:300, :, 2] = 50
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def night_street_image():
    # 400x300 night image with deep blacks and specular highlights
    np.random.seed(42)
    noise = np.random.normal(0, 2, (300, 400, 3))
    arr = np.full((300, 400, 3), 20.0, dtype=np.float32)
    # Bright specular neon street light
    arr[60:80, 180:220] = [255, 250, 240]
    arr[140:150, 80:100] = [255, 245, 220]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def test_scene_classification_portrait(portrait_image):
    res = classify_scene_content(portrait_image)
    assert res["is_photograph"] is True
    assert res["scene_genre"] == "portrait"
    assert res["subject_profile"]["has_human_subject"] is True
    assert "kodak_portra_400" in res["adaptive_recommendations"]["ideal_film_stocks"]


def test_scene_classification_landscape(landscape_image):
    res = classify_scene_content(landscape_image)
    assert res["is_photograph"] is True
    assert res["scene_genre"] == "landscape_nature"
    assert res["environment"]["has_foliage"] is True
    assert "fuji_velvia_50" in res["adaptive_recommendations"]["ideal_film_stocks"]


def test_all_13_film_stocks(portrait_image):
    stocks = list_available_film_stocks()
    assert len(stocks) == 13

    for stock_key in stocks.keys():
        graded = apply_film_stock(portrait_image, stock_name=stock_key, protect_skin=True)
        assert graded.size == portrait_image.size
        assert graded.mode == "RGB"


def test_film_halation(night_street_image):
    out = apply_film_halation(night_street_image, threshold=200.0, radius=15.0, intensity=0.8)
    assert out.size == night_street_image.size
    # Halation adds red warmth around speculars
    arr_in = np.array(night_street_image)
    arr_out = np.array(out)
    # Check pixels near specular light have increased red channel
    assert int(arr_out[70, 200, 0]) >= int(arr_in[70, 200, 0])


def test_orton_effect(landscape_image):
    out = apply_orton_effect(landscape_image, strength=0.35, blur_radius=20.0)
    assert out.size == landscape_image.size


def test_bleach_bypass(portrait_image):
    out = apply_bleach_bypass(portrait_image, strength=0.5, contrast_boost=1.2)
    assert out.size == portrait_image.size


def test_dehaze_image(landscape_image):
    out = dehaze_image(landscape_image, strength=0.6, window_size=11)
    assert out.size == landscape_image.size


def test_kelvin_color_temperature(portrait_image):
    # Warm (3200K)
    warm = set_color_temperature_kelvin(portrait_image, kelvin=3200, tint=0.0)
    # Cool (8500K)
    cool = set_color_temperature_kelvin(portrait_image, kelvin=8500, tint=0.0)
    
    arr_w = np.array(warm)
    arr_c = np.array(cool)
    # Warm image has higher red-to-blue ratio than cool image
    ratio_w = float(np.mean(arr_w[..., 0])) / float(np.mean(arr_w[..., 2]))
    ratio_c = float(np.mean(arr_c[..., 0])) / float(np.mean(arr_c[..., 2]))
    assert ratio_w > ratio_c


def test_photographic_grain(portrait_image):
    out = add_photographic_grain(portrait_image, amount=30.0, size=1.0, roughness=0.5)
    assert out.size == portrait_image.size


def test_smart_develop_workflow(portrait_image):
    developed, report = smart_develop(portrait_image, target_mood="auto")
    assert developed.size == portrait_image.size
    assert report["scene_diagnosis"]["scene_genre"] == "portrait"
    assert report["selected_stock"] == "kodak_portra_400"
    assert len(report["applied_workflow_steps"]) > 0


def test_mcp_new_tools_dispatch(portrait_image):
    canvas = Canvas.from_image(portrait_image)
    set_active_canvas(canvas)

    # 1. Classify scene
    res = tools.tool_classify_scene()
    assert res["is_photograph"] is True

    # 2. List film stocks
    res_list = tools.tool_list_film_stocks()
    assert len(res_list["film_stocks"]) == 13

    # 3. Apply Film Stock
    res_stock = tools.tool_apply_film_stock("cinestill_800t")
    assert res_stock["status"] == "success"

    # 4. Apply Halation
    res_hal = tools.tool_apply_film_halation()
    assert res_hal["status"] == "success"

    # 5. Apply Orton
    res_ort = tools.tool_apply_orton_effect()
    assert res_ort["status"] == "success"

    # 6. Apply Bleach Bypass
    res_bb = tools.tool_apply_bleach_bypass()
    assert res_bb["status"] == "success"

    # 7. Dehaze
    res_dh = tools.tool_dehaze_image()
    assert res_dh["status"] == "success"

    # 8. Kelvin
    res_k = tools.tool_set_color_temperature_kelvin(kelvin=4800, tint=5.0)
    assert res_k["status"] == "success"

    # 9. Grain
    res_gr = tools.tool_add_photographic_grain(amount=18.0)
    assert res_gr["status"] == "success"

    # 10. Smart develop
    res_dev = tools.tool_smart_develop(target_mood="auto")
    assert res_dev["status"] == "success"
