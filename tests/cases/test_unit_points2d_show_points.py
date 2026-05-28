"""
Unit tests for Points2D show_points option.
"""

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import kaxe
from runner import unit


def _finalize_points2d(obj):
    plot = kaxe.Plot([0, 10, 0, 10])
    plot.showProgressBar = False
    plot.printDebugInfo = False
    plot.add(obj)
    plot.save(BytesIO(), format="png")
    return obj


@unit()
def test_points2d_show_points_false_skips_markers():
    """connect=True, show_points=False draws a polyline with no marker shapes."""
    obj = kaxe.Points2D([0, 5, 10], [0, 5, 10], connect=True, show_points=False)
    _finalize_points2d(obj)

    from kaxe.core.shapes import Circle, Line, LineSegment

    assert len(obj.points) == 0
    assert len(obj.lines) == 0
    assert obj.legendSymbol == kaxe.symbol.LINE
    assert not any(isinstance(o, Circle) for o in obj.batch.objects)
    assert not any(isinstance(o, Line) for o in obj.batch.objects)
    assert any(isinstance(o, LineSegment) for o in obj.batch.objects)


@unit()
def test_points2d_show_points_false_two_points_uses_line():
    """Two visible points with show_points=False use a single Line."""
    obj = kaxe.Points2D([0, 10], [0, 10], connect=True, show_points=False)
    _finalize_points2d(obj)

    from kaxe.core.shapes import Circle, Line, LineSegment

    assert len(obj.lines) == 1
    assert not any(isinstance(o, Circle) for o in obj.batch.objects)
    assert not any(isinstance(o, LineSegment) for o in obj.batch.objects)


@unit()
def test_points2d_connect_scales_default_circles_to_line_width():
    """Default circles with connect=True match connector line width."""
    obj = kaxe.Points2D([0, 5, 10], [0, 5, 10], connect=True)
    _finalize_points2d(obj)

    from kaxe.core.shapes import Circle, Line

    circles = [o for o in obj.batch.objects if isinstance(o, Circle)]
    lines = [o for o in obj.batch.objects if isinstance(o, Line)]
    assert len(circles) == 3
    assert len(lines) == 2
    assert circles[0].radius == lines[0].thickness / 2


@unit()
def test_points2d_show_points_true_draws_markers():
    """Default show_points=True still draws symbol markers."""
    obj = kaxe.Points2D(
        [0, 5, 10],
        [0, 5, 10],
        connect=True,
        symbol=kaxe.symbol.CIRCLE,
    )
    _finalize_points2d(obj)

    assert len(obj.points) == 3
    assert len(obj.lines) == 2


@unit()
def test_points_passes_show_points_to_points2d():
    """kaxe.Points forwards show_points to Points2D in 2D."""
    obj = kaxe.Points([0, 5, 10], [0, 5, 10], connect=True, show_points=False)
    assert isinstance(obj, kaxe.Points2D)
    assert obj.show_points is False
