"""
Grid.adjust sizes the composite and propagates per-cell axis tick counts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.window import compute_adjust_styles, compute_axis_numbers
from runner import unit


def _make_plot():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x**2 - 2))
    plot.showProgressBar = False
    plot.printDebugInfo = False
    return plot


@unit()
def test_grid_adjust_propagates_to_cells():
    grid = kaxe.Grid()
    p1, p2, p3, p4 = _make_plot(), _make_plot(), _make_plot(), _make_plot()
    grid.addRow(p1, p2)
    grid.addRow(p3, p4)
    grid.adjust(0.5)

    assert grid.getAttr("xNumbers") >= 4
    assert grid.getAttr("yNumbers") >= 4

    grid._prepare_cells(vector=False)

    for plot in (p1, p2, p3, p4):
        assert plot.getAttr("fontSize") == grid.getAttr("fontSize")
        assert plot.getAttr("xNumbers") == grid.getAttr("xNumbers")
        assert plot.getAttr("yNumbers") == grid.getAttr("yNumbers")
        assert plot.getAttr("xNumbers") >= 4
        assert plot.getAttr("yNumbers") >= 4


@unit()
def test_grid_adjust_cell_axis_numbers_match_formula():
    grid = kaxe.Grid()
    grid.addRow(_make_plot(), _make_plot())
    grid.adjust(0.5)

    styles = compute_adjust_styles(0.5)
    cell_w = styles["width"] // 2
    cell_h = styles["height"] // 1
    expected_x, expected_y = compute_axis_numbers(
        cell_w, cell_h, styles["fontSize"]
    )
    assert grid.getAttr("xNumbers") == expected_x
    assert grid.getAttr("yNumbers") == expected_y
