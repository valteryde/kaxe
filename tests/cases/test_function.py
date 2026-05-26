"""
Test function plots.
"""

import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke


@smoke()
@sanity()
@judge(
    elements=["multiple curves", "axes", "distinct curves visible"],
    focus="function plot legibility",
)
def test_function():
    """Multiple functions: linear, sin, sqrt, inverse."""
    plot = kaxe.Plot()
    f1 = kaxe.objects.Function(lambda x, a: a * x, a=2)
    plot.add(f1)
    f1.fill(-10, 10)
    f2 = kaxe.objects.Function(lambda x, a: a * x, a=0, width=10)
    plot.add(f2)
    f3 = kaxe.objects.Function(lambda x: math.sin(x) * 2)
    f3.tangent(2)
    f3.fill(-math.pi, math.pi)
    plot.add(f3)
    f4 = kaxe.objects.Function(lambda x: math.sqrt(x))
    plot.add(f4)
    f4.fill(4, 8)
    f5 = kaxe.objects.Function(lambda x: 1 / x)
    plot.add(f5)
    f5.fill(4, 8)
    return plot


@smoke()
@sanity()
@judge(
    elements=["hyperbola curve", "axes"],
    focus="inverse proportional curve legibility",
)
def test_inverse_proportional():
    """Inverse proportional function."""
    plot = kaxe.Plot()
    f = kaxe.objects.Function(lambda x: 1 / x)
    plot.add(f)
    f.fill(4, 8)
    return plot


@smoke()
@sanity()
@judge(
    elements=["piecewise curve", "axes", "distinct segments"],
    focus="piecewise function legibility",
)
def test_piecewise():
    """Piecewise function."""
    plot = kaxe.Plot()

    def f(x):
        if x < -1:
            return 2
        elif x > 2:
            return x * 2 - 4
        else:
            return -x * 2 + 4

    plot.add(kaxe.objects.Function(f))
    return plot


@smoke()
@sanity()
@judge(
    elements=["linear line through origin", "axes"],
    focus="linear function legibility",
)
def test_linear_function():
    """Simple linear function."""
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function(lambda x: x))
    return plot
