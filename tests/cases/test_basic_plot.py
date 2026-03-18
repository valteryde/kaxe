"""
Test basic 2D plot with function.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke


@smoke()
@sanity()
@judge(
    elements=["parabola", "axes", "grid or markers"],
    focus="plot legibility and correct parabola shape",
)
def test_basic_plot():
    """Simple plot with a function."""
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.add(kaxe.Function2D(lambda x: x**2 - 4))
    return plot

