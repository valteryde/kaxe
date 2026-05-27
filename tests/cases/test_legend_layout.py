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
def test_legend_circle_is_not_clipped_at_bottom():
    """Legend circle markers should be symmetric and not clipped at the bottom edge."""
    parent = Window()
    parent.attrmap.default("width", 800)
    parent.attrmap.default("fontSize", 16)
    parent.attrmap.default("color", (0, 0, 0, 255))

    lb = LegendBox()
    lb.add("Simulation (Non-linear)", symbol.CIRCLE, (200, 0, 0, 255))
    img = lb.finalize(parent, sneaky=True)

    rgb = np.array(img)[..., :3]
    red = (rgb[:, :, 0] > 150) & (rgb[:, :, 1] < 80) & (rgb[:, :, 2] < 80)
    rows = np.where(red.any(axis=1))[0]
    cols = np.where(red.any(axis=0))[0]
    cluster = red[rows.min():rows.max() + 1, cols.min():cols.max() + 1]

    assert cluster.shape[0] >= 8, "legend circle marker looks clipped"
    row_widths = [cluster[i].sum() for i in range(cluster.shape[0])]
    assert abs(int(row_widths[0]) - int(row_widths[-1])) <= 1
    assert int(row_widths[-1]) < int(row_widths[len(row_widths) // 2])
    assert rows.max() < img.height - 1, "legend circle touches bottom edge"


@unit()
def test_legend_second_row_fits_multiple_entries():
    """Wrapped rows should still fit multiple entries when there is room."""
    img = _render_legend(415)
    bottom = slice(img.height // 2 - 4, img.height)
    clusters = _marker_cluster_ranges(img, bottom)
    assert len(clusters) == 2
    assert clusters[1][0] - clusters[0][1] >= 80
