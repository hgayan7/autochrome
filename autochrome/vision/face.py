"""Face & Portrait Localization for DP Auto-Centering and Portrait Retouching."""

from typing import Optional, Tuple, Dict, Any
import numpy as np
from PIL import Image


def detect_primary_face(image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    """Detects primary face bounding box (x, y, width, height) using skin tone and luminance saliency."""
    img_rgb = image.convert("RGB")
    w, h = image.size

    # Downsample for fast robust heuristic analysis
    thumb_w = 200
    thumb_h = int(h * (thumb_w / float(w)))
    thumb = img_rgb.resize((thumb_w, thumb_h), Image.Resampling.BILINEAR)
    arr = np.array(thumb, dtype=np.float32)

    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Skin color thresholding in normalized RGB space
    total = r + g + b + 1e-5
    nr, ng = r / total, g / total

    # Typical human skin chrominance cluster
    skin_mask = (nr > 0.35) & (nr < 0.60) & (ng > 0.25) & (ng < 0.40) & (r > g) & (g > b) & (r > 60)
    
    # Focus primarily in the upper 70% of the image
    y_weights = np.linspace(1.2, 0.4, thumb_h)[:, np.newaxis]
    weighted_mask = skin_mask.astype(np.float32) * y_weights

    if np.sum(weighted_mask) < 20:
        # Fallback to rule of thirds center face box
        return (int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.5))

    # Find center of mass of face cluster
    y_indices, x_indices = np.where(weighted_mask > 0.5)
    if len(x_indices) == 0:
        return (int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.5))

    scale_x = w / float(thumb_w)
    scale_y = h / float(thumb_h)

    x_min, x_max = int(np.percentile(x_indices, 10) * scale_x), int(np.percentile(x_indices, 90) * scale_x)
    y_min, y_max = int(np.percentile(y_indices, 10) * scale_y), int(np.percentile(y_indices, 90) * scale_y)

    box_w = max(int(w * 0.3), x_max - x_min)
    box_h = max(int(h * 0.3), y_max - y_min)
    box_x = max(0, min(x_min, w - box_w))
    box_y = max(0, min(y_min, h - box_h))

    return (box_x, box_y, box_w, box_h)
