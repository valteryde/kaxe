"""
Unit tests for BoxPlot overlay beeswarm offset assignment.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from kaxe.chart.box import _overlay_cluster_offsets
from runner import unit


def _point(overlay_idx, point_idx, value):
    return {"overlay_idx": overlay_idx, "point_idx": point_idx, "value": value}


@unit()
def test_cluster_single_point_offset_zero():
    points = [_point(0, 0, 10.0)]
    _overlay_cluster_offsets(points, box_height=100, jitter_frac=0.8)
    assert points[0]["offset"] == 0.0


@unit()
def test_cluster_two_points_same_value():
    points = [_point(0, 0, 15.0), _point(1, 0, 15.0)]
    _overlay_cluster_offsets(points, box_height=100, jitter_frac=0.8)
    span = 80.0
    assert points[0]["offset"] == -span / 2
    assert points[1]["offset"] == span / 2


@unit()
def test_cluster_unique_values_stay_on_center_line():
    points = [_point(0, 0, 10.0), _point(1, 0, 20.0)]
    _overlay_cluster_offsets(points, box_height=100, jitter_frac=0.8)
    assert points[0]["offset"] == 0.0
    assert points[1]["offset"] == 0.0


@unit()
def test_cluster_stable_order_by_overlay_then_point_index():
    points = [
        _point(1, 0, 5.0),
        _point(0, 1, 5.0),
        _point(0, 0, 5.0),
    ]
    _overlay_cluster_offsets(points, box_height=100, jitter_frac=1.0)
    span = 100.0
    assert points[2]["offset"] == -span / 2
    assert points[1]["offset"] == 0.0
    assert points[0]["offset"] == span / 2
