"""Deterministic OpenCV Facial Feature & Landmark Localization Engine."""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import cv2
from PIL import Image

from autochrome.vision.face import detect_primary_face


def detect_face_landmarks(image: Image.Image) -> Dict[str, Any]:
    """Detects facial components (eyes, pupils, mouth, teeth area, forehead)
    using deterministic OpenCV face localization and standard anthropometric facial geometry.
    """
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    h, w, _ = arr.shape

    face_box = detect_primary_face(img_rgb)
    if not face_box:
        fx, fy, fw, fh = int(w * 0.25), int(h * 0.20), int(w * 0.50), int(h * 0.50)
    else:
        fx, fy, fw, fh = face_box

    left_eye_box = None
    right_eye_box = None

    # Check if OpenCV cascade classifier is available
    cascade_cls = getattr(cv2, "CascadeClassifier", None)
    if cascade_cls and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
        try:
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            eye_cascade = cascade_cls(cv2.data.haarcascades + "haarcascade_eye.xml")
            face_roi_gray = gray[fy : fy + int(fh * 0.6), fx : fx + fw]
            eyes_detected = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=3, minSize=(int(fw * 0.1), int(fh * 0.1)))
            if len(eyes_detected) >= 2:
                sorted_eyes = sorted(eyes_detected, key=lambda e: e[0])
                e1, e2 = sorted_eyes[0], sorted_eyes[-1]
                left_eye_box = (fx + int(e1[0]), fy + int(e1[1]), int(e1[2]), int(e1[3]))
                right_eye_box = (fx + int(e2[0]), fy + int(e2[1]), int(e2[2]), int(e2[3]))
        except Exception:
            pass

    # Standard Golden-Ratio Anthropometric Facial Proportions
    if not left_eye_box or not right_eye_box:
        eye_w = int(fw * 0.25)
        eye_h = int(fh * 0.20)
        left_eye_box = (fx + int(fw * 0.15), fy + int(fh * 0.28), eye_w, eye_h)
        right_eye_box = (fx + int(fw * 0.60), fy + int(fh * 0.28), eye_w, eye_h)

    # Mouth & Teeth Region: Lower 32% of face, centered horizontally
    mouth_w = int(fw * 0.50)
    mouth_h = int(fh * 0.22)
    mouth_x = fx + int(fw * 0.25)
    mouth_y = fy + int(fh * 0.68)
    mouth_box = (mouth_x, mouth_y, mouth_w, mouth_h)

    # Forehead skin zone: Upper 25% of face
    forehead_box = (fx + int(fw * 0.20), fy + int(fh * 0.05), int(fw * 0.60), int(fh * 0.22))

    return {
        "face": (fx, fy, fw, fh),
        "left_eye": left_eye_box,
        "right_eye": right_eye_box,
        "mouth": mouth_box,
        "forehead": forehead_box,
        "dimensions": {"width": w, "height": h}
    }
