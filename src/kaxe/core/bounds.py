"""Coarse sampling helpers for auto-scaling plot windows from functions."""

import math
from typing import Callable, Optional, Sequence, Tuple

import numpy as np

from .helper import isRealNumber

DEFAULT_DOMAIN_1D = (-10.0, 10.0)
DEFAULT_DOMAIN_2D = (-10.0, 10.0, -10.0, 10.0)
DEFAULT_MARGIN = 0.05
BOUNDS_SAMPLES_1D = 128
BOUNDS_SAMPLES_2D = 32


def is_finite(value) -> bool:
    return isRealNumber(value) and math.isfinite(value)


def apply_margin(lo: float, hi: float, fraction: float = DEFAULT_MARGIN) -> Tuple[float, float]:
    if lo == hi:
        return lo - 1.0, hi + 1.0
    span = hi - lo
    pad = span * fraction
    return lo - pad, hi + pad


def resolve_interval(
    user_domain: Optional[Sequence[float]],
    plot_lo,
    plot_hi,
    default: Tuple[float, float],
) -> Tuple[float, float]:
    if plot_lo is not None and plot_hi is not None:
        return float(plot_lo), float(plot_hi)
    if user_domain is not None:
        return float(user_domain[0]), float(user_domain[1])
    return default


def sample_1d(
    f: Callable,
    x0: float,
    x1: float,
    n: int = BOUNDS_SAMPLES_1D,
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    if x0 == x1:
        x0 -= 0.5
        x1 += 0.5

    xs = np.linspace(x0, x1, n)
    ys = []
    for x in xs:
        try:
            y = f(float(x))
        except Exception:
            continue
        if is_finite(y):
            ys.append(float(y))

    if not ys:
        return None, None, None, None

    return float(x0), float(x1), min(ys), max(ys)


def sample_2d(
    f: Callable,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    n: int = BOUNDS_SAMPLES_2D,
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
]:
    if x0 == x1:
        x0 -= 0.5
        x1 += 0.5
    if y0 == y1:
        y0 -= 0.5
        y1 += 0.5

    xs = np.linspace(x0, x1, n)
    ys = np.linspace(y0, y1, n)
    x_grid, y_grid = np.meshgrid(xs, ys, indexing="ij")

    zs = []
    try:
        z_vals = np.asarray(f(x_grid, y_grid), dtype=np.float64)
        if z_vals.shape == x_grid.shape and np.issubdtype(z_vals.dtype, np.floating):
            for z in z_vals.ravel():
                if is_finite(z):
                    zs.append(float(z))
    except Exception:
        for x in xs:
            for y in ys:
                try:
                    z = f(float(x), float(y))
                except Exception:
                    continue
                if is_finite(z):
                    zs.append(float(z))

    if not zs:
        return None, None, None, None, None, None

    return float(x0), float(x1), float(y0), float(y1), min(zs), max(zs)


def sample_polar_1d(
    f: Callable,
    n: int = BOUNDS_SAMPLES_1D,
) -> Tuple[Optional[float], Optional[float]]:
    rs = []
    for i in range(n):
        theta = 2.0 * math.pi * i / n
        try:
            r = f(theta)
        except Exception:
            continue
        if is_finite(r):
            rs.append(float(r))

    if not rs:
        return None, None

    r_min = min(0.0, min(rs))
    r_max = max(rs)
    return apply_margin(r_min, r_max)


def append_axis_values(values: list, lo, hi):
    if lo is not None:
        values.append(lo)
    if hi is not None:
        values.append(hi)
