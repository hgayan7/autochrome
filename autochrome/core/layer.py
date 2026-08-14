"""Non-destructive layer definitions for Autochrome Canvas."""

from __future__ import annotations
import uuid
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np

from autochrome.core.blend import apply_blend


class Layer:
    """Base Layer class for non-destructive image compositing."""

    def __init__(
        self,
        name: str,
        layer_id: Optional[str] = None,
        visible: bool = True,
        opacity: float = 1.0,
        blend_mode: str = "normal",
    ):
        self.id = layer_id or str(uuid.uuid4())[:8]
        self.name = name
        self.visible = visible
        self.opacity = max(0.0, min(1.0, opacity))
        self.blend_mode = blend_mode.lower()
        self.mask: Optional[Image.Image] = None  # Single-channel 'L' mask

    def render(self, canvas_width: int, canvas_height: int) -> Image.Image:
        """Render this layer to an RGBA PIL Image sized (canvas_width, canvas_height)."""
        raise NotImplementedError

    def composite_over(self, base_img: Image.Image) -> Image.Image:
        """Composite this layer over base_img (RGBA) using its opacity and blend mode."""
        if not self.visible or self.opacity <= 0.0:
            return base_img

        layer_img = self.render(base_img.width, base_img.height)
        if layer_img.mode != "RGBA":
            layer_img = layer_img.convert("RGBA")

        # If a mask exists, apply it to layer alpha
        if self.mask is not None:
            mask_resized = self.mask.resize((base_img.width, base_img.height), Image.Resampling.LANCZOS)
            r, g, b, a = layer_img.split()
            combined_a = Image.fromarray((np.array(a, dtype=np.float32) * np.array(mask_resized, dtype=np.float32) / 255.0).astype(np.uint8))
            layer_img = Image.merge("RGBA", (r, g, b, combined_a))

        if self.blend_mode == "normal" and self.opacity >= 0.999:
            # Fast PIL alpha composite
            return Image.alpha_composite(base_img, layer_img)

        # NumPy accelerated blend
        base_arr = np.array(base_img, dtype=np.float32) / 255.0
        layer_arr = np.array(layer_img, dtype=np.float32) / 255.0

        out_arr = apply_blend(base_arr, layer_arr, self.blend_mode, self.opacity)
        return Image.fromarray((out_arr * 255.0).astype(np.uint8), mode="RGBA")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.__class__.__name__,
            "visible": self.visible,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode,
        }


class ImageLayer(Layer):
    """Layer containing a raster image."""

    def __init__(
        self,
        name: str,
        image: Image.Image,
        x: int = 0,
        y: int = 0,
        layer_id: Optional[str] = None,
        visible: bool = True,
        opacity: float = 1.0,
        blend_mode: str = "normal",
    ):
        super().__init__(name, layer_id, visible, opacity, blend_mode)
        self.image = image.convert("RGBA") if image.mode != "RGBA" else image.copy()
        self.x = x
        self.y = y

    def render(self, canvas_width: int, canvas_height: int) -> Image.Image:
        output = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        output.paste(self.image, (self.x, self.y), self.image)
        return output

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "x": self.x,
            "y": self.y,
            "width": self.image.width,
            "height": self.image.height,
        })
        return d


class VectorLayer(Layer):
    """Layer containing vector drawings, annotations, arrows, and shapes."""

    def __init__(
        self,
        name: str,
        render_fn,
        layer_id: Optional[str] = None,
        visible: bool = True,
        opacity: float = 1.0,
        blend_mode: str = "normal",
    ):
        super().__init__(name, layer_id, visible, opacity, blend_mode)
        self.render_fn = render_fn

    def render(self, canvas_width: int, canvas_height: int) -> Image.Image:
        return self.render_fn(canvas_width, canvas_height)
