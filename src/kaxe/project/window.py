"""Window/plot export and import for .kaxe projects."""

from __future__ import annotations

from typing import Any, List, Optional

from ..plot.constants import XYZPLOT
from .codec import apply_attrmap_styles, encode_attrmap_styles
from .context import ExportContext, ImportContext
from .registry import export_object, import_object


_UNSUPPORTED_KINDS = frozenset({
    "Grid",
    "Plot3D",
    "PlotCenter3D",
    "PlotFrame3D",
    "PlotEmpty3D",
    "Bar",
    "GroupBar",
    "BoxPlot",
    "Pie",
    "DoubleAxisPlot",
    "QQPlot",
})


def window_kind(window) -> str:
    return type(window).__name__


def assert_project_supported(window) -> None:
    kind = window_kind(window)
    if kind in _UNSUPPORTED_KINDS:
        raise NotImplementedError(
            f"{kind} project files are not supported in .kaxe v1 "
            f"(use Plot, LogPlot, BoxedPlot, PolarPlot, etc.)"
        )
    identity = getattr(window, "identity", None)
    if identity == XYZPLOT:
        raise NotImplementedError("3D plot project files are not supported in .kaxe v1")


def export_window(window, ctx: ExportContext) -> dict:
    assert_project_supported(window)
    kind = window_kind(window)
    payload = {
        "identity": getattr(window, "identity", None),
        "window_axis": _encode_window_axis(window),
        "styles": encode_attrmap_styles(window.attrmap.__attrs__),
    }
    payload.update(_export_window_extras(window, kind))
    return {"kind": kind, "window": payload}


def _encode_window_axis(window) -> Optional[list]:
    wa = getattr(window, "windowAxis", None)
    if wa is None:
        return None
    return [None if v is None else float(v) for v in wa]


def _export_window_extras(window, kind: str) -> dict:
    extras = {"titles": {}, "pad": None, "zoom_insets": []}

    if kind == "PolarPlot":
        extras["titles"] = {"radius": getattr(window, "radiusTitle", None)}
        extras["use_degrees"] = getattr(window, "useDegrees", False)
        return extras

    extras["titles"] = {
        "first": getattr(window, "firstTitle", None),
        "second": getattr(window, "secondTitle", None),
    }

    if kind in ("LogPlot", "BoxedLogPlot"):
        extras["log"] = {
            "first_axis_log": window.firstAxisLog,
            "second_axis_log": window.secondAxisLog,
            "hide_ugly": window.hideUgly,
        }

    rel_x = getattr(window, "_axis_pad_rel_x", 0.0)
    rel_y = getattr(window, "_axis_pad_rel_y", 0.0)
    abs_x = getattr(window, "_axis_pad_x", 0.0)
    abs_y = getattr(window, "_axis_pad_y", 0.0)
    if rel_x or rel_y or abs_x or abs_y:
        extras["pad"] = {
            "x": abs_x,
            "y": abs_y,
            "relative_x": rel_x,
            "relative_y": rel_y,
        }

    if hasattr(window, "zoom_insets"):
        extras["zoom_insets"] = [
            _export_zoom_inset(z) for z in window.zoom_insets
        ]

    return extras


def _export_zoom_inset(zoom) -> dict:
    return {
        "window_axis": list(zoom.windowAxis),
        "position": zoom.position if isinstance(zoom.position, str) else list(zoom.position),
        "size": list(zoom.size),
        "show_axes": zoom.showAxes,
        "connector_lines": zoom.connectorLines,
        "connector_corners": zoom.connectorCorners,
        "include_main": zoom.includeMain,
        "margin": zoom.margin,
        "selection_box_width": zoom.selectionBoxWidth,
        "selection_box_color": list(zoom.selectionBoxColor),
        "connector_width": zoom.connectorWidth,
        "connector_color": list(zoom.connectorColor),
        "titles": {
            "first": zoom.firstTitle,
            "second": zoom.secondTitle,
        },
        "objects": [
            export_object(obj, ExportContext(window=zoom.parent))
            for obj in zoom.objects
        ],
    }


def export_objects(window, ctx: ExportContext) -> List[dict]:
    return [export_object(obj, ctx) for obj in window.objects]


def import_window(data: dict, ctx: ImportContext):
    kind = data["kind"]
    win_data = data["window"]
    plot = _construct_window(kind, win_data)

    apply_attrmap_styles(plot.attrmap, win_data.get("styles", {}))

    wa = win_data.get("window_axis")
    if wa is not None:
        plot.windowAxis = [None if v is None else v for v in wa]

    _apply_window_extras(plot, kind, win_data)

    for obj_data in data.get("objects", []):
        plot.add(import_object(obj_data, ctx))

    return plot


def _construct_window(kind: str, win_data: dict):
    from ..plot.standard import Plot
    from ..plot.box import BoxedPlot
    from ..plot.log import LogPlot, BoxedLogPlot
    from ..plot.polar import PolarPlot

    wa = win_data.get("window_axis")
    if kind == "Plot":
        return Plot(wa)
    if kind == "BoxedPlot":
        return BoxedPlot(wa)
    if kind == "LogPlot":
        log = win_data.get("log", {})
        return LogPlot(
            wa,
            firstAxisLog=log.get("first_axis_log", False),
            secondAxisLog=log.get("second_axis_log", True),
            hideUgly=log.get("hide_ugly", True),
        )
    if kind == "BoxedLogPlot":
        log = win_data.get("log", {})
        return BoxedLogPlot(
            wa,
            firstAxisLog=log.get("first_axis_log", False),
            secondAxisLog=log.get("second_axis_log", True),
            hideUgly=log.get("hide_ugly", True),
        )
    if kind == "PolarPlot":
        return PolarPlot(wa, useDegrees=win_data.get("use_degrees", False))
    if kind == "EmptyPlot":
        from ..plot.empty import EmptyPlot
        return EmptyPlot(wa)
    raise ValueError(f"Unknown window kind in project: {kind!r}")


def _apply_window_extras(plot, kind: str, win_data: dict) -> None:
    titles = win_data.get("titles", {})
    if kind == "PolarPlot":
        if titles.get("radius"):
            plot.title(titles["radius"])
    else:
        first = titles.get("first")
        second = titles.get("second")
        if first is not None or second is not None:
            plot.title(first=first, second=second)

    pad = win_data.get("pad")
    if pad and hasattr(plot, "pad"):
        if pad.get("relative_x") or pad.get("relative_y"):
            plot.pad(
                pad.get("relative_x", 0),
                pad.get("relative_y", 0),
                relative=True,
            )
        if pad.get("x") or pad.get("y"):
            plot.pad(pad.get("x", 0), pad.get("y", 0))

    for zdata in win_data.get("zoom_insets", []):
        _import_zoom_inset(plot, zdata)


def _import_zoom_inset(plot, zdata: dict) -> None:
    wa = zdata["window_axis"]
    position = zdata["position"]
    if isinstance(position, list):
        position = tuple(position)
    zoom = plot.zoom(
        wa[0], wa[1], wa[2], wa[3],
        position=position,
        size=tuple(zdata["size"]),
        showAxes=zdata.get("show_axes", True),
        connectorLines=zdata.get("connector_lines", True),
        connectorCorners=zdata.get("connector_corners", "auto"),
        includeMain=zdata.get("include_main", True),
        margin=zdata.get("margin", 20),
        selectionBoxWidth=zdata.get("selection_box_width", 3),
        selectionBoxColor=tuple(zdata["selection_box_color"]),
        connectorWidth=zdata.get("connector_width", 2),
        connectorColor=tuple(zdata["connector_color"]),
    )
    t = zdata.get("titles", {})
    if t.get("first") or t.get("second"):
        zoom.title(first=t.get("first"), second=t.get("second"))
    ctx = ImportContext()
    for obj_data in zdata.get("objects", []):
        zoom.add(import_object(obj_data, ctx))


def build_document(window) -> dict:
    assert_project_supported(window)
    ctx = ExportContext(
        window=window,
        sample_count=max(500, min(4096, int(window.getAttr("width") or 2000))),
    )
    doc = export_window(window, ctx)
    doc["objects"] = export_objects(window, ctx)
    return doc
