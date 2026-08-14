"""Command-line interface for Autochrome."""

import sys
import os
import time
import argparse
from PIL import Image, ImageDraw

from autochrome.core.canvas import Canvas
from autochrome.preview.window import LivePreviewHost
from autochrome.mcp.tools import set_active_canvas, get_active_canvas
from autochrome.mcp import tools
from autochrome.mcp.server import run_stdio


def create_demo_portrait() -> str:
    """Generates a synthetic portrait test photo."""
    os.makedirs("/tmp/autochrome_demo", exist_ok=True)
    path = "/tmp/autochrome_demo/portrait_sample.png"
    img = Image.new("RGBA", (900, 1200), (45, 55, 72, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(1200):
        c = int(45 + (y / 1200) * 40)
        draw.line([(0, y), (900, y)], fill=(c, c + 5, c + 15, 255))

    # Silhouette / Portrait shoulders
    draw.ellipse([(200, 750), (700, 1400)], fill=(30, 41, 59, 255))
    # Neck
    draw.rectangle([(400, 600), (500, 800)], fill=(225, 175, 145, 255))
    # Face head
    draw.ellipse([(320, 320), (580, 680)], fill=(235, 185, 155, 255))
    # Hair
    draw.chord([(310, 280), (590, 560)], start=180, end=360, fill=(35, 25, 20, 255))
    # Eyes
    draw.ellipse([(390, 470), (425, 495)], fill=(255, 255, 255, 255))
    draw.ellipse([(402, 477), (417, 492)], fill=(50, 80, 120, 255))
    draw.ellipse([(475, 470), (510, 495)], fill=(255, 255, 255, 255))
    draw.ellipse([(483, 477), (498, 492)], fill=(50, 80, 120, 255))
    # Smile
    draw.arc([(420, 560), (480, 600)], start=0, end=180, fill=(180, 70, 70, 255), width=4)

    img.save(path)
    return path


def create_demo_screenshot() -> str:
    """Generates a synthetic UI screenshot test image."""
    os.makedirs("/tmp/autochrome_demo", exist_ok=True)
    path = "/tmp/autochrome_demo/screenshot_sample.png"
    img = Image.new("RGBA", (1000, 650), (18, 20, 24, 255))
    draw = ImageDraw.Draw(img)

    # Header navbar
    draw.rectangle([(0, 0), (1000, 50)], fill=(28, 32, 38, 255))
    draw.text((25, 18), "⚡ CloudApp Dashboard", fill=(240, 242, 245, 255))
    
    # API key card
    draw.rounded_rectangle([(60, 90), (940, 220)], radius=8, fill=(28, 32, 38, 255), outline=(50, 55, 65, 255), width=1)
    draw.text((85, 115), "Production Secret API Key:", fill=(160, 165, 175, 255))
    draw.text((85, 145), "key_prod_demo_sample_confidential_998877 (CONFIDENTIAL)", fill=(255, 95, 87, 255))
    draw.rounded_rectangle([(780, 135), (910, 175)], radius=6, fill=(0, 122, 255, 255))
    draw.text((810, 147), "Copy Key", fill=(255, 255, 255, 255))

    # User profile row
    draw.rounded_rectangle([(60, 260), (940, 420)], radius=8, fill=(28, 32, 38, 255), outline=(50, 55, 65, 255), width=1)
    draw.text((85, 285), "User Account: alex.founder@company.com", fill=(240, 242, 245, 255))
    draw.text((85, 325), "Billing Address: 440 Silicon Way, San Francisco, CA", fill=(160, 165, 175, 255))
    
    # Deploy button
    draw.rounded_rectangle([(60, 470), (280, 530)], radius=8, fill=(52, 199, 89, 255))
    draw.text((95, 492), "🚀 Deploy Production", fill=(255, 255, 255, 255))

    img.save(path)
    return path


def run_demo_workflow():
    """Runs an interactive end-to-end demo demonstrating both DP and Screenshot workflows with live preview."""
    print("\n" + "=" * 65)
    print(" 📸 AGENTPHOTO: LIVE AGENT EDITING TOUR")
    print("=" * 65)

    portrait_path = create_demo_portrait()
    print(f"\n[1/2] Launching DP Profile Picture Workflow on {portrait_path}...")

    canvas = Canvas.from_file(portrait_path)
    set_active_canvas(canvas)

    # Launch Live Preview Host (starts server and opens browser window)
    host = LivePreviewHost(canvas, port=8000, auto_open=True)
    host.start()
    time.sleep(1.5)

    # Step 1: Inspect
    print("\n🔍 Step 1: Agent inspects portrait metrics...")
    metrics = tools.tool_inspect_image()
    time.sleep(1.8)

    # Step 2: Smart Crop to 1:1 DP
    print("\n✂️ Step 2: Agent executes Smart Crop to 1:1 circular DP framing...")
    tools.tool_smart_crop(aspect_ratio="1:1")
    time.sleep(2.0)

    # Step 3: Primary Tone Balancing
    print("\n🎨 Step 3: Agent tunes Ambiance (+20), Warmth (+8), Highlights (-10)...")
    tools.tool_tune_image(brightness=4, contrast=8, ambiance=20, highlights=-10, shadows=15, warmth=8, saturation=6)
    time.sleep(2.0)

    # Step 4: Optical Lens Blur / Bokeh
    print("\n✨ Step 4: Agent applies optical Lens Blur (Bokeh Depth of Field)...")
    tools.tool_lens_blur_bokeh(inner_radius=220, outer_radius=420, blur_strength=35, bokeh_boost=15, vignette=12)
    time.sleep(2.0)

    # Step 5: Portrait Retouch
    print("\n👤 Step 5: Agent applies Portrait Retouch (Face Spotlight + Skin Smoothing + Eye Clarity)...")
    tools.tool_portrait_retouch(face_spotlight=20, skin_smoothing=25, eye_clarity=35, skin_tone_warmth=6)
    time.sleep(2.2)

    # Step 6: Details Structure Pop
    print("\n🔬 Step 6: Agent applies Structure & High-pass Sharpening...")
    tools.tool_adjust_details(structure=15, sharpening=25)
    time.sleep(2.5)

    print("\n" + "-" * 65)
    print(" [2/2] Now switching to Screenshot Beautifier & Redaction Workflow...")
    print("-" * 65)
    time.sleep(2.0)

    screenshot_path = create_demo_screenshot()
    tools.tool_open_image(screenshot_path)
    time.sleep(1.5)

    # Step 7: Redact Secret API key
    print("\n🔒 Step 7: Agent redacts sensitive API key with Gaussian privacy blur...")
    tools.tool_blur_region(x=80, y=140, width=680, height=32, radius=18)
    time.sleep(2.0)

    # Step 8: Spotlight Callout
    print("\n📦 Step 8: Agent highlights Deploy button with spotlight callout...")
    tools.tool_draw_callout(x=610, y=285, width=120, height=45, border_color="#FF9500", label="Action")
    time.sleep(2.0)

    # Step 9: Vector Arrow
    print("\n🏹 Step 9: Agent draws curved vector arrow pointing to the action...")
    tools.tool_draw_arrow(start_x=450, start_y=350, end_x=600, end_y=310, color="#FF9500", curvature=0.15)
    time.sleep(2.0)

    # Step 10: Window Frame
    print("\n🖼️ Step 10: Agent wraps into presentation frame with mesh sunset backdrop...")
    tools.tool_beautify_screenshot(frame_type="macos_dark", backdrop="mesh_sunset", padding=60)
    time.sleep(1.5)

    print("\n" + "=" * 65)
    print("🎉 TOUR COMPLETED! Final outputs rendered live on your screen.")
    print("=" * 65 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting Autochrome demo.")


def main():
    parser = argparse.ArgumentParser(description="Autochrome: Autonomous photographic color science & MCP server")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # MCP server command
    subparsers.add_parser("mcp", help="Run standard stdio MCP server for Claude, Gemini, Cursor")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Open an image and start Live Preview server")
    preview_parser.add_argument("image_path", help="Path to image file")
    preview_parser.add_argument("--port", type=int, default=8000, help="Port for Live Preview (default: 8000)")
    preview_parser.add_argument("--native", action="store_true", default=True, help="Open floating native Mac desktop window (default)")
    preview_parser.add_argument("--browser", action="store_true", help="Open in default web browser instead of native window")

    # Develop command (Autonomous Master Development)
    dev_parser = subparsers.add_parser("develop", help="Autonomously critique, score, and develop an image to studio perfection")
    dev_parser.add_argument("image_path", help="Path to raw image file")
    dev_parser.add_argument("--output", "-o", default=None, help="Output path for developed image")
    dev_parser.add_argument("--preview", "-p", action="store_true", help="Launch live preview window")

    # Batch command (Batch shoot color matching & development)
    batch_parser = subparsers.add_parser("batch", help="Batch develop and match an entire folder of shoot photos to a reference image")
    batch_parser.add_argument("input_dir", help="Directory containing source images")
    batch_parser.add_argument("--reference", "-r", default=None, help="Path to hero reference image to match against")
    batch_parser.add_argument("--output", "-o", default="batch_output", help="Output directory for developed images")
    batch_parser.add_argument("--strength", "-s", type=float, default=0.85, help="Color match strength (0.0 to 1.0)")

    args = parser.parse_args()

    if args.command == "mcp":
        run_stdio()
    elif args.command == "batch":
        from autochrome.engine.batch import process_batch_shoot
        print(f"\n🚀 Processing batch in '{args.input_dir}'...")
        res = process_batch_shoot(args.input_dir, args.output, reference_path=args.reference, strength=args.strength)
        print(f"✅ Successfully developed {res['processed_count']} images into '{res['output_directory']}'\n")
    elif args.command == "develop":
        from autochrome.engine.master_critic import auto_master_develop
        raw_img = Image.open(args.image_path)
        out_img, report = auto_master_develop(raw_img)
        
        b_crit = report["before_critique"]
        a_crit = report["after_critique"]
        
        print("\n" + "=" * 65)
        print(" 🎞️ AUTOCHROME: MASTER PHOTOGRAPHIC DEVELOPMENT REPORT")
        print("=" * 65)
        print(f" Input File: {args.image_path}")
        print(f"\n 📊 BEFORE CRITIQUE:")
        print(f"   • Overall Aesthetic Index: {b_crit['overall_aesthetic_index']}/100 ({b_crit['quality_tier']})")
        print(f"   • Exposure: {b_crit['metrics']['exposure_score']}/100 | Contrast: {b_crit['metrics']['tonal_contrast_score']}/100")
        print(f"   • Skin Radiance: {b_crit['metrics']['skin_tone_radiance_score']}/100 | Sharpness: {b_crit['metrics']['sharpness_clarity_score']}/100")
        
        print(f"\n 🚀 AFTER MASTER DEVELOPMENT:")
        print(f"   • Overall Aesthetic Index: {a_crit['overall_aesthetic_index']}/100 ({a_crit['quality_tier']})")
        print(f"   • Exposure: {a_crit['metrics']['exposure_score']}/100 | Contrast: {a_crit['metrics']['tonal_contrast_score']}/100")
        print(f"   • Skin Radiance: {a_crit['metrics']['skin_tone_radiance_score']}/100 | Sharpness: {a_crit['metrics']['sharpness_clarity_score']}/100")
        print(f"   • Quality Gain: +{report['score_improvement']} points")
        
        out_path = args.output or f"developed_{os.path.splitext(os.path.basename(args.image_path))[0]}.png"
        out_img.save(out_path, quality=98)
        print(f"\n ✅ Master Developed Image Saved: {out_path}")
        print("=" * 65 + "\n")
        
        if args.preview:
            canvas = Canvas.from_image(out_img)
            set_active_canvas(canvas)
            host = LivePreviewHost(canvas, port=8000, auto_open=True, native=True)
            host.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down.")
    elif args.command == "preview":
        canvas = Canvas.from_file(args.image_path)
        set_active_canvas(canvas)
        use_native = not args.browser
        host = LivePreviewHost(canvas, port=args.port, auto_open=True, native=use_native)
        host.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down.")
    elif args.command == "demo":
        run_demo_workflow()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
