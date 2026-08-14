"""3D Cube LUT (.cube) Engine: Parser with Trilinear Interpolation and Exporter.
Supports industry-standard 17x17x17, 33x33x33, and 65x65x65 .cube formats (DaVinci Resolve / Adobe).
"""

from typing import Tuple, Optional
import os
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image


def parse_cube_lut(cube_content_or_path: str) -> Tuple[np.ndarray, int]:
    """Parses a standard .cube LUT string or file path into a 3D NumPy array of shape (N, N, N, 3)."""
    if os.path.exists(cube_content_or_path):
        with open(cube_content_or_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    else:
        lines = cube_content_or_path.strip().splitlines()

    lut_size = None
    data_points = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("LUT_3D_SIZE"):
            lut_size = int(line.split()[1])
            continue
        if line.startswith("TITLE") or line.startswith("DOMAIN_"):
            continue

        parts = line.split()
        if len(parts) == 3:
            try:
                r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                data_points.append([r, g, b])
            except ValueError:
                continue

    if lut_size is None:
        # Infer size from total points (N^3)
        total = len(data_points)
        lut_size = int(round(total ** (1.0 / 3.0)))

    lut_data = np.array(data_points, dtype=np.float32)
    if len(lut_data) != lut_size ** 3:
        raise ValueError(f"Invalid .cube LUT: Expected {lut_size**3} points, got {len(lut_data)}")

    # Reshape to (N_red, N_green, N_blue, 3) where red is inner, green is mid, blue is outer
    lut_grid = lut_data.reshape((lut_size, lut_size, lut_size, 3), order="F")
    return lut_grid, lut_size


def apply_3d_lut(image: Image.Image, lut_grid: np.ndarray, lut_size: int) -> Image.Image:
    """Applies a 3D LUT to an image using fast trilinear interpolation."""
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32) / 255.0  # Normalize to [0, 1]

    # Map normalized coordinates [0, 1] to LUT grid indices [0, lut_size - 1]
    coords = arr * (lut_size - 1)
    r_coords = coords[..., 0].flatten()
    g_coords = coords[..., 1].flatten()
    b_coords = coords[..., 2].flatten()

    sample_coords = np.array([r_coords, g_coords, b_coords])

    # Interpolate for each color channel R, G, B
    out_r = map_coordinates(lut_grid[..., 0], sample_coords, order=1, mode="nearest")
    out_g = map_coordinates(lut_grid[..., 1], sample_coords, order=1, mode="nearest")
    out_b = map_coordinates(lut_grid[..., 2], sample_coords, order=1, mode="nearest")

    out_arr = np.stack([out_r, out_g, out_b], axis=-1).reshape(arr.shape)
    out_arr = np.clip(out_arr * 255.0, 0, 255).astype(np.uint8)

    return Image.fromarray(out_arr, mode="RGB")


def export_canvas_to_cube_lut(
    transform_fn,
    lut_size: int = 33,
    title: str = "Autochrome Master Grade"
) -> str:
    """Generates a standard .cube 3D LUT string by running an adjustment function over a 3D RGB lattice."""
    # Create 3D lattice points
    vals = np.linspace(0.0, 1.0, lut_size, dtype=np.float32)
    b_grid, g_grid, r_grid = np.meshgrid(vals, vals, vals, indexing="ij")
    
    # Flatten lattice into an image strip of shape (1, lut_size^3, 3)
    lattice_rgb = np.stack([r_grid.flatten(), g_grid.flatten(), b_grid.flatten()], axis=-1)
    lattice_img = Image.fromarray((lattice_rgb * 255.0).astype(np.uint8).reshape((1, -1, 3)), mode="RGB")

    # Run the transform function
    transformed_img = transform_fn(lattice_img)
    transformed_arr = np.array(transformed_img, dtype=np.float32) / 255.0
    transformed_pts = transformed_arr.reshape((-1, 3))

    lines = [
        f'TITLE "{title}"',
        f'LUT_3D_SIZE {lut_size}',
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
        ""
    ]

    for pt in transformed_pts:
        lines.append(f"{pt[0]:.6f} {pt[1]:.6f} {pt[2]:.6f}")

    return "\n".join(lines)
