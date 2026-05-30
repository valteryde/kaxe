"""
Test inequality plots.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.shapes import shapes
from runner import judge, sanity, smoke, unit


@smoke()
@sanity()
@judge(
    elements=["contour curves", "inequality boundary", "hatched forbidden region", "axes"],
    focus="inequality boundary and forbidden-side hatching legibility",
    min_score=5,
)
def test_inequality_with_contour():
    """Contour plot with an inequality boundary and forbidden-side hatching."""
    plot = kaxe.Plot()

    f = lambda x, y: (x - 1) ** 2 + (y - 2) ** 2
    g = lambda x, y: x + y - 3

    plot.add(kaxe.Contour(f))
    plot.add(kaxe.Inequality(g, lambda x, y: 0))
    return plot


@unit()
def test_inequality_batches():
    """Inequality produces boundary shapes and hatch line segments after finalize."""
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.width = 800
    plot.height = 800
    plot.windowBox = [0, 0, 800, 800]
    plot.__calculateWindowBorders__()
    plot.__prepare__()

    ineq = kaxe.Inequality(lambda x, y: x + y - 3, lambda x, y: 0)
    ineq.finalize(plot)

    assert len(ineq.boundary.batch.objects) > 0
    hatch_lines = [obj for obj in ineq.hatch_batch.objects if isinstance(obj, shapes.Line)]
    assert len(hatch_lines) > 0
