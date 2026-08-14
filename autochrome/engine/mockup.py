"""CleanShot-style Mockup Engine: macOS window frames, drop shadows, and gradient backdrops."""

from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from autochrome.types import MockupParams, ColorRGBA


GRADIENTS = {
    "mesh_sunset": [
        (255, 94, 98),   # Coral red
        (255, 153, 102), # Peach
        (138, 43, 226),  # Violet
    ],
    "mesh_ocean": [
        (0, 198, 255),   # Aqua
        (0, 114, 255),   # Deep blue
        (58, 28, 113),   # Purple navy
    ],
    "gradient_slate": [
        (30, 41, 59),    # Slate 800
        (15, 23, 42),    # Slate 900
        (2, 6, 23),      # Slate 950
    ],
    "gradient_purple": [
        (120, 50, 220),
        (70, 20, 140),
        (25, 10, 60),
    ],
    "solid_dark": [
        (24, 24, 27),
        (24, 24, 27),
        (24, 24, 27),
    ],
}


def generate_gradient_backdrop(width: int, height: int, preset: str = "mesh_sunset") -> Image.Image:
    """Generates a smooth multi-stop diagonal gradient backdrop."""
    colors = GRADIENTS.get(preset, GRADIENTS["mesh_sunset"])
    c1, c2, c3 = colors[0], colors[1], colors[2]

    # Create coordinate grids
    y, x = np.mgrid[0:height, 0:width]
    # Diagonal normalized progress [0, 1]
    t = (x / float(width) + y / float(height)) / 2.0

    r = np.where(t <= 0.5, c1[0] + (c2[0] - c1[0]) * (t * 2.0), c2[0] + (c3[0] - c2[0]) * ((t - 0.5) * 2.0))
    g = np.where(t <= 0.5, c1[1] + (c2[1] - c1[1]) * (t * 2.0), c2[1] + (c3[1] - c2[1]) * ((t - 0.5) * 2.0))
    b = np.where(t <= 0.5, c1[2] + (c2[2] - c1[2]) * (t * 2.0), c2[2] + (c3[2] - c2[2]) * ((t - 0.5) * 2.0))
    a = np.full((height, width), 255, dtype=np.float32)

    arr = np.stack([r, g, b, a], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, mode="RGBA")


def beautify_screenshot(image: Image.Image, params: MockupParams) -> Image.Image:
    """Wraps a screenshot in a sleek macOS window frame with traffic lights, drop shadow, and gradient backdrop."""
    src_img = image.convert("RGBA")
    src_w, src_h = src_img.size

    titlebar_h = 36 if params.frame_type in ["macos_dark", "macos_light", "browser_window"] else 0
    win_w = src_w
    win_h = src_h + titlebar_h
    corner_r = params.corner_radius

    # 1. Create the framed window image
    window = Image.new("RGBA", (win_w, win_h), (0, 0, 0, 0))
    win_draw = ImageDraw.Draw(window)

    # Background color for window titlebar / base
    if params.frame_type == "macos_dark":
        tb_color = (36, 37, 38, 255)
        border_color = (255, 255, 255, 30)
    elif params.frame_type == "macos_light":
        tb_color = (240, 240, 243, 255)
        border_color = (0, 0, 0, 30)
    elif params.frame_type == "browser_window":
        tb_color = (40, 42, 48, 255)
        border_color = (255, 255, 255, 35)
    else:
        tb_color = (0, 0, 0, 0)
        border_color = (0, 0, 0, 0)

    # Draw rounded window base
    win_draw.rounded_rectangle([(0, 0), (win_w - 1, win_h - 1)], radius=corner_r, fill=tb_color)

    # Traffic light dots (Red, Yellow, Green)
    if titlebar_h > 0:
        dot_y = titlebar_h // 2
        # Red
        win_draw.ellipse([(16, dot_y - 6), (28, dot_y + 6)], fill=(255, 95, 87, 255))
        # Yellow
        win_draw.ellipse([(36, dot_y - 6), (48, dot_y + 6)], fill=(254, 188, 46, 255))
        # Green
        win_draw.ellipse([(56, dot_y - 6), (68, dot_y + 6)], fill=(40, 200, 64, 255))

        if params.frame_type == "browser_window":
            # Search / URL pill
            pill_x0 = 84
            pill_x1 = win_w - 84
            win_draw.rounded_rectangle([(pill_x0, dot_y - 10), (pill_x1, dot_y + 10)], radius=6, fill=(255, 255, 255, 20))

    # Mask and paste screenshot with bottom rounded corners
    src_mask = Image.new("L", (src_w, src_h), 255)
    if corner_r > 0:
        src_mask_draw = ImageDraw.Draw(src_mask)
        # Rounded bottom mask
        src_mask_draw.rectangle([(0, 0), (src_w, src_h - corner_r)], fill=255)
        src_mask_draw.rounded_rectangle([(0, 0), (src_w - 1, src_h - 1)], radius=corner_r, fill=255)

    window.paste(src_img, (0, titlebar_h), src_mask)

    # Fine window outline border
    win_draw.rounded_rectangle([(0, 0), (win_w - 1, win_h - 1)], radius=corner_r, outline=border_color, width=1)

    # 2. Add Drop Shadow
    pad = params.padding
    canvas_w = win_w + pad * 2
    canvas_h = win_h + pad * 2

    shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    # Shadow offset + blur
    shadow_offset_y = 12
    shadow_draw.rounded_rectangle(
        [(pad, pad + shadow_offset_y), (pad + win_w, pad + win_h + shadow_offset_y)],
        radius=corner_r + 4,
        fill=(0, 0, 0, int(255 * params.shadow_opacity)),
    )
    shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=params.shadow_blur))

    # 3. Create Backdrop Canvas
    if params.backdrop != "transparent":
        canvas = generate_gradient_backdrop(canvas_w, canvas_h, params.backdrop)
    else:
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    # Composite: Backdrop -> Drop Shadow -> Window
    canvas = Image.alpha_composite(canvas, shadow_blurred)
    canvas.paste(window, (pad, pad), window)
    return canvas
