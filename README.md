# 📸 Autochrome

> **Autonomous photographic color science engine, MCP server, and real-time live preview studio for AI Agents (Claude, Gemini, GPT-4o, Antigravity).**

---

## 🌟 Overview

Generative AI models create new images from text prompts, but they hallucinate details, distort human identity, and lack pixel precision. Traditional photo editors require manual human mouse and stylus manipulation.

**Autochrome** is built for the **era of autonomous agents**:
- **100% Local & Fast**: Runs entirely on your Mac/PC using NumPy, Pillow, and SciPy. Zero cloud dependencies.
- **Master Photographic Color Science**: Dynamic Zone System exposure balancing, 8-channel HSL color mixing, 3-way color wheels (Lift/Gamma/Gain), tone curves, and analog film emulation profiles.
- **Portrait & Texture Retouching**: Face spotlight illumination, texture skin smoothing, eye clarity pop, micro-contrast structure, and patch healing.
- **Presentation & Screenshot Studio**: Native macOS window frames with traffic light bezels, drop shadows, mesh gradient backdrops, curved vector arrows, spotlight callout boxes, highlighters, numbered tutorial badges, and privacy redactions (Gaussian blur, mosaic pixelate, blackout).
- **Distraction-Free Live Preview**: Real-time WebSocket live canvas that updates instantly as the agent executes each edit step, with a press-and-hold original comparison feature.
- **Model Context Protocol (MCP) Server**: Plugs directly into Claude Desktop, Cursor, Gemini CLI, or custom agents with standard stdio transport.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/your-username/agentic-photo-editor.git
cd agentic-photo-editor

# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### 2. Run the Interactive Tour Demo
Watch the agent autonomously edit a portrait and beautify a presentation screenshot with real-time live preview:
```bash
autochrome demo
```
*This opens your browser to `http://localhost:8000` and streams the live transformations step-by-step!*

---

### 3. Open Live Preview on Any Image
```bash
autochrome preview path/to/your/photo.jpg
```

---

## 🤖 Connecting to AI Agents (Claude Desktop, Cursor, Gemini)

### Claude Desktop Configuration
Add Autochrome to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "autochrome": {
      "command": "/Users/your-username/agentic-photo-editor/.venv/bin/autochrome",
      "args": ["mcp"]
    }
  }
}
```

---

## 🛠️ Complete Tool Catalog

### Photographic Color Science & Deterministic CV Tools
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `master_develop` | *none* | Autonomous 5-phase master development loop elevating quality scores to 90+ Master Studio Quality |
| `score_quality` | *none* | Computes 0-100 Photographic Aesthetic Index across Dynamic Range, Skin Radiance, Sharpness |
| `apply_3d_cube_lut` | `cube_path_or_content` | Applies DaVinci Resolve / ARRI 3D LUT (.cube format) using trilinear interpolation |
| `export_3d_cube_lut` | `output_path`, `lut_size` | Exports active canvas grade as a standard .cube 3D LUT file |
| `remove_chromatic_aberration` | `purple_amount`, `green_amount` | Eliminates purple & green lateral chromatic aberration color fringing |
| `correct_lens_vignetting` | `amount`, `midpoint` | Compensates for optical lens light falloff (vignetting) |
| `merge_mertens_hdr` | `image_paths` | Merges bracketed exposures into high-dynamic-range photo using OpenCV Mertens fusion |
| `scan_document` | `mode`, `corners` | Quad-corner document edge detection & flatbed perspective rectification |
| `render_code_snippet` | `code_text`, `language`, `title` | Carbon/Ray.so syntax-highlighted code snippet presentation mockup |
| `match_color_to_reference` | `reference_image_path`, `strength` | Matches canvas color grade to a hero reference photo via CIELAB transfer |
| `apply_filter` | `filter_name` | 16-Filter Library presets ('polaroid_70s', 'cinematic_pop', 'cross_process', etc.) |
| `list_filters` | *none* | Lists all 16 available photo filters with descriptions |
| `passport_studio_portrait` | `aspect_ratio`, `backdrop` | Creates official biometric ISO 35x45mm and US 2x2 studio passport photos (~75% face ratio) |
| `replace_background` | `target_bg` | Deterministic chroma-key background replacement with 100% pure foreground protection |
| `frequency_separation` | `blur_radius`, `smoothing_strength` | Professional Frequency Separation: smooths skin tones while retaining 100% genuine pore texture |
| `keystone_correction` | `pitch`, `yaw`, `roll` | 4-Point perspective homography correcting converging lines |
| `lens_distortion_correction` | `k1`, `k2` | Camera calibration radial lens distortion removal (barrel / pincushion) |
| `zone_system_calibration` | `zone_adjustments` | Ansel Adams 11-Zone photographic luminance calibration |
| `adaptive_color_grade` | `mood` | Analyzes image histogram & lighting to compute and apply a custom tailored grade |
| `hsl_color_mixer` | `hue_shifts`, `saturation_shifts`, `luminance_shifts` | 8-Channel targeted color grading (Orange for skin, Green for eyes, etc.) |
| `color_wheels_grade` | `shadows`, `midtones`, `highlights` | 3-Way Lift/Gamma/Gain color wheels grading |
| `apply_film_profile` | `profile` | Analog film emulation (`kodak_portra_400`, `fuji_pro_400h`, `cinematic_teal_orange`, `moody_nordic`) |
| `tune_image` | `brightness`, `contrast`, `ambiance`, `highlights`, `shadows`, `warmth`, `tint`, `saturation` | Primary tone curve and local dynamic balancing (-100 to +100) |
| `adjust_details` | `structure`, `sharpening` | Fine micro-contrast texture pop and high-pass sharpening |
| `adjust_curves` | `preset`, `channel` | Spline tone curves (`hard_contrast`, `brighten`, `darken`, `matte_vintage`, `cross_process`) |
| `portrait_retouch`| `face_spotlight`, `skin_smoothing`, `eye_clarity`, `skin_tone_warmth` | Facial illumination, skin texture preservation, and iris pop |
| `heal_blemish` | `center_x`, `center_y`, `radius` | Content-aware inpaint patch healing brush |
| `selective_adjust`| `center_x`, `center_y`, `radius`, `brightness`, `contrast` | Localized radial control points |

### Framing & Screenshot Studio Tools
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `smart_crop` | `aspect_ratio` ("1:1", "16:9", "4:5", "9:16") | Smart composition crop centered on face or focus point |
| `beautify_screenshot` | `frame_type`, `backdrop`, `padding`, `corner_radius` | macOS window bezel with traffic lights + mesh gradient backdrops |
| `draw_arrow_with_label` | `start_x`, `start_y`, `end_x`, `end_y`, `label_text` | Anti-aliased curved vector arrow with embedded descriptive text pill badge |
| `draw_arrow` | `start_x`, `start_y`, `end_x`, `end_y`, `color`, `curvature` | Anti-aliased curved/straight vector arrow |
| `draw_callout` | `x`, `y`, `width`, `height`, `border_color`, `label` | Spotlight rounded callout box with optional badge label |
| `draw_highlighter` | `x`, `y`, `width`, `height`, `color`, `opacity` | Semi-transparent marker highlight |
| `add_numbered_badge` | `x`, `y`, `number`, `bg_color` | Circular numbered tutorial step badge (1, 2, 3) |
| `add_magnifier_loupe` | `target_x`, `target_y`, `loupe_x`, `loupe_y`, `radius`, `zoom_factor` | Zoom-in glass loupe showcasing fine detail |
| `blur_region` | `x`, `y`, `width`, `height`, `radius` | Gaussian privacy blur for passwords / sensitive keys |
| `pixelate_region` | `x`, `y`, `width`, `height`, `block_size` | Mosaic pixelation for emails / names |
| `blackout_region` | `x`, `y`, `width`, `height` | Solid opaque blackout bar |

### Vision & Inspection
| Tool Name | Description |
| :--- | :--- |
| `inspect_image` | Returns luminance, contrast, dynamic range, dominant color palette, and face bounding coordinates |
| `get_grid_overlay` | Overlays a calibrated coordinate grid (`100px` step) to assist VLMs in exact pixel targeting |

---

## 🧪 Testing

Run the automated test suite:
```bash
pytest -v
```

---

## 📄 License
MIT License
