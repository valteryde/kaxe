"""
Tests for HeatMap.fromFunction.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import sanity, smoke, unit


def _calc_borders(plot):
    plot.__calculateWindowBorders__()
    return plot.windowAxis


@unit()
def test_from_function_grid_shape():
    hm = kaxe.HeatMap.fromFunction(lambda x, y: x + y, numSamples=50)
    assert len(hm.data) == 50
    assert len(hm.data[0]) == 50


@unit()
def test_from_function_placement():
    hm = kaxe.HeatMap.fromFunction(
        lambda x, y: x * y,
        numSamples=50,
        domain=(-10, 10, -10, 10),
    )
    assert hm.position == (-10, -10)
    assert hm.unitPerPixel == [0.4, 0.4]


@unit()
def test_from_function_auto_scale():
    plot = kaxe.Plot()
    plot.add(kaxe.HeatMap.fromFunction(
        lambda x, y: math.sin(x) * math.cos(y),
        numSamples=100,
        domain=(-10, 10, -10, 10),
    ))
    wa = _calc_borders(plot)
    assert wa[0] == -10
    assert wa[1] == 10
    assert wa[2] == -10
    assert wa[3] == 10


@smoke()
@sanity()
def test_heatmap_from_function_render():
    """Heatmap from a 2D function (matches tests/test_4.py)."""
    plot = kaxe.Plot()
    plot.add(kaxe.HeatMap.fromFunction(
        lambda x, y: math.sin(x) * math.cos(y),
        numSamples=100,
        domain=(-10, 10, -10, 10),
    ))
    return plot
