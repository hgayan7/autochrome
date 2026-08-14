"""Photographic 3D LUT Color Science & Ansel Adams 11-Zone Calibration Suite."""

from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
from scipy.interpolate import interp1d


def apply_zone_system_calibration(
    image: Image.Image,
    zone_adjustments: Optional[Dict[int, float]] = None,
) -> Image.Image:
    """Calibrates image across the 11 Ansel Adams Photographic Zones (Zone 0 = pure black to Zone X = pure white).
    zone_adjustments: dict mapping zone index (0-10) to EV shift (-2.0 to +2.0).
    """
    if not zone_adjustments:
        zone_adjustments = {
            2: 0.15, # Lift deep shadow textures (Zone II)
            3: 0.20, # Fill textured shadows (Zone III)
            5: 0.05, # Neutral 18% gray skin base (Zone V)
            7: -0.10 # Protect high-key skin highlights (Zone VII)
        }

    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb, dtype=np.float32) / 255.0

    # 11-Zone boundaries from 0.0 to 1.0
    zone_nodes = np.linspace(0.0, 1.0, 11)
    target_nodes = zone_nodes.copy()

    for z_idx, shift in zone_adjustments.items():
        if 0 <= z_idx <= 10:
            target_nodes[z_idx] = np.clip(zone_nodes[z_idx] + shift * 0.08, 0.0, 1.0)

    # Monotonic cubic interpolation for curve mapping
    zone_lut = interp1d(zone_nodes, target_nodes, kind="cubic", fill_value="extrapolate")

    calibrated = np.clip(zone_lut(arr), 0.0, 1.0)
    return Image.fromarray((calibrated * 255.0).astype(np.uint8), mode="RGB")
