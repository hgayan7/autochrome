"""Privacy & Redaction Engine: Gaussian Blur, Pixelation Mosaic, and Blackout Boxes."""

from typing import Literal
from PIL import Image, ImageFilter, ImageDraw
import numpy as np


def blur_region(image: Image.Image, x: int, y: int, width: int, height: int, radius: int = 20) -> Image.Image:
    """Applies a smooth Gaussian blur to a target bounding box for privacy/redaction."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.size

    x0 = max(0, min(x, w - 1))
    y0 = max(0, min(y, h - 1))
    x1 = max(x0 + 1, min(x0 + width, w))
    y1 = max(y0 + 1, min(y0 + height, h))

    # Crop target region, blur it, and paste back
    cropped = img_rgba.crop((x0, y0, x1, y1))
    blurred = cropped.filter(ImageFilter.GaussianBlur(radius=radius))
    
    output = img_rgba.copy()
    output.paste(blurred, (x0, y0))
    return output


def pixelate_region(image: Image.Image, x: int, y: int, width: int, height: int, block_size: int = 12) -> Image.Image:
    """Applies a mosaic pixelation effect to redact sensitive information."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.size

    x0 = max(0, min(x, w - 1))
    y0 = max(0, min(y, h - 1))
    x1 = max(x0 + 1, min(x0 + width, w))
    y1 = max(y0 + 1, min(y0 + height, h))

    cropped = img_rgba.crop((x0, y0, x1, y1))
    cw, ch = cropped.size
    
    # Downsample and upsample nearest neighbor
    small_w = max(1, cw // block_size)
    small_h = max(1, ch // block_size)
    pixelated = cropped.resize((small_w, small_h), Image.Resampling.NEAREST).resize((cw, ch), Image.Resampling.NEAREST)

    output = img_rgba.copy()
    output.paste(pixelated, (x0, y0))
    return output


def blackout_region(image: Image.Image, x: int, y: int, width: int, height: int, color=(0, 0, 0, 255)) -> Image.Image:
    """Draws an opaque blackout bar over sensitive data."""
    img_rgba = image.convert("RGBA")
    draw = ImageDraw.Draw(img_rgba)
    draw.rectangle([(x, y), (x + width, y + height)], fill=color)
    return img_rgba
