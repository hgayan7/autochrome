"""Unit tests for Document Scanner and Code Snippet Beautifier."""

import pytest
import numpy as np
from PIL import Image

from autochrome.engine.scanner import scan_and_rectify_document, detect_document_quad
from autochrome.engine.code_beautifier import render_code_snippet


def test_document_scanner():
    # Synthetic white sheet on dark background
    arr = np.full((300, 300, 3), 30, dtype=np.uint8)
    arr[50:250, 50:250] = [240, 240, 240]
    img = Image.fromarray(arr, mode="RGB")

    scanned = scan_and_rectify_document(img, mode="enhanced_color")
    assert scanned.size[0] > 100
    assert scanned.size[1] > 100


def test_code_snippet_beautifier():
    code = """def calculate_exposure(iso, shutter, aperture):
    # Sunny 16 rule
    ev = 16.0
    return (iso * shutter) / (aperture ** 2)
"""
    rendered = render_code_snippet(code, language="python", title="exposure.py")
    assert rendered.size[0] >= 420
    assert rendered.size[1] >= 100
