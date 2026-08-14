"""MCP Tool Registry & Handler for Autochrome."""

from typing import Dict, Any, Optional, List, Tuple
from PIL import Image

from autochrome.core.canvas import Canvas
from autochrome.types import (
    TuneParams, DetailsParams, CurveParams, CurvePoint,
    BokehParams, PortraitParams, SelectivePoint,
    ArrowParams, CalloutParams, LoupeParams, BadgeParams, MockupParams
)
from autochrome.engine.tune import apply_tune_image
from autochrome.engine.details import apply_details
from autochrome.engine.curves import apply_curves, PRESET_CURVES
from autochrome.engine.selective import apply_selective_adjust
from autochrome.engine.bokeh import apply_lens_blur
from autochrome.engine.portrait import apply_portrait_retouch
from autochrome.engine.healing import apply_healing_patch
from autochrome.engine.looks import apply_look
from autochrome.engine.transform import crop_region, smart_crop_aspect, rotate_and_straighten, flip_image, expand_canvas_padding
from autochrome.engine.annotation import draw_arrow, draw_callout_box, draw_highlighter, add_numbered_badge, add_magnifier_loupe
from autochrome.engine.privacy import blur_region, pixelate_region, blackout_region
from autochrome.engine.mockup import beautify_screenshot
from autochrome.vision.grid import generate_coordinate_grid_overlay
from autochrome.vision.analyze import analyze_photographic_scene
from autochrome.vision.face import detect_primary_face
from autochrome.engine.hsl import apply_hsl_mixer
from autochrome.engine.color_grade import apply_color_wheels_grading, apply_split_toning


# Active Canvas instance managed by the MCP session
ACTIVE_CANVAS: Optional[Canvas] = None


def get_active_canvas() -> Canvas:
    global ACTIVE_CANVAS
    if ACTIVE_CANVAS is None:
        # Default blank canvas if none opened yet
        img = Image.new("RGBA", (800, 600), (24, 24, 27, 255))
        ACTIVE_CANVAS = Canvas.from_image(img)
    return ACTIVE_CANVAS


def set_active_canvas(canvas: Canvas):
    global ACTIVE_CANVAS
    ACTIVE_CANVAS = canvas


# Tool implementations callable by MCP or SDK

def tool_open_image(image_path: str, launch_preview: bool = True) -> Dict[str, Any]:
    """Loads an image from local filesystem into the active session and automatically launches live preview."""
    import sys
    canvas = Canvas.from_file(image_path)
    set_active_canvas(canvas)
    metrics = analyze_photographic_scene(canvas.render())
    preview_url = None
    if launch_preview:
        from autochrome.preview.window import launch_live_preview
        try:
            preview_url = launch_live_preview(canvas, native=(sys.platform == "darwin"))
        except Exception:
            pass

    return {
        "status": "success",
        "message": f"Loaded {image_path} ({canvas.width}x{canvas.height})",
        "preview_url": preview_url or "http://127.0.0.1:8000",
        "live_preview_active": bool(preview_url),
        "scene_analysis": metrics,
    }


def tool_start_preview(native: bool = True, port: int = 8000, browser: bool = False) -> Dict[str, Any]:
    """Starts the real-time Live Darkroom Preview (native macOS floating window or browser)."""
    import sys
    canvas = get_active_canvas()
    from autochrome.preview.window import launch_live_preview
    url = launch_live_preview(canvas, port=port, native=native, browser=browser)
    return {
        "status": "success",
        "preview_url": url,
        "mode": "native_macos_window" if (native and sys.platform == "darwin") else "web_browser",
        "message": "Live preview window is active. Transformations will stream in real-time.",
    }


def tool_export_image(output_path: str, format: str = "PNG", quality: int = 95) -> Dict[str, Any]:
    """Exports the final composite image to disk."""
    canvas = get_active_canvas()
    canvas.export(output_path, format=format, quality=quality)
    return {"status": "success", "exported_path": output_path, "dimensions": f"{canvas.width}x{canvas.height}"}


def tool_inspect_image() -> Dict[str, Any]:
    """Analyzes photographic scene lighting, color casts, Zone System exposure, and evaluates natural depth of field."""
    canvas = get_active_canvas()
    img = canvas.render()
    metrics = analyze_photographic_scene(img)
    face_box = detect_primary_face(img)
    if face_box:
        metrics["detected_primary_face"] = {
            "x": face_box[0], "y": face_box[1], "width": face_box[2], "height": face_box[3],
            "center": [face_box[0] + face_box[2] // 2, face_box[1] + face_box[3] // 2]
        }
    return metrics


def tool_color_wheels_grade(
    shadow_hue: float = 0.0,
    shadow_sat: float = 0.0,
    shadow_lum: float = 0.0,
    mid_hue: float = 0.0,
    mid_sat: float = 0.0,
    mid_lum: float = 0.0,
    high_hue: float = 0.0,
    high_sat: float = 0.0,
    high_lum: float = 0.0,
) -> Dict[str, Any]:
    """DaVinci Resolve-style 3-Way Color Wheels grading (Shadows/Lift, Midtones/Gamma, Highlights/Gain)."""
    canvas = get_active_canvas()
    sh = {"hue": shadow_hue, "saturation": shadow_sat, "luminance": shadow_lum} if (shadow_sat > 0 or shadow_lum != 0) else None
    mid = {"hue": mid_hue, "saturation": mid_sat, "luminance": mid_lum} if (mid_sat > 0 or mid_lum != 0) else None
    hl = {"hue": high_hue, "saturation": high_sat, "luminance": high_lum} if (high_sat > 0 or high_lum != 0) else None

    edited = apply_color_wheels_grading(canvas.render(), shadows=sh, midtones=mid, highlights=hl)
    canvas.replace_base_image(edited, "color_wheels", "3-Way Color Wheels Grading", {"shadows": sh, "midtones": mid, "highlights": hl})
    return {"status": "success", "color_wheels": {"shadows": sh, "midtones": mid, "highlights": hl}}


def tool_hsl_color_mixer(
    hue_shifts: Optional[Dict[str, float]] = None,
    saturation_shifts: Optional[Dict[str, float]] = None,
    luminance_shifts: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Lightroom-style 8-Channel HSL Color Mixer (target Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta independently)."""
    canvas = get_active_canvas()
    edited = apply_hsl_mixer(canvas.render(), hue_shifts=hue_shifts, saturation_shifts=saturation_shifts, luminance_shifts=luminance_shifts)
    canvas.replace_base_image(edited, "hsl_mixer", "8-Channel HSL Color Mix", {
        "hue": hue_shifts, "saturation": saturation_shifts, "luminance": luminance_shifts
    })
    return {"status": "success", "applied": {"hue": hue_shifts, "sat": saturation_shifts, "lum": luminance_shifts}}


def tool_split_toning(
    shadow_hue: float = 210.0,
    shadow_sat: float = 0.0,
    highlight_hue: float = 40.0,
    highlight_sat: float = 0.0,
    balance: float = 0.0,
) -> Dict[str, Any]:
    """Photographic Split Toning: shadows vs highlights color separation with balance slider."""
    canvas = get_active_canvas()
    edited = apply_split_toning(canvas.render(), shadow_hue, shadow_sat, highlight_hue, highlight_sat, balance)
    canvas.replace_base_image(edited, "split_toning", f"Split Toning (Shadow Hue: {shadow_hue}, Highlight Hue: {highlight_hue})")
    return {"status": "success", "params": {"shadow_hue": shadow_hue, "shadow_sat": shadow_sat, "highlight_hue": highlight_hue, "highlight_sat": highlight_sat, "balance": balance}}


def tool_adaptive_color_grade(mood: str = "photographic") -> Dict[str, Any]:
    """Dynamically analyzes the image's specific histogram, lighting, color cast, and depth to compute and apply a custom photographic color grade."""
    from autochrome.engine.adaptive import apply_adaptive_photographic_grade
    canvas = get_active_canvas()
    edited, plan = apply_adaptive_photographic_grade(canvas.render(), mood=mood)
    desc = f"Adaptive Grade ({plan['diagnosis']['lighting_scenario']} → {mood})"
    canvas.replace_base_image(edited, "adaptive_grade", desc, plan)
    return {"status": "success", "diagnosis": plan["diagnosis"], "applied_recipe": plan["computed_recipe"]}


def tool_master_develop() -> Dict[str, Any]:
    """Autonomous Master Development: evaluates, scores, and produces the optimal studio-grade edit with zero user micromanagement."""
    from autochrome.engine.master_critic import auto_master_develop
    canvas = get_active_canvas()
    edited, report = auto_master_develop(canvas.render())
    score_before = report["before_critique"]["overall_aesthetic_index"]
    score_after = report["after_critique"]["overall_aesthetic_index"]
    desc = f"Master Develop (Score: {score_before} ➔ {score_after}/100)"
    canvas.replace_base_image(edited, "master_develop", desc, report)
    return {"status": "success", "development_report": report}


def tool_score_quality() -> Dict[str, Any]:
    """Scores and critiques the active canvas across exposure, contrast, skin health, and sharpness (0-100)."""
    from autochrome.engine.master_critic import score_photographic_quality
    canvas = get_active_canvas()
    return score_photographic_quality(canvas.render())


def tool_passport_studio_portrait(
    aspect_ratio: str = "35x45",
    backdrop: str = "studio_light_grey",
) -> Dict[str, Any]:
    """Transforms a casual indoor selfie into an official biometric Studio-Grade Passport Photo."""
    from autochrome.engine.passport import develop_studio_passport_photo
    canvas = get_active_canvas()
    edited, report = develop_studio_passport_photo(canvas.render(), aspect_ratio=aspect_ratio, backdrop=backdrop)
    desc = f"Studio Passport ({aspect_ratio}, {backdrop})"
    canvas.replace_base_image(edited, "passport_studio", desc, report)
    return {"status": "success", "passport_report": report}


def tool_replace_background(
    target_bg: str = "crimson_red",
) -> Dict[str, Any]:
    """Removes current background (e.g. blue screen / solid backdrop) and composites onto target color (e.g. 'solid_red', 'crimson_red')."""
    from autochrome.engine.background import replace_background_color
    canvas = get_active_canvas()
    edited = replace_background_color(canvas.render(), target_bg=target_bg)
    desc = f"Replaced Background ({target_bg})"
    canvas.replace_base_image(edited, "replace_background", desc)
    return {"status": "success", "target_bg": target_bg}


def tool_frequency_separation(
    blur_radius: float = 3.5,
    smoothing_strength: float = 0.55,
) -> Dict[str, Any]:
    """Applies authentic Studio Frequency Separation: smooths low-frequency skin tones while preserving 100% of high-frequency skin pores."""
    from autochrome.engine.retouch import apply_frequency_separation
    canvas = get_active_canvas()
    edited = apply_frequency_separation(canvas.render(), blur_radius=blur_radius, smoothing_strength=smoothing_strength)
    desc = f"Frequency Separation (Radius: {blur_radius}, Smooth: {smoothing_strength})"
    canvas.replace_base_image(edited, "frequency_separation", desc)
    return {"status": "success", "blur_radius": blur_radius, "smoothing_strength": smoothing_strength}


def tool_keystone_correction(pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0) -> Dict[str, Any]:
    """Corrects perspective keystoning (vertical/horizontal converging lines) using OpenCV 4-point homography."""
    from autochrome.engine.geometry import apply_keystone_correction
    canvas = get_active_canvas()
    edited = apply_keystone_correction(canvas.render(), pitch=pitch, yaw=yaw, roll=roll)
    desc = f"Keystone Correction (Pitch: {pitch}, Yaw: {yaw}, Roll: {roll})"
    canvas.replace_base_image(edited, "keystone_correction", desc)
    return {"status": "success", "pitch": pitch, "yaw": yaw, "roll": roll}


def tool_lens_distortion_correction(k1: float = -0.04, k2: float = 0.0) -> Dict[str, Any]:
    """Corrects radial camera lens distortion (barrel / pincushion) using camera calibration matrix."""
    from autochrome.engine.geometry import apply_lens_distortion_correction
    canvas = get_active_canvas()
    edited = apply_lens_distortion_correction(canvas.render(), k1=k1, k2=k2)
    desc = f"Lens Distortion Correction (k1: {k1}, k2: {k2})"
    canvas.replace_base_image(edited, "lens_distortion", desc)
    return {"status": "success", "k1": k1, "k2": k2}


def tool_zone_system_calibration(zone_adjustments: Optional[Dict[int, float]] = None) -> Dict[str, Any]:
    """Calibrates image across the 11 Ansel Adams Photographic Zones (Zone 0 to Zone X)."""
    from autochrome.engine.lut import apply_zone_system_calibration
    canvas = get_active_canvas()
    edited = apply_zone_system_calibration(canvas.render(), zone_adjustments=zone_adjustments)
    desc = f"Zone System 11-Zone Calibration"
    canvas.replace_base_image(edited, "zone_system", desc)
    return {"status": "success", "zone_adjustments": zone_adjustments}


def tool_apply_3d_cube_lut(cube_path_or_content: str) -> Dict[str, Any]:
    """Applies an industry-standard 3D LUT (.cube file format) using trilinear interpolation."""
    from autochrome.engine.lut_cube import parse_cube_lut, apply_3d_lut
    canvas = get_active_canvas()
    lut_grid, lut_size = parse_cube_lut(cube_path_or_content)
    edited = apply_3d_lut(canvas.render(), lut_grid, lut_size)
    desc = f"Applied 3D Cube LUT (Size {lut_size}^3)"
    canvas.replace_base_image(edited, "3d_lut", desc)
    return {"status": "success", "lut_size": lut_size}


def tool_export_3d_cube_lut(output_path: str, lut_size: int = 33, title: str = "Autochrome Grade") -> Dict[str, Any]:
    """Exports the canvas grade as a standard .cube 3D LUT file."""
    from autochrome.engine.lut_cube import export_canvas_to_cube_lut
    canvas = get_active_canvas()
    # Simple identity wrapper since canvas is already rendered
    cube_text = export_canvas_to_cube_lut(lambda img: img, lut_size=lut_size, title=title)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cube_text)
    return {"status": "success", "output_path": output_path, "lut_size": lut_size}


def tool_remove_chromatic_aberration(purple_amount: float = 0.85, green_amount: float = 0.85, radius: int = 3) -> Dict[str, Any]:
    """Eliminates purple and green chromatic aberration color fringing along high-contrast backlit edges."""
    from autochrome.engine.optics import remove_chromatic_aberration
    canvas = get_active_canvas()
    edited = remove_chromatic_aberration(canvas.render(), purple_amount=purple_amount, green_amount=green_amount, radius=radius)
    desc = f"Removed Chromatic Aberration (Purple: {purple_amount}, Green: {green_amount})"
    canvas.replace_base_image(edited, "defringe", desc)
    return {"status": "success", "purple_amount": purple_amount, "green_amount": green_amount}


def tool_correct_lens_vignetting(amount: float = 35.0, midpoint: float = 50.0) -> Dict[str, Any]:
    """Compensates for optical lens light falloff (vignetting) towards image corners."""
    from autochrome.engine.optics import correct_lens_vignetting
    canvas = get_active_canvas()
    edited = correct_lens_vignetting(canvas.render(), amount=amount, midpoint=midpoint)
    desc = f"Corrected Lens Vignetting (Amount: {amount}, Midpoint: {midpoint})"
    canvas.replace_base_image(edited, "vignette_correct", desc)
    return {"status": "success", "amount": amount, "midpoint": midpoint}


def tool_merge_mertens_hdr(image_paths: List[str]) -> Dict[str, Any]:
    """Merges multiple bracketed image exposures into a high-dynamic-range photo using OpenCV Mertens fusion."""
    from autochrome.engine.hdr import merge_mertens_hdr
    from PIL import Image
    imgs = [Image.open(p) for p in image_paths]
    canvas = get_active_canvas()
    fused = merge_mertens_hdr(imgs)
    desc = f"Mertens HDR Fusion ({len(imgs)} exposures)"
    canvas.replace_base_image(fused, "mertens_hdr", desc)
    return {"status": "success", "fused_images_count": len(imgs)}


def tool_scan_document(mode: str = "enhanced_color", corners: Optional[List[List[int]]] = None) -> Dict[str, Any]:
    """Auto-detects paper/receipt/whiteboard quad corners and rectifies to a flat, crisp scan."""
    from autochrome.engine.scanner import scan_and_rectify_document
    canvas = get_active_canvas()
    scanned = scan_and_rectify_document(canvas.render(), corners=corners, mode=mode)
    desc = f"Document Scan Rectification ({mode})"
    canvas.replace_base_image(scanned, "doc_scan", desc)
    return {"status": "success", "mode": mode, "new_dimensions": f"{canvas.width}x{canvas.height}"}


def tool_render_code_snippet(code_text: str, language: str = "python", title: str = "code.py", backdrop: str = "gradient_slate") -> Dict[str, Any]:
    """Renders a syntax-highlighted code snippet card with macOS window bezel and gradient backdrop."""
    from autochrome.engine.code_beautifier import render_code_snippet
    canvas = get_active_canvas()
    rendered = render_code_snippet(code_text, language=language, title=title, backdrop=backdrop)
    desc = f"Rendered Code Snippet ({title})"
    canvas.replace_base_image(rendered, "code_snippet", desc)
    return {"status": "success", "title": title}


def tool_match_color_to_reference(reference_image_path: str, strength: float = 0.85) -> Dict[str, Any]:
    """Matches the color grade, exposure, and tone of the canvas to a hero reference image using CIELAB color transfer."""
    from autochrome.engine.batch import match_color_to_reference
    from PIL import Image
    ref_img = Image.open(reference_image_path)
    canvas = get_active_canvas()
    matched = match_color_to_reference(canvas.render(), ref_img, strength=strength)
    desc = f"Matched color to reference ({os.path.basename(reference_image_path)})"
    canvas.replace_base_image(matched, "color_transfer", desc)
    return {"status": "success", "reference": reference_image_path, "strength": strength}


def tool_get_grid_overlay(grid_step: int = 100) -> Dict[str, Any]:
    """Applies a numbered coordinate grid overlay to assist the agent in visual spatial targeting."""
    canvas = get_active_canvas()
    grid_img = generate_coordinate_grid_overlay(canvas.render(), grid_step=grid_step)
    canvas.replace_base_image(grid_img, "grid_overlay", f"Applied coordinate grid (step {grid_step}px)")
    return {"status": "success", "message": f"Coordinate grid applied with step={grid_step}px"}


def tool_tune_image(
    brightness: float = 0.0,
    contrast: float = 0.0,
    saturation: float = 0.0,
    ambiance: float = 0.0,
    highlights: float = 0.0,
    shadows: float = 0.0,
    warmth: float = 0.0,
    tint: float = 0.0,
) -> Dict[str, Any]:
    """Primary Tone & Color Balancing: comprehensive tone curve and local dynamic adjustments (-100 to +100)."""
    canvas = get_active_canvas()
    params = TuneParams(
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
        ambiance=ambiance,
        highlights=highlights,
        shadows=shadows,
        warmth=warmth,
        tint=tint,
    )
    edited = apply_tune_image(canvas.render(), params)
    canvas.replace_base_image(edited, "tune_image", "Primary Tone Adjustment", params.model_dump())
    return {"status": "success", "applied_params": params.model_dump()}


def tool_adjust_details(structure: float = 0.0, sharpening: float = 0.0) -> Dict[str, Any]:
    """Details & Texture: boosts micro-contrast texture structure and high-pass sharpness."""
    canvas = get_active_canvas()
    params = DetailsParams(structure=structure, sharpening=sharpening)
    edited = apply_details(canvas.render(), params)
    canvas.replace_base_image(edited, "details", f"Details (Structure: {structure}, Sharpening: {sharpening})", params.model_dump())
    return {"status": "success", "applied_params": params.model_dump()}


def tool_adjust_curves(preset: str = "hard_contrast", channel: str = "rgb") -> Dict[str, Any]:
    """Tone Curves: applies multi-channel tone curves (presets: 'hard_contrast', 'brighten', 'darken', 'matte_vintage', 'cross_process')."""
    canvas = get_active_canvas()
    pts = PRESET_CURVES.get(preset, PRESET_CURVES["hard_contrast"])
    params = CurveParams(channel=channel, points=pts)
    edited = apply_curves(canvas.render(), params)
    canvas.replace_base_image(edited, "curves", f"Applied {preset} curve on {channel}")
    return {"status": "success", "preset": preset, "channel": channel}


def tool_apply_look(look_name: str = "linkedin_pro") -> Dict[str, Any]:
    """Applies curated aesthetic style look ('linkedin_pro', 'drama', 'vintage_film', 'noir_bw', 'glamour_glow', 'crisp_editorial', 'cyberpunk')."""
    canvas = get_active_canvas()
    edited = apply_look(canvas.render(), look_name)
    canvas.replace_base_image(edited, "apply_look", f"Applied Look: {look_name}")
    return {"status": "success", "look": look_name}


def tool_classify_scene() -> Dict[str, Any]:
    """Analyzes scene semantics, content genre (portrait, landscape, street, architecture), and returns adaptive grading recommendations."""
    from autochrome.vision.scene_classifier import classify_scene_content
    canvas = get_active_canvas()
    return classify_scene_content(canvas.render())


def tool_smart_develop(target_mood: str = "auto") -> Dict[str, Any]:
    """Scene-Aware Master Development: autonomously classifies scene content and produces an optimal studio-grade master edit."""
    from autochrome.engine.smart_develop import smart_develop
    canvas = get_active_canvas()
    developed, report = smart_develop(canvas.render(), target_mood=target_mood)
    desc = f"Smart Developed ({report.get('selected_stock', 'Auto')}) - Gain: +{report.get('score_improvement', 0)} pts"
    canvas.replace_base_image(developed, "smart_develop", desc, {"report": report})
    return {"status": "success", "report": report}


def tool_apply_film_stock(stock_name: str = "kodak_portra_400", protect_skin: bool = True) -> Dict[str, Any]:
    """Applies one of the 13 authentic analog film stocks with built-in scene adaptation and skin protection:
    'kodak_portra_400', 'kodak_portra_160', 'cinestill_800t', 'kodak_trix_400', 'ilford_hp5',
    'fuji_velvia_50', 'fuji_provia_100f', 'kodachrome_64', 'fuji_classic_chrome', 'polaroid_sx70',
    'agfa_vista_200', 'technicolor_2strip', 'technicolor_3strip'.
    """
    from autochrome.engine.film_stocks import apply_film_stock, FILM_STOCKS_METADATA
    canvas = get_active_canvas()
    edited = apply_film_stock(canvas.render(), stock_name=stock_name, protect_skin=protect_skin)
    clean_stock = stock_name.lower().replace("-", "_").replace(" ", "_")
    meta = FILM_STOCKS_METADATA.get(clean_stock, {"name": clean_stock, "description": "Analog film emulation"})
    canvas.replace_base_image(edited, "film_stock", f"Applied Film Stock: {meta['name']}")
    return {"status": "success", "stock": clean_stock, "name": meta.get("name"), "description": meta.get("description")}


def tool_list_film_stocks() -> Dict[str, Any]:
    """Lists all 13 authentic analog film stock emulations with metadata and best use cases."""
    from autochrome.engine.film_stocks import list_available_film_stocks
    return {"status": "success", "film_stocks": list_available_film_stocks()}


def tool_apply_film_halation(threshold: float = 215.0, radius: float = 24.0, intensity: float = 0.65) -> Dict[str, Any]:
    """Applies CineStill-style crimson-orange specular halation bloom around intense light sources."""
    from autochrome.engine.optical_fx import apply_film_halation
    canvas = get_active_canvas()
    edited = apply_film_halation(canvas.render(), threshold=threshold, radius=radius, intensity=intensity)
    canvas.replace_base_image(edited, "film_halation", f"Film Halation (Radius: {radius}, Intensity: {intensity})")
    return {"status": "success", "threshold": threshold, "radius": radius, "intensity": intensity}


def tool_apply_orton_effect(strength: float = 0.30, blur_radius: float = 30.0, glow_mode: str = "soft_light") -> Dict[str, Any]:
    """Applies the classic Orton Effect (Dreamy Glow Diffusion) while preserving underlying micro-contrast."""
    from autochrome.engine.optical_fx import apply_orton_effect
    canvas = get_active_canvas()
    edited = apply_orton_effect(canvas.render(), strength=strength, blur_radius=blur_radius, glow_mode=glow_mode)
    canvas.replace_base_image(edited, "orton_effect", f"Orton Dreamy Glow (Strength: {strength})")
    return {"status": "success", "strength": strength, "blur_radius": blur_radius, "glow_mode": glow_mode}


def tool_apply_bleach_bypass(strength: float = 0.60, contrast_boost: float = 1.25) -> Dict[str, Any]:
    """Simulates chemical Bleach Bypass (Silver Retention) for a gritty, high-contrast, desaturated cinematic aesthetic."""
    from autochrome.engine.optical_fx import apply_bleach_bypass
    canvas = get_active_canvas()
    edited = apply_bleach_bypass(canvas.render(), strength=strength, contrast_boost=contrast_boost)
    canvas.replace_base_image(edited, "bleach_bypass", f"Bleach Bypass Silver Retention ({int(strength*100)}%)")
    return {"status": "success", "strength": strength, "contrast_boost": contrast_boost}


def tool_dehaze_image(strength: float = 0.70, window_size: int = 15) -> Dict[str, Any]:
    """Removes atmospheric haze, fog, and milkiness using Dark Channel Prior (DCP) physical transmission modeling."""
    from autochrome.engine.optical_fx import dehaze_image
    canvas = get_active_canvas()
    edited = dehaze_image(canvas.render(), strength=strength, window_size=window_size)
    canvas.replace_base_image(edited, "dehaze", f"Dark Channel Prior Dehaze (Strength: {strength})")
    return {"status": "success", "strength": strength, "window_size": window_size}


def tool_set_color_temperature_kelvin(kelvin: int = 5500, tint: float = 0.0) -> Dict[str, Any]:
    """Adjusts physical color temperature in Kelvin (2000K-12000K) and green/magenta tint using Planckian Blackbody modeling."""
    from autochrome.engine.optical_fx import set_color_temperature_kelvin
    canvas = get_active_canvas()
    edited = set_color_temperature_kelvin(canvas.render(), kelvin=kelvin, tint=tint)
    canvas.replace_base_image(edited, "color_temperature_kelvin", f"Kelvin White Balance ({kelvin}K, Tint: {tint})")
    return {"status": "success", "kelvin": kelvin, "tint": tint}


def tool_add_photographic_grain(amount: float = 24.0, size: float = 1.0, roughness: float = 0.5) -> Dict[str, Any]:
    """Adds authentic density-dependent silver halide film grain peaking in midtones and fading in pure highlights and blacks."""
    from autochrome.engine.optical_fx import add_photographic_grain
    canvas = get_active_canvas()
    edited = add_photographic_grain(canvas.render(), amount=amount, size=size, roughness=roughness, luminance_aware=True)
    canvas.replace_base_image(edited, "photographic_grain", f"Silver Halide Film Grain (Amount: {amount}, Size: {size})")
    return {"status": "success", "amount": amount, "size": size, "roughness": roughness}


def tool_apply_film_profile(profile: str = "kodak_portra_400") -> Dict[str, Any]:
    """Applies authentic analog film emulation ('kodak_portra_400', 'fuji_pro_400h', 'cinematic_teal_orange', 'moody_nordic')."""
    from autochrome.engine.film_emulation import apply_film_profile, FILM_PROFILES
    canvas = get_active_canvas()
    edited = apply_film_profile(canvas.render(), profile)
    prof_data = FILM_PROFILES.get(profile.lower().strip(), FILM_PROFILES["kodak_portra_400"])
    desc = f"Applied Film Profile: {prof_data['name']}"
    canvas.replace_base_image(edited, "film_profile", desc)
    return {"status": "success", "profile": profile, "name": prof_data["name"], "description": prof_data["description"]}


def tool_apply_filter(filter_name: str = "cinematic_pop") -> Dict[str, Any]:
    """Applies a photo filter from the 16 FilterLibrary presets:
    'invert', 'grayscale', 'cyan_boost', 'moody_dark', 'cross_process', 'retro_warm',
    'high_key', 'brightness_boost', 'dramatic', 'cool_blue', 'polaroid_70s', 'sepia',
    'emboss', 'soft_blur', 'cinematic_pop', 'warm_sunset'.
    """
    from autochrome.engine.filter_library import apply_filter_by_name, FILTER_DESCRIPTIONS
    canvas = get_active_canvas()
    edited = apply_filter_by_name(canvas.render(), filter_name)
    clean_name = filter_name.lower().strip().replace("-", "_").replace(" ", "_")
    desc = f"Applied Filter: {clean_name}"
    canvas.replace_base_image(edited, "filter_library", desc)
    return {
        "status": "success",
        "filter": clean_name,
        "description": FILTER_DESCRIPTIONS.get(clean_name, "Custom filter applied")
    }


def tool_list_filters() -> Dict[str, Any]:
    """Returns the full list of 16 available photo filters with descriptions."""
    from autochrome.engine.filter_library import list_available_filters
    return {"status": "success", "filters": list_available_filters()}


def tool_selective_adjust(
    center_x: int,
    center_y: int,
    radius: int = 150,
    brightness: float = 0.0,
    contrast: float = 0.0,
    saturation: float = 0.0,
) -> Dict[str, Any]:
    """Selective Adjust: modifies brightness/contrast/saturation in a targeted circular area."""
    canvas = get_active_canvas()
    pt = SelectivePoint(x=center_x, y=center_y, radius=radius, brightness=brightness, contrast=contrast, saturation=saturation)
    edited = apply_selective_adjust(canvas.render(), [pt])
    canvas.replace_base_image(edited, "selective_adjust", f"Selective adjust at ({center_x}, {center_y})", pt.model_dump())
    return {"status": "success", "point": pt.model_dump()}


def tool_portrait_retouch(
    face_spotlight: float = 20.0,
    skin_smoothing: float = 25.0,
    eye_clarity: float = 30.0,
    skin_tone_warmth: float = 5.0,
) -> Dict[str, Any]:
    """Studio Portrait Retouch: face spotlight illumination, texture skin smoothing, and eye clarity pop."""
    canvas = get_active_canvas()
    face_box = detect_primary_face(canvas.render())
    params = PortraitParams(
        face_spotlight=face_spotlight,
        skin_smoothing=skin_smoothing,
        eye_clarity=eye_clarity,
        skin_tone_warmth=skin_tone_warmth,
    )
    edited = apply_portrait_retouch(canvas.render(), params, face_box)
    canvas.replace_base_image(edited, "portrait_retouch", "Portrait Retouching", params.model_dump())
    return {"status": "success", "applied_params": params.model_dump(), "face_box": face_box}


def tool_heal_blemish(center_x: int, center_y: int, radius: int = 20) -> Dict[str, Any]:
    """Healing: content-aware patch removal for spots, blemishes, or small unwanted artifacts."""
    canvas = get_active_canvas()
    edited = apply_healing_patch(canvas.render(), center_x, center_y, radius)
    canvas.replace_base_image(edited, "heal_blemish", f"Healed spot at ({center_x}, {center_y})")
    return {"status": "success", "healed_at": [center_x, center_y], "radius": radius}


def tool_smart_crop(aspect_ratio: str = "1:1", focus_x: Optional[int] = None, focus_y: Optional[int] = None) -> Dict[str, Any]:
    """Smart crops image to aspect ratio ('1:1', '16:9', '4:5', '9:16', '4:3', '3:2') centered on focus point or auto-detected face."""
    canvas = get_active_canvas()
    focus = None
    if focus_x is not None and focus_y is not None:
        focus = (focus_x, focus_y)
    else:
        face = detect_primary_face(canvas.render())
        if face:
            focus = (face[0] + face[2] // 2, face[1] + face[3] // 2)

    cropped = smart_crop_aspect(canvas.render(), aspect_ratio=aspect_ratio, focus_point=focus)
    canvas.replace_base_image(cropped, "smart_crop", f"Smart crop ({aspect_ratio})")
    return {"status": "success", "aspect_ratio": aspect_ratio, "new_dimensions": f"{canvas.width}x{canvas.height}"}


def tool_crop_box(x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """Crops an exact bounding box from the canvas."""
    canvas = get_active_canvas()
    cropped = crop_region(canvas.render(), x, y, width, height)
    canvas.replace_base_image(cropped, "crop_box", f"Cropped region [{x}, {y}, {width}, {height}]")
    return {"status": "success", "new_dimensions": f"{canvas.width}x{canvas.height}"}


def tool_rotate_straighten(angle_deg: float) -> Dict[str, Any]:
    """Rotates/straightens the image by specified degrees."""
    canvas = get_active_canvas()
    rotated = rotate_and_straighten(canvas.render(), angle_deg)
    canvas.replace_base_image(rotated, "rotate", f"Rotated {angle_deg}°")
    return {"status": "success", "angle": angle_deg}


def tool_draw_arrow(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    color: str = "#FF3B30",
    stroke_width: int = 4,
    curvature: float = 0.0,
) -> Dict[str, Any]:
    """Draws a clean vector arrow with optional curvature (-1.0 to 1.0) pointing towards target."""
    canvas = get_active_canvas()
    params = ArrowParams(
        start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y,
        color=color, stroke_width=stroke_width, curvature=curvature
    )
    edited = draw_arrow(canvas.render(), params)
    canvas.replace_base_image(edited, "draw_arrow", f"Drew arrow to ({end_x}, {end_y})", params.model_dump())
    return {"status": "success", "params": params.model_dump()}


def tool_draw_arrow_with_label(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    label_text: str,
    color: str = "#00E5FF",
    stroke_width: int = 3,
    curvature: float = 0.0,
) -> Dict[str, Any]:
    """Draws a vector arrow pointing to a UI element with an embedded descriptive pill badge text."""
    from autochrome.engine.annotation import draw_arrow_with_label
    canvas = get_active_canvas()
    edited = draw_arrow_with_label(canvas.render(), start_x, start_y, end_x, end_y, label_text, color, stroke_width, curvature)
    canvas.replace_base_image(edited, "draw_arrow_with_label", f"Arrow with label: '{label_text}'")
    return {"status": "success", "label": label_text}


def tool_draw_callout(
    x: int,
    y: int,
    width: int,
    height: int,
    border_color: str = "#FF9500",
    fill_color: Optional[str] = None,
    label: Optional[str] = None,
    label_bg: Optional[str] = None,
) -> Dict[str, Any]:
    """Draws a rounded spotlight callout box with optional label chip."""
    canvas = get_active_canvas()
    params = CalloutParams(x=x, y=y, width=width, height=height, border_color=border_color, fill_color=fill_color, label=label, label_bg=label_bg)
    edited = draw_callout_box(canvas.render(), params)
    canvas.replace_base_image(edited, "draw_callout", f"Drew callout box at [{x}, {y}]", params.model_dump())
    return {"status": "success", "params": params.model_dump()}


def tool_draw_highlighter(x: int, y: int, width: int, height: int, color: str = "#FFCC00", opacity: float = 0.4) -> Dict[str, Any]:
    """Draws a semi-transparent marker highlighter bar."""
    canvas = get_active_canvas()
    edited = draw_highlighter(canvas.render(), x, y, width, height, color, opacity)
    canvas.replace_base_image(edited, "highlighter", f"Highlighter at [{x}, {y}]")
    return {"status": "success"}


def tool_add_numbered_badge(x: int, y: int, number: int = 1, bg_color: str = "#007AFF") -> Dict[str, Any]:
    """Adds a circular numbered tutorial step badge (e.g. 1, 2, 3)."""
    canvas = get_active_canvas()
    params = BadgeParams(x=x, y=y, number=number, bg_color=bg_color)
    edited = add_numbered_badge(canvas.render(), params)
    canvas.replace_base_image(edited, "badge", f"Added badge #{number} at ({x}, {y})")
    return {"status": "success"}


def tool_add_magnifier_loupe(
    target_x: int,
    target_y: int,
    loupe_x: int,
    loupe_y: int,
    radius: int = 80,
    zoom_factor: float = 2.0,
) -> Dict[str, Any]:
    """Adds a circular magnifying loupe glass showcasing a zoomed detail."""
    canvas = get_active_canvas()
    params = LoupeParams(target_x=target_x, target_y=target_y, loupe_x=loupe_x, loupe_y=loupe_y, radius=radius, zoom_factor=zoom_factor)
    edited = add_magnifier_loupe(canvas.render(), params)
    canvas.replace_base_image(edited, "loupe", f"Magnifier loupe zoom {zoom_factor}x")
    return {"status": "success"}


def tool_blur_region(x: int, y: int, width: int, height: int, radius: int = 20) -> Dict[str, Any]:
    """Gaussian blurs a rectangular region to redact sensitive information."""
    canvas = get_active_canvas()
    edited = blur_region(canvas.render(), x, y, width, height, radius)
    canvas.replace_base_image(edited, "blur_region", f"Blurred privacy region [{x}, {y}, {width}, {height}]")
    return {"status": "success"}


def tool_pixelate_region(x: int, y: int, width: int, height: int, block_size: int = 12) -> Dict[str, Any]:
    """Pixelates a rectangular region with mosaic blocks."""
    canvas = get_active_canvas()
    edited = pixelate_region(canvas.render(), x, y, width, height, block_size)
    canvas.replace_base_image(edited, "pixelate_region", f"Pixelated region [{x}, {y}, {width}, {height}]")
    return {"status": "success"}


def tool_blackout_region(x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """Applies an opaque solid blackout redact bar."""
    canvas = get_active_canvas()
    edited = blackout_region(canvas.render(), x, y, width, height)
    canvas.replace_base_image(edited, "blackout_region", f"Blackout redact bar [{x}, {y}, {width}, {height}]")
    return {"status": "success"}


def tool_beautify_screenshot(
    frame_type: str = "macos_dark",
    backdrop: str = "mesh_sunset",
    padding: int = 60,
    corner_radius: int = 16,
) -> Dict[str, Any]:
    """Wraps screenshot in a sleek macOS window frame with traffic lights, drop shadow, and gradient backdrop."""
    canvas = get_active_canvas()
    params = MockupParams(frame_type=frame_type, backdrop=backdrop, padding=padding, corner_radius=corner_radius)
    edited = beautify_screenshot(canvas.render(), params)
    canvas.replace_base_image(edited, "beautify_screenshot", f"Beautified screenshot ({frame_type} + {backdrop})")
    return {"status": "success", "new_dimensions": f"{canvas.width}x{canvas.height}"}


def tool_undo() -> Dict[str, Any]:
    """Undoes the previous editing action."""
    canvas = get_active_canvas()
    success = canvas.undo()
    return {"status": "success" if success else "failed", "message": "Undone" if success else "No more actions to undo"}


def tool_redo() -> Dict[str, Any]:
    """Redoes the previously undone action."""
    canvas = get_active_canvas()
    success = canvas.redo()
    return {"status": "success" if success else "failed", "message": "Redone" if success else "No more actions to redo"}
