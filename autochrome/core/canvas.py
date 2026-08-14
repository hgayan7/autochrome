"""Core Canvas Engine managing layers, composition, and state."""

from __future__ import annotations
import os
import io
import base64
from typing import List, Optional, Callable, Dict, Any
from PIL import Image
import numpy as np

from autochrome.core.layer import Layer, ImageLayer
from autochrome.core.history import HistoryManager


class Canvas:
    """Master non-destructive Canvas."""

    def __init__(self, width: int = 800, height: int = 600, background_color=(0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.layers: List[Layer] = []
        self.history = HistoryManager()
        self.original_image: Optional[Image.Image] = None
        self._on_change_callbacks: List[Callable[["Canvas"], None]] = []

    @classmethod
    def from_image(cls, image: Image.Image) -> "Canvas":
        img_rgba = image.convert("RGBA")
        canvas = cls(width=img_rgba.width, height=img_rgba.height)
        canvas.original_image = img_rgba.copy()
        base_layer = ImageLayer(name="Background", image=img_rgba)
        canvas.layers.append(base_layer)
        canvas.history.push_state(
            tool_name="init_canvas",
            description="Loaded original image",
            image=img_rgba,
            params={"width": img_rgba.width, "height": img_rgba.height},
        )
        return canvas

    @classmethod
    def from_file(cls, file_path: str) -> "Canvas":
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        with Image.open(file_path) as img:
            return cls.from_image(img)

    def subscribe(self, callback: Callable[["Canvas"], None]):
        """Subscribe to canvas changes for real-time live preview broadcasting."""
        if callback not in self._on_change_callbacks:
            self._on_change_callbacks.append(callback)

    def notify(self):
        """Notify all listeners that the canvas has been updated."""
        for cb in self._on_change_callbacks:
            try:
                cb(self)
            except Exception as e:
                print(f"[Canvas Notify Error] {e}")

    def render(self) -> Image.Image:
        """Render all visible layers into a single RGBA image."""
        composite = Image.new("RGBA", (self.width, self.height), self.background_color)
        for layer in self.layers:
            if layer.visible and layer.opacity > 0:
                composite = layer.composite_over(composite)
        return composite

    def commit_change(self, tool_name: str, description: str, params: Optional[Dict[str, Any]] = None):
        """Render current composite, record history snapshot, and notify live preview."""
        rendered = self.render()
        self.history.push_state(tool_name, description, rendered, params or {})
        self.notify()

    def replace_base_image(self, new_img: Image.Image, tool_name: str, description: str, params: Optional[Dict[str, Any]] = None):
        """Update the base layer and adjust canvas dimensions if needed."""
        new_rgba = new_img.convert("RGBA")
        self.width = new_rgba.width
        self.height = new_rgba.height
        
        # Replace or update base layer
        if self.layers and isinstance(self.layers[0], ImageLayer):
            self.layers[0] = ImageLayer(name="Base", image=new_rgba, layer_id=self.layers[0].id)
        else:
            self.layers.insert(0, ImageLayer(name="Base", image=new_rgba))
            
        self.commit_change(tool_name, description, params)

    def add_layer(self, layer: Layer, tool_name: str = "add_layer", description: str = "Added layer"):
        self.layers.append(layer)
        self.commit_change(tool_name, description)

    def undo(self) -> bool:
        snap = self.history.undo()
        if snap:
            # Restore image to base
            self.width = snap.image.width
            self.height = snap.image.height
            self.layers = [ImageLayer(name="Base", image=snap.image)]
            self.notify()
            return True
        return False

    def redo(self) -> bool:
        snap = self.history.redo()
        if snap:
            self.width = snap.image.width
            self.height = snap.image.height
            self.layers = [ImageLayer(name="Base", image=snap.image)]
            self.notify()
            return True
        return False

    def to_base64_jpeg(self, quality: int = 90) -> str:
        img = self.render().convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def to_base64_png(self) -> str:
        img = self.render()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def export(self, output_path: str, format: str = "PNG", quality: int = 95):
        img = self.render()
        fmt = format.upper()
        if fmt in ["JPG", "JPEG"]:
            img.convert("RGB").save(output_path, format="JPEG", quality=quality)
        elif fmt == "WEBP":
            img.save(output_path, format="WEBP", quality=quality)
        else:
            img.save(output_path, format="PNG")
