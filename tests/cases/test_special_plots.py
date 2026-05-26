"""
Test polar, logarithmic, and other special plot types.
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
    elements=["polar axes", "curves", "legend"],
    focus="polar plot legibility",
    min_score=5,
)
def test_polar_plot():
    """Polar plot with functions and points."""
    plt = kaxe.PolarPlot([0, 7])
    plt.add(kaxe.objects.Function(lambda x: math.sin(x) * math.cos(x)))
    plt.add(kaxe.objects.Function(lambda x: 0.5))
    plt.add(kaxe.objects.Function(lambda x: x))
    plt.add(kaxe.objects.Equation(lambda x, y: y, lambda x, y: 3))
    plt.add(kaxe.objects.Equation(lambda x, y: y, lambda x, y: x))
    steps = [(i / 1000) * math.pi * 2 for i in range(0, 1000)]
    plt.add(kaxe.objects.Points(steps, [math.cos(i) for i in steps], connect=True).legend("test"))
    plt.title("en titel på radius ting")
    return plt


@smoke()
@sanity()
@judge(
    elements=["log scale axes", "curves", "data points"],
    focus="logarithmic plot legibility",
)
def test_logarithmic():
    """Log plot."""
    plt = kaxe.LogPlot([0, 100, 0.01, 10000000000])
    plt.add(kaxe.objects.Points(range(0, 100), [i * 1000 for i in range(0, 100)]))
    plt.add(kaxe.objects.Function(lambda x: 10 * x))
    plt.add(kaxe.objects.Function(lambda x: math.pow(10, x)))
    plt.add(kaxe.objects.Points([10, 20, 30, 40, 50, 60], [0.1, 0.05, 0.075, 0.1, 1, 0.015]))
    return plt


@smoke()
@sanity()
@judge(
    elements=["axes", "plot area"],
    focus="empty log-log plot renders correctly",
)
def test_loglog():
    """Log-log plot."""
    plt = kaxe.LogPlot([0, 4121, 0, 1212], firstAxisLog=True, secondAxisLog=True)
    return plt


@smoke()
@sanity()
@judge(
    elements=["points", "plot area"],
    focus="plot legibility",
)
def test_labels():
    """Plot with LaTeX title."""
    plot = kaxe.Plot()
    plot.title("$f(x)=\\cases{2}{x<2}{4*x+2}{x>2}$", "en lang titel der strækker sig langt")
    plot.add(kaxe.objects.Points(range(0, 100), [0.25 * i**2 for i in range(0, 100)]))
    return plot
