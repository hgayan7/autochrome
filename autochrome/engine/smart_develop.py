"""Scene-Aware Smart Development Orchestrator."""

from typing import Dict, Any, Tuple, Optional
from PIL import Image

from autochrome.vision.scene_classifier import classify_scene_content
from autochrome.engine.film_stocks import apply_film_stock
from autochrome.engine.optical_fx import apply_film_halation, apply_orton_effect, dehaze_image, add_photographic_grain
from autochrome.engine.portrait import apply_portrait_retouch
from autochrome.engine.details import apply_details
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.master_critic import score_photographic_quality


def smart_develop(image: Image.Image, target_mood: str = "auto") -> Tuple[Image.Image, Dict[str, Any]]:
    """Autonomously analyzes image content, classifies scene genre, and produces an optimal studio-grade master edit."""
    img_rgb = image.convert("RGB")
    before_critique = score_photographic_quality(img_rgb)
    
    # 1. Scene & Content Understanding
    scene_diagnosis = classify_scene_content(img_rgb)
    genre = scene_diagnosis.get("scene_genre", "general_editorial")
    
    if not scene_diagnosis.get("is_photograph", True):
        # Non-photographic / UI screenshot handling
        from autochrome.engine.mockup import beautify_screenshot
        from autochrome.types import MockupParams
        params = MockupParams(frame_type="macos_dark", backdrop="gradient_slate", padding=50)
        developed = beautify_screenshot(img_rgb, params)
        return developed, {
            "scene_diagnosis": scene_diagnosis,
            "development_type": "ui_screenshot_mockup",
            "applied_recipe": ["beautify_screenshot_macos_dark"],
            "before_critique": before_critique,
            "after_critique": score_photographic_quality(developed),
        }

    # 2. Select Optimal Film Stock & Grading Strategy
    mood_key = target_mood.lower().replace("-", "_")
    if mood_key in ["auto", "smart", "master"]:
        if genre == "portrait":
            selected_stock = "kodak_portra_400"
        elif genre == "landscape_nature":
            selected_stock = "fuji_velvia_50"
        elif genre == "street_night":
            selected_stock = "cinestill_800t"
        elif genre == "architecture_interior":
            selected_stock = "fuji_classic_chrome"
        else:
            selected_stock = "kodak_portra_400"
    elif mood_key in ["bw", "noir", "black_and_white", "monochrome"]:
        selected_stock = "kodak_trix_400"
    elif mood_key in ["vintage", "retro", "nostalgia"]:
        selected_stock = "kodachrome_64"
    elif mood_key in ["cinematic", "night", "neon"]:
        selected_stock = "cinestill_800t"
    elif mood_key in ["vivid", "landscape", "nature"]:
        selected_stock = "fuji_velvia_50"
    elif mood_key in ["editorial", "documentary", "classic"]:
        selected_stock = "fuji_classic_chrome"
    else:
        selected_stock = mood_key if mood_key in ["kodak_portra_400", "cinestill_800t", "fuji_velvia_50", "kodak_trix_400", "kodachrome_64"] else "kodak_portra_400"

    # 3. Step-by-Step Multi-Phase Development
    applied_steps = []
    current_img = img_rgb

    # Phase A: Scene-Aware Film Stock Calibration
    current_img = apply_film_stock(current_img, stock_name=selected_stock, protect_skin=True)
    applied_steps.append(f"apply_film_stock({selected_stock})")

    # Phase B: Dehaze if landscape/overcast
    if scene_diagnosis["adaptive_recommendations"]["dehaze_candidate"]:
        current_img = dehaze_image(current_img, strength=0.55)
        applied_steps.append("dehaze_image(strength=0.55)")

    # Phase C: Portrait Retouching (Key lighting, Skin Radiance, Iris clarity)
    if genre == "portrait" or scene_diagnosis["subject_profile"]["has_human_subject"]:
        from autochrome.types import PortraitParams
        current_img = apply_portrait_retouch(current_img, PortraitParams(face_spotlight=14.0, skin_smoothing=16.0, eye_clarity=28.0))
        applied_steps.append("portrait_retouch(face_spotlight=14, skin_smoothing=16, eye_clarity=28)")

    # Phase D: Halation on Night Speculars
    if scene_diagnosis["adaptive_recommendations"]["halation_candidate"] and selected_stock != "cinestill_800t":
        current_img = apply_film_halation(current_img, threshold=220.0, radius=20.0, intensity=0.6)
        applied_steps.append("apply_film_halation(threshold=220, radius=20)")

    # Phase E: Optical Micro-Contrast & Detail Refinement
    from autochrome.types import DetailsParams
    current_img = apply_details(current_img, DetailsParams(structure=10.0, sharpening=18.0))
    applied_steps.append("adjust_details(structure=10, sharpening=18)")

    # 4. Final Quality Evaluation
    after_critique = score_photographic_quality(current_img)
    score_improvement = max(0, after_critique["overall_aesthetic_index"] - before_critique["overall_aesthetic_index"])

    report = {
        "scene_diagnosis": scene_diagnosis,
        "selected_stock": selected_stock,
        "applied_workflow_steps": applied_steps,
        "score_improvement": score_improvement,
        "before_critique": before_critique,
        "after_critique": after_critique,
    }

    return current_img, report
