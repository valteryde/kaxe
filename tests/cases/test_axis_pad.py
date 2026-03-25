"""
Unit tests for Plot.pad() data-space axis padding.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import unit


@unit()
def test_pad_symmetric_expands_window():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(1)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1, 11, -1, 11]


@unit()
def test_pad_asymmetric_x_y():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(x=2, y=0.5)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-2, 12, -0.5, 10.5]


@unit()
def test_pad_y_defaults_to_x():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(0.25)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-0.25, 10.25, -0.25, 10.25]


@unit()
def test_pad_zero_restores_after_repeat_calculate():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(1)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1, 11, -1, 11]
    plt.pad(0)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [0, 10, 0, 10]


@unit()
def test_double_calculate_idempotent():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(1)
    plt.__calculateWindowBorders__()
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1, 11, -1, 11]


@unit()
def test_double_axis_plot_both_y_scales():
    plt = kaxe.DoubleAxisPlot([0, 10, 0, 10, 0, 20])
    plt.pad(1)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:6] == [-1, 11, -1, 11, -1, 21]


@unit()
def test_pad_relative_fraction_of_span():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(0.1, relative=True)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1, 11, -1, 11]


@unit()
def test_pad_percent_matches_relative_fraction():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(10, percent=True)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1, 11, -1, 11]


@unit()
def test_pad_relative_then_absolute():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(0.1, relative=True)
    plt.pad(0.5)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-1.5, 11.5, -1.5, 11.5]


@unit()
def test_pad_relative_double_calculate_idempotent():
    plt = kaxe.Plot([0, 100, 0, 50])
    plt.pad(0.02, relative=True)
    plt.__calculateWindowBorders__()
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [-2, 102, -1, 51]


@unit()
def test_pad_relative_double_axis_each_y_span():
    plt = kaxe.DoubleAxisPlot([0, 10, 0, 10, 0, 20])
    plt.pad(0.1, relative=True)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:6] == [-1, 11, -1, 11, -2, 22]


@unit()
def test_pad_relative_zero_after_nonzero():
    plt = kaxe.Plot([0, 10, 0, 10])
    plt.pad(0.1, relative=True)
    plt.__calculateWindowBorders__()
    plt.pad(0, relative=True)
    plt.__calculateWindowBorders__()
    assert plt.windowAxis[:4] == [0, 10, 0, 10]
