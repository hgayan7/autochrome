"""Code Snippet Beautifier: Renders syntax-highlighted code cards in sleek macOS frames with mesh gradient backdrops (Carbon / Ray.so style)."""

import re
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

from autochrome.engine.mockup import generate_gradient_backdrop


SYNTAX_COLORS = {
    "keyword": (255, 123, 114, 255),    # Coral Red
    "function": (210, 168, 255, 255),   # Violet Purple
    "string": (165, 214, 255, 255),     # Soft Cyan
    "number": (121, 192, 255, 255),     # Sky Blue
    "comment": (139, 148, 158, 255),    # Muted Slate
    "default": (230, 237, 243, 255),    # Crisp White
    "linenum": (110, 118, 129, 255),    # Dim Grey
}

KEYWORDS = {
    "def", "class", "import", "from", "return", "if", "elif", "else", "for", "while",
    "try", "except", "with", "as", "async", "await", "function", "const", "let", "var"
}


def tokenize_python_line(line: str) -> List[Tuple[str, str]]:
    """Simple syntax tokenizer for code presentation."""
    if not line:
        return [("", "default")]
    
    tokens = []
    # Comment
    if "#" in line:
        code_part, comment_part = line.split("#", 1)
        tokens.extend(tokenize_code_segment(code_part))
        tokens.append(("#" + comment_part, "comment"))
        return tokens

    return tokenize_code_segment(line)


def tokenize_code_segment(segment: str) -> List[Tuple[str, str]]:
    tokens = []
    # Match strings, identifiers, numbers, operators
    pattern = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\b\d+\b|\b[a-zA-Z_]\w*\b|[^\s\w]+|\s+)')
    matches = pattern.findall(segment)
    
    for m in matches:
        if m.startswith(('"', "'")):
            tokens.append((m, "string"))
        elif m in KEYWORDS:
            tokens.append((m, "keyword"))
        elif m.isdigit():
            tokens.append((m, "number"))
        elif re.match(r'^[a-zA-Z_]\w*\(', m):
            tokens.append((m, "function"))
        else:
            tokens.append((m, "default"))
    return tokens


def render_code_snippet(
    code_text: str,
    language: str = "python",
    title: str = "script.py",
    backdrop: str = "gradient_slate",
    padding: int = 60,
    show_line_numbers: bool = True,
) -> Image.Image:
    """Renders a syntax-highlighted code snippet card with macOS window bezel and gradient backdrop."""
    lines = code_text.strip().splitlines()
    if not lines:
        lines = ["# No code provided"]

    font = ImageFont.load_default()
    line_h = 18
    char_w = 7.2

    max_line_len = max(len(l) for l in lines)
    gutter_w = 40 if show_line_numbers else 16
    content_w = int(max_line_len * char_w) + gutter_w + 32
    content_h = len(lines) * line_h + 32

    win_w = max(420, content_w)
    titlebar_h = 36
    win_h = content_h + titlebar_h
    corner_r = 12

    # 1. Draw Window
    window = Image.new("RGBA", (win_w, win_h), (0, 0, 0, 0))
    win_draw = ImageDraw.Draw(window)

    # Dark window base
    win_draw.rounded_rectangle([(0, 0), (win_w - 1, win_h - 1)], radius=corner_r, fill=(18, 20, 24, 255), outline=(255, 255, 255, 25), width=1)

    # Traffic light dots (Red, Yellow, Green)
    dots = [(14, 18, (255, 95, 87)), (34, 18, (254, 188, 46)), (54, 18, (40, 200, 64))]
    for x, y, col in dots:
        win_draw.ellipse([(x - 5, y - 5), (x + 5, y + 5)], fill=col)

    # Title text
    bbox = win_draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    win_draw.text(((win_w - tw) // 2, 12), title, fill=(139, 148, 158, 255), font=font)

    # Render code lines with syntax colors
    for idx, line in enumerate(lines):
        y_pos = titlebar_h + 16 + idx * line_h
        
        # Line number
        if show_line_numbers:
            ln_str = str(idx + 1).rjust(3)
            win_draw.text((16, y_pos), ln_str, fill=SYNTAX_COLORS["linenum"], font=font)

        # Tokens
        tokens = tokenize_python_line(line)
        cur_x = gutter_w + 16
        for text, token_type in tokens:
            col = SYNTAX_COLORS.get(token_type, SYNTAX_COLORS["default"])
            win_draw.text((cur_x, y_pos), text, fill=col, font=font)
            t_bbox = win_draw.textbbox((0, 0), text, font=font)
            cur_x += (t_bbox[2] - t_bbox[0])

    # 2. Composite onto Backdrop with Drop Shadow
    bg_w = win_w + padding * 2
    bg_h = win_h + padding * 2
    backdrop_img = generate_gradient_backdrop(bg_w, bg_h, preset=backdrop)

    # Drop shadow
    shadow = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([(padding, padding + 8), (padding + win_w, padding + win_h + 8)], radius=corner_r, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=24))

    backdrop_img.paste(shadow, (0, 0), shadow)
    backdrop_img.paste(window, (padding, padding), window)

    return backdrop_img.convert("RGB")
