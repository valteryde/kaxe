"""
Unit tests for Points2D dashed/dotted resampling.
"""

import math
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import kaxe
from kaxe.core.helper import resample_polyline
from runner import unit


def _finalize_points2d(obj):
    plot = kaxe.Plot([0, 10, 0, 10])
    plot.showProgressBar = False
    plot.printDebugInfo = False
    plot.add(obj)
    plot.save(BytesIO(), format="png")
    return obj


def _line_segments(obj):
    from kaxe.core.shapes import LineSegment

    return [o for o in obj.batch.objects if isinstance(o, LineSegment)]


@unit()
def test_resample_polyline_straight_line_spacing():
    """Horizontal line resamples to roughly length / spacing + 1 points."""
    points = [(0.0, 0.0), (300.0, 0.0)]
    spacing = 30
    result = resample_polyline(points, spacing)

    assert result[0] == points[0]
    assert result[-1] == points[-1]
    assert 9 <= len(result) <= 12

    for i in range(1, len(result)):
        dist = math.hypot(result[i][0] - result[i - 1][0], result[i][1] - result[i - 1][1])
        assert spacing - 0.01 <= dist <= spacing + 0.01


@unit()
def test_resample_polyline_preserves_endpoints():
    """First and last input points are always kept."""
    points = [(1.0, 2.0), (50.0, 80.0), (200.0, 40.0)]
    result = resample_polyline(points, 25)

    assert result[0] == points[0]
    assert result[-1] == points[-1]


@unit()
def test_resample_polyline_noop_for_invalid_spacing():
    """Invalid spacing returns input unchanged."""
    points = [(0.0, 0.0), (10.0, 0.0)]
    assert resample_polyline(points, 0) == points
    assert resample_polyline(points, -5) == points
    assert resample_polyline([(1.0, 1.0)], 10) == [(1.0, 1.0)]


@unit()
def test_points2d_dense_dashed_reduces_vertices():
    """Many collinear points are resampled before dashed LineSegment rendering."""
    n = 1000
    x = [i * 10 / n for i in range(n)]
    y = [0] * n
    obj = kaxe.Points2D(x, y, connect=True, show_points=False, dashed=30)
    _finalize_points2d(obj)

    segments = _line_segments(obj)
    assert len(segments) == 1
    assert len(segments[0].points) < n
    assert segments[0].dashed is True
    assert segments[0].dashedDist == 30


@unit()
def test_points2d_sparse_dashed_adds_vertices():
    """Sparse input is densified along the path for even dash spacing."""
    obj = kaxe.Points2D([0, 10], [0, 0], connect=True, show_points=False, dashed=30)
    _finalize_points2d(obj)

    segments = _line_segments(obj)
    assert len(segments) == 1
    assert len(segments[0].points) > 2


@unit()
def test_points2d_dashed_with_markers_skips_pairwise_lines():
    """Dashed connect draws resampled LineSegment and markers, not pairwise Lines."""
    obj = kaxe.Points2D([0, 5, 10], [0, 5, 10], connect=True, dashed=30)
    _finalize_points2d(obj)

    from kaxe.core.shapes import Circle, Line

    assert len(_line_segments(obj)) == 1
    assert not any(isinstance(o, Line) for o in obj.batch.objects)
    assert any(isinstance(o, Circle) for o in obj.batch.objects)


@unit()
def test_points_passes_dashed_to_points2d():
    """kaxe.Points forwards dashed to Points2D in 2D."""
    obj = kaxe.Points([0, 10], [0, 0], connect=True, show_points=False, dashed=30)
    assert isinstance(obj, kaxe.Points2D)
    assert obj.dashed == 30
