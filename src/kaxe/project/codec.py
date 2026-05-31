"""JSON-safe encoding helpers for Kaxe project files."""

from __future__ import annotations

from typing import Any, Optional

from ..core.color import Colormap, Colormaps, to_rgba
from ..core.styles import ComputedAttribute


def encode_color(value) -> Any:
    if value is None:
        return None
    if isinstance(value, Colormap):
        return encode_colormap(value)
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], (list, tuple)):
            return [list(to_rgba(c)) for c in value]
        return list(to_rgba(value))
    return list(to_rgba(value))


def encode_colormap(cmap: Colormap) -> dict:
    for name in (
        "standard", "green", "brown", "blue", "yellow", "cream",
        "red", "rainbow", "purple", "orange",
    ):
        preset = getattr(Colormaps, name, None)
        if preset is cmap:
            return {"preset": name}
    steps = []
    for step in cmap.colorGradientSteps:
        steps.append(list(int(round(c)) for c in step))
    return {"gradient": steps}


def decode_colormap(data: Optional[dict]) -> Colormap:
    if not data:
        return Colormaps.standard
    if "preset" in data:
        name = data["preset"]
        preset = getattr(Colormaps, name, None)
        if preset is None:
            raise ValueError(f"Unknown colormap preset: {name!r}")
        return preset
    if "gradient" in data:
        return Colormap(data["gradient"])
    raise ValueError(f"Invalid colormap payload: {data!r}")


def encode_attrmap_styles(attrs: dict) -> dict:
    """Serialize user style overrides only."""
    out = {}
    for scope, values in attrs.items():
        if not values:
            continue
        scope_out = {}
        for key, val in values.items():
            if isinstance(val, ComputedAttribute):
                continue
            if key == "color" or key.endswith("Color"):
                scope_out[key] = encode_color(val)
            else:
                scope_out[key] = _encode_value(val)
        if scope_out:
            out[scope] = scope_out
    return out


def apply_attrmap_styles(attrmap, styles: dict) -> None:
    for scope, values in (styles or {}).items():
        for key, val in values.items():
            if scope == "global":
                attrmap.setAttr(key, _decode_value(val))
            else:
                attrmap.setAttr(key, _decode_value(val), obj=scope)


def _encode_value(val: Any) -> Any:
    if isinstance(val, (list, tuple)):
        return [_encode_value(v) for v in val]
    if isinstance(val, Colormap):
        return encode_colormap(val)
    return val


def _decode_value(val: Any) -> Any:
    if isinstance(val, dict) and ("preset" in val or "gradient" in val):
        return decode_colormap(val)
    if isinstance(val, list) and val and isinstance(val[0], list):
        return [tuple(to_rgba(c)) for c in val]
    if isinstance(val, list) and len(val) in (3, 4) and all(isinstance(c, (int, float)) for c in val):
        return to_rgba(val)
    return val


def encode_legend(obj) -> Optional[dict]:
    text = getattr(obj, "legendText", None)
    if text is None:
        return None
    sym = getattr(obj, "legendSymbol", None)
    sym_name = sym if isinstance(sym, str) else None
    color = getattr(obj, "legendColor", None)
    return {
        "text": text,
        "symbol": sym_name,
        "color": encode_color(color) if color is not None else None,
    }


def apply_legend(obj, data: Optional[dict]) -> None:
    if not data:
        return
    if hasattr(obj, "legend"):
        kwargs = {}
        if data.get("symbol"):
            kwargs["symbol"] = data["symbol"]
        if data.get("color") is not None:
            kwargs["color"] = data["color"]
        obj.legend(data["text"], **kwargs)
    else:
        obj.legendText = data["text"]
        if data.get("symbol"):
            obj.legendSymbol = data["symbol"]
        if data.get("color") is not None:
            obj.legendColor = to_rgba(data["color"])


def encode_list(values) -> list:
    return [float(v) for v in values]


def encode_grid(data) -> list:
    return [[float(cell) for cell in row] for row in data]
