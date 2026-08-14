"""Vector Annotation Engine: Curved & Straight Arrows, Callouts, Highlighters, Loupe Magnifiers, and Step Badges."""

import math
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

from autochrome.types import ArrowParams, CalloutParams, LoupeParams, BadgeParams, ColorRGBA


def draw_arrow(image: Image.Image, params: ArrowParams) -> Image.Image:
    """Draws a clean, anti-aliased vector arrow with optional smooth curvature."""
    img_rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x0, y0 = float(params.start_x), float(params.start_y)
    x1, y1 = float(params.end_x), float(params.end_y)

    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist < 5:
        return image

    color = ColorRGBA.from_hex(params.color).to_tuple()
    head_size = params.head_size
    stroke_w = params.stroke_width

    if abs(params.curvature) > 0.05:
        # Quadratic Bezier Curve
        # Control point perpendicular to midpoint
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        perp_x, perp_y = -dy / dist, dx / dist
        cx = mx + perp_x * (params.curvature * dist * 0.4)
        cy = my + perp_y * (params.curvature * dist * 0.4)

        # Generate smooth polyline points
        steps = 40
        curve_pts = []
        for i in range(steps + 1):
            t = i / float(steps)
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
            curve_pts.append((bx, by))

        # Draw smooth line
        draw.line(curve_pts, fill=color, width=stroke_w, joint="curve")

        # Arrow head angle derived from last tangent segment
        tx = curve_pts[-1][0] - curve_pts[-3][0]
        ty = curve_pts[-1][1] - curve_pts[-3][1]
        angle = math.atan2(ty, tx)
    else:
        # Straight arrow
        draw.line([(x0, y0), (x1, y1)], fill=color, width=stroke_w)
        angle = math.atan2(dy, dx)

    # Draw Arrowhead
    arrow_angle = math.pi / 6.0  # 30 degrees
    p1 = (x1 - head_size * math.cos(angle - arrow_angle), y1 - head_size * math.sin(angle - arrow_angle))
    p2 = (x1 - head_size * math.cos(angle + arrow_angle), y1 - head_size * math.sin(angle + arrow_angle))
    draw.polygon([(x1, y1), p1, p2], fill=color)

    # Subtle drop shadow for crisp visibility
    shadow = overlay.filter(ImageFilter.GaussianBlur(radius=2))
    shadow_np = np.array(shadow, dtype=np.float32)
    shadow_np[..., 3] = shadow_np[..., 3] * 0.4
    shadow_img = Image.fromarray(shadow_np.astype(np.uint8), mode="RGBA")

    composite = Image.alpha_composite(img_rgba, shadow_img)
    return Image.alpha_composite(composite, overlay)


def draw_arrow_with_label(
    image: Image.Image,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    label_text: str,
    color: str = "#00E5FF",
    stroke_width: int = 3,
    curvature: float = 0.0,
    label_position: str = "start", # "start", "mid"
) -> Image.Image:
    """Draws an arrow with an embedded sleek pill badge displaying the descriptive label."""
    img_rgba = image.convert("RGBA")
    
    # 1. Draw arrow
    params = ArrowParams(
        start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y,
        color=color, stroke_width=stroke_width, curvature=curvature, head_size=16
    )
    img_with_arrow = draw_arrow(img_rgba, params)

    # 2. Draw stylish pill badge with label at start_x, start_y
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x, pad_y = 10, 6
    bx0 = start_x - tw // 2 - pad_x
    by0 = start_y - th // 2 - pad_y
    bx1 = bx0 + tw + pad_x * 2
    by1 = by0 + th + pad_y * 2

    # Draw rounded pill badge with shadow
    bg_color = ColorRGBA.from_hex(color).to_tuple()
    draw.rounded_rectangle([(bx0 - 1, by0 - 1), (bx1 + 1, by1 + 1)], radius=6, fill=(15, 23, 42, 240), outline=bg_color, width=2)
    draw.text((bx0 + pad_x, by0 + pad_y - 1), label_text, fill=(255, 255, 255, 255), font=font)

    return Image.alpha_composite(img_with_arrow, overlay)


def draw_callout_box(image: Image.Image, params: CalloutParams) -> Image.Image:
    """Draws a rounded spotlight callout box with optional label tag."""
    img_rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x0, y0 = params.x, params.y
    x1, y1 = params.x + params.width, params.y + params.height
    border_color = ColorRGBA.from_hex(params.border_color).to_tuple()
    fill_color = ColorRGBA.from_hex(params.fill_color).to_tuple() if params.fill_color else None

    # Rounded rectangle
    draw.rounded_rectangle(
        [(x0, y0), (x1, y1)],
        radius=params.corner_radius,
        outline=border_color,
        fill=fill_color,
        width=params.stroke_width,
    )

    # Optional label badge at top-left
    if params.label:
        label_bg = ColorRGBA.from_hex(params.label_bg or params.border_color).to_tuple()
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), params.label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        badge_pad_x, badge_pad_y = 8, 4
        bx0 = x0 + 8
        by0 = y0 - (th + badge_pad_y * 2) // 2
        bx1 = bx0 + tw + badge_pad_x * 2
        by1 = by0 + th + badge_pad_y * 2

        draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=4, fill=label_bg)
        draw.text((bx0 + badge_pad_x, by0 + badge_pad_y - 1), params.label, fill=(255, 255, 255, 255), font=font)

    return Image.alpha_composite(img_rgba, overlay)


def draw_highlighter(image: Image.Image, x: int, y: int, width: int, height: int, color_hex: str = "#FFCC00", opacity: float = 0.4) -> Image.Image:
    """Draws a semi-transparent highlighter marker rectangle."""
    img_rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    c = ColorRGBA.from_hex(color_hex, alpha=int(255 * opacity)).to_tuple()
    draw.rounded_rectangle([(x, y), (x + width, y + height)], radius=4, fill=c)
    return Image.alpha_composite(img_rgba, overlay)


def add_numbered_badge(image: Image.Image, params: BadgeParams) -> Image.Image:
    """Adds a circular numbered tutorial step badge (e.g. 1, 2, 3)."""
    img_rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    cx, cy = params.x, params.y
    r = params.radius
    bg = ColorRGBA.from_hex(params.bg_color).to_tuple()
    fg = ColorRGBA.from_hex(params.text_color).to_tuple()

    # Draw circle with white stroke
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=bg, outline=(255, 255, 255, 240), width=2)

    # Center text number
    font = ImageFont.load_default()
    txt = str(params.number)
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 1), txt, fill=fg, font=font)

    return Image.alpha_composite(img_rgba, overlay)


def add_magnifier_loupe(image: Image.Image, params: LoupeParams) -> Image.Image:
    """Adds a high-end magnifying loupe glass circle showing a zoomed-in view of target region."""
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.size

    tx, ty = params.target_x, params.target_y
    lx, ly = params.loupe_x, params.loupe_y
    r = params.radius
    zoom = params.zoom_factor

    # 1. Extract target region for zoom
    crop_radius = int(r / zoom)
    x0 = max(0, tx - crop_radius)
    y0 = max(0, ty - crop_radius)
    x1 = min(w, tx + crop_radius)
    y1 = min(h, ty + crop_radius)

    cropped = img_rgba.crop((x0, y0, x1, y1))
    zoomed = cropped.resize((r * 2, r * 2), Image.Resampling.LANCZOS)

    # 2. Circular mask for loupe
    mask = Image.new("L", (r * 2, r * 2), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([(0, 0), (r * 2 - 1, r * 2 - 1)], fill=255)

    # 3. Create Loupe Layer with drop shadow & sleek border
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(zoomed, (lx - r, ly - r), mask)

    draw = ImageDraw.Draw(overlay)
    border_col = ColorRGBA.from_hex(params.border_color).to_tuple()
    # Crisp ring border
    draw.ellipse([(lx - r, ly - r), (lx + r, ly + r)], outline=border_col, width=params.border_width)
    # Inner subtle rim
    draw.ellipse([(lx - r + 3, ly - r + 3), (lx + r - 3, ly + r - 3)], outline=(255, 255, 255, 180), width=1)

    # 4. Optional target pin line connecting target to loupe
    if params.show_pin:
        draw.line([(tx, ty), (lx, ly)], fill=border_col, width=2)
        draw.ellipse([(tx - 4, ty - 4), (tx + 4, ty + 4)], fill=border_col, outline=(255, 255, 255, 255), width=2)

    return Image.alpha_composite(img_rgba, overlay)
