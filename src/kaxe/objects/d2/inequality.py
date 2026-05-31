
from ...core.shapes import shapes
from ...core.color import to_rgba
from ...core.symbol import symbol
from ...plot import identities
from .equation import Equation

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


class Inequality:
    """
    A class to represent a two-variable inequality ``left op right``.

    Draws the boundary curve (same as :class:`Equation`) and red diagonal
    hatching on the forbidden side of the inequality.

    Supported in classical plots, polar plot and 3D plots as a 2D object with ``z=0``.

    Parameters
    ----------
    left : callable
        Left side of the inequality.
    right : callable
        Right side of the inequality.
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
    computePadding : int, optional
        Extra padding when sampling the plot area (default is 50).

    Examples
    --------
    >>> g = lambda x, y: x + y - 3
    >>> ineq = Inequality(g, lambda x, y: 0)
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
        computePadding=50,
    ):
        self.left = left
        self.right = right
        self.computePadding = computePadding
        self.hatch_spacing = hatch_spacing
        self.hatch_width = hatch_width
        self.hatch_color = to_rgba(hatch_color)

        if op not in _OPS:
            raise ValueError(f"Unsupported operator {op!r}; use one of {sorted(_OPS)}")
        self.op = op
        self._is_forbidden = _OPS[op]

        self.boundary = Equation(left, right, color=color, width=width, computePadding=computePadding)
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

        width = x1 - x0
        height = y1 - y0
        spacing = self.hatch_spacing
        sample_step = 2
        eps = 1e-9

        scale = getattr(parent, 'getVisualScale', lambda: 1.0)()
        hatch_width = max(1, int(self.hatch_width * scale))

        max_extent = int(width + height)
        for offset in range(-int(height), int(width + height), spacing):
            segment_start = None
            last_point = None

            for t in range(0, max_extent, sample_step):
                px = x0 + t
                py = y0 + t + offset

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
