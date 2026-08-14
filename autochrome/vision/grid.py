"""Visual Coordinate Grid Calibration Engine for Multimodal Vision Agents."""

from PIL import Image, ImageDraw, ImageFont


def generate_coordinate_grid_overlay(image: Image.Image, grid_step: int = 100, color: str = "#00E5FF", opacity: float = 0.6) -> Image.Image:
    """Overlays a crisp, semi-transparent coordinate grid with pixel coordinate labels.
    
    This enables Multimodal Vision LLMs (Claude, Gemini, GPT-4o) to visually identify
    exact (x, y) coordinates of any element without hallucination.
    """
    img_rgba = image.convert("RGBA")
    w, h = img_rgba.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    line_color = (0, 229, 255, int(255 * opacity))
    label_bg = (10, 10, 15, 200)
    label_fg = (255, 255, 255, 240)

    # Vertical grid lines
    for x in range(0, w, grid_step):
        draw.line([(x, 0), (x, h)], fill=line_color, width=1)
        # Label at top
        lbl = str(x)
        draw.rectangle([(x + 2, 2), (x + 30, 14)], fill=label_bg)
        draw.text((x + 4, 3), lbl, fill=label_fg, font=font)

    # Horizontal grid lines
    for y in range(0, h, grid_step):
        draw.line([(0, y), (w, y)], fill=line_color, width=1)
        # Label at left
        lbl = str(y)
        draw.rectangle([(2, y + 2), (28, y + 14)], fill=label_bg)
        draw.text((4, y + 3), lbl, fill=label_fg, font=font)

    # Add center crosshair
    cx, cy = w // 2, h // 2
    draw.line([(cx - 15, cy), (cx + 15, cy)], fill=(255, 59, 48, 220), width=2)
    draw.line([(cx, cy - 15), (cx, cy + 15)], fill=(255, 59, 48, 220), width=2)

    return Image.alpha_composite(img_rgba, overlay)
