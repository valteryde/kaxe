
import math

from .shapes import Batch, Line, Shape, shapes


class SymbolGroup(Shape):
    """Composite symbol built from shapes in a size×size local box."""

    def __init__(self, size: int, parts: list, batch: Batch = None):
        self.size = int(size)
        self.parts = parts
        self.x = 0
        self.y = 0
        self.batch = batch
        super().__init__()
        if batch:
            batch.add(self)

    def getBoundingBox(self):
        return [self.size, self.size]

    def centerAlign(self):
        self.x -= self.size / 2
        self.y -= self.size / 2

    def push(self, x, y):
        self.x += x
        self.y += y

    def _offset_part(self, part, dx, dy):
        if isinstance(part, Line):
            part.push(dx, dy)
        else:
            part.x += dx
            part.y += dy

    def _restore_part(self, part, dx, dy):
        if isinstance(part, Line):
            part.push(-dx, -dy)
        else:
            part.x -= dx
            part.y -= dy

    def _draw_parts(self, draw_fn):
        for part in self.parts:
            self._offset_part(part, self.x, self.y)
            draw_fn(part)
            self._restore_part(part, self.x, self.y)

    def drawPillow(self, surface):
        self._draw_parts(lambda part: part.drawPillow(surface))

    def drawSvg(self, doc):
        self._draw_parts(lambda part: part.drawSvg(doc))


# SYMBOLS
class symbol:
    CIRCLE = 'o'
    LINE = 'LINE'
    TRIANGLE = 'TRI'
    STAR = 'STAR'
    RECTANGLE = "RECT"
    LOLLIPOP = 'LOLLIPOP'
    THICKLINE = 'THICKLINE'
    CROSS = "CROSS"
    DONUT = "DONUT"


def _triangle_symbol(size: int, color: tuple, batch: Batch):
    return SymbolGroup(
        size,
        [shapes.Polygon((size / 2, 0), (0, size), (size, size), color=color, batch=None)],
        batch=batch,
    )


def _star_symbol(size: int, color: tuple, batch: Batch):
    cx = cy = size / 2
    outer_r = size / 2
    inner_r = outer_r * 0.4
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = outer_r if i % 2 == 0 else inner_r
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    return SymbolGroup(size, [shapes.Polygon(*points, color=color, batch=None)], batch=batch)


def _cross_symbol(size: int, color: tuple, batch: Batch):
    thickness = max(1, int(size / 6))
    parts = [
        Line(0, 0, size, size, color=color, width=thickness, batch=None),
        Line(size, 0, 0, size, color=color, width=thickness, batch=None),
    ]
    return SymbolGroup(size, parts, batch=batch)


def _lollipop_symbol(size: int, color: tuple, batch: Batch):
    stem_h = max(1, size // 4)
    stem_y = (size - stem_h) // 2
    head_r = max(1, size // 3)
    stem_w = max(1, size - head_r)
    parts = [
        shapes.Rectangle(0, stem_y, stem_w, stem_h, color=color, batch=None),
        shapes.Circle(size - head_r, size // 2, head_r, color=color, batch=None, cornerAlign=False),
    ]
    return SymbolGroup(size, parts, batch=batch)


def makeSymbolShapes(symb: str, height: int, color: tuple, batch):
    size = int(height)
    if symb == symbol.LINE:
        return shapes.Rectangle(0, 0, size, size / 6, color=color, batch=batch)
    if symb == symbol.THICKLINE:
        return shapes.Rectangle(0, 0, size, size / 2, color=color, batch=batch)
    if symb == symbol.RECTANGLE:
        return shapes.Rectangle(0, 0, size, size, color=color, batch=batch)
    if symb == symbol.CIRCLE:
        return shapes.Circle(0, 0, int(size / 2), cornerAlign=True, color=color, batch=batch)
    if symb == symbol.TRIANGLE:
        return _triangle_symbol(size, color, batch)
    if symb == symbol.STAR:
        return _star_symbol(size, color, batch)
    if symb == symbol.LOLLIPOP:
        return _lollipop_symbol(size, color, batch)
    if symb == symbol.CROSS:
        return _cross_symbol(size, color, batch)
    if symb == symbol.DONUT:
        return shapes.Circle(
            0,
            0,
            int(size / 2),
            cornerAlign=True,
            fill=False,
            width=max(1, size // 8),
            color=color,
            batch=batch,
        )
