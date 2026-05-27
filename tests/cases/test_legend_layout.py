"""Legend box layout tests."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kaxe.core.legend import LegendBox
from kaxe.core.symbol import symbol
from kaxe.core.window import Window
from runner import unit


def _render_legend(plot_width: int):
    parent = Window()
    parent.attrmap.default("width", plot_width)
    parent.attrmap.default("fontSize", 16)
    parent.attrmap.default("color", (0, 0, 0, 255))

    lb = LegendBox()
    for label in [
        "Simulation (Non-linear)",
        "Simulation (Linear)",
        "Simulation (Linear FF)",
    ]:
        lb.add(label, symbol.CIRCLE, (200, 0, 0, 255))

    return lb.finalize(parent, sneaky=True)


def _marker_cluster_ranges(img, row_slice):
    rgb = np.array(img)[row_slice, :, :3]
    red = (rgb[:, :, 0] > 150) & (rgb[:, :, 1] < 80) & (rgb[:, :, 2] < 80)
    row = red.any(axis=0)

    ranges = []
    in_cluster = False
    start = 0
    for x, has in enumerate(row):
        if has and not in_cluster:
            start = x
            in_cluster = True
        elif not has and in_cluster:
            ranges.append((start, x))
            in_cluster = False
    if in_cluster:
        ranges.append((start, len(row)))
    return ranges


@unit()
def test_legend_multiline_wraps_without_overlap():
    """Two legend entries on one row must not overlap horizontally."""
    img = _render_legend(420)
    assert img.width >= 340

    top = slice(0, img.height // 2 + 4)
    clusters = _marker_cluster_ranges(img, top)
    assert len(clusters) == 2
    assert clusters[1][0] - clusters[0][1] >= 100


@unit()
def test_legend_multiline_wraps_to_new_row():
    """Legend entries that exceed max width should wrap to additional rows."""
    img = _render_legend(400)
    assert img.height >= 40
    assert img.width < 220

    top = slice(0, img.height // 2 + 4)
    bottom = slice(img.height // 2 - 4, img.height)
    assert len(_marker_cluster_ranges(img, top)) == 1
    assert len(_marker_cluster_ranges(img, bottom)) == 1


@unit()
def test_legend_second_row_fits_multiple_entries():
    """Wrapped rows should still fit multiple entries when there is room."""
    img = _render_legend(415)
    bottom = slice(img.height // 2 - 4, img.height)
    clusters = _marker_cluster_ranges(img, bottom)
    assert len(clusters) == 2
    assert clusters[1][0] - clusters[0][1] >= 80
