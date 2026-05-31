"""
Plot.adjust sets explicit xNumbers and yNumbers with sensible minimums.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.window import compute_adjust_styles, compute_axis_numbers
from runner import unit


@unit()
def test_compute_axis_numbers_minimum():
    x, y = compute_axis_numbers(800, 600, 100, min_ticks=4)
    assert x >= 4
    assert y >= 4
    assert x == max(4, 800 // 200)
    assert y == max(4, 600 // 200)


@unit()
def test_plot_adjust_sets_axis_numbers():
    plt = kaxe.Plot()
    plt.adjust(0.6)
    assert plt.getAttr("xNumbers") is not None
    assert plt.getAttr("yNumbers") is not None
    assert plt.getAttr("xNumbers") >= 4
    assert plt.getAttr("yNumbers") >= 4
    styles = compute_adjust_styles(0.6)
    expected_x, expected_y = compute_axis_numbers(
        styles["width"], styles["height"], styles["fontSize"]
    )
    assert plt.getAttr("xNumbers") == expected_x
    assert plt.getAttr("yNumbers") == expected_y
