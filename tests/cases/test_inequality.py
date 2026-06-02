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
    elements=["contour curves", "inline contour labels", "inequality boundary", "hatched forbidden region", "axes"],
    focus="inequality boundary and forbidden-side hatching legibility",
    min_score=5,
)
def test_inequality_with_contour():
    """Contour plot with an inequality boundary and forbidden-side hatching."""
    plot = kaxe.Plot()

    f = lambda x, y: (x - 1) ** 2 + (y - 2) ** 2
    g = lambda x, y: x + y - 3

    plot.add(kaxe.Contour(f))
    plot.add(kaxe.Inequality(g, 0))
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

    ineq = kaxe.Inequality(lambda x, y: x + y - 3, 0)
    ineq.finalize(plot)

    assert len(ineq.boundary.batch.objects) > 0
    hatch_lines = [obj for obj in ineq.hatch_batch.objects if isinstance(obj, shapes.Line)]
    assert len(hatch_lines) > 0


@unit()
def test_inequality_numeric_left():
    """A numeric left side is treated as a constant."""
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.width = 800
    plot.height = 800
    plot.windowBox = [0, 0, 800, 800]
    plot.__calculateWindowBorders__()
    plot.__prepare__()

    ineq = kaxe.Inequality(0, lambda x, y: x + y - 3, op='>=')
    ineq.finalize(plot)

    assert len(ineq.boundary.batch.objects) > 0


@unit()
def test_inequality_hatch_past_axis_intercept():
    """Hatching continues past where the boundary leaves the plot (e.g. x-intercept)."""
    g = lambda x, y: 208 / 250 * x + y - 208
    plot = kaxe.Plot([0, 300, 0, 300])
    ineq = kaxe.Inequality(g, 0, hatch_spacing=10)
    plot.add(ineq)
    plot.printDebugInfo = False
    plot.showProgressBar = False
    plot.__bake__()

    wb = plot.windowBox
    px, py = plot.pixel(270, 5)
    assert plot.inside(px, py)

    covered = False
    for ln in ineq.hatch_batch.objects:
        if not isinstance(ln, shapes.Line):
            continue
        xmin, xmax = sorted((ln.x0, ln.x1))
        ymin, ymax = sorted((ln.y0, ln.y1))
        if xmin <= px <= xmax and ymin <= py <= ymax:
            covered = True
            break

    assert covered, "forbidden point past x-intercept should lie on a hatch segment"
