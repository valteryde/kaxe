"""Per-type export/import handlers for .kaxe projects."""

from __future__ import annotations

from .codec import (
    apply_legend,
    encode_color,
    encode_colormap,
    encode_grid,
    encode_legend,
    encode_list,
)
from .context import ExportContext, ImportContext
from .registry import register_type
from .sample import sample_curve
from .sampled_curve import SampledCurve2D


def _export_function2d(obj, ctx: ExportContext) -> dict:
    first_log = getattr(ctx.window, "firstAxisLog", False)
    x, y = sample_curve(
        obj.function,
        domain=obj.domain,
        window_axis=ctx.plot_window_axis(),
        plot_identity=ctx.plot_identity(),
        first_axis_log=first_log,
        n=ctx.sample_count,
        args=obj.otherArgs,
        kwargs=obj.otherKwargs,
    )
    payload = {
        "type": "Function2D",
        "representation": "sampled",
        "x": x,
        "y": y,
        "color": encode_color(obj.color),
        "thickness": obj.thickness,
        "dotted": obj.dotted,
        "dashed": obj.dashed,
        "legend": encode_legend(obj),
    }
    if obj.domain is not None:
        payload["domain"] = list(obj.domain)
    return payload


def _import_function2d(data: dict, ctx: ImportContext):
    from ..core.color import to_rgba

    color = to_rgba(data["color"]) if data.get("color") else None
    curve = SampledCurve2D(
        data["x"],
        data["y"],
        color,
        thickness=data.get("thickness", 10),
        dotted=data.get("dotted", 0),
        dashed=data.get("dashed", 0),
    )
    if data.get("legend"):
        apply_legend(curve, data["legend"])
    return curve


def _export_points2d(obj, ctx: ExportContext) -> dict:
    return {
        "type": "Points2D",
        "x": encode_list(obj.x),
        "y": encode_list(obj.y),
        "color": encode_color(obj.color),
        "size": obj.size,
        "symbol": obj.symbol,
        "connect": obj.connect,
        "lollipop": obj.lollipop,
        "show_points": obj.show_points,
        "legend": encode_legend(obj),
    }


def _import_points2d(data: dict, ctx: ImportContext):
    from ..objects.d2.point import Points2D
    from ..core.color import to_rgba

    pts = Points2D(
        data["x"],
        data["y"],
        color=to_rgba(data["color"]) if data.get("color") else None,
        size=data.get("size"),
        symbol=data.get("symbol"),
        connect=data.get("connect", False),
        lollipop=data.get("lollipop", False),
        show_points=data.get("show_points", True),
    )
    apply_legend(pts, data.get("legend"))
    return pts


def _export_text(obj, ctx: ExportContext) -> dict:
    return {
        "type": "Text",
        "text": obj.text,
        "center": list(obj.center),
        "color": encode_color(obj.color),
    }


def _import_text(data: dict, ctx: ImportContext):
    from ..objects.text import Text
    from ..core.color import to_rgba

    return Text(
        data["text"],
        tuple(data["center"]),
        color=to_rgba(data["color"]) if data.get("color") else None,
    )


def _export_arrow(obj, ctx: ExportContext) -> dict:
    return {
        "type": "Arrow",
        "p0": list(obj.p0),
        "p1": list(obj.p1),
        "color": encode_color(obj.color),
        "headSize": obj.headSize,
        "lineThickness": obj.lineThickness,
        "legend": encode_legend(obj),
    }


def _import_arrow(data: dict, ctx: ImportContext):
    from ..objects.d2.arrow import Arrow
    from ..core.color import to_rgba

    arr = Arrow(
        tuple(data["p0"]),
        tuple(data["p1"]),
        color=to_rgba(data["color"]) if data.get("color") else None,
        headSize=data.get("headSize", 42),
        lineThickness=data.get("lineThickness", 10),
    )
    apply_legend(arr, data.get("legend"))
    return arr


def _export_pillars(obj, ctx: ExportContext) -> dict:
    return {
        "type": "Pillars",
        "x": encode_list(obj.x),
        "heights": obj.heights,
        "colors": encode_color(obj.color),
        "width": obj.width,
        "outlineWidth": obj.outlineWidth,
        "outlineColor": encode_color(obj.outlineColor),
        "legend": encode_legend(obj),
    }


def _import_pillars(data: dict, ctx: ImportContext):
    from ..objects.d2.pillar import Pillars
    from ..core.color import to_rgba

    colors = data.get("colors")
    if colors is not None:
        colors = to_rgba(colors) if not (
            isinstance(colors, list) and colors and isinstance(colors[0], list)
        ) else [to_rgba(c) for c in colors]

    p = Pillars(
        data["x"],
        data["heights"],
        colors=colors,
        width=data.get("width"),
        outlineWidth=data.get("outlineWidth", 5),
        outlineColor=to_rgba(data["outlineColor"]) if data.get("outlineColor") else (0, 0, 0, 255),
    )
    apply_legend(p, data.get("legend"))
    return p


def _export_heatmap(obj, ctx: ExportContext) -> dict:
    return {
        "type": "HeatMap",
        "data": encode_grid(obj.data),
        "colormap": encode_colormap(obj.cmap),
        "unitPerPixel": list(obj.unitPerPixel),
        "position": list(obj.position),
        "minValue": obj.minValue,
        "maxValue": obj.maxValue,
    }


def _import_heatmap(data: dict, ctx: ImportContext):
    from ..objects.d2.map import HeatMap
    from .codec import decode_colormap

    return HeatMap(
        data["data"],
        cmap=decode_colormap(data.get("colormap")),
        unitPerPixel=data.get("unitPerPixel", [1, 1]),
        position=tuple(data.get("position", (0, 0))),
        minValue=data.get("minValue"),
        maxValue=data.get("maxValue"),
    )


def _export_colorscale(obj, ctx: ExportContext) -> dict:
    return {
        "type": "ColorScale",
        "lower": obj.lower,
        "upper": obj.upper,
        "lowerTitle": obj.lowerTitle,
        "upperTitle": obj.upperTitle,
        "colormap": encode_colormap(obj.cmap),
        "width": obj.width,
        "title": obj.title,
    }


def _import_colorscale(data: dict, ctx: ImportContext):
    from ..objects.d2.map import ColorScale
    from .codec import decode_colormap

    return ColorScale(
        data["lower"],
        data["upper"],
        cmap=decode_colormap(data.get("colormap")),
        width=data.get("width"),
        title=data.get("title"),
    )


def _export_ghostlegend(obj, ctx: ExportContext) -> dict:
    return {
        "type": "GhostLegend",
        "text": obj.legendText,
        "color": encode_color(obj.legendColor),
        "symbol": obj.legendSymbol,
    }


def _import_ghostlegend(data: dict, ctx: ImportContext):
    from ..objects.legend import GhostLegend
    from ..core.color import to_rgba

    return GhostLegend(
        data["text"],
        to_rgba(data["color"]),
        data["symbol"],
    )


def _export_bubble(obj, ctx: ExportContext) -> dict:
    return {
        "type": "Bubble",
        "text": obj.text,
        "centerPos": list(obj.centerPos),
        "lineEndPos": list(obj.lineEndPos),
        "color": encode_color(obj.color),
        "lineThickness": obj.lineThickness,
        "fontSize": obj.fontSize,
        "backgroundColor": encode_color(obj.backgroundColor),
        "outlineColor": encode_color(obj.outlineColor),
        "padding": obj.padding,
        "legend": encode_legend(obj),
    }


def _import_bubble(data: dict, ctx: ImportContext):
    from ..objects.d2.bubble import Bubble
    from ..core.color import to_rgba

    b = Bubble(
        data["text"],
        tuple(data["centerPos"]),
        tuple(data["lineEndPos"]),
        color=to_rgba(data["color"]) if data.get("color") else None,
        lineThickness=data.get("lineThickness", 5),
        fontSize=data.get("fontSize", 32),
        backgroundColor=to_rgba(data["backgroundColor"]) if data.get("backgroundColor") else None,
        outlineColor=to_rgba(data["outlineColor"]) if data.get("outlineColor") else None,
        padding=data.get("padding", 10),
    )
    apply_legend(b, data.get("legend"))
    return b


def _register_all():
    register_type("Function2D", _export_function2d, _import_function2d)
    register_type("Points2D", _export_points2d, _import_points2d)
    register_type("Text", _export_text, _import_text)
    register_type("Arrow", _export_arrow, _import_arrow)
    register_type("Pillars", _export_pillars, _import_pillars)
    register_type("HeatMap", _export_heatmap, _import_heatmap)
    register_type("ColorScale", _export_colorscale, _import_colorscale)
    register_type("GhostLegend", _export_ghostlegend, _import_ghostlegend)
    register_type("Bubble", _export_bubble, _import_bubble)


_register_all()
