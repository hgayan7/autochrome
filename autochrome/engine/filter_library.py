"""Autochrome FilterLibrary Suite (Ported from Android FilterLibrary by Himshikhar Gayan).
Provides 16 classic and modern photo filters executing via fast deterministic NumPy/OpenCV matrix math.
"""

from enum import Enum
from typing import Dict, Any, List
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageFilter


class FilterType(str, Enum):
    INVERT = "invert"
    GRAYSCALE = "grayscale"
    CYAN_BOOST = "cyan_boost"
    MOODY_DARK = "moody_dark"
    CROSS_PROCESS = "cross_process"
    RETRO_WARM = "retro_warm"
    HIGH_KEY = "high_key"
    BRIGHTNESS_BOOST = "brightness_boost"
    DRAMATIC = "dramatic"
    COOL_BLUE = "cool_blue"
    POLAROID_70S = "polaroid_70s"
    SEPIA = "sepia"
    EMBOSS = "emboss"
    SOFT_BLUR = "soft_blur"
    CINEMATIC_POP = "cinematic_pop"
    WARM_SUNSET = "warm_sunset"


FILTER_DESCRIPTIONS: Dict[str, str] = {
    "invert": "Inverts color channels to create a striking negative effect",
    "grayscale": "Classic monochrome conversion using Rec.709 photographic luminance weights",
    "cyan_boost": "Boosts cyan and teal tones while cooling shadows",
    "moody_dark": "Deep compressed shadows with dramatic low-key tone curves",
    "cross_process": "Simulates analog C-41 in E-6 cross-processing with cyan/yellow splits",
    "retro_warm": "Warm vintage nostalgic color matrix with amber midtones",
    "high_key": "Luminous, ethereal high-key aesthetic with bright clean highlights",
    "brightness_boost": "Linear dynamic exposure boost with highlight protection",
    "dramatic": "High-contrast dynamic tone mapping with rich micro-textures",
    "cool_blue": "Cinematic cold blue color grade with crisp cool whites",
    "polaroid_70s": "Authentic 1970s instant film color matrix with lifted matte black floor",
    "sepia": "Traditional darkroom archival sepia duotone toning",
    "emboss": "3x3 directional spatial convolution relief filter",
    "soft_blur": "Dreamy, luminous soft-focus diffusion glow",
    "cinematic_pop": "Blockbuster movie grade: rich contrast, deep blacks, and punchy saturation",
    "warm_sunset": "Golden hour sunlight simulation with golden amber and coral hues",
}


def apply_filter_by_name(image: Image.Image, filter_name: str) -> Image.Image:
    """Applies one of the 16 FilterLibrary filters to a PIL Image."""
    f_key = filter_name.lower().strip().replace("-", "_").replace(" ", "_")
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)

    if f_key in ("invert", "1"):
        out_arr = 255.0 - arr

    elif f_key in ("grayscale", "2"):
        gray = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
        out_arr = np.stack([gray, gray, gray], axis=-1)

    elif f_key in ("cyan_boost", "3"):
        # Boost Blue and Green, cool down Red
        r = arr[..., 0] * 0.85
        g = np.clip(arr[..., 1] * 1.15 + 10.0, 0, 255)
        b = np.clip(arr[..., 2] * 1.25 + 15.0, 0, 255)
        out_arr = np.stack([r, g, b], axis=-1)

    elif f_key in ("moody_dark", "4"):
        # Dark tone curve with lifted shadow floor
        norm = arr / 255.0
        curve = np.power(norm, 1.45) * 0.88 + 0.04
        out_arr = np.clip(curve * 255.0, 0, 255)

    elif f_key in ("cross_process", "5"):
        # Cross processing: boost red in highlights, green/blue in shadows
        norm = arr / 255.0
        r = np.where(norm[..., 0] > 0.5, np.power(norm[..., 0], 0.8), np.power(norm[..., 0], 1.25))
        g = np.power(norm[..., 1], 1.1)
        b = np.where(norm[..., 2] < 0.5, norm[..., 2] * 1.2 + 0.08, norm[..., 2] * 0.9)
        out_arr = np.clip(np.stack([r, g, b], axis=-1) * 255.0, 0, 255)

    elif f_key in ("retro_warm", "6"):
        # Matrix: Warm amber shift
        r = np.clip(arr[..., 0] * 1.18 + 12.0, 0, 255)
        g = np.clip(arr[..., 1] * 1.05 + 4.0, 0, 255)
        b = arr[..., 2] * 0.82
        out_arr = np.stack([r, g, b], axis=-1)

    elif f_key in ("high_key", "7"):
        # Lift exposure and compress highlights cleanly
        norm = arr / 255.0
        lifted = np.power(norm, 0.72) * 1.15
        out_arr = np.clip(lifted * 255.0, 0, 255)

    elif f_key in ("brightness_boost", "8"):
        out_arr = np.clip(arr * 1.22 + 15.0, 0, 255)

    elif f_key in ("dramatic", "9"):
        # High-pass micro-contrast pop + S-curve
        gray = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (0, 0), 3.0)
        high_pass = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        norm = (arr / 255.0 - 0.5) * 1.35 + 0.5
        norm = np.clip(norm, 0.0, 1.0)
        out_arr = np.clip(norm * 255.0, 0, 255)

    elif f_key in ("cool_blue", "10"):
        r = arr[..., 0] * 0.82
        g = arr[..., 1] * 0.95
        b = np.clip(arr[..., 2] * 1.25 + 18.0, 0, 255)
        out_arr = np.stack([r, g, b], axis=-1)

    elif f_key in ("polaroid_70s", "11"):
        # Matte shadows (lifted black floor) + warm green/yellow tint
        norm = arr / 255.0
        r = np.clip(norm[..., 0] * 0.92 + 0.10, 0, 1)
        g = np.clip(norm[..., 1] * 0.95 + 0.08, 0, 1)
        b = np.clip(norm[..., 2] * 0.80 + 0.14, 0, 1)
        out_arr = np.clip(np.stack([r, g, b], axis=-1) * 255.0, 0, 255)

    elif f_key in ("sepia", "12"):
        # Standard Photographic Sepia 3x3 Color Matrix
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        out_arr = np.dot(arr, sepia_matrix.T)

    elif f_key in ("emboss", "13"):
        kernel = np.array([
            [-2, -1, 0],
            [-1,  1, 1],
            [ 0,  1, 2]
        ], dtype=np.float32)
        embossed = cv2.filter2D(arr.astype(np.uint8), -1, kernel) + 128
        out_arr = np.clip(embossed, 0, 255)

    elif f_key in ("soft_blur", "14"):
        blurred = cv2.GaussianBlur(arr.astype(np.uint8), (15, 15), 0).astype(np.float32)
        # Screen blend with original
        out_arr = 255.0 - ((255.0 - arr) * (255.0 - blurred) / 255.0)

    elif f_key in ("cinematic_pop", "15"):
        # Rich contrast S-curve + saturation pop
        hsv = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * 1.30, 0, 255)
        # S-curve on Value
        v_norm = hsv[..., 2] / 255.0
        v_scurve = np.where(v_norm < 0.5, 2.0 * v_norm * v_norm, 1.0 - 2.0 * (1.0 - v_norm) * (1.0 - v_norm))
        hsv[..., 2] = np.clip(v_scurve * 255.0, 0, 255)
        out_arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

    elif f_key in ("warm_sunset", "16"):
        # Golden hour sunset gradient
        r = np.clip(arr[..., 0] * 1.25 + 20.0, 0, 255)
        g = np.clip(arr[..., 1] * 1.08 + 8.0, 0, 255)
        b = np.clip(arr[..., 2] * 0.75 - 5.0, 0, 255)
        out_arr = np.stack([r, g, b], axis=-1)

    else:
        out_arr = arr

    return Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), mode="RGB")


def list_available_filters() -> List[Dict[str, str]]:
    """Returns a list of all 16 filters with descriptions."""
    return [{"name": k, "description": v} for k, v in FILTER_DESCRIPTIONS.items()]
