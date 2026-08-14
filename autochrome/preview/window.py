"""Native macOS preview window and background host."""

import threading
import time
import webbrowser
import uvicorn
from typing import Optional

from autochrome.core.canvas import Canvas
from autochrome.preview.server import app, attach_canvas


class LivePreviewHost:
    """Manages the background HTTP/WebSocket server and Native macOS floating window."""

    def __init__(self, canvas: Canvas, port: int = 8000, auto_open: bool = True, native: bool = True):
        self.canvas = canvas
        self.port = port
        self.auto_open = auto_open
        self.native = native
        self.server_thread: Optional[threading.Thread] = None
        attach_canvas(self.canvas)

    def start_server(self):
        """Starts the Uvicorn server in a background daemon thread."""
        def _run():
            config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning")
            server = uvicorn.Server(config)
            server.run()

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
