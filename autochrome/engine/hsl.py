"""Professional 8-Channel HSL Color Mixer Engine (Lightroom / Capture One / Snapseed style)."""

from typing import Dict, Optional, Tuple
import numpy as np
from PIL import Image


# Hue ranges in degrees [0, 360)
COLOR_HUE_CENTERS = {
    "red": 0.0,
    "orange": 30.0,
    "yellow": 60.0,
    "green": 120.0,
    "aqua": 180.0,
    "blue": 240.0,
    "purple": 280.0,
    "magenta": 320.0,
}


def rgb_to_hsl(rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Converts normalized float RGB (H, W, 3) in [0, 1] to H in [0, 360), S in [0, 1], L in [0, 1]."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    # Luminance
    l = (cmax + cmin) / 2.0

    # Saturation
    s = np.zeros_like(l)
    non_zero = delta > 1e-6
    s[non_zero] = np.where(l[non_zero] <= 0.5, delta[non_zero] / (cmax[non_zero] + cmin[non_zero] + 1e-7), delta[non_zero] / (2.0 - cmax[non_zero] - cmin[non_zero] + 1e-7))

    # Hue
    h = np.zeros_like(l)
    r_max = non_zero & (cmax == r)
    g_max = non_zero & (cmax == g)
    b_max = non_zero & (cmax == b)

    h[r_max] = (60.0 * (((g[r_max] - b[r_max]) / delta[r_max]) % 6.0))
    h[g_max] = (60.0 * (((b[g_max] - r[g_max]) / delta[g_max]) + 2.0))
    h[b_max] = (60.0 * (((r[b_max] - g[b_max]) / delta[b_max]) + 4.0))

    return h, s, l


def hsl_to_rgb(h: np.ndarray, s: np.ndarray, l: np.ndarray) -> np.ndarray:
    """Converts H in [0, 360), S in [0, 1], L in [0, 1] back to normalized float RGB in [0, 1]."""
    c = (1.0 - np.abs(2.0 * l - 1.0)) * s
    h_prime = (h % 360.0) / 60.0
    x = c * (1.0 - np.abs((h_prime % 2.0) - 1.0))
    m = l - c / 2.0

    rgb = np.zeros((h.shape[0], h.shape[1], 3), dtype=np.float32)

    cond0 = (h_prime >= 0) & (h_prime < 1)
    cond1 = (h_prime >= 1) & (h_prime < 2)
    cond2 = (h_prime >= 2) & (h_prime < 3)
    cond3 = (h_prime >= 3) & (h_prime < 4)
    cond4 = (h_prime >= 4) & (h_prime < 5)
    cond5 = (h_prime >= 5) & (h_prime < 6)

    rgb[cond0] = np.stack([c[cond0], x[cond0], np.zeros_like(c[cond0])], axis=-1)
    rgb[cond1] = np.stack([x[cond1], c[cond1], np.zeros_like(c[cond1])], axis=-1)
    rgb[cond2] = np.stack([np.zeros_like(c[cond2]), c[cond2], x[cond2]], axis=-1)
    rgb[cond3] = np.stack([np.zeros_like(c[cond3]), x[cond3], c[cond3]], axis=-1)
    rgb[cond4] = np.stack([x[cond4], np.zeros_like(c[cond4]), c[cond4]], axis=-1)
    rgb[cond5] = np.stack([c[cond5], np.zeros_like(c[cond5]), x[cond5]], axis=-1)

    rgb += m[..., np.newaxis]
    return np.clip(rgb, 0.0, 1.0)


def apply_hsl_mixer(
    image: Image.Image,
    hue_shifts: Optional[Dict[str, float]] = None,
    saturation_shifts: Optional[Dict[str, float]] = None,
    luminance_shifts: Optional[Dict[str, float]] = None,
) -> Image.Image:
    """Applies selective 8-channel HSL color mixing (Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta).
    
    Parameters per channel:
    - hue_shift: -100 to +100 (shifts hue towards adjacent colors)
    - saturation_shift: -100 to +100 (desaturates or intensifies this specific color range)
    - luminance_shift: -100 to +100 (lightens or darkens this specific color range)
    """
    hue_shifts = hue_shifts or {}
    saturation_shifts = saturation_shifts or {}
    luminance_shifts = luminance_shifts or {}

    if not hue_shifts and not saturation_shifts and not luminance_shifts:
        return image

    img_rgba = image.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.float32)
    rgb = arr[..., :3] / 255.0
    alpha = arr[..., 3:4]

    h, s, l = rgb_to_hsl(rgb)

    for color_name, center_h in COLOR_HUE_CENTERS.items():
        dh = hue_shifts.get(color_name, 0.0)
        ds = saturation_shifts.get(color_name, 0.0)
        dl = luminance_shifts.get(color_name, 0.0)

        if dh == 0.0 and ds == 0.0 and dl == 0.0:
            continue

        # Compute angular distance from color center in degrees
        angle_diff = np.abs((h - center_h + 180.0) % 360.0 - 180.0)
        # Soft bell curve weight mask (width ~ 35 degrees)
        weight = np.clip(1.0 - (angle_diff / 35.0), 0.0, 1.0)
        weight = weight * weight * (3.0 - 2.0 * weight) # smooth hermite

        # Apply shifts
        if dh != 0.0:
            # Shift hue by up to +/- 30 degrees
            h = (h + weight * (dh / 100.0) * 30.0) % 360.0

        if ds != 0.0:
            sat_mult = 1.0 + weight * (ds / 100.0)
            s = np.clip(s * sat_mult, 0.0, 1.0)

        if dl != 0.0:
            lum_delta = weight * (dl / 100.0) * 0.35
            l = np.clip(l + lum_delta, 0.0, 1.0)

    out_rgb = hsl_to_rgb(h, s, l)
    out_arr = np.concatenate([np.clip(out_rgb, 0.0, 1.0) * 255.0, alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGBA")
