"""Layer blending algorithms implemented efficiently in NumPy."""

import numpy as np


def blend_normal(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Normal alpha blending: base, top are float arrays in [0, 1] with shape (H, W, 4)."""
    top_rgb = top[..., :3]
    top_a = top[..., 3:4] * opacity
    base_rgb = base[..., :3]
    base_a = base[..., 3:4]

    out_a = top_a + base_a * (1.0 - top_a)
    safe_out_a = np.where(out_a == 0, 1.0, out_a)

    out_rgb = (top_rgb * top_a + base_rgb * base_a * (1.0 - top_a)) / safe_out_a
    out = np.concatenate([out_rgb, out_a], axis=-1)
    return np.clip(out, 0.0, 1.0)


def blend_multiply(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    blend_rgb = base[..., :3] * top[..., :3]
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


def blend_screen(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    blend_rgb = 1.0 - (1.0 - base[..., :3]) * (1.0 - top[..., :3])
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


def blend_overlay(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    b = base[..., :3]
    t = top[..., :3]
    blend_rgb = np.where(b <= 0.5, 2.0 * b * t, 1.0 - 2.0 * (1.0 - b) * (1.0 - t))
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


def blend_soft_light(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    b = base[..., :3]
    t = top[..., :3]
    blend_rgb = (1.0 - 2.0 * t) * (b ** 2) + 2.0 * t * b
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


def blend_darken(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    blend_rgb = np.minimum(base[..., :3], top[..., :3])
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


def blend_lighten(base: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    blend_rgb = np.maximum(base[..., :3], top[..., :3])
    top_mod = np.concatenate([blend_rgb, top[..., 3:4]], axis=-1)
    return blend_normal(base, top_mod, opacity)


BLEND_FUNCTIONS = {
    "normal": blend_normal,
    "multiply": blend_multiply,
    "screen": blend_screen,
    "overlay": blend_overlay,
    "soft_light": blend_soft_light,
    "darken": blend_darken,
    "lighten": blend_lighten,
}


def apply_blend(base_np: np.ndarray, top_np: np.ndarray, mode: str = "normal", opacity: float = 1.0) -> np.ndarray:
    """Blend top image over base image using specified mode and opacity."""
    func = BLEND_FUNCTIONS.get(mode.lower(), blend_normal)
    return func(base_np, top_np, opacity)
