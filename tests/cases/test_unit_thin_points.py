"""
Unit tests for kaxe.thin_points.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import kaxe
from runner import unit


@unit()
def test_thin_points_every_stride():
    """every=n keeps roughly n/stride points with endpoints preserved."""
    n = 1000
    x = list(range(n))
    y = [0] * n

    x_thin, y_thin = kaxe.thin_points(x, y, every=10)

    assert x_thin[0] == 0
    assert x_thin[-1] == n - 1
    assert 99 <= len(x_thin) <= 101
    assert len(x_thin) == len(y_thin)


@unit()
def test_thin_points_max_points():
    """max_points caps count and preserves endpoints."""
    n = 10_000
    x = list(range(n))
    y = [0] * n

    x_thin, y_thin = kaxe.thin_points(x, y, max_points=500)

    assert x_thin[0] == 0
    assert x_thin[-1] == n - 1
    assert len(x_thin) == 500
    assert len(x_thin) == len(y_thin)


@unit()
def test_thin_points_max_points_noop_when_small():
    """max_points larger than input returns all points."""
    x = [1, 2, 3]
    y = [4, 5, 6]

    x_thin, y_thin = kaxe.thin_points(x, y, max_points=10)

    assert x_thin == x
    assert y_thin == y


@unit()
def test_thin_points_min_distance_data():
    """Data-space min_distance thins collinear points to expected spacing."""
    x = [float(i) for i in range(0, 101)]
    y = [0.0] * len(x)

    x_thin, y_thin = kaxe.thin_points(x, y, min_distance=10.0)

    assert x_thin[0] == 0.0
    assert x_thin[-1] == 100.0
    assert len(x_thin) == 11
    for i in range(1, len(x_thin)):
        dx = x_thin[i] - x_thin[i - 1]
        dy = y_thin[i] - y_thin[i - 1]
        assert math.hypot(dx, dy) >= 10.0 - 1e-9


@unit()
def test_thin_points_min_distance_pixel():
    """Pixel-space min_distance reduces dense collinear data."""
    n = 1000
    x = [i * 10 / n for i in range(n)]
    y = [1.0] * n

    plot = kaxe.Plot([0, 10, 0, 10])
    plot.theme(kaxe.Themes.A4Medium)

    x_thin, y_thin = kaxe.thin_points(
        x, y, min_distance=5, space="pixel", plot=plot
    )

    assert x_thin[0] == x[0]
    assert x_thin[-1] == x[-1]
    assert len(x_thin) < n


@unit()
def test_thin_points_z_passthrough():
    """Optional z is thinned with the same indices as x and y."""
    x = list(range(20))
    y = [i * 2 for i in x]
    z = [i * 3 for i in x]

    x_thin, y_thin, z_thin = kaxe.thin_points(x, y, z, every=5)

    assert len(x_thin) == len(y_thin) == len(z_thin)
    assert x_thin[0] == 0 and z_thin[0] == 0
    assert x_thin[-1] == 19 and z_thin[-1] == 57


@unit()
def test_thin_points_filters_non_finite():
    """NaN and non-real values are dropped before thinning."""
    x = [1, float("nan"), 3, 4]
    y = [1, 2, float("nan"), 4]

    x_thin, y_thin = kaxe.thin_points(x, y, every=1)

    assert x_thin == [1, 4]
    assert y_thin == [1, 4]


@unit()
def test_thin_points_requires_exactly_one_mode():
    """Providing zero or multiple modes raises ValueError."""
    x, y = [0, 1], [0, 1]

    try:
        kaxe.thin_points(x, y)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Exactly one" in str(exc)

    try:
        kaxe.thin_points(x, y, every=2, max_points=10)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Exactly one" in str(exc)


@unit()
def test_thin_points_pixel_requires_plot():
    """Pixel-space min_distance without plot raises ValueError."""
    x, y = [0, 1, 2], [0, 0, 0]

    try:
        kaxe.thin_points(x, y, min_distance=1, space="pixel")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "plot is required" in str(exc)


@unit()
def test_thin_points_pixel_requires_fixed_bounds():
    """Auto-scaled plot without bounds raises ValueError for pixel thinning."""
    x, y = [0, 1, 2], [0, 0, 0]
    plot = kaxe.Plot()

    try:
        kaxe.thin_points(x, y, min_distance=1, space="pixel", plot=plot)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "fixed axis bounds" in str(exc)
