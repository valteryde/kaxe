"""
SVG export tests for 2D plots.
"""

import sys
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit


SVG_NS = "http://www.w3.org/2000/svg"


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


@unit()
def test_svg_smoke_parse():
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function2D(lambda x: x**2 - 4))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        path = tmp.name

    try:
        plot.save(path)
        content = Path(path).read_text(encoding="utf-8")
        root = _parse_svg(content)
        assert root.get("width") is not None
        assert root.get("height") is not None
    finally:
        Path(path).unlink(missing_ok=True)


@unit()
def test_svg_structure_has_curve_and_axes():
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function2D(lambda x: x**2 - 4))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="svg")
    content = buf.getvalue().decode("utf-8")
    tags = _collect_tags(_parse_svg(content))

    assert "polyline" in tags or "path" in tags or "line" in tags
    assert "line" in tags


@unit()
def test_svg_png_then_svg_not_cached():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    with tempfile.TemporaryDirectory() as tmpdir:
        png_path = Path(tmpdir) / "plot.png"
        svg_path = Path(tmpdir) / "plot.svg"

        plot.save(str(png_path))
        assert png_path.exists()

        plot.save(str(svg_path))
        content = svg_path.read_text(encoding="utf-8")
        root = _parse_svg(content)
        assert _local_tag(root.tag) == "svg"


@unit()
def test_svg_vector_text_labels():
    plot = kaxe.Plot([-3, 3, -2, 5])
    plot.add(kaxe.Function2D(lambda x: x**2))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="svg")
    content = buf.getvalue().decode("utf-8")
    tags = _collect_tags(_parse_svg(content))

    assert "text" in tags
    assert "style" in tags


@unit()
def test_svg_chart_pie():
    chart = kaxe.Pie()
    chart.add(5.0, legend="a", label="5")
    chart.add(3.0, legend="b", label="3")
    chart.showProgressBar = False
    chart.printDebugInfo = False

    buf = BytesIO()
    chart.save(buf, format="svg")
    tags = _collect_tags(_parse_svg(buf.getvalue().decode("utf-8")))

    assert "path" in tags
