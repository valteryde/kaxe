"""Utilities for reducing large point series before plotting."""

from typing import List, Optional, Sequence, Tuple, Union

import numpy as np

from .helper import isRealNumber


def decimate_by_distance(
    points: Sequence[Tuple[float, float]],
    min_distance: float,
) -> List[Tuple[float, float]]:
    """
    Sequential min-distance filter on a polyline; always keeps endpoints.

    Parameters
    ----------
    points : sequence of (x, y)
        Points in traversal order.
    min_distance : float
        Minimum Euclidean distance between consecutive kept points.
    """
    if min_distance <= 0:
        return list(points)
    if len(points) < 2:
        return list(points)

    result = [points[0]]
    last = points[0]
    min_dist_sq = min_distance * min_distance

    for point in points[1:]:
        dx = point[0] - last[0]
        dy = point[1] - last[1]
        if dx * dx + dy * dy >= min_dist_sq:
            result.append(point)
            last = point

    if result[-1] != points[-1]:
        result.append(points[-1])

    return result


def _decimate_indices_by_distance(
    coords: Sequence[Tuple[float, float]],
    min_distance: float,
) -> List[int]:
    if len(coords) < 2:
        return list(range(len(coords)))

    kept = [0]
    last = coords[0]
    min_dist_sq = min_distance * min_distance

    for i in range(1, len(coords)):
        point = coords[i]
        dx = point[0] - last[0]
        dy = point[1] - last[1]
        if dx * dx + dy * dy >= min_dist_sq:
            kept.append(i)
            last = point

    if kept[-1] != len(coords) - 1:
        kept.append(len(coords) - 1)

    return kept


def _filter_finite(
    x: Sequence,
    y: Sequence,
    z: Optional[Sequence] = None,
) -> Union[Tuple[list, list], Tuple[list, list, list]]:
    cx, cy, cz = [], [], []
    for i in range(len(x)):
        if not (isRealNumber(x[i]) and isRealNumber(y[i])):
            continue
        if z is not None and not isRealNumber(z[i]):
            continue
        cx.append(x[i])
        cy.append(y[i])
        if z is not None:
            cz.append(z[i])

    if z is not None:
        return cx, cy, cz
    return cx, cy


def _thin_every(n: int, every: int) -> List[int]:
    if every <= 0:
        raise ValueError("every must be a positive integer")
    if n == 0:
        return []
    indices = list(range(0, n, every))
    if indices[-1] != n - 1:
        indices.append(n - 1)
    return indices


def _thin_max_points(n: int, max_points: int) -> List[int]:
    if max_points <= 0:
        raise ValueError("max_points must be a positive integer")
    if n <= max_points:
        return list(range(n))

    indices = np.linspace(0, n - 1, max_points, dtype=int)
    kept = []
    seen = set()
    for idx in indices:
        i = int(idx)
        if i not in seen:
            seen.add(i)
            kept.append(i)

    if kept[0] != 0:
        kept.insert(0, 0)
    if kept[-1] != n - 1:
        kept.append(n - 1)

    return kept


def _data_to_pixel(plot, x_val: float, y_val: float) -> Tuple[float, float]:
    width = plot.getAttr("width")
    height = plot.getAttr("height")
    x0, x1, y0, y1 = plot.windowAxis[:4]
    scale_x = width / (x1 - x0)
    scale_y = height / (y1 - y0)
    offset_x = x0 * scale_x
    offset_y = y0 * scale_y
    padding = getattr(plot, "padding", [0, 0, 0, 0])
    px = x_val * scale_x - offset_x + padding[0]
    py = y_val * scale_y - offset_y + padding[1]
    return px, py


def _ensure_plot_ready(plot) -> None:
    if not hasattr(plot, "getAttr"):
        raise ValueError("plot must provide getAttr() for width and height")
    if plot.getAttr("width") is None or plot.getAttr("height") is None:
        raise ValueError("plot must have width and height set (e.g. via theme())")

    window_axis = getattr(plot, "windowAxis", None)
    if window_axis is None or any(v is None for v in window_axis[:4]):
        raise ValueError(
            "plot must have fixed axis bounds (pass explicit window limits to Plot)"
        )


def _pixel_coords(plot, x: Sequence, y: Sequence) -> Tuple[List[int], List[Tuple[float, float]]]:
    _ensure_plot_ready(plot)

    indices = []
    coords = []
    for i, (xi, yi) in enumerate(zip(x, y)):
        px, py = _data_to_pixel(plot, float(xi), float(yi))
        indices.append(i)
        coords.append((px, py))

    return indices, coords


def _subset(indices: List[int], *arrays: Sequence) -> tuple:
    return tuple([arrays[i][j] for j in indices] for i in range(len(arrays)))


def thin_points(
    x,
    y,
    z=None,
    *,
    every: Optional[int] = None,
    min_distance: Optional[float] = None,
    max_points: Optional[int] = None,
    space: str = "data",
    plot=None,
) -> tuple:
    """
    Reduce a large point series before plotting.

    Provide exactly one of ``every``, ``min_distance``, or ``max_points``.

    Parameters
    ----------
    x, y : array-like
        Point coordinates in input order.
    z : array-like, optional
        Optional third coordinate; thinned with the same indices as x and y.
    every : int, optional
        Keep every nth point by index (always keeps first and last).
    min_distance : float, optional
        Keep points at least this far apart. Uses data coordinates by default;
        with ``space="pixel"``, distance is measured in screen pixels.
    max_points : int, optional
        Cap the number of points via uniform index sampling (always keeps
        first and last when possible).
    space : str, optional
        ``"data"`` (default) or ``"pixel"``. Only affects ``min_distance``.
    plot : plot window, optional
        Required when ``space="pixel"`` and ``min_distance`` is set. Must have
        fixed axis bounds and width/height (e.g. ``kaxe.Plot([x0, x1, y0, y1])``
        with ``theme()`` applied).

    Returns
    -------
    tuple
        ``(x, y)`` or ``(x, y, z)`` with the thinned coordinates.
    """
    modes = [
        every is not None,
        min_distance is not None,
        max_points is not None,
    ]
    if sum(modes) != 1:
        raise ValueError("Exactly one of every, min_distance, or max_points must be provided")

    if space not in ("data", "pixel"):
        raise ValueError('space must be "data" or "pixel"')

    if z is None:
        cx, cy = _filter_finite(x, y)
        cz = None
    else:
        cx, cy, cz = _filter_finite(x, y, z)

    n = len(cx)
    if n == 0:
        return (cx, cy, cz) if cz is not None else (cx, cy)

    if every is not None:
        kept = _thin_every(n, every)
    elif max_points is not None:
        kept = _thin_max_points(n, max_points)
    else:
        if min_distance <= 0:
            raise ValueError("min_distance must be positive")
        if space == "pixel":
            if plot is None:
                raise ValueError('plot is required when space="pixel"')
            data_indices, coords = _pixel_coords(plot, cx, cy)
            if len(coords) < 2:
                kept = data_indices
            else:
                local_kept = _decimate_indices_by_distance(coords, min_distance)
                kept = [data_indices[i] for i in local_kept]
        else:
            coords = [(float(cx[i]), float(cy[i])) for i in range(n)]
            kept = _decimate_indices_by_distance(coords, min_distance)

    if cz is not None:
        return _subset(kept, cx, cy, cz)
    return _subset(kept, cx, cy)
