# 📸 Autochrome

> **Autonomous photographic color science engine, MCP server, and real-time live preview studio for AI Agents (Claude Code, Cursor, Gemini CLI, Antigravity).**

---

<div align="center">

![Autochrome Product Launch Demo](assets/autochrome_demo.gif)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Ready](https://img.shields.io/badge/MCP-Standard%20stdio-green.svg)](https://modelcontextprotocol.io/)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-blueviolet.svg)](SKILL.md)
[![Zero Diffusion Distortions](https://img.shields.io/badge/CV-100%25%20Deterministic-orange.svg)](https://github.com/hgayan7/autochrome)

</div>

---

## 🤖 AI Agent Quick Reference & Protocol (For LLMs & Assistants)

If you are an **AI Agent (Claude, Cursor, Gemini, Antigravity, OpenCode, Codex)**, Autochrome provides deterministic, professional-grade computer vision tools and color science heuristics to edit photos and annotate screenshots.

### 📐 Standard 4-Step Agent Execution Lifecycle

When given a photo editing or screenshot annotation task, follow this standard sequence:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CANONICAL AGENT EXECUTION LIFECYCLE                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. OPEN & PREVIEW    ▶  open_image(image_path)                                                         │
│                         • Initializes session and boots Native macOS Live Darkroom Window for user.    │
│                                                                                                        │
│ 2. DIAGNOSE SCENE    ▶  inspect_image()                                                                │
│                         • Inspects Zone System exposure, lighting scenario, color cast, and depth.     │
│                                                                                                        │
│ 3. COLOR GRADE & CV  ▶  tune_image(), hsl_color_mixer(), color_wheels_grade(), portrait_retouch()      │
│                         • Dispatches deterministic CV tools (streamed to user's screen in real time).  │
│                                                                                                        │
│ 4. FINALIZE & EXPORT ▶  export_image(output_path, format="PNG")                                        │
│                         • Saves the final developed master asset to disk.                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### ⚡ Agent Rules of Engagement & Guardrails
1. **Always Open Preview First**: Calling `open_image(image_path)` automatically launches the **Native macOS Live Darkroom Preview** window (or Web Studio) on the user's screen. Inform the user they can press **`Space`** to hold-to-compare or **`S`** to toggle the split curtain slider.
2. **Never Guess Parameters Without Diagnosis**: Always run `inspect_image()` to check `lighting_scenario` (e.g. `overcast_flat`, `golden_hour`, `harsh_sunlight`), `optical_depth_evaluation`, and `zone_system_analysis`.
3. **Respect Optical Depth (Zero Fake Blur)**: If `has_natural_depth_of_field` is `True`, **DO NOT** apply fake lens blur. Use tonal separation and micro-contrast instead to avoid edge halos.
4. **Preserve Skin Tones on the 120° Vectorscope Line**: Always use `hsl_color_mixer(luminance_shifts={"orange": 12.0})` to enhance skin radiance without altering backgrounds or clothing colors.
5. **One-Shot Master Development**: For general enhancement without micromanagement, call `master_develop()` to run the autonomous 5-phase critique and development loop.

---

## 🌟 The Two Core Agent Superpowers

AI Agents can write code, browse the web, and run terminal commands. **Autochrome** gives them the missing visual superpowers:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       AUTOCHROME AGENT SUPERPOWERS                                      │
├────────────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│ 📸 SUPERPOWER 01: AGENTS EDITING PHOTOS            │ ✏️ SUPERPOWER 02: AGENTS ANNOTATING SCREENSHOTS    │
│ • Ansel Adams 11-Zone Luminance Calibration        │ • CleanShot-Style macOS Dark Window Bezels         │
│ • True Frequency Separation (100% Pore Retention)  │ • Multi-Stop Slate Gradient Mesh Backdrops         │
│ • Kodak Portra 400 & Analog Film Emulation         │ • Curved Anti-Aliased Vector Arrows                │
│ • 8-Channel HSL Mixing & 3-Way Color Wheels        │ • Sleek Embedded Pill Badges & Label Chips         │
│ • 100% Deterministic CV — Zero Diffusion Artifacts │ • 2.2x Floating Optical Detail Loupes              │
└────────────────────────────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## 🖥️ Live Darkroom Preview: Mac Native & Web Studio

Autochrome provides two preview experiences for monitoring AI agent edits in real-time, **preferring native Mac preview by default**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        DUAL LIVE PREVIEW MODES                                          │
├────────────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│ 🍏 PREFERRED: NATIVE MAC PREVIEW WINDOW            │ 🌐 WEB BROWSER STUDIO (Cross-Platform)             │
│ • Default mode on macOS                            │ • Access via browser at http://localhost:8000      │
│ • Dedicated floating darkroom window               │ • Real-time WebSocket canvas streaming            │
│ • Zero browser tabs or URL bar clutter             │ • Interactive Split-Screen Curtain Slider (Key: S) │
│ • Native macOS Cocoa rendering & instant launch   │ • Hold-to-Compare Original View (Key: Space)       │
│                                                    │ • Live Action Ledger & Quality Index telemetry     │
└────────────────────────────────────────────────────┴────────────────────────────────────────────────────┘
```

### 1. Launch Native Mac Preview (Default Preferred)
```bash
autochrome preview path/to/your/photo.jpg
```
*Launches an isolated native macOS floating darkroom window that updates in real-time as the agent dispatches MCP tools.*

### 2. Launch Web Browser Studio
```bash
autochrome preview path/to/your/photo.jpg --browser
```
*Opens the interactive Web Studio at `http://localhost:8000` with interactive curtain slider and comparison controls.*

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/hgayan7/autochrome.git
cd autochrome

# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### 2. Run the Interactive Tour Demo
Watch the agent autonomously develop a photo and beautify a presentation screenshot with real-time live preview:
```bash
autochrome demo
```
*Streams the live transformations step-by-step with hold-to-compare and split curtain slider controls.*

---

## 🤖 Connecting to AI Agents (Claude Code, Cursor, Gemini, Antigravity)

Autochrome provides both **MCP Tools** (the execution engine) and an **Agent Skill (`SKILL.md`)** (the artistic heuristics and photographic color science brain).

### 1. MCP Server Configuration (Tools)

#### Claude Desktop Configuration
Add Autochrome to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "autochrome": {
      "command": "/path/to/autochrome/.venv/bin/autochrome",
      "args": ["mcp"]
    }
  }
}
```

#### Cursor & Antigravity MCP Setup
In `.cursor/mcp.json` or Antigravity MCP settings:
```json
{
  "mcpServers": {
    "autochrome": {
      "command": "autochrome",
      "args": ["mcp"]
    }
  }
}
```

---

### 2. 🧠 Agent Skill Setup (`SKILL.md`)

While MCP provides raw tool endpoints, the **Autochrome Skill ([`SKILL.md`](SKILL.md))** teaches AI agents *how* to edit like professional colorists and master photographers rather than blindly executing random adjustments.

#### Installing the Skill for AI Agents

```bash
# Antigravity & Gemini CLI
mkdir -p ~/.gemini/config/skills/autochrome
cp SKILL.md ~/.gemini/config/skills/autochrome/SKILL.md

# Claude Code
mkdir -p ~/.claude/skills/autochrome
cp SKILL.md ~/.claude/skills/autochrome/SKILL.md

# Cursor
mkdir -p .cursor/skills/autochrome
cp SKILL.md .cursor/skills/autochrome/SKILL.md
```

---

## 🐍 Python SDK Reference (For Code-Generating Agents)

Agents writing direct Python automation scripts can import Autochrome engine modules directly:

```python
from autochrome.core.canvas import Canvas
from autochrome.mcp import tools

# 1. Load photo into session
tools.tool_open_image("input.jpg", launch_preview=True)

# 2. Diagnose scene lighting and metrics
metrics = tools.tool_inspect_image()

# 3. Apply color grading & retouching
tools.tool_tune_image(brightness=5, contrast=8, ambiance=20, highlights=-12, shadows=10, warmth=6)
tools.tool_hsl_color_mixer(luminance_shifts={"orange": 14.0})
tools.tool_portrait_retouch(face_spotlight=15, skin_smoothing=18, eye_clarity=30)
tools.tool_adjust_details(structure=12, sharpening=22)

# 4. Save result
tools.tool_export_image("output.png")
```

---

## 🛠️ Complete MCP Tool Catalog

### 🖥️ Live Darkroom Preview & Session Control
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `open_image` | `image_path: str`, `launch_preview: bool = True` | Loads photo into active canvas and auto-launches Live Preview (Native macOS floating window or browser) |
| `start_preview` | `native: bool = True`, `port: int = 8000`, `browser: bool = False` | Explicitly launches or connects the real-time Live Darkroom Preview window |
| `export_image` | `output_path: str`, `format: str = "PNG"`, `quality: int = 95` | Exports final edited composite image to disk (`PNG`, `JPEG`, `WEBP`) |
| `undo` | *none* | Undoes the last editing action on the active canvas |
| `redo` | *none* | Redoes the last undone action |

### 📸 Photographic Color Science & Analog Film Stocks
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `classify_scene` | *none* | Scene semantics, content genre (portrait, landscape, street, architecture), and adaptive recommendations |
| `smart_develop` | `target_mood: str = "auto"` | Autonomous scene-aware master development: diagnoses scene, adapts film stock, retouches portraits, and refines details |
| `apply_film_stock` | `stock_name: str`, `protect_skin: bool = True` | 13 authentic analog film stocks (`kodak_portra_400`, `cinestill_800t`, `fuji_velvia_50`, `kodak_trix_400`, `kodachrome_64`, `fuji_classic_chrome`, `polaroid_sx70`, `technicolor_3strip`, etc.) |
| `list_film_stocks` | *none* | Lists all 13 authentic film stock emulations with metadata and best use cases |
| `apply_film_halation` | `threshold: float = 215.0`, `radius: float = 24.0`, `intensity: float = 0.65` | CineStill-style crimson-orange specular halation bloom on intense light sources |
| `apply_orton_effect` | `strength: float = 0.30`, `blur_radius: float = 30.0` | Classic Michael Orton dreamy glow diffusion with micro-contrast retention |
| `apply_bleach_bypass` | `strength: float = 0.60`, `contrast_boost: float = 1.25` | Chemical silver retention for a gritty, high-contrast, desaturated cinematic aesthetic |
| `dehaze_image` | `strength: float = 0.70`, `window_size: int = 15` | Dark Channel Prior (DCP) atmospheric haze and fog removal |
| `set_color_temperature_kelvin` | `kelvin: int = 5500`, `tint: float = 0.0` | Physical 2000K-12000K Planckian Blackbody white balance and green/magenta tint |
| `add_photographic_grain` | `amount: float = 24.0`, `size: float = 1.0`, `roughness: float = 0.5` | Authentic density-dependent silver halide film grain peaking in Zone V midtones |
| `master_develop` | *none* | Autonomous 5-phase master development loop elevating quality scores to 90+ Master Studio Quality |
| `score_quality` | *none* | Computes 0-100 Photographic Aesthetic Index across Dynamic Range, Skin Radiance, Sharpness |
| `apply_3d_cube_lut` | `cube_path_or_content: str` | Applies DaVinci Resolve / ARRI 3D LUT (.cube format) using trilinear interpolation |
| `export_3d_cube_lut` | `output_path: str`, `lut_size: int = 33` | Exports active canvas grade as a standard .cube 3D LUT file |
| `remove_chromatic_aberration` | `purple_amount: float = 0.85`, `green_amount: float = 0.85`, `radius: int = 3` | Eliminates purple & green lateral chromatic aberration color fringing |
| `correct_lens_vignetting` | `amount: float = 35.0`, `midpoint: float = 50.0` | Compensates for optical lens light falloff (vignetting) |
| `merge_mertens_hdr` | `image_paths: List[str]` | Merges bracketed exposures into high-dynamic-range photo using OpenCV Mertens fusion |
| `scan_document` | `mode: str = "enhanced_color"`, `corners: Optional[List[List[int]]] = None` | Quad-corner document edge detection & flatbed perspective rectification |
| `render_code_snippet` | `code_text: str`, `language: str = "python"`, `title: str = "code.py"` | Carbon/Ray.so syntax-highlighted code snippet presentation mockup |
| `match_color_to_reference` | `reference_image_path: str`, `strength: float = 0.85` | Matches canvas color grade to a hero reference photo via CIELAB transfer |
| `apply_filter` | `filter_name: str` | 16-Filter Library presets ('polaroid_70s', 'cinematic_pop', 'cross_process', etc.) |
| `list_filters` | *none* | Lists all 16 available photo filters with descriptions |
| `passport_studio_portrait` | `aspect_ratio: str = "35x45"`, `backdrop: str = "studio_light_grey"` | Creates official biometric ISO 35x45mm and US 2x2 studio passport photos (~75% face ratio) |
| `replace_background` | `target_bg: str = "crimson_red"` | Deterministic chroma-key background replacement with 100% pure foreground protection |
| `frequency_separation` | `blur_radius: float = 3.5`, `smoothing_strength: float = 0.55` | Professional Frequency Separation: smooths skin tones while retaining 100% genuine pore texture |
| `keystone_correction` | `pitch: float = 0.0`, `yaw: float = 0.0`, `roll: float = 0.0` | 4-Point perspective homography correcting converging lines |
| `lens_distortion_correction` | `k1: float = -0.04`, `k2: float = 0.0` | Camera calibration radial lens distortion removal (barrel / pincushion) |
| `zone_system_calibration` | `zone_adjustments: Optional[Dict[int, float]] = None` | Ansel Adams 11-Zone photographic luminance calibration |
| `adaptive_color_grade` | `mood: str = "photographic"` | Analyzes image histogram & lighting to compute and apply a custom tailored grade |
| `hsl_color_mixer` | `hue_shifts`, `saturation_shifts`, `luminance_shifts` | 8-Channel targeted color grading (Orange for skin, Green for eyes, etc.) |
| `color_wheels_grade` | `shadow_hue`, `shadow_sat`, `shadow_lum`, `mid_*`, `high_*` | 3-Way Lift/Gamma/Gain color wheels grading |
| `tune_image` | `brightness`, `contrast`, `ambiance`, `highlights`, `shadows`, `warmth`, `tint`, `saturation` | Primary tone curve and local dynamic balancing (-100 to +100) |
| `adjust_details` | `structure: float = 0.0`, `sharpening: float = 0.0` | Fine micro-contrast texture pop and high-pass sharpening |
| `adjust_curves` | `preset: str = "hard_contrast"`, `channel: str = "rgb"` | Spline tone curves (`hard_contrast`, `brighten`, `darken`, `matte_vintage`, `cross_process`) |
| `portrait_retouch`| `face_spotlight`, `skin_smoothing`, `eye_clarity`, `skin_tone_warmth` | Facial illumination, skin texture preservation, and iris pop |
| `heal_blemish` | `center_x: int`, `center_y: int`, `radius: int = 20` | Content-aware inpaint patch healing brush |
| `selective_adjust`| `center_x`, `center_y`, `radius`, `brightness`, `contrast` | Localized radial control points |

---

### ✏️ Framing & Screenshot Studio Tools
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `smart_crop` | `aspect_ratio: str = "1:1"` ("1:1", "16:9", "4:5", "9:16", "4:3", "3:2") | Smart composition crop centered on face or focus point |
| `beautify_screenshot` | `frame_type: str = "macos_dark"`, `backdrop: str = "gradient_slate"`, `padding: int = 60` | macOS window bezel with traffic lights + mesh gradient backdrops |
| `draw_arrow_with_label` | `start_x`, `start_y`, `end_x`, `end_y`, `label_text: str` | Anti-aliased curved vector arrow with embedded descriptive text pill badge |
| `draw_arrow` | `start_x`, `start_y`, `end_x`, `end_y`, `color: str = "#FF9500"`, `curvature: float = 0.0` | Anti-aliased curved/straight vector arrow |
| `draw_callout` | `x`, `y`, `width`, `height`, `border_color: str`, `label: Optional[str]` | Spotlight rounded callout box with optional badge label |
| `draw_highlighter` | `x`, `y`, `width`, `height`, `color: str = "#FFCC00"`, `opacity: float = 0.4` | Semi-transparent marker highlight |
| `add_numbered_badge` | `x: int`, `y: int`, `number: int = 1`, `bg_color: str = "#007AFF"` | Circular numbered tutorial step badge (1, 2, 3) |
| `add_magnifier_loupe` | `target_x`, `target_y`, `loupe_x`, `loupe_y`, `radius: int = 70`, `zoom_factor: float = 2.2` | Zoom-in glass loupe showcasing fine detail |
| `blur_region` | `x`, `y`, `width`, `height`, `radius: int = 20` | Gaussian privacy blur for passwords / sensitive keys |
| `pixelate_region` | `x`, `y`, `width`, `height`, `block_size: int = 12` | Mosaic pixelation for emails / names |
| `blackout_region` | `x`, `y`, `width`, `height` | Solid opaque blackout bar |

---

### 👁️ Vision & Inspection
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `inspect_image` | *none* | Returns luminance, contrast, dynamic range, dominant color palette, and face bounding coordinates |
| `get_grid_overlay` | `grid_step: int = 100` | Overlays a calibrated coordinate grid (`100px` step) to assist VLMs in exact pixel targeting |

---

## 🧪 Testing

Run the automated test suite:
```bash
pytest -v
```

---

## 📄 License
MIT License • Created by [@hgayan7](https://github.com/hgayan7)
