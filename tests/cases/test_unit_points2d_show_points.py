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
    """connect=True, show_points=False draws lines and line-width junction circles."""
    obj = kaxe.Points2D([0, 5, 10], [0, 5, 10], connect=True, show_points=False)
    _finalize_points2d(obj)

    from kaxe.core.shapes import Circle, Line

    assert len(obj.points) == 0
    assert len(obj.lines) == 2
    assert obj.legendSymbol == kaxe.symbol.LINE
    junctions = [o for o in obj.batch.objects if isinstance(o, Circle)]
    connectors = [o for o in obj.batch.objects if isinstance(o, Line)]
    assert len(junctions) == 3
    assert len(connectors) == 2
    assert junctions[0].radius == connectors[0].thickness / 2


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
