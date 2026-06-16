"""
Tests for default Okabe–Ito palette and per-figure color cycle reset.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from ward import test

import kaxe
from kaxe.core.color import Colormaps, to_rgba
from kaxe.core.palette import DEFAULT_SERIES_COLORS, OKABE_ITO_SERIES
from kaxe.core.styles import getRandomColor, isLightOrDark, resetColor, setDefaultColors


@test("first series color is Okabe–Ito orange")
def _():
    resetColor()
    assert getRandomColor() == to_rgba("#E69F00")


@test("series palette has seven Okabe–Ito colors")
def _():
    assert len(DEFAULT_SERIES_COLORS) == 7
    assert DEFAULT_SERIES_COLORS[0] == to_rgba(OKABE_ITO_SERIES[0])
    assert DEFAULT_SERIES_COLORS[-1] == to_rgba(OKABE_ITO_SERIES[-1])


@test("series cycle wraps after seven colors")
def _():
    resetColor()
    seen = [getRandomColor() for _ in range(7)]
    assert seen == DEFAULT_SERIES_COLORS
    assert getRandomColor() == DEFAULT_SERIES_COLORS[0]


@test("new Plot resets series cycle to first color")
def _():
    plt1 = kaxe.Plot([0, 1, 0, 1])
    func1 = kaxe.Function2D(lambda x: x)
    plt1.add(func1)

    plt2 = kaxe.Plot([0, 1, 0, 1])
    func2 = kaxe.Function2D(lambda x: x)
    plt2.add(func2)

    assert func1.color == func2.color == to_rgba("#E69F00")


@test("setDefaultColors replaces the series palette")
def _():
    try:
        setDefaultColors(["#ff0000"])
        resetColor()
        assert getRandomColor() == (255, 0, 0, 255)
        assert getRandomColor() == (255, 0, 0, 255)
    finally:
        setDefaultColors(OKABE_ITO_SERIES)


@test("Okabe yellow is treated as light for pie label contrast")
def _():
    assert isLightOrDark(to_rgba("#F0E442")) is True


@test("Colormaps.standard endpoints use sequential ramp")
def _():
    cmap = Colormaps.standard
    low = cmap.getColor(0, 0, 10)
    high = cmap.getColor(10, 0, 10)
    assert low == to_rgba("#0072B2")
    assert high == to_rgba("#56B4E9")
