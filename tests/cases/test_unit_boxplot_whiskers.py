"""
Unit tests for boxplot whisker calculation (Tukey convention).

Whiskers extend to min/max of data within fence [Q1-1.5*IQR, Q3+1.5*IQR].
Points outside the fence are outliers.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from kaxe.plot.zoom_connector import compute_boxplot_whiskers
from runner import unit


@unit()
def test_whiskers_no_outliers():
    """Data entirely within fence: whiskers at min and max of data."""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    left, right = compute_boxplot_whiskers(data)
    assert left == 1.0
    assert right == 10.0


@unit()
def test_whiskers_single_outlier():
    """Data [1..10, 100]: fence [-4, 16], whiskers at 1 and 10, 100 is outlier."""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    left, right = compute_boxplot_whiskers(data)
    assert left == 1.0
    assert right == 10.0


@unit()
def test_whiskers_multiple_outliers():
    """Data with outliers on both sides."""
    data = [-100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    left, right = compute_boxplot_whiskers(data)
    assert left == 1.0
    assert right == 10.0


@unit()
def test_whiskers_tight_fence():
    """When IQR is 0 (all middle values equal), fence collapses; whiskers at data min/max in fence."""
    # Data [1, 1, 1, 1, 1, 1, 1, 1, 1, 100]: Q1=1, Q3=1, IQR=0, fence=[1, 1].
    # Only 1s are in fence -> left=1, right=1.
    data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 100]
    left, right = compute_boxplot_whiskers(data)
    assert left == 1.0
    assert right == 1.0


@unit()
def test_whiskers_single_point():
    """Single data point: whisker at that point."""
    data = [42.0]
    left, right = compute_boxplot_whiskers(data)
    assert left == 42.0
    assert right == 42.0


@unit()
def test_whiskers_two_points():
    """Two points: Q1=Q3, IQR=0, fence = [q-0, q+0] = [q, q]."""
    data = [10, 20]
    left, right = compute_boxplot_whiskers(data)
    # Q1=12.5, Q3=17.5, IQR=5, fence=[5, 25]. Both points in fence.
    assert left == 10.0
    assert right == 20.0


@unit()
def test_whiskers_tukey_vs_fence():
    """Whiskers are at data min/max within fence, NOT at fence boundaries."""
    # If we used fence: left=-4, right=16. Correct: left=1, right=10.
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    left, right = compute_boxplot_whiskers(data)
    assert left != -4.0, "Whisker should be at data min (1), not fence (-4)"
    assert right != 16.0, "Whisker should be at data max (10), not fence (16)"
