---
name: autochrome
description: Autonomous photographic color science engine, screenshot annotation studio, and live darkroom preview for AI Agents (Claude Code, Cursor, Gemini).
---

# Autochrome: Professional Photography, Film Science & Darkroom Playbook

This skill equips AI agents (Claude, Gemini, GPT-4o, Antigravity) with the deep artistic and technical principles of professional photography, color science (DaVinci Resolve / Lightroom), analog film stock emulation, and scene-aware image processing.

---

## 1. Fundamental Rules of Photography & Live Workflow for AI Agents

1. **RULE 0: ALWAYS LAUNCH LIVE DARKROOM PREVIEW FIRST**:
   - Whenever starting any image editing or development task, **ALWAYS begin by calling `open_image(image_path)`** (which automatically boots the Live Preview) or `start_preview()`.
   - Autochrome defaults to a dedicated **Native macOS Floating Darkroom Window** (or Web Studio at `http://localhost:8000`), streaming every single adjustment in real-time with zero latency.
   - Inform the user right away that the Live Darkroom window is open and streaming their photo:
     > *"I've opened the Native macOS Live Darkroom window on your screen. You can watch adjustments live as I edit, press and hold **Space** to hold-to-compare with the original, or press **S** to toggle the split curtain slider."*

2. **RULE 1: ALWAYS ANALYZE FIRST BEFORE APPLYING ANY GRADE**:
   - **Never blindly apply a film stock or preset without understanding the image first**.
   - Call `classify_scene()` or `inspect_image()` to diagnose:
     - **Content Genre**: `portrait`, `landscape_nature`, `street_night`, `architecture_interior`, `ui_screenshot`
     - **Subject Profile**: Human faces, skin vectorscope ratio, eye/hair clarity
     - **Atmospheric & Optical Conditions**: Foliage, sky, specular highlights, dynamic range, estimated Kelvin temperature (2000K-12000K)
   - Based on this analysis, choose or adapt the optimal color grade, film stock, and optical physics pipeline.

3. **RULE 2: RESPECT OPTICAL DEPTH-OF-FIELD & SKIN HEALTH**:
   - **Never apply fake elliptical blur** to photos with natural environmental backgrounds. True depth is achieved through **tonal separation, micro-contrast, and color contrast (warm foreground vs cool background)**.
   - **Skin Protection**: Human skin falls on the 120° vectorscope I-Line. When applying intense color grades (e.g. Fuji Velvia or Bleach Bypass), Autochrome's `protect_skin=True` automatically preserves healthy, radiant skin tones.

---

## 2. Master Film Stocks (13 Iconic Emulations)

Autochrome includes 13 authentic, scientifically calibrated analog film stocks:

| Film Stock | Category | Signature Look & Best Use Case |
| :--- | :--- | :--- |
| `kodak_portra_400` | Portrait & Editorial | Warm golden skin tones, gentle highlight rolloff, soft pastels, cyan-subtracted shadows. Ideal for portraits & golden hour. |
| `kodak_portra_160` | Studio Portrait | Ultra-fine grain, neutral warm skin, smooth pastel transitions. Best for studio lighting & fashion. |
| `cinestill_800t` | Cinematic & Night | Tungsten 3200K balance, cool teal/cyan shadows, glowing crimson halation bloom around street lights. |
| `kodak_trix_400` | Black & White Noir | Zone I/II velvety blacks, silver halide midtone micro-grain, punchy contrast. Best for street photojournalism. |
| `ilford_hp5` | Documentary B&W | Wide exposure latitude, soft medium contrast, rich shadow detail, smooth tonal gradations. |
| `fuji_velvia_50` | Vibrant Landscape | Hyper-saturated emerald greens, deep cobalt blues, punchy contrast. Built-in skin protection. |
| `fuji_provia_100f` | Reversal Slide | Neutral, faithful color rendition, vivid primaries, balanced contrast. |
| `kodachrome_64` | Vintage Classic | Rich warm reds, golden amber midtones, deep inky blacks. 1970s National Geographic print look. |
| `fuji_classic_chrome` | Documentary / Street | Muted greens and cyans, warm earthen midtones, hard shadow contrast. Minimalist editorial look. |
| `polaroid_sx70` | Instant Vintage | Faded matte blacks, warm green/magenta crossover, dreamy diffusion, retro instant print charm. |
| `agfa_vista_200` | Color Print Vintage | Vibrant golden-red bias, punchy dynamic contrast, 1990s color print nostalgia. |
| `technicolor_2strip` | 1920s Cinema | Early Hollywood two-color beam splitter (Red & Cyan). Subtracted blues, coral skin tones. |
| `technicolor_3strip` | Golden Age Cinema | 1930s-1950s dye-transfer imbibition: hyper-saturated primaries, deep dense blacks. |

---

## 3. Optical Physics & Darkroom Algorithms

- **`apply_film_halation(threshold, radius, intensity)`**: Simulates CineStill crimson specular bloom where high-intensity light scatters across the bottom red emulsion layer.
- **`apply_orton_effect(strength, blur_radius)`**: Classic 1980s Michael Orton sandwich slide glow while preserving micro-contrast sharpness.
- **`apply_bleach_bypass(strength, contrast)`**: Chemical silver retention for a gritty, desaturated cinematic aesthetic.
- **`dehaze_image(strength, window_size)`**: Dark Channel Prior (DCP) physical transmission map inversion to eliminate atmospheric fog and milkiness.
- **`set_color_temperature_kelvin(kelvin, tint)`**: Planckian Blackbody color temperature grading (2000K-12000K) and green/magenta tint.
- **`add_photographic_grain(amount, size, roughness)`**: True zone-dependent silver halide grain peaking in Zone V midtones ($f(L) = \sin(\pi \cdot L)$).

---

## 4. Scene-Aware Master Development (`smart_develop`)

When you want an autonomous, complete master development with zero micromanagement:
1. Call `smart_develop(target_mood="auto")`.
2. It automatically:
   - Diagnoses scene content (`portrait`, `landscape`, `night`, etc.)
   - Calibrates the ideal film stock with skin protection
   - Clears atmospheric haze if overcast/landscape
   - Retouches portrait lighting and pops iris clarity if a human subject is detected
   - Triggers specular halation on night lights
   - Refines micro-contrast texture and edge sharpness
   - Quantifies the before-and-after improvement on the 0-100 Aesthetic Index

---

## 5. Complete Tool Reference

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `open_image` | `image_path`, `launch_preview` | Loads photo and automatically opens Native macOS Live Darkroom Window |
| `start_preview` | `native`, `port`, `browser` | Explicitly opens Native macOS floating darkroom window or web studio |
| `classify_scene` | None | Scene semantics, content genre, and adaptive grading recommendations |
| `smart_develop` | `target_mood` | Autonomous scene-aware master development workflow |
| `apply_film_stock` | `stock_name`, `protect_skin` | Applies 1 of the 13 authentic analog film stocks |
| `list_film_stocks` | None | Returns catalog of all 13 film stocks with descriptions |
| `apply_film_halation`| `threshold`, `radius`, `intensity` | CineStill crimson halation bloom on specular highlights |
| `apply_orton_effect` | `strength`, `blur_radius` | Dreamy Orton glow diffusion with micro-contrast retention |
| `apply_bleach_bypass`| `strength`, `contrast_boost` | Gritty cinematic silver retention bypass |
| `dehaze_image` | `strength`, `window_size` | Dark Channel Prior atmospheric haze removal |
| `set_color_temperature_kelvin` | `kelvin`, `tint` | 2000K-12000K Planckian Blackbody white balance |
| `add_photographic_grain` | `amount`, `size`, `roughness` | True luminance-aware silver halide grain |
| `hsl_color_mixer` | `hue_shifts`, `saturation_shifts`, `luminance_shifts` | 8-channel targeted color grading |
| `color_wheels_grade`| `shadows`, `midtones`, `highlights` | 3-way Lift/Gamma/Gain color grading |
| `split_toning` | `shadow_hue`, `shadow_sat`, `highlight_hue`, `highlight_sat`, `balance` | Shadows vs highlights color separation |
| `tune_image` | `brightness`, `contrast`, `ambiance`, `highlights`, `shadows`, `warmth`, `tint` | Tone balancing and local dynamic contrast |
| `adjust_curves` | `preset`, `channel` | Tone curves (spline interpolation) |
| `portrait_retouch`| `face_spotlight`, `skin_smoothing`, `eye_clarity` | Facial key-lighting and iris clarity |
| `adjust_details` | `structure`, `sharpening` | High-pass micro-contrast texture popping |
| `export_image` | `output_path`, `format`, `quality` | Save the final developed master photo to disk |
