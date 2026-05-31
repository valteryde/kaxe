"""Sample callable curves for project export."""

from __future__ import annotations

import math
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from ..core.bounds import (
    DEFAULT_DOMAIN_1D,
    resolve_interval,
)
from ..core.helper import isRealNumber
from ..plot import identities


def sample_curve(
    f: Callable,
    *,
    domain: Optional[Sequence[float]],
    window_axis,
    plot_identity: Optional[str],
    first_axis_log: bool = False,
    n: int = 2000,
    args: tuple = (),
    kwargs: dict = None,
) -> Tuple[List[float], List[float]]:
    """
    Sample f(x) on a uniform grid for project storage.

    Returns parallel x, y lists (finite points only).
    """
    kwargs = kwargs or {}
    wa = list(window_axis or [None, None, None, None])
    while len(wa) < 4:
        wa.append(None)

    default_x = (0.01, 10.0) if first_axis_log else DEFAULT_DOMAIN_1D
    x0, x1 = resolve_interval(domain, wa[0], wa[1], default_x)
    if first_axis_log and x0 <= 0:
        x0 = 0.01
    if x0 == x1:
        x0 -= 0.5
        x1 += 0.5

    xs = np.linspace(x0, x1, n)
    x_out, y_out = [], []

    if plot_identity == identities.POLAR:
        fidelity = max(n, 360)
        for angle_deg in range(0, 360 * 100, max(1, 360 * 100 // fidelity)):
            angle = math.radians(angle_deg / 100.0)
            try:
                r = f(angle, *args, **kwargs)
            except Exception:
                continue
            if isRealNumber(r):
                x_out.append(float(angle))
                y_out.append(float(r))
        return x_out, y_out

    for x in xs:
        try:
            y = f(float(x), *args, **kwargs)
        except Exception:
            continue
        if isRealNumber(y) and math.isfinite(float(y)):
            x_out.append(float(x))
            y_out.append(float(y))

    return x_out, y_out
