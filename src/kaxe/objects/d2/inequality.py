import math

from ...core.shapes import shapes
from ...core.color import to_rgba
from ...core.symbol import symbol
from ...core.helper import isRealNumber
from ...plot import identities
from .equation import Equation, trace_contour_polylines


def _as_2d_expr(expr):
    if isRealNumber(expr):
        value = float(expr)
        return lambda x, y, _v=value: _v
    return expr

_OPS = {
    '<=': lambda d: d > 0,
    'le': lambda d: d > 0,
    '≤': lambda d: d > 0,
    '<': lambda d: d >= 0,
    'lt': lambda d: d >= 0,
    '>=': lambda d: d < 0,
    'ge': lambda d: d < 0,
    '≥': lambda d: d < 0,
    '>': lambda d: d <= 0,
    'gt': lambda d: d <= 0,
}


def _resolve_plot(parent):
    if getattr(parent, 'identity', None) == identities.XYZPLOT:
        from ..._require_3d import require_3d
        require_3d()
        from ...core.d3.translator import getEquivalent2DPlot
        return getEquivalent2DPlot(parent)
    return parent


def _eval_diff(parent, left, right, px, py):
    try:
        x, y = parent.inversepixel(px, py)
        if x is None or y is None:
            return None
        return left(x, y) - right(x, y)
    except (TypeError, ZeroDivisionError, ValueError):
        return None


def _boundary_band_points(boundary, parent):
    points = []
    for polyline in trace_contour_polylines(boundary.dotsPosAbstract, parent):
        points.extend(_decimate_polyline(polyline, min_step=8))
    return points


def _decimate_polyline(polyline, min_step=8):
    if len(polyline) < 2:
        return polyline
    result = [polyline[0]]
    last = polyline[0]
    min_step_sq = min_step * min_step
    for point in polyline[1:]:
        dx = point[0] - last[0]
        dy = point[1] - last[1]
        if dx * dx + dy * dy >= min_step_sq:
            result.append(point)
            last = point
    if result[-1] != polyline[-1]:
        result.append(polyline[-1])
    return result


def _build_band_cells(points, band, x0, y0, x1, y1):
    cell = max(1, int(band / 2))
    reach = band + cell * 0.7071067811865476
    reach_sq = reach * reach
    near = set()

    for px, py in points:
        ci0 = int((px - reach - x0) // cell)
        ci1 = int((px + reach - x0) // cell)
        ri0 = int((py - reach - y0) // cell)
        ri1 = int((py + reach - y0) // cell)

        for ci in range(ci0, ci1 + 1):
            cx = x0 + ci * cell + cell * 0.5
            for ri in range(ri0, ri1 + 1):
                cy = y0 + ri * cell + cell * 0.5
                dx = cx - px
                dy = cy - py
                if dx * dx + dy * dy <= reach_sq:
                    near.add((ci, ri))

    return cell, near, x0, y0


def _point_in_band_cells(px, py, cell, near, origin_x, origin_y):
    ci = int((px - origin_x) // cell)
    ri = int((py - origin_y) // cell)
    return (ci, ri) in near


class Inequality:
    """
    A class to represent a two-variable inequality ``left op right``.

    Draws the boundary curve (same as :class:`Equation`) and red diagonal
    hatching on the forbidden side of the inequality.

    Supported in classical plots, polar plot and 3D plots as a 2D object with ``z=0``.

    Parameters
    ----------
    left : callable or real
        Left side of the inequality. A real number is treated as constant in ``x`` and ``y``.
    right : callable or real
        Right side of the inequality. A real number is treated as constant in ``x`` and ``y``.
    op : str, optional
        Comparison operator: ``<=``, ``<``, ``>=``, or ``>`` (default is ``<=``).
    color : tuple | list, optional
        Boundary line color. Random if omitted.
    width : int, optional
        Boundary line thickness (default is 2).
    hatch_color : tuple | list, optional
        Color of forbidden-region hatching (default is red with transparency).
    hatch_spacing : int, optional
        Pixel spacing between parallel hatch lines (default is 10).
    hatch_width : int, optional
        Hatch line thickness (default is 1).
    hatch_angle : float, optional
        Hatch line angle in degrees, measured counter-clockwise from the
        horizontal axis (default is 45).
    hatch_band : float, optional
        Maximum pixel distance from the boundary to draw hatching. When
        omitted, the entire forbidden side is hatched.
    computePadding : int, optional
        Extra padding when sampling the plot area (default is 50).

    Examples
    --------
    >>> g = lambda x, y: x + y - 3
    >>> ineq = Inequality(g, 0)
    >>> plt.add(ineq)
    """

    def __init__(
        self,
        left,
        right,
        op='<=',
        color=None,
        width=2,
        hatch_color=(255, 0, 0, 180),
        hatch_spacing=10,
        hatch_width=1,
        hatch_angle=45,
        hatch_band=None,
        computePadding=50,
    ):
        self.left = _as_2d_expr(left)
        self.right = _as_2d_expr(right)
        self.computePadding = computePadding
        self.hatch_spacing = hatch_spacing
        self.hatch_width = hatch_width
        self.hatch_angle = hatch_angle
        self.hatch_band = hatch_band
        self.hatch_color = to_rgba(hatch_color)

        if op not in _OPS:
            raise ValueError(f"Unsupported operator {op!r}; use one of {sorted(_OPS)}")
        self.op = op
        self._is_forbidden = _OPS[op]

        self.boundary = Equation(self.left, self.right, color=color, width=width, computePadding=computePadding)
        self.hatch_batch = shapes.Batch()
        self.color = self.boundary.color
        self.legendColor = self.boundary.legendColor
        self.width = width

        self.supports = [identities.XYPLOT, identities.POLAR, identities.XYZPLOT]

    def __build_hatch__(self, parent):
        box = parent.windowBox
        x0 = box[0] - self.computePadding
        x1 = box[2] + self.computePadding
        y0 = box[1] - self.computePadding
        y1 = box[3] + self.computePadding

        spacing = self.hatch_spacing
        sample_step = 2
        eps = 1e-9

        band_cells = None
        if self.hatch_band is not None:
            boundary_points = _boundary_band_points(self.boundary, parent)
            if not boundary_points:
                return
            band_cells = _build_band_cells(
                boundary_points, self.hatch_band, x0, y0, x1, y1
            )

        scale = getattr(parent, 'getVisualScale', lambda: 1.0)()
        hatch_width = max(1, int(self.hatch_width * scale))

        angle_rad = math.radians(self.hatch_angle)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        nx = -dy
        ny = dx

        corners = ((x0, y0), (x1, y0), (x0, y1), (x1, y1))
        normal_proj = [nx * cx + ny * cy for cx, cy in corners]
        o_min = int(min(normal_proj)) - spacing
        o_max = int(max(normal_proj)) + spacing

        for o in range(o_min, o_max + 1, spacing):
            segment_start = None
            last_point = None

            base_x = x0 + o * nx
            base_y = y0 + o * ny
            t_values = []
            for cx, cy in corners:
                if abs(dx) > 1e-9:
                    t_values.append((cx - base_x) / dx)
                if abs(dy) > 1e-9:
                    t_values.append((cy - base_y) / dy)
            if not t_values:
                continue
            t_start = int(min(t_values)) - 1
            t_end = int(max(t_values)) + 1

            for t in range(t_start, t_end, sample_step):
                px = base_x + t * dx
                py = base_y + t * dy

                if px < x0 or px > x1 or py < y0 or py > y1:
                    if segment_start is not None and last_point is not None:
                        self.__add_hatch_segment__(segment_start, last_point, hatch_width)
                    segment_start = None
                    last_point = None
                    continue

                if not parent.inside(px, py):
                    if segment_start is not None and last_point is not None:
                        self.__add_hatch_segment__(segment_start, last_point, hatch_width)
                    segment_start = None
                    last_point = None
                    continue

                in_band = True
                if band_cells is not None:
                    cell, near, origin_x, origin_y = band_cells
                    in_band = _point_in_band_cells(px, py, cell, near, origin_x, origin_y)

                diff = _eval_diff(parent, self.left, self.right, px, py)
                if diff is None:
                    if segment_start is not None and last_point is not None:
                        self.__add_hatch_segment__(segment_start, last_point, hatch_width)
                    segment_start = None
                    last_point = None
                    continue

                if abs(diff) < eps:
                    # On the boundary: skip without breaking an open segment so
                    # hatching stays continuous past axis intercepts and corners.
                    continue

                forbidden = self._is_forbidden(diff)

                if forbidden:
                    if not in_band:
                        if segment_start is not None and last_point is not None:
                            self.__add_hatch_segment__(segment_start, last_point, hatch_width)
                        segment_start = None
                        last_point = None
                        continue
                    point = (px, py)
                    if segment_start is None:
                        segment_start = point
                    last_point = point
                elif segment_start is not None and last_point is not None:
                    self.__add_hatch_segment__(segment_start, last_point, hatch_width)
                    segment_start = None
                    last_point = None

            if segment_start is not None and last_point is not None:
                self.__add_hatch_segment__(segment_start, last_point, hatch_width)

    def __add_hatch_segment__(self, start, end, hatch_width):
        if start == end:
            return
        shapes.Line(
            start[0],
            start[1],
            end[0],
            end[1],
            color=self.hatch_color,
            width=hatch_width,
            batch=self.hatch_batch,
        )

    def finalize(self, parent):
        from ..._require_3d import require_3d
        from ...core.d3.translator import translate2DTo3DObjects, has3DReference

        plot = _resolve_plot(parent)
        self.boundary.finalize(plot)
        self.__build_hatch__(plot)

        if has3DReference(plot):
            require_3d()
            translate2DTo3DObjects(plot, self.hatch_batch)

    def push(self, x, y):
        self.hatch_batch.push(x, y)
        self.boundary.push(x, y)

    def draw(self, *args, **kwargs):
        self.hatch_batch.draw(*args, **kwargs)
        self.boundary.draw(*args, **kwargs)

    def legend(self, text: str, symbol=symbol.LINE, color=None):
        """
        Adds a legend entry for this inequality.

        Parameters
        ----------
        text : str
            The text to display in the legend.
        symbol : symbols, optional
            The symbol to use in the legend.
        color : optional
            Legend color. Uses the boundary color if omitted.

        Returns
        -------
        self
        """
        self.legendText = text
        self.legendSymbol = symbol
        if color:
            self.legendColor = to_rgba(color)
        return self
