"""
Test point plots.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke


@smoke()
@sanity()
@judge(
    elements=["scatter points", "legend"],
    focus="point plot legibility",
)
def test_point_plot():
    """Point plot with title and legend."""
    plot = kaxe.Plot()
    plot.title("en lang titel der strakker sig langt", "en lang titel der strakker sig langt")
    p = kaxe.objects.Points(range(0, 100), [0.25 * i**2 - 100 for i in range(0, 100)]).legend("test")
    plot.add(p)
    return plot


@smoke()
@sanity()
@judge(
    elements=["scatter points", "data visible"],
    focus="point plot legibility",
)
def test_linear_point_plot():
    """Linear point plot."""
    plot = kaxe.Plot()
    plot.title("hejsa")
    p = kaxe.objects.Points(range(0, 100), [i for i in range(0, 100)]).legend("test")
    plot.add(p)
    return plot
