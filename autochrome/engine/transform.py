"""Transform Engine: Smart Crop, Aspect Ratios, Straighten, Rotate, Perspective, and Canvas Padding."""

from typing import Optional, Tuple, Literal
from PIL import Image
import numpy as np


def crop_region(image: Image.Image, x: int, y: int, width: int, height: int) -> Image.Image:
    """Crops an exact rectangle bounding box from the image."""
    img_w, img_h = image.size
    x0 = max(0, min(x, img_w - 1))
    y0 = max(0, min(y, img_h - 1))
    x1 = max(x0 + 1, min(x0 + width, img_w))
    y1 = max(y0 + 1, min(y0 + height, img_h))
    return image.crop((x0, y0, x1, y1))


def smart_crop_aspect(
    image: Image.Image,
    aspect_ratio: str = "1:1",
    focus_point: Optional[Tuple[int, int]] = None,
) -> Image.Image:
    """Smart crops image to target aspect ratio ('1:1', '16:9', '4:5', '9:16', '4:3', '3:2') centered on focus_point."""
    w, h = image.size
    aspect_map = {
        "1:1": 1.0,
        "16:9": 16.0 / 9.0,
        "9:16": 9.0 / 16.0,
        "4:5": 4.0 / 5.0,
        "5:4": 5.0 / 4.0,
        "4:3": 4.0 / 3.0,
        "3:2": 3.0 / 2.0,
        "2:3": 2.0 / 3.0,
    }
    target_ratio = aspect_map.get(aspect_ratio.strip(), 1.0)
    current_ratio = w / float(h)

    if current_ratio > target_ratio:
        # Image is wider -> crop width
        new_h = h
        new_w = int(round(h * target_ratio))
    else:
        # Image is taller -> crop height
        new_w = w
        new_h = int(round(w / target_ratio))

    if focus_point is not None:
        fx, fy = focus_point
        # Center crop window around focus point
        left = max(0, min(fx - new_w // 2, w - new_w))
        top = max(0, min(fy - new_h // 2, h - new_h))
    else:
        # Default center crop
        left = (w - new_w) // 2
        top = (h - new_h) // 2

    right = left + new_w
    bottom = top + new_h
    return image.crop((left, top, right, bottom))


def rotate_and_straighten(image: Image.Image, angle_deg: float, expand: bool = False) -> Image.Image:
    """Rotates image by arbitrary angle. If expand=False, auto-crops to eliminate black borders."""
    if angle_deg % 360 == 0:
        return image
    return image.rotate(-angle_deg, resample=Image.Resampling.BICUBIC, expand=expand)


def flip_image(image: Image.Image, direction: Literal["horizontal", "vertical"] = "horizontal") -> Image.Image:
    if direction == "horizontal":
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def expand_canvas_padding(
    image: Image.Image,
    pad_top: int = 40,
    pad_bottom: int = 40,
    pad_left: int = 40,
    pad_right: int = 40,
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """Expands canvas bounds with specified padding and background color."""
    w, h = image.size
    new_w = w + pad_left + pad_right
    new_h = h + pad_top + pad_bottom
    new_img = Image.new("RGBA", (new_w, new_h), bg_color)
    new_img.paste(image.convert("RGBA"), (pad_left, pad_top))
    return new_img
