"""
Grid fontSize propagation: legend and subplot cells share grid typography.
"""

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit


def _make_plot():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x**2 - 2))
    plot.showProgressBar = False
    plot.printDebugInfo = False
    return plot


@unit()
def test_grid_propagates_font_size_to_cells():
    grid = kaxe.Grid()
    grid.style(width=1200, height=600, fontSize=90, color=(10, 20, 30, 255))
    p1, p2 = _make_plot(), _make_plot()
    grid.addRow(p1, p2)

    assert p1.getAttr("fontSize") == 50
    assert p2.getAttr("fontSize") == 50

    grid._prepare_cells(vector=False)

    assert p1.getAttr("fontSize") == 90
    assert p2.getAttr("fontSize") == 90
    assert p1.getAttr("color") == (10, 20, 30, 255)
    assert p2.getAttr("color") == (10, 20, 30, 255)


@unit()
def test_grid_with_legend_exports_smoke():
    grid = kaxe.Grid()
    grid.style(width=800, height=400, fontSize=72)
    p1, p2 = _make_plot(), _make_plot()
    grid.addRow(p1, p2)
    grid.legends(
        ("Series A", kaxe.symbol.LINE, (222, 107, 72, 255)),
        ("Series B", kaxe.symbol.CIRCLE, (0, 114, 178, 255)),
    )

    buf = BytesIO()
    grid.save(buf, format="png")
    assert len(buf.getvalue()) > 1000

    buf = BytesIO()
    grid.save(buf, format="svg")
    assert b"<svg" in buf.getvalue()


@unit()
def test_grid_theme_sets_font_size_on_cells():
    grid = kaxe.Grid()
    grid.theme(kaxe.Themes.A4Mini)
    p1 = _make_plot()
    grid.addRow(p1)

    grid._prepare_cells(vector=False)

    assert p1.getAttr("fontSize") == kaxe.Themes.A4Mini["fontSize"]
