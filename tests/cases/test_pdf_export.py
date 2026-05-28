"""
PDF export tests for 2D plots and grids.
"""

import sys
import tempfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit

try:
    import reportlab  # noqa: F401
except ImportError:
    reportlab = None


def _skip_without_reportlab():
    if reportlab is None:
        return True
    return False


def _is_pdf(data: bytes) -> bool:
    return data.startswith(b"%PDF")


@unit()
def test_pdf_smoke():
    if _skip_without_reportlab():
        return

    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function2D(lambda x: x**2 - 4))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="pdf")
    data = buf.getvalue()
    assert _is_pdf(data)
    assert len(data) > 1000


@unit()
def test_pdf_with_math_title():
    if _skip_without_reportlab():
        return

    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function2D(lambda x: x**2))
    plot.style(title="Parabola $y=x^2$")
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="pdf")
    data = buf.getvalue()
    assert _is_pdf(data)
    assert len(data) > 1000


@unit()
def test_pdf_infer_format_extension():
    if _skip_without_reportlab():
        return

    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        path = tmp.name

    try:
        plot.save(path)
        data = Path(path).read_bytes()
        assert _is_pdf(data)
    finally:
        Path(path).unlink(missing_ok=True)


@unit()
def test_pdf_infer_format_explicit():
    if _skip_without_reportlab():
        return

    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="pdf")
    assert _is_pdf(buf.getvalue())


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
def test_pdf_grid_2x2():
    if _skip_without_reportlab():
        return

    grid = _make_grid_2x2()
    buf = BytesIO()
    grid.save(buf, format="pdf")
    data = buf.getvalue()
    assert _is_pdf(data)
    assert len(data) > 1000


@unit()
def test_pdf_rotated_axis_title():
    if _skip_without_reportlab():
        return

    plot = kaxe.Plot([0, 8, 0, 60])
    plot.add(kaxe.Function2D(lambda x: 40 if x > 0.7 else 0))
    plot.title(None, "$\\omega_{mech}$ [rad/s]")
    plot.style(fontSize=40)
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="pdf")
    data = buf.getvalue()
    assert _is_pdf(data)
    assert len(data) > 1000


@unit()
def test_pdf_group_transform_keeps_tick_labels_on_page():
    if _skip_without_reportlab():
        return

    from kaxe.core import svg_pdf

    height = 2312
    matrix = svg_pdf._parse_transform("translate(263.84,2091.0)")
    transform = svg_pdf._matrix_to_reportlab_transform(matrix, height, nested=False)
    local_x, local_y = 16.0, -52.0
    rl_x = transform[0] * local_x + transform[2] * local_y + transform[4]
    rl_y = transform[1] * local_x + transform[3] * local_y + transform[5]
    assert 0 <= rl_x <= 3000
    assert 0 <= rl_y <= height


@unit()
def test_pdf_missing_reportlab_raises():
    from kaxe.core import svg_pdf

    original = svg_pdf._require_reportlab

    def _fail():
        raise ImportError(svg_pdf._PDF_INSTALL_HINT)

    svg_pdf._require_reportlab = _fail
    try:
        plot = kaxe.Plot([-3, 3, -3, 3])
        plot.add(kaxe.Function2D(lambda x: x))
        plot.showProgressBar = False
        plot.printDebugInfo = False

        try:
            plot.save(BytesIO(), format="pdf")
            assert False, "expected ImportError"
        except ImportError as exc:
            assert "kaxe[pdf]" in str(exc)
    finally:
        svg_pdf._require_reportlab = original
