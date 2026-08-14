---
name: agentic-photo-editor
description: Professional autonomous photographic color grading, portrait retouching, and Snapseed/Lightroom-grade image processing for AI agents.
---

# Autochrome: Professional Photography & Color Science Playbook

This skill equips AI agents (Claude, Gemini, GPT-4o, Antigravity) with the deep artistic and technical principles of professional photography, color science (DaVinci Resolve / Lightroom), and scene-aware image processing.

---

## 1. Fundamental Rules of Photography for AI Agents

1. **Scene-Aware Intelligence Over Fixed Macros**:
   - Never blindly execute the same sequence of tools. Every photo has unique lighting, existing depth-of-field, color harmony, and emotional intent.
   - Always call `inspect_image()` first to diagnose the **lighting scenario**, **Zone System exposure balance**, **color temperature**, and **optical depth metrics**.

2. **CRITICAL: Respect Optical Depth-of-Field (Do NOT Apply Fake Blur)**:
   - If `optical_depth_evaluation.has_natural_depth_of_field` is `True` or if the photo is in a natural environment (car interior, cafe, urban street) where background elements are geometrically complex, **DO NOT apply artificial elliptical lens blur**.
   - Artificial blur creates jarring edge halos around shoulders, hair, and clothing. True professional photographers achieve depth through **tonal separation, micro-contrast, and color contrast (warm foreground vs cool background)**.

3. **Color Science & Color Grading Principles**:
   - **Vectorscope Skin Tone Line (I-Line)**: Human skin (all ethnicities) falls on the 120° hue line. Use the `hsl_color_mixer` (specifically `orange` and `red` channels) to adjust skin luminance and saturation without tinting clothing or background.
   - **Color Harmony & Color Wheels**: Use `color_wheels_grade` (Lift, Gamma, Gain) to introduce complementary harmonies (e.g. subtle navy/teal in shadows with golden champagne in highlights).
   - **Split Toning**: Create cinematic separation by tinting shadows (`shadow_hue: 215°`, `shadow_sat: 10-18%`) and highlights (`highlight_hue: 38-45°`, `highlight_sat: 8-15%`).

---

## 2. Professional Photographic Workflows

### A. Golden Hour / Editorial Portrait Color Grading (e.g., Car Selfies, Natural Light)
When color grading portraits with flat or overcast lighting:

1. **Step 1: Diagnose Scene**:
   - `inspect_image()` $\rightarrow$ Check if overcast, flat, or cool-cast.
2. **Step 2: Correct Tone & Dynamic Balance (`tune_image`)**:
   - Recover clipped highlights (`highlights: -12 to -20`).
   - Lift shadow details (`shadows: +8 to +16`).
   - Introduce local midtone dynamics with **Ambiance** (`ambiance: +20 to +30`).
   - Adjust global warmth and saturation subtly (`warmth: +4 to +8`, `saturation: +4 to +8`).
3. **Step 3: 8-Channel Selective HSL Color Mix (`hsl_color_mixer`)**:
   - **Orange**: Increase luminance (`luminance: +10 to +18`) for glowing radiant skin without over-saturating.
   - **Yellow / Green**: Target eye irises or foliage (`saturation: +15`, `luminance: +8`).
   - **Blue / Aqua**: Deepen or enrich clothing/sky.
4. **Step 4: 3-Way Color Wheels Separation (`color_wheels_grade`)**:
   - **Shadows**: Add cool navy/slate depth (`shadow_hue: 215`, `shadow_sat: 12`, `shadow_lum: -4`).
   - **Highlights**: Add golden champagne warmth (`high_hue: 42`, `high_sat: 14`, `high_lum: +3`).
5. **Step 5: Portrait Retouching & Eye Catchlights (`portrait_retouch`)**:
   - Gently pop iris clarity (`eye_clarity: +30 to +40`).
   - Soften sensor noise while preserving freckles (`skin_smoothing: +12 to +18`).
6. **Step 6: Optical Micro-Contrast (`adjust_details`)**:
   - Refine eyelashes, eyebrows, and hair texture (`structure: +10 to +14`, `sharpening: +22 to +28`).

---

### B. High-Contrast Monochrome / Fine Art Noir
1. Desaturate via `tune_image(saturation: -100, contrast: +30, ambiance: +35)`.
2. Curve S-curve for deep velvety Zone I blacks and Zone VIII crisp whites via `adjust_curves(preset: "hard_contrast")`.
3. Pop micro-texture with `adjust_details(structure: +30, sharpening: +30)`.

---

## 3. Tool Reference

| Tool Name | Parameters | Best Use Case |
| :--- | :--- | :--- |
| `inspect_image` | None | Scene lighting diagnosis, Zone System exposure, depth evaluation |
| `hsl_color_mixer` | `hue_shifts`, `saturation_shifts`, `luminance_shifts` | 8-channel targeted color grading (Orange=skin, Green=eyes) |
| `color_wheels_grade`| `shadows`, `midtones`, `highlights` | 3-way Lift/Gamma/Gain color grading |
| `split_toning` | `shadow_hue`, `shadow_sat`, `highlight_hue`, `highlight_sat`, `balance` | Highlights vs shadows color separation |
| `tune_image` | `brightness`, `contrast`, `ambiance`, `highlights`, `shadows`, `warmth`, `tint` | Tone balancing and local dynamic contrast |
| `adjust_curves` | `preset`, `channel` | Tone curves (spline interpolation) |
| `portrait_retouch`| `face_spotlight`, `skin_smoothing`, `eye_clarity` | Facial key-lighting and iris clarity |
| `adjust_details` | `structure`, `sharpening` | High-pass micro-contrast texture popping |
