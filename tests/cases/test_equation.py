"""
Test equation and pillars plots.
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
    elements=["pillars", "gaussian curve", "axes"],
    focus="pillar plot and curve legibility",
)
def test_pillars():
    """Pillars with gaussian distribution."""
    plot = kaxe.Plot([-40, 30, None, None])
    sigma = 10
    mu = 0
    f = lambda x: (1 / (sigma * math.sqrt(2 * math.pi)) * math.e ** (-1 / 2 * (((x - mu) / sigma) ** 2)))
    x = range(0, 40)
    plot.add(kaxe.objects.Pillars(x, [f(i) for i in x]))
    plot.add(kaxe.objects.Function(f))
    return plot


@smoke()
@sanity()
@judge(
    elements=["curves", "axes"],
    focus="equation plot legibility",
    min_score=5,
)
def test_equation():
    """Implicit equations (circles, etc)."""
    plot = kaxe.Plot([-10, 10, -10, 10])
    center = (0, 1)
    plot.add(kaxe.objects.Equation(lambda x, y: (x - center[0])**2 + (y - center[1])**2, lambda x, y: 2**2))
    plot.add(kaxe.objects.Equation(lambda x, y: (x - center[0])**2 + (y - center[1])**2, lambda x, y: 6**2))
    plot.add(kaxe.objects.Equation(lambda x, y: math.sin(8 * x), lambda x, y: y))
    plot.add(kaxe.objects.Equation(lambda x, y: 4 * x, lambda x, y: y))
    plot.add(kaxe.objects.Equation(lambda x, y: math.sin(y) * 4, lambda x, y: x))
    return plot
