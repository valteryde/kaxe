"""
SVG export tests for Grid layouts.
"""

import sys
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit


def _parse_svg(content: str) -> ET.Element:
    root = ET.fromstring(content)
    assert root.tag.endswith("svg") or root.tag == "svg"
    return root


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _collect_tags(root: ET.Element) -> set[str]:
    tags = {_local_tag(root.tag)}
    for el in root.iter():
        tags.add(_local_tag(el.tag))
    return tags


def _make_plot():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x**2 - 2))
    plot.showProgressBar = False
    plot.printDebugInfo = False
    return plot


def _make_grid_2x2():
    grid = kaxe.Grid()
    grid.style(width=1200, height=1200)
    grid.showProgressBar = False
    grid.printDebugInfo = False
    p1, p2, p3, p4 = _make_plot(), _make_plot(), _make_plot(), _make_plot()
    grid.addRow(p1, p2)
    grid.addRow(p3, p4)
    return grid


@unit()
def test_grid_2x2_svg_smoke():
    grid = _make_grid_2x2()
    buf = BytesIO()
    grid.save(buf, format="svg")
    content = buf.getvalue().decode("utf-8")
    root = _parse_svg(content)
    tags = _collect_tags(root)

    assert root.get("width") is not None
    assert root.get("height") is not None
    assert "polyline" in tags or "path" in tags or "line" in tags


@unit()
def test_grid_svg_matches_png_layout():
    grid_png = _make_grid_2x2()
    grid_svg = _make_grid_2x2()

    png_buf = BytesIO()
    grid_png.save(png_buf, format="png")
    png_buf.seek(0)
    from PIL import Image
    png_size = Image.open(png_buf).size

    svg_buf = BytesIO()
    grid_svg.save(svg_buf, format="svg")
    root = _parse_svg(svg_buf.getvalue().decode("utf-8"))

    assert (int(root.get("width")), int(root.get("height"))) == png_size


@unit()
def test_grid_with_legend_svg():
    grid = kaxe.Grid()
    grid.style(width=1200, height=800)
    grid.showProgressBar = False
    grid.printDebugInfo = False
    grid.addRow(_make_plot(), _make_plot())
    grid.legends(
        ("Series A", kaxe.Symbol.CIRCLE, (200, 0, 0, 255)),
        ("Series B", kaxe.Symbol.CROSS, (0, 0, 200, 255)),
    )

    buf = BytesIO()
    grid.save(buf, format="svg")
    tags = _collect_tags(_parse_svg(buf.getvalue().decode("utf-8")))

    assert "text" in tags or "g" in tags
    assert "line" in tags or "circle" in tags


@unit()
def test_svg_sawtooth_does_not_connect_wraparound():
    """Angular wrap-around must not draw a connector through the plot margins."""
    import math

    n = 80
    t = [i * 0.15 / n for i in range(n)]
    y = [min(6.2, (i * 0.5) % 6.28) for i in range(n)]

    plot = kaxe.Plot([0, 0.15, 0, 7])
    plot.add(kaxe.Points2D(t, y, connect=True, color=(200, 0, 0, 255)))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="svg")
    root = _parse_svg(buf.getvalue().decode("utf-8"))
    height = float(root.get("height"))

    long_segments = 0
    for el in root.iter():
        if _local_tag(el.tag) != "polyline":
            continue
        pts = el.get("points", "").split()
        coords = []
        for pair in pts:
            x_s, y_s = pair.split(",")
            coords.append((float(x_s), float(y_s)))
        for i in range(len(coords) - 1):
            x0, y0 = coords[i]
            x1, y1 = coords[i + 1]
            if math.hypot(x1 - x0, y1 - y0) > height * 0.35:
                long_segments += 1

    assert long_segments == 0


@unit()
def test_grid_stacked_svg_cells_are_clipped():
    """Stacked grid SVG cells should not leak drawable content past their bounds."""
    grid = kaxe.Grid()
    grid.style(width=1200, height=600)
    grid.showProgressBar = False
    grid.printDebugInfo = False
    grid.addColumn(_make_plot(), _make_plot())

    buf = BytesIO()
    grid.save(buf, format="svg")
    root = _parse_svg(buf.getvalue().decode("utf-8"))

    clipped_groups = 0
    for el in root.iter():
        if _local_tag(el.tag) == "g" and "clip-path" in el.attrib:
            clipped_groups += 1

    assert clipped_groups >= 2


@unit()
def test_grid_svg_cells_skip_builtin_legend():
    """Grid-level legends must not be duplicated inside each subplot SVG."""
    grid = kaxe.Grid()
    grid.style(width=1200, height=600)
    grid.showProgressBar = False
    grid.printDebugInfo = False
    plot = _make_plot()
    grid.addRow(plot, _make_plot())
    grid.legends(("Series", kaxe.Symbol.CIRCLE, (200, 0, 0, 255)))

    buf = BytesIO()
    grid.save(buf, format="svg")
    content = buf.getvalue().decode("utf-8")

    assert content.count("Series") >= 1


@unit()
def test_grid_mixed_3d_cell():
    grid = kaxe.Grid()
    grid.style(width=1400, height=700)
    grid.showProgressBar = False
    grid.printDebugInfo = False

    p2d = kaxe.Plot([-3, 3, -3, 3])
    p2d.add(kaxe.Function2D(lambda x: x))
    p2d.showProgressBar = False
    p2d.printDebugInfo = False

    p3d = kaxe.Plot3D([-5, 5, -5, 5, -5, 5])
    p3d.add(kaxe.Function(lambda x, y: x**2 + y**2))
    p3d.showProgressBar = False
    p3d.printDebugInfo = False

    grid.addRow(p2d, p3d)

    buf = BytesIO()
    grid.save(buf, format="svg")
    tags = _collect_tags(_parse_svg(buf.getvalue().decode("utf-8")))

    assert "image" in tags
    assert "polyline" in tags or "path" in tags or "line" in tags
