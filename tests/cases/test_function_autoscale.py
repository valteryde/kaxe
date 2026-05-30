"""
Tests for function auto-scaling (bounds estimation and window integration).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.bounds import apply_margin, is_finite, sample_1d
from runner import unit


def _calc_borders(plot):
    plot.__calculateWindowBorders__()
    return plot.windowAxis


@unit()
def test_bounds_apply_margin():
    lo, hi = apply_margin(0.0, 10.0, fraction=0.05)
    assert lo == -0.5
    assert hi == 10.5


@unit()
def test_bounds_apply_margin_degenerate():
    lo, hi = apply_margin(3.0, 3.0)
    assert lo == 2.0
    assert hi == 4.0


@unit()
def test_bounds_is_finite_rejects_nan_and_inf():
    assert not is_finite(float('nan'))
    assert not is_finite(float('inf'))
    assert is_finite(1.5)


@unit()
def test_bounds_sample_1d_sin():
    _, _, y0, y1 = sample_1d(math.sin, -math.pi, math.pi, n=64)
    assert y0 is not None
    assert y1 is not None
    assert y0 <= -0.9
    assert y1 >= 0.9


@unit()
def test_function2d_auto_sin():
    plot = kaxe.Plot()
    plot.add(kaxe.Function2D(math.sin))
    wa = _calc_borders(plot)
    assert wa[0] == -11.0
    assert wa[1] == 11.0
    assert abs(wa[2] + 1.1) < 0.05
    assert abs(wa[3] - 1.1) < 0.05


@unit()
def test_function2d_auto_parabola():
    plot = kaxe.Plot()
    plot.add(kaxe.Function2D(lambda x: x**2 - 4))
    wa = _calc_borders(plot)
    assert wa[2] <= -4.1
    assert wa[3] >= 4.0


@unit()
def test_function2d_fixed_x_auto_y():
    plot = kaxe.Plot([-5, 5, None, None])
    plot.add(kaxe.Function2D(math.sin))
    wa = _calc_borders(plot)
    assert wa[0] == -5
    assert wa[1] == 5
    assert abs(wa[2] + 1.1) < 0.05
    assert abs(wa[3] - 1.1) < 0.05


@unit()
def test_function2d_domain_override():
    plot = kaxe.Plot()
    plot.add(kaxe.Function2D(math.sin, domain=(-math.pi, math.pi)))
    wa = _calc_borders(plot)
    assert abs(wa[0] + math.pi * 1.05) < 0.2
    assert abs(wa[1] - math.pi * 1.05) < 0.2


@unit()
def test_function2d_range_override():
    plot = kaxe.Plot()
    plot.add(kaxe.Function2D(math.sin, range=(-2, 2)))
    wa = _calc_borders(plot)
    assert wa[2] == -2
    assert wa[3] == 2


@unit()
def test_function2d_with_points():
    plot = kaxe.Plot()
    plot.add(kaxe.Points2D([-20, 20], [0, 0]))
    plot.add(kaxe.Function2D(math.sin, domain=(-math.pi, math.pi)))
    wa = _calc_borders(plot)
    assert wa[0] <= -20
    assert wa[1] >= 20


@unit()
def test_function3d_auto():
    plot = kaxe.Plot3D()
    plot.add(kaxe.Function3D(lambda x, y: math.sin(x) * math.cos(y), numPoints=10))
    wa = _calc_borders(plot)
    assert all(v is not None for v in wa[:6])
    assert wa[4] < 1.1
    assert wa[5] > -1.1
    assert not (wa[0] == -10 and wa[1] == 10 and wa[4] == -10 and wa[5] == 10)


@unit()
def test_function3d_domain():
    plot = kaxe.Plot3D()
    plot.add(kaxe.Function3D(
        lambda x, y: x + y,
        domain=(-2, 2, -3, 3),
        numPoints=10,
    ))
    wa = _calc_borders(plot)
    assert abs(wa[0] + 2.2) < 0.01
    assert abs(wa[1] - 2.2) < 0.01
    assert abs(wa[2] + 3.3) < 0.01
    assert abs(wa[3] - 3.3) < 0.01


@unit()
def test_bounds_merges_with_none():
    plot = kaxe.Plot([-5, 5, None, None])
    plot.add(kaxe.Function2D(lambda x: x))
    wa = _calc_borders(plot)
    assert wa[0] == -5
    assert wa[1] == 5
    assert wa[2] <= -5.5
    assert wa[3] >= 5.5
