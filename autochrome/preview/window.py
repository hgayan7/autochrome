"""Native macOS preview window and background host."""

import threading
import time
import webbrowser
import uvicorn
from typing import Optional

from autochrome.core.canvas import Canvas
import socket


def find_available_port(start_port: int = 8000, max_attempts: int = 25) -> int:
    """Finds first available TCP port on localhost."""
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start_port


class LivePreviewHost:
    """Manages the background HTTP/WebSocket server and Native macOS floating window."""

    def __init__(self, canvas: Canvas, port: int = 8000, auto_open: bool = True, native: bool = True):
        self.canvas = canvas
        self.port = find_available_port(port)
        self.auto_open = auto_open
        self.native = native
        self.server_thread: Optional[threading.Thread] = None
        attach_canvas(self.canvas)

    def start_server(self):
        """Starts the Uvicorn server in a background daemon thread."""
        def _run():
            try:
                config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning")
                server = uvicorn.Server(config)
                server.run()
            except Exception:
                pass

        self.server_thread = threading.Thread(target=_run, daemon=True)
        self.server_thread.start()
        time.sleep(0.6)

    def start(self):
        """Starts server and opens native Mac window or browser."""
        self.start_server()
        url = f"http://127.0.0.1:{self.port}"
        print(f"\n[Autochrome Live Preview] Active at {url}")

        if self.native:
            try:
                import webview
                print("[Autochrome] Launching Native macOS Floating Window...")
                window = webview.create_window(
                    title="Autochrome • Live Native Preview",
                    url=url,
                    width=980,
                    height=780,
                    resizable=True,
                    on_top=False,
                    background_color="#0C0D0F",
                )
                webview.start()
                return
            except Exception as e:
                print(f"[Autochrome] Fallback to browser (Native window note: {e})")

        if self.auto_open:
            webbrowser.open(url)


# Global preview singleton for MCP server / Agent sessions
GLOBAL_PREVIEW_HOST: Optional[LivePreviewHost] = None
GLOBAL_WINDOW_PROC: Optional[Any] = None


def launch_live_preview(canvas: Canvas, port: int = 8000, native: bool = True, browser: bool = False) -> str:
    """Non-blocking launcher for MCP & Agent sessions."""
    global GLOBAL_PREVIEW_HOST, GLOBAL_WINDOW_PROC
    import subprocess
    import sys

    attach_canvas(canvas)

    if GLOBAL_PREVIEW_HOST is None:
        GLOBAL_PREVIEW_HOST = LivePreviewHost(canvas, port=port, auto_open=False, native=False)
        GLOBAL_PREVIEW_HOST.start_server()

    url = f"http://127.0.0.1:{port}"

    if native and sys.platform == "darwin":
        if GLOBAL_WINDOW_PROC is None or GLOBAL_WINDOW_PROC.poll() is not None:
            try:
                GLOBAL_WINDOW_PROC = subprocess.Popen(
                    [sys.executable, "-m", "autochrome.preview.window", str(port)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception:
                webbrowser.open(url)
    elif browser or not native:
        webbrowser.open(url)

    return url


def run_standalone_native_window(port: int = 8000):
    """Entry point for standalone preview GUI process."""
    try:
        import webview
        url = f"http://127.0.0.1:{port}"
        webview.create_window(
            title="Autochrome • Live Native Preview",
            url=url,
            width=980,
            height=780,
            resizable=True,
            on_top=False,
            background_color="#0C0D0F",
        )
        webview.start()
    except Exception as e:
        print(f"Error starting native window: {e}", file=sys.stderr)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_standalone_native_window(port)

