"""
Test contour plots.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke, unit


@smoke()
@sanity()
@judge(
    elements=["contour curves", "inline contour labels", "axes"],
    focus="contour level numbers readable on lines",
    min_score=5,
)
def test_contour_labels():
    """Contour plot with inline level labels on curves."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])

    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2

    plot.add(kaxe.Contour(f, a=0.2, b=1.7, steps=7, label=True))
    return plot


@smoke()
@sanity()
@judge(
    elements=["contour curves", "axes"],
    focus="contour curves without inline labels",
)
def test_contour_without_labels():
    """Contour plot with labels disabled."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])

    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2

    plot.add(kaxe.Contour(f, a=0.2, b=1.7, steps=7, label=False))
    return plot


@unit()
def test_contour_label_batch():
    """Inline labels are added to the contour batch without exploding in count."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])
    plot.width = 800
    plot.height = 600
    plot.windowBox = [0, 0, 800, 600]
    plot.__calculateWindowBorders__()
    plot.__prepare__()

    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2
    contour = kaxe.Contour(f, a=0.2, b=1.7, steps=7, label=True)
    contour.finalize(plot)

    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    assert len(texts) > 0
    assert len(texts) < 100
