"""Curve from stored x/y samples (reload of exported Function2D)."""

from __future__ import annotations

from ..core.shapes import shapes
from ..core.helper import isRealNumber
from ..plot import identities


class SampledCurve2D:
    """Line curve from project file samples; preserves line style metadata."""

    def __init__(
        self,
        x,
        y,
        color,
        thickness=10,
        dotted=0,
        dashed=0,
    ):
        self.x = list(x)
        self.y = list(y)
        self.color = color
        self.thickness = thickness
        self.dotted = dotted
        self.dashed = dashed
        self.batch = shapes.Batch()
        self.supports = [identities.XYPLOT, identities.POLAR, identities.LOGPLOT]
        self.legendColor = color

    def finalize(self, parent):
        self.lineSegments = [[]]
        last = None
        for x, y in zip(self.x, self.y):
            if not (isRealNumber(x) and isRealNumber(y)):
                continue
            px, py = parent.pixel(x, y)
            if not px or not py:
                continue
            pt = parent.clamp(px, py)
            if last is None:
                last = [px, py]
                continue
            if parent.inside(px, py) or parent.inside(*last):
                self.lineSegments[-1].append(parent.clamp(last[0], last[1]))
                self.lineSegments[-1].append(pt)
            else:
                self.lineSegments.append([])
            last = [px, py]

        scale = getattr(parent, "getVisualScale", lambda: 1.0)()
        width = max(1, int(self.thickness * scale))
        for segment in self.lineSegments:
            if len(segment) < 2:
                continue
            shapes.LineSegment(
                segment,
                color=self.color,
                width=width,
                batch=self.batch,
                dotted=self.dotted > 0,
                dashed=self.dashed > 0,
                dashedDist=self.dashed,
                dottedDist=self.dotted,
            )

    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)

    def push(self, *args, **kwargs):
        self.batch.push(*args, **kwargs)

    def legend(self, text, symbol=None, color=None):
        from ..core.symbol import symbol as symbols

        self.legendText = text
        self.legendSymbol = symbol if symbol else symbols.LINE
        if color is not None:
            from ..core.color import to_rgba
            self.legendColor = to_rgba(color)
        return self
