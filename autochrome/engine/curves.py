"""Snapseed-grade Curves Engine: Multi-channel Tone Curves & Spline Interpolation."""

from typing import List, Dict
import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator
from autochrome.types import CurvePoint, CurveParams


PRESET_CURVES: Dict[str, List[CurvePoint]] = {
    "neutral": [
        CurvePoint(in_val=0, out_val=0),
        CurvePoint(in_val=255, out_val=255),
    ],
    "hard_contrast": [
        CurvePoint(in_val=0, out_val=0),
        CurvePoint(in_val=64, out_val=40),
        CurvePoint(in_val=192, out_val=215),
        CurvePoint(in_val=255, out_val=255),
    ],
    "brighten": [
        CurvePoint(in_val=0, out_val=0),
        CurvePoint(in_val=128, out_val=165),
        CurvePoint(in_val=255, out_val=255),
    ],
    "darken": [
        CurvePoint(in_val=0, out_val=0),
        CurvePoint(in_val=128, out_val=95),
        CurvePoint(in_val=255, out_val=255),
    ],
    "matte_vintage": [
        CurvePoint(in_val=0, out_val=35),
        CurvePoint(in_val=70, out_val=75),
        CurvePoint(in_val=180, out_val=190),
        CurvePoint(in_val=255, out_val=235),
    ],
    "cross_process": [
        CurvePoint(in_val=0, out_val=20),
        CurvePoint(in_val=80, out_val=55),
        CurvePoint(in_val=170, out_val=205),
        CurvePoint(in_val=255, out_val=245),
    ],
}


def build_lut(points: List[CurvePoint]) -> np.ndarray:
    """Constructs a 256-element Look-Up Table from control points using monotone cubic interpolation."""
    if not points or len(points) < 2:
        return np.arange(256, dtype=np.uint8)

    # Sort points by in_val
    sorted_pts = sorted(points, key=lambda p: p.in_val)
    x = [p.in_val for p in sorted_pts]
    y = [p.out_val for p in sorted_pts]

    # Ensure boundaries 0 and 255 exist
    if x[0] > 0:
        x.insert(0, 0)
        y.insert(0, 0)
    if x[-1] < 255:
        x.append(255)
        y.append(255)

    interpolator = PchipInterpolator(x, y)
    inputs = np.arange(256, dtype=np.float32)
    outputs = np.clip(interpolator(inputs), 0.0, 255.0).astype(np.uint8)
    return outputs


def apply_curves(image: Image.Image, params: CurveParams) -> Image.Image:
    """Applies tone curve to image channels."""
    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba)
    rgb = arr[..., :3]
    alpha = arr[..., 3:4]

    lut = build_lut(params.points)

    if params.channel == "rgb" or params.channel == "luminance":
        for c in range(3):
            rgb[..., c] = lut[rgb[..., c]]
    elif params.channel == "red":
        rgb[..., 0] = lut[rgb[..., 0]]
    elif params.channel == "green":
        rgb[..., 1] = lut[rgb[..., 1]]
    elif params.channel == "blue":
        rgb[..., 2] = lut[rgb[..., 2]]

    out_arr = np.concatenate([rgb, alpha], axis=-1)
    return Image.fromarray(out_arr, mode="RGBA")
