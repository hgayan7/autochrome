"""Document Scanning & Quad Rectification Engine: Auto-detects paper/receipt/whiteboard corners and unwarps to clean flatbed scans."""

from typing import Tuple, Optional, List
import numpy as np
import cv2
from PIL import Image


def order_quad_points(pts: np.ndarray) -> np.ndarray:
    """Orders 4 coordinates as [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left has smallest sum (x+y)
    rect[2] = pts[np.argmax(s)]  # Bottom-right has largest sum (x+y)

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right has smallest diff (y-x)
    rect[3] = pts[np.argmax(diff)]  # Bottom-left has largest diff (y-x)

    return rect


def detect_document_quad(image: Image.Image) -> Optional[np.ndarray]:
    """Locates the 4 corner points of a document/whiteboard/receipt in the image."""
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > 1000:
            return approx.reshape(4, 2)

    return None


def scan_and_rectify_document(
    image: Image.Image,
    corners: Optional[List[List[int]]] = None,
    mode: str = "enhanced_color",  # "enhanced_color", "clean_bw", "color_original"
) -> Image.Image:
    """Unwarps and enhances a document into a crisp flatbed scan."""
    arr = np.array(image.convert("RGB"))
    h, w, _ = arr.shape

    if corners is not None and len(corners) == 4:
        pts = np.array(corners, dtype=np.float32)
    else:
        detected = detect_document_quad(image)
        if detected is not None:
            pts = detected.astype(np.float32)
        else:
            # Fallback to full image borders
            pts = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)

    rect = order_quad_points(pts)
    (tl, tr, br, bl) = rect

    # Compute target dimensions
    width_top = np.hypot(tr[0] - tl[0], tr[1] - tl[1])
    width_bottom = np.hypot(br[0] - bl[0], br[1] - bl[1])
    max_w = max(int(width_top), int(width_bottom))

    height_right = np.hypot(tr[0] - br[0], tr[1] - br[1])
    height_left = np.hypot(tl[0] - bl[0], tl[1] - bl[1])
    max_h = max(int(height_right), int(height_left))

    dst = np.array([
        [0, 0],
        [max_w - 1, 0],
        [max_w - 1, max_h - 1],
        [0, max_h - 1]
    ], dtype=np.float32)

    # 4-point homography transform
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(arr, M, (max_w, max_h), flags=cv2.INTER_CUBIC)

    if mode == "clean_bw":
        # Adaptive thresholding for crisp black-and-white text
        gray_w = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
        bw = cv2.adaptiveThreshold(gray_w, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
        out = cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)
    elif mode == "enhanced_color":
        # Contrast & shadow elimination
        lab = cv2.cvtColor(warped, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        out = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    else:
        out = warped

    return Image.fromarray(out, mode="RGB")
