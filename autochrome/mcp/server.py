"""Standard MCP (Model Context Protocol) Server for Autochrome."""

import asyncio
from typing import Optional, List, Dict, Any
from mcp.server.mcpserver import MCPServer
from autochrome.mcp import tools

mcp_server = MCPServer("autochrome", description="Autonomous photographic color science and image editing studio for AI agents")


@mcp_server.tool(name="open_image", description="Loads an image from local filesystem into the active session.")
def open_image(image_path: str) -> Dict[str, Any]:
    return tools.tool_open_image(image_path)


@mcp_server.tool(name="export_image", description="Exports the final edited composite image to disk (format: 'PNG', 'JPEG', 'WEBP').")
def export_image(output_path: str, format: str = "PNG", quality: int = 95) -> Dict[str, Any]:
    return tools.tool_export_image(output_path, format, quality)


@mcp_server.tool(name="inspect_image", description="Analyzes current image metrics: luminance, contrast, dynamic range, dominant color palette, and face localization.")
def inspect_image() -> Dict[str, Any]:
    return tools.tool_inspect_image()


@mcp_server.tool(name="get_grid_overlay", description="Applies a numbered coordinate grid overlay to assist the agent in visual spatial targeting.")
def get_grid_overlay(grid_step: int = 100) -> Dict[str, Any]:
    return tools.tool_get_grid_overlay(grid_step)


@mcp_server.tool(name="tune_image", description="Primary Tone & Color Balancing: comprehensive tone curve and local dynamic adjustments (-100 to +100 for each parameter).")
def tune_image(
    brightness: float = 0.0,
    contrast: float = 0.0,
    saturation: float = 0.0,
    ambiance: float = 0.0,
    highlights: float = 0.0,
    shadows: float = 0.0,
    warmth: float = 0.0,
    tint: float = 0.0,
) -> Dict[str, Any]:
    return tools.tool_tune_image(brightness, contrast, saturation, ambiance, highlights, shadows, warmth, tint)


@mcp_server.tool(name="adjust_details", description="Details & Texture: boosts micro-contrast texture structure and high-pass sharpness.")
def adjust_details(structure: float = 0.0, sharpening: float = 0.0) -> Dict[str, Any]:
    return tools.tool_adjust_details(structure, sharpening)


@mcp_server.tool(name="adjust_curves", description="Tone Curves: applies multi-channel tone curves ('hard_contrast', 'brighten', 'darken', 'matte_vintage', 'cross_process').")
def adjust_curves(preset: str = "hard_contrast", channel: str = "rgb") -> Dict[str, Any]:
    return tools.tool_adjust_curves(preset, channel)


@mcp_server.tool(name="color_wheels_grade", description="3-Way Color Wheels grading (Shadows/Lift, Midtones/Gamma, Highlights/Gain).")
def color_wheels_grade(
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
    return tools.tool_color_wheels_grade(shadow_hue, shadow_sat, shadow_lum, mid_hue, mid_sat, mid_lum, high_hue, high_sat, high_lum)


@mcp_server.tool(name="hsl_color_mixer", description="8-Channel HSL Color Mixer (target Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta independently).")
def hsl_color_mixer(
    hue_shifts: Optional[Dict[str, float]] = None,
    saturation_shifts: Optional[Dict[str, float]] = None,
    luminance_shifts: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    return tools.tool_hsl_color_mixer(hue_shifts, saturation_shifts, luminance_shifts)


@mcp_server.tool(name="master_develop", description="Autonomous Master Development: evaluates, scores, and produces the optimal studio-grade edit with zero user micromanagement.")
def master_develop() -> Dict[str, Any]:
    return tools.tool_master_develop()


@mcp_server.tool(name="score_quality", description="Scores and critiques the image across exposure, tonal contrast, skin health, and sharpness (0-100).")
def score_quality() -> Dict[str, Any]:
    return tools.tool_score_quality()


@mcp_server.tool(name="passport_studio_portrait", description="Transforms a casual indoor selfie into an official biometric Studio-Grade Passport Photo.")
def passport_studio_portrait(aspect_ratio: str = "35x45", backdrop: str = "studio_light_grey") -> Dict[str, Any]:
    return tools.tool_passport_studio_portrait(aspect_ratio, backdrop)


@mcp_server.tool(name="replace_background", description="Removes current background (e.g. blue screen / solid backdrop) and composites onto target color (e.g. 'solid_red', 'crimson_red', 'studio_yellow').")
def replace_background(target_bg: str = "crimson_red") -> Dict[str, Any]:
    return tools.tool_replace_background(target_bg)


@mcp_server.tool(name="frequency_separation", description="Applies authentic Studio Frequency Separation: smooths low-frequency skin tones while preserving 100% of high-frequency skin pores.")
def frequency_separation(blur_radius: float = 3.5, smoothing_strength: float = 0.55) -> Dict[str, Any]:
    return tools.tool_frequency_separation(blur_radius, smoothing_strength)


@mcp_server.tool(name="keystone_correction", description="Corrects perspective keystoning (vertical/horizontal converging lines) using OpenCV 4-point homography.")
def keystone_correction(pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0) -> Dict[str, Any]:
    return tools.tool_keystone_correction(pitch, yaw, roll)


@mcp_server.tool(name="lens_distortion_correction", description="Corrects radial camera lens distortion (barrel / pincushion) using camera calibration matrix.")
def lens_distortion_correction(k1: float = -0.04, k2: float = 0.0) -> Dict[str, Any]:
    return tools.tool_lens_distortion_correction(k1, k2)


@mcp_server.tool(name="zone_system_calibration", description="Calibrates image across the 11 Ansel Adams Photographic Zones (Zone 0 to Zone X).")
def zone_system_calibration(zone_adjustments: Optional[Dict[int, float]] = None) -> Dict[str, Any]:
    return tools.tool_zone_system_calibration(zone_adjustments)


@mcp_server.tool(name="adaptive_color_grade", description="Dynamically analyzes the image's specific histogram, lighting, color cast, and depth to compute and apply a custom photographic color grade.")
def adaptive_color_grade(mood: str = "photographic") -> Dict[str, Any]:
    return tools.tool_adaptive_color_grade(mood)


@mcp_server.tool(name="split_toning", description="Photographic Split Toning: shadows vs highlights color separation with balance slider.")
def split_toning(
    shadow_hue: float = 210.0,
    shadow_sat: float = 0.0,
    highlight_hue: float = 40.0,
    highlight_sat: float = 0.0,
    balance: float = 0.0,
) -> Dict[str, Any]:
    return tools.tool_split_toning(shadow_hue, shadow_sat, highlight_hue, highlight_sat, balance)


@mcp_server.tool(name="apply_3d_cube_lut", description="Applies an industry-standard 3D LUT (.cube format) using trilinear interpolation.")
def apply_3d_cube_lut(cube_path_or_content: str) -> Dict[str, Any]:
    return tools.tool_apply_3d_cube_lut(cube_path_or_content)


@mcp_server.tool(name="export_3d_cube_lut", description="Exports the active grade as a standard .cube 3D LUT file.")
def export_3d_cube_lut(output_path: str, lut_size: int = 33, title: str = "Autochrome Grade") -> Dict[str, Any]:
    return tools.tool_export_3d_cube_lut(output_path, lut_size, title)


@mcp_server.tool(name="remove_chromatic_aberration", description="Eliminates purple and green color fringing along high-contrast backlit edges.")
def remove_chromatic_aberration(purple_amount: float = 0.85, green_amount: float = 0.85, radius: int = 3) -> Dict[str, Any]:
    return tools.tool_remove_chromatic_aberration(purple_amount, green_amount, radius)


@mcp_server.tool(name="correct_lens_vignetting", description="Compensates for optical lens light falloff (vignetting) towards image corners.")
def correct_lens_vignetting(amount: float = 35.0, midpoint: float = 50.0) -> Dict[str, Any]:
    return tools.tool_correct_lens_vignetting(amount, midpoint)


@mcp_server.tool(name="merge_mertens_hdr", description="Merges multiple bracketed image exposures into a high-dynamic-range photo using OpenCV Mertens fusion.")
def merge_mertens_hdr(image_paths: List[str]) -> Dict[str, Any]:
    return tools.tool_merge_mertens_hdr(image_paths)


@mcp_server.tool(name="scan_document", description="Auto-detects paper/receipt/whiteboard quad corners and rectifies to a flat, crisp scan.")
def scan_document(mode: str = "enhanced_color", corners: Optional[List[List[int]]] = None) -> Dict[str, Any]:
    return tools.tool_scan_document(mode, corners)


@mcp_server.tool(name="render_code_snippet", description="Renders a syntax-highlighted code snippet card with macOS window bezel and gradient backdrop.")
def render_code_snippet(code_text: str, language: str = "python", title: str = "code.py", backdrop: str = "gradient_slate") -> Dict[str, Any]:
    return tools.tool_render_code_snippet(code_text, language, title, backdrop)


@mcp_server.tool(name="match_color_to_reference", description="Matches the color grade, exposure, and tone of the canvas to a hero reference image using CIELAB color transfer.")
def match_color_to_reference(reference_image_path: str, strength: float = 0.85) -> Dict[str, Any]:
    return tools.tool_match_color_to_reference(reference_image_path, strength)


@mcp_server.tool(name="apply_film_profile", description="Applies authentic analog film emulation ('kodak_portra_400', 'fuji_pro_400h', 'cinematic_teal_orange', 'moody_nordic').")
def apply_film_profile(profile: str = "kodak_portra_400") -> Dict[str, Any]:
    return tools.tool_apply_film_profile(profile)


@mcp_server.tool(name="apply_filter", description="Applies one of the 16 FilterLibrary photo filters ('invert', 'grayscale', 'cyan_boost', 'moody_dark', 'cross_process', 'retro_warm', 'high_key', 'brightness_boost', 'dramatic', 'cool_blue', 'polaroid_70s', 'sepia', 'emboss', 'soft_blur', 'cinematic_pop', 'warm_sunset').")
def apply_filter(filter_name: str = "cinematic_pop") -> Dict[str, Any]:
    return tools.tool_apply_filter(filter_name)


@mcp_server.tool(name="list_filters", description="Lists all 16 available photo filters with descriptions.")
def list_filters() -> Dict[str, Any]:
    return tools.tool_list_filters()


@mcp_server.tool(name="apply_look", description="Applies curated aesthetic style look ('linkedin_pro', 'drama', 'vintage_film', 'noir_bw', 'glamour_glow', 'crisp_editorial', 'cyberpunk').")
def apply_look(look_name: str = "linkedin_pro") -> Dict[str, Any]:
    return tools.tool_apply_look(look_name)


@mcp_server.tool(name="selective_adjust", description="Selective Adjust: modifies brightness/contrast/saturation in a targeted circular area.")
def selective_adjust(
    center_x: int,
    center_y: int,
    radius: int = 150,
    brightness: float = 0.0,
    contrast: float = 0.0,
    saturation: float = 0.0,
) -> Dict[str, Any]:
    return tools.tool_selective_adjust(center_x, center_y, radius, brightness, contrast, saturation)


@mcp_server.tool(name="portrait_retouch", description="Studio Portrait Retouch: face spotlight illumination, texture skin smoothing, and eye clarity pop.")
def portrait_retouch(
    face_spotlight: float = 20.0,
    skin_smoothing: float = 25.0,
    eye_clarity: float = 30.0,
    skin_tone_warmth: float = 5.0,
) -> Dict[str, Any]:
    return tools.tool_portrait_retouch(face_spotlight, skin_smoothing, eye_clarity, skin_tone_warmth)


@mcp_server.tool(name="heal_blemish", description="Healing: content-aware patch removal for spots, blemishes, or small unwanted artifacts.")
def heal_blemish(center_x: int, center_y: int, radius: int = 20) -> Dict[str, Any]:
    return tools.tool_heal_blemish(center_x, center_y, radius)


@mcp_server.tool(name="smart_crop", description="Smart crops image to aspect ratio ('1:1', '16:9', '4:5', '9:16', '4:3', '3:2') centered on focus point or auto-detected face.")
def smart_crop(aspect_ratio: str = "1:1", focus_x: Optional[int] = None, focus_y: Optional[int] = None) -> Dict[str, Any]:
    return tools.tool_smart_crop(aspect_ratio, focus_x, focus_y)


@mcp_server.tool(name="crop_box", description="Crops an exact bounding box from the canvas.")
def crop_box(x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    return tools.tool_crop_box(x, y, width, height)


@mcp_server.tool(name="rotate_straighten", description="Rotates/straightens the image by specified degrees.")
def rotate_straighten(angle_deg: float) -> Dict[str, Any]:
    return tools.tool_rotate_straighten(angle_deg)


@mcp_server.tool(name="draw_arrow", description="Draws a clean vector arrow with optional curvature (-1.0 to 1.0) pointing towards target.")
def draw_arrow(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    color: str = "#FF3B30",
    stroke_width: int = 4,
    curvature: float = 0.0,
) -> Dict[str, Any]:
    return tools.tool_draw_arrow(start_x, start_y, end_x, end_y, color, stroke_width, curvature)


@mcp_server.tool(name="draw_arrow_with_label", description="Draws a vector arrow pointing to a UI element with an embedded descriptive pill badge text.")
def draw_arrow_with_label(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    label_text: str,
    color: str = "#00E5FF",
    stroke_width: int = 3,
    curvature: float = 0.0,
) -> Dict[str, Any]:
    return tools.tool_draw_arrow_with_label(start_x, start_y, end_x, end_y, label_text, color, stroke_width, curvature)


@mcp_server.tool(name="draw_callout", description="Draws a rounded spotlight callout box with optional label chip.")
def draw_callout(
    x: int,
    y: int,
    width: int,
    height: int,
    border_color: str = "#FF9500",
    fill_color: Optional[str] = None,
    label: Optional[str] = None,
    label_bg: Optional[str] = None,
) -> Dict[str, Any]:
    return tools.tool_draw_callout(x, y, width, height, border_color, fill_color, label, label_bg)


@mcp_server.tool(name="draw_highlighter", description="Draws a semi-transparent marker highlighter bar.")
def draw_highlighter(x: int, y: int, width: int, height: int, color: str = "#FFCC00", opacity: float = 0.4) -> Dict[str, Any]:
    return tools.tool_draw_highlighter(x, y, width, height, color, opacity)


@mcp_server.tool(name="add_numbered_badge", description="Adds a circular numbered tutorial step badge (e.g. 1, 2, 3).")
def add_numbered_badge(x: int, y: int, number: int = 1, bg_color: str = "#007AFF") -> Dict[str, Any]:
    return tools.tool_add_numbered_badge(x, y, number, bg_color)


@mcp_server.tool(name="add_magnifier_loupe", description="Adds a circular magnifying loupe glass showcasing a zoomed detail.")
def add_magnifier_loupe(
    target_x: int,
    target_y: int,
    loupe_x: int,
    loupe_y: int,
    radius: int = 80,
    zoom_factor: float = 2.0,
) -> Dict[str, Any]:
    return tools.tool_add_magnifier_loupe(target_x, target_y, loupe_x, loupe_y, radius, zoom_factor)


@mcp_server.tool(name="blur_region", description="Gaussian blurs a rectangular region to redact sensitive information.")
def blur_region(x: int, y: int, width: int, height: int, radius: int = 20) -> Dict[str, Any]:
    return tools.tool_blur_region(x, y, width, height, radius)


@mcp_server.tool(name="pixelate_region", description="Pixelates a rectangular region with mosaic blocks.")
def pixelate_region(x: int, y: int, width: int, height: int, block_size: int = 12) -> Dict[str, Any]:
    return tools.tool_pixelate_region(x, y, width, height, block_size)


@mcp_server.tool(name="blackout_region", description="Applies an opaque solid blackout redact bar.")
def blackout_region(x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    return tools.tool_blackout_region(x, y, width, height)


@mcp_server.tool(name="beautify_screenshot", description="Wraps screenshot in a sleek macOS window frame with traffic lights, drop shadow, and gradient backdrop.")
def beautify_screenshot(
    frame_type: str = "macos_dark",
    backdrop: str = "mesh_sunset",
    padding: int = 60,
    corner_radius: int = 16,
) -> Dict[str, Any]:
    return tools.tool_beautify_screenshot(frame_type, backdrop, padding, corner_radius)


@mcp_server.tool(name="undo", description="Undoes the previous editing action.")
def undo() -> Dict[str, Any]:
    return tools.tool_undo()


@mcp_server.tool(name="redo", description="Redoes the previously undone action.")
def redo() -> Dict[str, Any]:
    return tools.tool_redo()


def run_stdio():
    """Runs the MCP server over standard input/output for Claude Desktop, Gemini, etc."""
    asyncio.run(mcp_server.run_stdio_async())


if __name__ == "__main__":
    run_stdio()
