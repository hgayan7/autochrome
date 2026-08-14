"""Type definitions and schemas for Autochrome."""

from __future__ import annotations
from typing import List, Optional, Tuple, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class Size(BaseModel):
    width: int
    height: int


class Rect(BaseModel):
    x: int
    y: int
    width: int
    height: int


class ColorRGBA(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    a: int = Field(default=255, ge=0, le=255)

    @classmethod
    def from_hex(cls, hex_str: str, alpha: int = 255) -> "ColorRGBA":
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 3:
            hex_str = "".join([c * 2 for c in hex_str])
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return cls(r=r, g=g, b=b, a=alpha)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            return cls(r=r, g=g, b=b, a=a)
        return cls(r=0, g=0, b=0, a=alpha)

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)


class TuneParams(BaseModel):
    """Parameters for Primary Tone & Dynamic Color Balancing."""
    brightness: float = Field(default=0.0, ge=-100.0, le=100.0, description="Range -100 to +100")
    contrast: float = Field(default=0.0, ge=-100.0, le=100.0, description="Range -100 to +100")
    saturation: float = Field(default=0.0, ge=-100.0, le=100.0, description="Range -100 to +100")
    ambiance: float = Field(default=0.0, ge=-100.0, le=100.0, description="Local dynamic balance and midtone vibrancy")
    highlights: float = Field(default=0.0, ge=-100.0, le=100.0, description="Recover or boost highlights")
    shadows: float = Field(default=0.0, ge=-100.0, le=100.0, description="Lift or deepen shadows")
    warmth: float = Field(default=0.0, ge=-100.0, le=100.0, description="Color temperature (cool to warm)")
    tint: float = Field(default=0.0, ge=-100.0, le=100.0, description="Green/Magenta tint adjustment")


class DetailsParams(BaseModel):
    """Parameters for Texture & Micro-Contrast Details."""
    structure: float = Field(default=0.0, ge=-100.0, le=100.0, description="Micro-contrast and fine texture pop")
    sharpening: float = Field(default=0.0, ge=0.0, le=100.0, description="High-pass edge sharpening")


class CurvePoint(BaseModel):
    in_val: float = Field(ge=0.0, le=255.0)
    out_val: float = Field(ge=0.0, le=255.0)


class CurveParams(BaseModel):
    channel: Literal["rgb", "luminance", "red", "green", "blue"] = "rgb"
    points: List[CurvePoint] = Field(default_factory=list)


class SelectivePoint(BaseModel):
    x: int
    y: int
    radius: int = Field(default=150, ge=10)
    brightness: float = Field(default=0.0, ge=-100.0, le=100.0)
    contrast: float = Field(default=0.0, ge=-100.0, le=100.0)
    saturation: float = Field(default=0.0, ge=-100.0, le=100.0)
    structure: float = Field(default=0.0, ge=-100.0, le=100.0)


class BokehParams(BaseModel):
    center_x: Optional[int] = None
    center_y: Optional[int] = None
    inner_radius: int = Field(default=150, ge=10)
    outer_radius: int = Field(default=350, ge=20)
    blur_strength: float = Field(default=25.0, ge=0.0, le=100.0)
    bokeh_boost: float = Field(default=10.0, ge=0.0, le=100.0)
    vignette: float = Field(default=0.0, ge=0.0, le=100.0)
    shape: Literal["ellipse", "circle", "linear"] = "ellipse"
    rotation_deg: float = 0.0


class PortraitParams(BaseModel):
    face_spotlight: float = Field(default=15.0, ge=0.0, le=100.0, description="Illumination on face area")
    skin_smoothing: float = Field(default=20.0, ge=0.0, le=100.0, description="Bilateral texture smoothing")
    eye_clarity: float = Field(default=25.0, ge=0.0, le=100.0, description="Sharpening & contrast on eye region")
    skin_tone_warmth: float = Field(default=5.0, ge=-50.0, le=50.0)


class ArrowParams(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    color: str = "#FF3B30"
    stroke_width: int = 4
    curvature: float = Field(default=0.0, ge=-1.0, le=1.0, description="0 for straight, >0 or <0 for curved")
    head_size: int = 16


class CalloutParams(BaseModel):
    x: int
    y: int
    width: int
    height: int
    border_color: str = "#FF9500"
    stroke_width: int = 3
    corner_radius: int = 12
    fill_color: Optional[str] = None
    label: Optional[str] = None
    label_bg: Optional[str] = None


class LoupeParams(BaseModel):
    target_x: int
    target_y: int
    loupe_x: int
    loupe_y: int
    radius: int = 90
    zoom_factor: float = 2.0
    border_color: str = "#007AFF"
    border_width: int = 3
    show_pin: bool = True


class BadgeParams(BaseModel):
    x: int
    y: int
    number: int = 1
    radius: int = 18
    bg_color: str = "#007AFF"
    text_color: str = "#FFFFFF"


class RedactParams(BaseModel):
    x: int
    y: int
    width: int
    height: int
    method: Literal["blur", "pixelate", "blackout"] = "blur"
    strength: int = 20


class MockupParams(BaseModel):
    frame_type: Literal["macos_dark", "macos_light", "browser_window", "plain_shadow"] = "macos_dark"
    backdrop: Literal["mesh_sunset", "mesh_ocean", "gradient_slate", "gradient_purple", "solid_dark", "transparent"] = "mesh_sunset"
    padding: int = 60
    corner_radius: int = 16
    shadow_blur: int = 30
    shadow_opacity: float = 0.45


class ActionRecord(BaseModel):
    id: str
    tool_name: str
    description: str
    parameters: Dict[str, Any]
    timestamp: float
