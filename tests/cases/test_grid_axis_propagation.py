"""
Grid theme and style propagate xNumbers / yNumbers to subplot cells at bake time.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit


def _make_plot():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x))
    plot.showProgressBar = False
    plot.printDebugInfo = False
    return plot


@unit()
def test_grid_theme_propagates_axis_numbers():
    grid = kaxe.Grid()
    grid.theme(kaxe.Themes.A4Mini)
    p1, p2 = _make_plot(), _make_plot()
    grid.addRow(p1, p2)

    grid._prepare_cells(vector=False)

    assert p1.getAttr("xNumbers") == kaxe.Themes.A4Mini["xNumbers"]
    assert p1.getAttr("yNumbers") == kaxe.Themes.A4Mini["yNumbers"]
    assert p2.getAttr("xNumbers") == kaxe.Themes.A4Mini["xNumbers"]
    assert p2.getAttr("yNumbers") == kaxe.Themes.A4Mini["yNumbers"]


@unit()
def test_grid_style_propagates_axis_numbers():
    grid = kaxe.Grid()
    grid.style(width=1200, height=600, xNumbers=8, yNumbers=6)
    p1 = _make_plot()
    grid.addRow(p1)

    grid._prepare_cells(vector=False)

    assert p1.getAttr("xNumbers") == 8
    assert p1.getAttr("yNumbers") == 6
