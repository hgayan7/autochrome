"""Advanced Optical Physics, Halation Bloom, Orton Diffusion, Bleach Bypass, Dehaze & Film Grain."""

from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter
import cv2


def apply_film_halation(
    image: Image.Image,
    threshold: float = 215.0,
    radius: float = 24.0,
    intensity: float = 0.65,
    tint_rgb: Tuple[int, int, int] = (255, 55, 20),
) -> Image.Image:
    """Simulates CineStill / Motion Picture analog film halation (crimson specular bloom).
    
    In real film without an anti-halation remjet layer, intense specular light penetrates 
    the emulsion, reflects off the camera pressure plate, and scatters back into the red-sensitive bottom layer.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)

    # 1. Compute luminance map
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]

    # 2. Isolate specular highlights
    # Smooth threshold curve above threshold (e.g. 215)
    highlight_mask = np.clip((lum - threshold) / (255.0 - threshold), 0.0, 1.0)
    
    if np.max(highlight_mask) < 0.01:
        # No significant highlights to bloom
        return image

    # 3. Create tinted halation layer
    tint_r, tint_g, tint_b = tint_rgb
    halation_layer = np.zeros_like(arr)
    halation_layer[..., 0] = highlight_mask * tint_r
    halation_layer[..., 1] = highlight_mask * tint_g
    halation_layer[..., 2] = highlight_mask * tint_b

    # 4. Multi-scale Gaussian scatter (optical diffusion)
    # Scatter mostly into red channel with softer glow into green
    blur_r = gaussian_filter(halation_layer[..., 0], sigma=radius)
    blur_g = gaussian_filter(halation_layer[..., 1], sigma=radius * 0.65)
    blur_b = gaussian_filter(halation_layer[..., 2], sigma=radius * 0.4)

    scattered = np.stack([blur_r, blur_g, blur_b], axis=-1) * intensity

    # 5. Screen blend mode: 1 - (1 - A)*(1 - B)
    # Normed 0-1
    base_norm = arr / 255.0
    scat_norm = np.clip(scattered / 255.0, 0.0, 1.0)
    screened = 1.0 - (1.0 - base_norm) * (1.0 - scat_norm)
    
    out_arr = np.clip(screened * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")


def apply_orton_effect(
    image: Image.Image,
    strength: float = 0.30,
    blur_radius: float = 30.0,
    glow_mode: str = "soft_light",
) -> Image.Image:
    """Applies the classic Orton Effect (Dreamy Glow Diffusion) while preserving micro-contrast.
    
    Originated by Michael Orton in the 1980s by sandwiching a sharp slide with an overexposed out-of-focus slide.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)

    # 1. Overexposed, blurred glow layer
    # Boost brightness & contrast slightly before blurring
    brightened = np.clip((arr - 128.0) * 1.15 + 128.0 + 20.0, 0.0, 255.0)
    blurred = gaussian_filter(brightened, sigma=[blur_radius, blur_radius, 0])

    # 2. Blend modes (Soft Light or Screen)
    base_norm = arr / 255.0
    glow_norm = blurred / 255.0

    if glow_mode == "screen":
        blended = 1.0 - (1.0 - base_norm) * (1.0 - glow_norm)
    else:  # Soft Light (Photoshop pegtop formula)
        blended = (1.0 - 2.0 * glow_norm) * (base_norm ** 2) + 2.0 * glow_norm * base_norm

    # 3. Linear interpolation with strength
    final_norm = base_norm * (1.0 - strength) + blended * strength
    out_arr = np.clip(final_norm * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")


def apply_bleach_bypass(
    image: Image.Image,
    strength: float = 0.60,
    contrast_boost: float = 1.25,
) -> Image.Image:
    """Simulates chemical Bleach Bypass (Silver Retention) for a gritty, high-contrast cinematic look.
    
    Retains metallic silver in the film emulsion, creating desaturated tones and deep punchy blacks.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)

    # 1. Compute high-contrast grayscale luminance
    lum = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    # S-curve contrast on luminance
    lum_norm = lum / 255.0
    lum_contrast = np.clip((lum_norm - 0.5) * contrast_boost + 0.5, 0.0, 1.0)
    silver_layer = np.stack([lum_contrast] * 3, axis=-1)

    # 2. Overlay blend mode
    base_norm = arr / 255.0
    overlay = np.where(
        base_norm < 0.5,
        2.0 * base_norm * silver_layer,
        1.0 - 2.0 * (1.0 - base_norm) * (1.0 - silver_layer)
    )

    # 3. Blend back with original
    final_norm = base_norm * (1.0 - strength) + overlay * strength
    out_arr = np.clip(final_norm * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")


def dehaze_image(
    image: Image.Image,
    strength: float = 0.70,
    window_size: int = 15,
) -> Image.Image:
    """Removes atmospheric fog, haze, and milkiness using Dark Channel Prior (DCP) physics."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32) / 255.0
    h, w, _ = arr.shape

    # 1. Compute Dark Channel: min over channels, then min filter over window
    min_channel = np.min(arr, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (window_size, window_size))
    dark_channel = cv2.erode(min_channel, kernel)

    # 2. Estimate Atmospheric Light (A) from top 0.1% brightest pixels in dark channel
    num_brightest = max(1, int(h * w * 0.001))
    dark_flat = dark_channel.flatten()
    arr_flat = arr.reshape(-1, 3)
    indices = np.argpartition(dark_flat, -num_brightest)[-num_brightest:]
    atm_light = np.max(arr_flat[indices], axis=0)
    atm_light = np.clip(atm_light, 0.7, 1.0)

    # 3. Transmission map estimation
    omega = strength * 0.95
    norm_arr = arr / atm_light
    min_norm_channel = np.min(norm_arr, axis=2)
    raw_transmission = 1.0 - omega * cv2.erode(min_norm_channel, kernel)

    # Refine transmission using fast guided/bilateral filter
    transmission = cv2.bilateralFilter(raw_transmission.astype(np.float32), d=7, sigmaColor=0.1, sigmaSpace=7)
    transmission = np.clip(transmission, 0.15, 1.0)

    # 4. Recover radiance J(x) = (I(x) - A) / max(t(x), t0) + A
    t_3d = np.stack([transmission] * 3, axis=-1)
    a_3d = np.array(atm_light).reshape(1, 1, 3)
    
    recovered = (arr - a_3d) / t_3d + a_3d
    recovered = np.clip(recovered, 0.0, 1.0)

    out_arr = (recovered * 255.0).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")


def set_color_temperature_kelvin(
    image: Image.Image,
    kelvin: int = 5500,
    tint: float = 0.0,
) -> Image.Image:
    """Adjusts physical Color Temperature (2000K-12000K) and Tint using Planckian Blackbody Approximation."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)

    # 1. Tanner Helland Kelvin to RGB multiplier curve
    k = max(2000, min(12000, kelvin))
    t = k / 100.0

    # Red
    if t <= 66.0:
        r_mult = 255.0
    else:
        r_mult = 329.698727446 * ((t - 60.0) ** -0.1332047592)

    # Green
    if t <= 66.0:
        g_mult = 99.4708025861 * np.log(t) - 161.1195681661
    else:
        g_mult = 288.1221695283 * ((t - 60.0) ** -0.0755148492)

    # Blue
    if t <= 19.0:
        b_mult = 0.0
    elif t <= 66.0:
        b_mult = 138.5177312231 * np.log(t - 10.0) - 305.0447927307
    else:
        b_mult = 255.0

    r_mult = np.clip(r_mult, 0.0, 255.0) / 255.0
    g_mult = np.clip(g_mult, 0.0, 255.0) / 255.0
    b_mult = np.clip(b_mult, 0.0, 255.0) / 255.0

    # Neutral point is ~6500K (D65 daylight)
    # Calculate relative adjustment factors
    d65_r, d65_g, d65_b = 1.0, 0.99, 1.0
    scale_r = r_mult / d65_r
    scale_g = g_mult / d65_g
    scale_b = b_mult / d65_b

    # Tint adjustment (Green vs Magenta: tint -100 = green, +100 = magenta)
    scale_g *= (1.0 - (tint / 200.0))

    # Apply scaling with luminance preservation
    lum_before = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    
    scaled = np.zeros_like(arr)
    scaled[..., 0] = arr[..., 0] * scale_r
    scaled[..., 1] = arr[..., 1] * scale_g
    scaled[..., 2] = arr[..., 2] * scale_b

    lum_after = 0.2126 * scaled[..., 0] + 0.7152 * scaled[..., 1] + 0.0722 * scaled[..., 2] + 1e-6
    lum_ratio = np.clip(lum_before / lum_after, 0.7, 1.3)

    final_arr = np.clip(scaled * lum_ratio[..., np.newaxis], 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(final_arr, mode="RGB")


def add_photographic_grain(
    image: Image.Image,
    amount: float = 24.0,
    size: float = 1.0,
    roughness: float = 0.5,
    luminance_aware: bool = True,
) -> Image.Image:
    """Generates authentic density-dependent silver halide film grain.
    
    Grain density peaks in midtones (sinusoidal response) and vanishes in pure speculars and deep blacks.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32)
    h, w, _ = arr.shape

    # 1. Generate organic Gaussian noise field
    np.random.seed()
    noise = np.random.normal(0.0, amount, (h, w)).astype(np.float32)

    # 2. Scale grain size if needed (spatial filtering)
    if size > 1.0:
        noise = gaussian_filter(noise, sigma=size * 0.6)

    # 3. Luminance-aware masking: f(L) = sin(pi * L), where L in [0, 1]
    if luminance_aware:
        lum = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]) / 255.0
        # Bell curve / sinusoidal response peaking in Zone V (midtones ~0.5)
        weight = np.sin(np.pi * np.clip(lum, 0.0, 1.0)) ** (1.0 + (1.0 - roughness) * 0.5)
        noise = noise * weight

    # 4. Overlay noise with base image
    noise_3d = np.stack([noise] * 3, axis=-1)
    out_arr = np.clip(arr + noise_3d, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out_arr, mode="RGB")
