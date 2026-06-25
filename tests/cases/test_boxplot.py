"""
Test boxplot, including correct whisker calculation (Tukey convention).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
import numpy as np
from runner import smoke, sanity


@smoke()
@sanity()
def test_boxplot_basic():
    """Boxplot renders without error."""
    chart = kaxe.BoxPlot()
    chart.add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    chart.add([4, 1, 6, 1, 6.3, 1, 6.2, 7, 9.1])
    chart.legends("dataset 1", "dataset 2")
    return chart


@smoke()
@sanity()
def test_boxplot_whiskers():
    """
    Boxplot with clear outlier: whiskers extend to min/max within fence, not fence boundaries.
    Data [1..10, 100]: Q1=3.5, Q3=8.5, IQR=5, fence=[-4, 16].
    Whiskers should be at 1 and 10 (data min/max within fence), 100 is outlier.
    """
    chart = kaxe.BoxPlot()
    chart.add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100])
    chart.legends("with outlier")
    return chart


@smoke()
@sanity()
def test_boxplot_overlay():
    """Manual overlay points on a box row with custom colors and symbols."""
    chart = kaxe.BoxPlot()
    chart.add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    chart.overlay(
        [2, 3, 4],
        box=0,
        color=(220, 50, 50, 255),
        symbol=kaxe.symbol.CIRCLE,
        legend="low",
    )
    chart.overlay(
        [8, 9, 10],
        box=0,
        color=(50, 80, 220, 255),
        symbol=kaxe.symbol.CROSS,
        legend="high",
    )
    chart.legends("full group")
    return chart
