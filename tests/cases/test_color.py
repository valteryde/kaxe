"""
Unit tests for centralized color parsing (to_rgba).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import numpy as np
from ward import test

import kaxe
from kaxe.core.color import to_rgba, SingleColormap, Colormaps
from kaxe.core.d3.helper import formatColor
from kaxe.core.shapes import shapes


@test("hex string parses to RGBA tuple")
def _():
    assert to_rgba("#FF5154") == (255, 81, 84, 255)


@test("RGB sequence gets opaque alpha")
def _():
    assert to_rgba((10, 20, 30)) == (10, 20, 30, 255)


@test("RGBA sequence is preserved")
def _():
    assert to_rgba((10, 20, 30, 100)) == (10, 20, 30, 100)


@test("numpy RGBA array is accepted")
def _():
    assert to_rgba(np.array([1, 2, 3, 4])) == (1, 2, 3, 4)


@test("Colormap instances are rejected")
def _():
    try:
        to_rgba(Colormaps.standard)
        raised = False
    except TypeError:
        raised = True
    assert raised


@test("Rectangle accepts hex color")
def _():
    rect = shapes.Rectangle(0, 0, 10, 10, color="#AFE3C0")
    assert rect.color == (175, 227, 192, 255)


@test("formatColor accepts hex for 3D")
def _():
    arr = formatColor("#004b23")
    assert len(arr) == 4
    assert int(arr[0]) == 0
    assert int(arr[1]) == 75
    assert int(arr[2]) == 35
    assert int(arr[3]) == 255


@test("SingleColormap accepts hex without NameError")
def _():
    cmap = SingleColormap("#004b23", total=3)
    assert len(cmap.colorGradientSteps) == 3
