"""Live Preview HTTP & WebSocket Server."""

from __future__ import annotations
import os
import json
import asyncio
from typing import List, Optional, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from PIL import Image

from autochrome.core.canvas import Canvas


app = FastAPI(title="Autochrome Live Preview")

# Active WebSocket connections
connected_clients: Set[WebSocket] = set()
current_canvas: Optional[Canvas] = None
latest_description: str = "Ready for Agent edits"

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


SERVER_LOOP: Optional[asyncio.AbstractEventLoop] = None
canvas_version: int = 0


@app.on_event("startup")
async def on_startup():
    global SERVER_LOOP
    SERVER_LOOP = asyncio.get_running_loop()


@app.get("/")
async def get_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
async def get_state():
    from autochrome.mcp.tools import get_active_canvas
    canvas = current_canvas or get_active_canvas()
    if canvas:
        payload = build_update_payload(canvas, latest_description)
        payload["version"] = canvas_version
        return payload
    return {"status": "empty", "version": canvas_version}


@app.post("/api/execute")
async def execute_tool(request: dict):
    """Executes a tool on the active canvas and broadcasts the update live."""
    global current_canvas, latest_description, canvas_version
    from autochrome.mcp import tools
    from autochrome.mcp.tools import get_active_canvas, set_active_canvas

    tool_name = request.get("tool")
    args = request.get("args", {})

    fn_name = f"tool_{tool_name}"
    fn = getattr(tools, fn_name, None)
    if not fn:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    # Ensure server's current_canvas is attached and synced
    if current_canvas:
        set_active_canvas(current_canvas)

    res = fn(**args)
    current_canvas = get_active_canvas()
    canvas_version += 1
    latest_description = current_canvas.history.get_current_snapshot().action.description if current_canvas.history.get_current_snapshot() else "Updated"
    broadcast_canvas_update(current_canvas, latest_description)
    return {"status": "success", "result": res, "description": latest_description, "version": canvas_version}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global SERVER_LOOP
    SERVER_LOOP = asyncio.get_running_loop()
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        from autochrome.mcp.tools import get_active_canvas
        canvas = current_canvas or get_active_canvas()
        if canvas:
            payload = build_update_payload(canvas, latest_description)
            payload["version"] = canvas_version
            await websocket.send_text(json.dumps(payload))

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception:
        connected_clients.discard(websocket)


def build_update_payload(canvas: Canvas, description: str) -> dict:
    orig_b64 = None
    if canvas.original_image:
        import io, base64
        buf = io.BytesIO()
        canvas.original_image.convert("RGB").save(buf, format="JPEG", quality=85)
        orig_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "type": "update",
        "version": canvas_version,
        "image_b64": canvas.to_base64_jpeg(quality=88),
        "original_b64": orig_b64,
        "description": description,
        "width": canvas.width,
        "height": canvas.height,
        "action_count": len(canvas.history.actions),
    }


def broadcast_canvas_update(canvas: Canvas, description: str = "Updated canvas"):
    """Broadcasts a live update to all WebSocket listeners."""
    global current_canvas, latest_description, canvas_version, SERVER_LOOP
    current_canvas = canvas
    latest_description = description
    canvas_version += 1

    if not connected_clients:
        return

    payload = build_update_payload(canvas, description)
    text_data = json.dumps(payload)

    if SERVER_LOOP and SERVER_LOOP.is_running():
        for ws in list(connected_clients):
            try:
                asyncio.run_coroutine_threadsafe(ws.send_text(text_data), SERVER_LOOP)
            except Exception:
                pass


def attach_canvas(canvas: Canvas):
    """Hooks a Canvas instance to broadcast live updates automatically on every commit."""
    global current_canvas
    current_canvas = canvas

    def _listener(c: Canvas):
        snap = c.history.get_current_snapshot()
        desc = snap.action.description if snap else "Updated"
        broadcast_canvas_update(c, desc)

    canvas.subscribe(_listener)
