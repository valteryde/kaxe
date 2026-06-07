"""
Test inequality plots.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.shapes import shapes
from runner import judge, sanity, smoke, unit


def _hatch_covers_point(ineq, plot, x, y):
    px, py = plot.pixel(x, y)
    if not plot.inside(px, py):
        return False
    for ln in ineq.hatch_batch.objects:
        if not isinstance(ln, shapes.Line):
            continue
        xmin, xmax = sorted((ln.x0, ln.x1))
        ymin, ymax = sorted((ln.y0, ln.y1))
        if xmin <= px <= xmax and ymin <= py <= ymax:
            return True
    return False


def _count_hatch_lines(ineq):
    return sum(1 for obj in ineq.hatch_batch.objects if isinstance(obj, shapes.Line))


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


@unit()
def test_inequality_hatch_band_near_boundary():
    """A small hatch_band still hatches forbidden points close to the boundary."""
    g = lambda x, y: x + y - 3
    plot = kaxe.Plot([0, 5, 0, 5])
    ineq = kaxe.Inequality(g, 0, hatch_spacing=10, hatch_band=25)
    plot.add(ineq)
    plot.printDebugInfo = False
    plot.showProgressBar = False
    plot.__bake__()

    assert _hatch_covers_point(ineq, plot, 2.52, 0.52), (
        "forbidden point near boundary should lie on a hatch segment"
    )


@unit()
def test_inequality_hatch_band_excludes_far_forbidden():
    """hatch_band limits hatching to a pixel band and skips far forbidden points."""
    g = lambda x, y: x + y - 3
    plot = kaxe.Plot([0, 10, 0, 10])
    ineq = kaxe.Inequality(g, 0, hatch_spacing=10, hatch_band=25)
    plot.add(ineq)
    plot.printDebugInfo = False
    plot.showProgressBar = False
    plot.__bake__()

    assert not _hatch_covers_point(ineq, plot, 9, 9), (
        "forbidden point far from boundary should not lie on a hatch segment"
    )


@unit()
def test_inequality_hatch_band_circle_near_boundary():
    """hatch_band hatches around a curved boundary, not just straight lines."""
    import math

    f = lambda x, y: (x - 5) ** 2 + (y - 5) ** 2 - 9
    plot = kaxe.Plot([0, 10, 0, 10])
    ineq = kaxe.Inequality(f, 0, hatch_spacing=10, hatch_band=30)
    plot.add(ineq)
    plot.printDebugInfo = False
    plot.showProgressBar = False
    plot.__bake__()

    covered = 0
    checked = 0
    for deg in range(0, 360, 15):
        angle = math.radians(deg)
        x = 5 + 3.15 * math.cos(angle)
        y = 5 + 3.15 * math.sin(angle)
        if f(x, y) <= 0:
            continue
        checked += 1
        if _hatch_covers_point(ineq, plot, x, y):
            covered += 1

    assert checked > 0
    assert covered >= checked // 2, "most near-boundary forbidden samples should be hatched"


@unit()
def test_inequality_hatch_band_none_full_fill():
    """Default hatch_band=None hatches more of the forbidden region than a small band."""
    g = lambda x, y: x + y - 3
    plot = kaxe.Plot([0, 10, 0, 10])
    plot.printDebugInfo = False
    plot.showProgressBar = False

    full = kaxe.Inequality(g, 0, hatch_spacing=10)
    band = kaxe.Inequality(g, 0, hatch_spacing=10, hatch_band=25)
    plot.add(full)
    plot.__bake__()
    full_count = _count_hatch_lines(full)

    plot2 = kaxe.Plot([0, 10, 0, 10])
    plot2.printDebugInfo = False
    plot2.showProgressBar = False
    plot2.add(band)
    plot2.__bake__()
    band_count = _count_hatch_lines(band)

    assert full_count > band_count
