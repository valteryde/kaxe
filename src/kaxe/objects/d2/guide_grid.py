
from math import cos, sin, radians
from ...core.styles import *
from ...core.color import to_rgba
from ...core.shapes import shapes
from ...core.text import Text
from ...core.helper import *
from ...plot import identities


def _angles_to_draw(angles, symmetric):
    if not angles:
        return []
    result = []
    seen = set()
    for angle in angles:
        for a in (angle, -angle) if symmetric else (angle,):
            key = round(a % 360, 6)
            if key not in seen:
                seen.add(key)
                result.append(a)
    return result


def _border_point_in_direction(parent, center, angle_deg):
    rad = radians(angle_deg)
    n = (cos(rad), sin(rad))
    p1, p2 = parent.pointOnWindowBorderFromLine(center, n)
    pc = parent.pixel(*center)
    best = p1
    best_dot = float('-inf')
    for p in (p1, p2):
        d = (p[0] - pc[0], p[1] - pc[1])
        dot = d[0] * n[0] * parent.scale[0] + d[1] * n[1] * parent.scale[1]
        if dot > best_dot:
            best_dot = dot
            best = p
    return best


class PolarGuideGrid:
    """Polar-style guide overlay on a Cartesian plot.

    Draws concentric circles or arcs and radial lines through a configurable
    center in data coordinates. Useful for s-plane root locus plots and other
    diagrams that combine Cartesian axes with polar guide geometry.

    Parameters
    ----------
    center : tuple
        Guide origin ``(x, y)`` in data coordinates. Default ``(0, 0)``.
    radii : list, optional
        Circle radii in data units. ``None`` skips circles.
    angles : list, optional
        Radial line angles in degrees, CCW from +x. ``None`` skips radials.
    arc_span : tuple, optional
        ``(start_deg, end_deg)`` to draw partial arcs instead of full circles.
    radius_labels : bool or list, optional
        ``True`` labels each radius at the negative-x intersection; or pass
        explicit strings aligned with ``radii``.
    angle_labels : bool or list, optional
        ``True`` labels each angle at the plot border; or pass explicit strings
        aligned with ``angles``.
    radial_extent : str or float, optional
        ``'plot'`` clips radials to the plot border; a float sets a fixed data
        length from ``center``.
    symmetric : bool, optional
        When ``True``, each angle also draws its mirror about the x-axis.
    dashed : bool, optional
        Draw guide lines dashed.
    dotted : bool, optional
        Draw guide lines dotted.
    dashed_dist : int, optional
        Pixel spacing between dashes.
    dotted_dist : int, optional
        Pixel spacing between dots.
    color : tuple, optional
        Line color. Defaults to ``Marker.gridlineColor``.
    width : int, optional
        Line width. Defaults to ``Marker.gridlineWidth``.

    Examples
    --------
    >>> plt = kaxe.Plot([-10, 2, -5, 5])
    >>> plt.add(kaxe.PolarGuideGrid(
    ...     radii=[2, 4, 6, 8, 10],
    ...     angles=[120, 135, 150],
    ...     arc_span=(90, 270),
    ...     radius_labels=True,
    ... ))
    """

    def __init__(
        self,
        center=(0, 0),
        radii=None,
        angles=None,
        arc_span=None,
        radius_labels=False,
        angle_labels=False,
        radial_extent='plot',
        symmetric=True,
        dashed=False,
        dotted=False,
        dashed_dist=30,
        dotted_dist=30,
        color=None,
        width=None,
    ):
        self.center = center
        self.radii = list(radii) if radii is not None else None
        self.angles = list(angles) if angles is not None else None
        self.arc_span = arc_span
        self.radius_labels = radius_labels
        self.angle_labels = angle_labels
        self.radial_extent = radial_extent
        self.symmetric = symmetric
        self.dashed = dashed
        self.dotted = dotted
        self.dashed_dist = dashed_dist
        self.dotted_dist = dotted_dist
        self.color = to_rgba(color) if color is not None else None
        self.width = width

        self.batch = shapes.Batch()
        self.texts = []
        self._shape_count = 0
        self.legendColor = self.color or (128, 128, 128, 180)
        self.supports = [identities.XYPLOT]

    def _line_kwargs(self, parent):
        color = self.color
        if color is None:
            color = parent.getAttr('Marker.gridlineColor')
        width = self.width
        if width is None:
            width = parent.getAttr('Marker.gridlineWidth')
        return {
            'color': color,
            'width': width,
            'batch': self.batch,
            'dashed': self.dashed,
            'dotted': self.dotted,
            'dashedDist': self.dashed_dist,
            'dottedDist': self.dotted_dist,
        }

    def _arc_points(self, parent, radius, start_deg, end_deg, n_points=64):
        cx, cy = self.center
        span = end_deg - start_deg
        if span <= 0:
            span += 360
        n = max(8, int(n_points * span / 360))
        points = []
        for i in range(n + 1):
            t = start_deg + span * i / n
            x = cx + radius * cos(radians(t))
            y = cy + radius * sin(radians(t))
            px, py = parent.pixel(x, y)
            if px is None or py is None:
                continue
            if parent.inside(px, py):
                points.append((px, py))
        return points

    def _draw_circle_or_arc(self, parent, radius, line_kw):
        if self.arc_span is None:
            start_deg, end_deg = 0, 360
        else:
            start_deg, end_deg = self.arc_span

        points = self._arc_points(parent, radius, start_deg, end_deg)
        if len(points) < 2:
            return

        if len(points) >= 3 or (self.dashed or self.dotted):
            shapes.LineSegment(points, **line_kw)
        elif len(points) == 2:
            shapes.Line(*points[0], *points[1], **{k: v for k, v in line_kw.items()
                                                      if k not in ('dashed', 'dotted', 'dashedDist', 'dottedDist')})
        self._shape_count += 1

    def _draw_radial(self, parent, angle_deg, line_kw):
        cx, cy = self.center
        rad = radians(angle_deg)
        n = (cos(rad), sin(rad))

        if self.radial_extent == 'plot':
            p1, p2 = parent.pointOnWindowBorderFromLine(self.center, n)
            shapes.Line(*p1, *p2, **{k: v for k, v in line_kw.items()
                                      if k not in ('dashed', 'dotted', 'dashedDist', 'dottedDist')})
        else:
            extent = float(self.radial_extent)
            x0, y0 = cx, cy
            x1, y1 = cx + n[0] * extent, cy + n[1] * extent
            x2, y2 = cx - n[0] * extent, cy - n[1] * extent
            px0, py0 = parent.pixel(x0, y0)
            px1, py1 = parent.pixel(x1, y1)
            px2, py2 = parent.pixel(x2, y2)
            if px0 is not None and px1 is not None:
                shapes.Line(px0, py0, px1, py1, **{k: v for k, v in line_kw.items()
                                                      if k not in ('dashed', 'dotted', 'dashedDist', 'dottedDist')})
            if px0 is not None and px2 is not None:
                shapes.Line(px0, py0, px2, py2, **{k: v for k, v in line_kw.items()
                                                      if k not in ('dashed', 'dotted', 'dashedDist', 'dottedDist')})
        self._shape_count += 1

    def _add_label(self, parent, text, px, py, color, fontsize):
        label = Text(
            str(text),
            px, py,
            fontSize=int(fontsize),
            color=color,
            batch=self.batch,
            anchor_x='center',
            anchor_y='center',
        )
        self.texts.append(label)
        self._shape_count += 1

    def finalize(self, parent):
        line_kw = self._line_kwargs(parent)
        color = line_kw['color']
        fontsize = parent.getAttr('fontSize')

        if self.radii:
            for i, radius in enumerate(self.radii):
                self._draw_circle_or_arc(parent, radius, line_kw)

                if self.radius_labels:
                    if isinstance(self.radius_labels, list):
                        label = self.radius_labels[i]
                    else:
                        label = radius
                    lx = self.center[0] - radius
                    ly = self.center[1]
                    px, py = parent.pixel(lx, ly)
                    if px is not None and parent.inside(px, py):
                        self._add_label(parent, label, px, py, color, fontsize)

        if self.angles:
            draw_angles = _angles_to_draw(self.angles, self.symmetric)
            for angle in draw_angles:
                self._draw_radial(parent, angle, line_kw)

            if self.angle_labels:
                for i, angle in enumerate(self.angles):
                    if isinstance(self.angle_labels, list):
                        label = self.angle_labels[i]
                    else:
                        label = angle
                    px, py = _border_point_in_direction(parent, self.center, angle)
                    if parent.inside(px, py):
                        self._add_label(parent, label, px, py, color, fontsize)
                    if self.symmetric:
                        px, py = _border_point_in_direction(parent, self.center, -angle)
                        if parent.inside(px, py):
                            self._add_label(parent, label, px, py, color, fontsize)

        parent.addDrawingFunction(self.batch, z=1)

    def draw(self, *args, **kwargs):
        pass

    def push(self, x, y):
        self.batch.push(x, y)
