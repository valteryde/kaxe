
import math

from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import symbol as symbols
from ...core.helper import contour_label_angle
from ...core.text import Text
from ...core.round import koundTeX
from ...plot import identities
from .equation import Equation, trace_contour_polylines
from types import FunctionType
from typing import Union
from ...core.color import Colormaps, Colormap, to_rgba


def _format_contour_level(z, a, b, steps):
    step_size = abs(b - a) / steps if steps else abs(b - a)
    if step_size > 0:
        digits = max(4, int(-math.log10(step_size)) + 2)
    else:
        digits = 4
    return str(koundTeX(round(z, digits)))


def _polyline_arc_length(polyline):
    total = 0.0
    for i in range(1, len(polyline)):
        dx = polyline[i][0] - polyline[i - 1][0]
        dy = polyline[i][1] - polyline[i - 1][1]
        total += math.hypot(dx, dy)
    return total


def _simplify_polyline(polyline):
    if not polyline:
        return []

    simplified = [polyline[0]]
    for point in polyline[1:]:
        if point != simplified[-1]:
            simplified.append(point)

    if len(simplified) > 2 and simplified[0] == simplified[-1]:
        simplified.pop()

    return simplified


def _point_at_arc_length(polyline, target):
    if not polyline:
        return 0, (0, 0)

    if target <= 0:
        return 0, polyline[0]

    walked = 0.0
    for i in range(1, len(polyline)):
        dx = polyline[i][0] - polyline[i - 1][0]
        dy = polyline[i][1] - polyline[i - 1][1]
        seg_len = math.hypot(dx, dy)
        if seg_len == 0:
            continue
        if walked + seg_len >= target:
            t = (target - walked) / seg_len
            px = polyline[i - 1][0] + t * dx
            py = polyline[i - 1][1] + t * dy
            return i, (px, py)
        walked += seg_len

    return len(polyline) - 1, polyline[-1]


def _closest_polyline_index(polyline, point):
    best_index = 0
    best_dist = float('inf')
    for i, (px, py) in enumerate(polyline):
        dist = (px - point[0]) ** 2 + (py - point[1]) ** 2
        if dist < best_dist:
            best_dist = dist
            best_index = i
    return best_index


def _label_positions(polyline, spacing, max_labels=2):
    polyline = _simplify_polyline(polyline)
    if len(polyline) < 2:
        return []

    arc = _polyline_arc_length(polyline)
    if arc < spacing:
        return []

    num_labels = min(max_labels, max(1, int(arc / spacing)))
    positions = []
    for k in range(num_labels):
        target = (k + 0.5) * arc / num_labels
        index, point = _point_at_arc_length(polyline, target)
        positions.append((point, _closest_polyline_index(polyline, point)))

    return positions


def _point_in_expanded_bbox(x, y, bbox, padding):
    left, top, width, height = bbox
    return (
        left - padding <= x <= left + width + padding
        and top - padding <= y <= top + height + padding
    )


class Contour:
    """
    A class used to represent a Contour.
    
    Parameters
    ----------
    func3D : FunctionType
        A function that represents the 3D function to be contoured.
    a : Union[int, float], optional
        The starting value for the contour range (default is -20).
    b : Union[int, float], optional
        The ending value for the contour range (default is 20).
    steps : Union[int, float], optional
        The number of steps in the contour (default is 15).
    colorMap : Colormap, optional
        The colormap to be used for the contour (default is None, which uses the standard colormap).
    lineThickness : int, optional
        The thickness of the contour lines (default is 10).
    computePadding: int, optional
        When generating the contour equations some padding can be needed to include the edges properly (default is 50).
    label : bool, optional
        Draw inline level labels on contour lines (default is True).
    labelSpacing : int, optional
        Minimum pixel spacing between labels along a contour (default is 100).
    labelColor : tuple, optional
        Color of inline contour labels (default is black).
        
    Examples
    --------
    >>> def example_func(x, y):
    >>>     return x**2 + y**2
    >>> contour = Contour(example_func)
    >>> plt.add(contour)

    """
    
    def __init__(
        self,
        func3D: FunctionType,
        a: Union[int, float] = -20,
        b: Union[int, float] = 20,
        steps: Union[int, float] = 15,
        colorMap: Colormap = None,
        lineThickness: int = 2,
        computePadding: int = 50,
        label: bool = True,
        labelSpacing: int = 100,
        labelColor=(0, 0, 0, 255),
    ):
        self.batch = shapes.Batch()
    
        self.func = func3D
        self.a = a
        self.b = b
        self.steps = steps

        self.lineThickness = lineThickness
        self.label = label
        self.labelSpacing = labelSpacing
        self.labelColor = to_rgba(labelColor)
    
        # color
        if colorMap is None:
            self.color = Colormaps.standard
        else:
            self.color = colorMap
    
        self.legendColor = self.color.getColor(5, -10, 10)

        self.supports = [identities.XYPLOT, identities.POLAR, identities.XYZPLOT]

        self.__equations = []

        self.computePadding = computePadding

    
    def finalize(self, parent):
        plot_parent = parent
        label_parent = parent
        if parent == identities.XYZPLOT:
            from ...core.d3.translator import getEquivalent2DPlot
            label_parent = getEquivalent2DPlot(parent)

        for i in range(self.steps):
            z = self.a + (self.b - self.a) * i / self.steps

            eq = Equation(
                lambda *args, z=z: z,
                self.func,
                color=self.color.getColor(z, self.a, self.b),
                width=self.lineThickness,
                computePadding=self.computePadding,
            )
            eq.finalize(plot_parent)
            self.__equations.append((z, eq))

        if self.label and label_parent == identities.XYPLOT:
            self.__finalizeLabels__(label_parent)

    def __finalizeLabels__(self, parent):
        fontSize = parent.getAttr('fontSize')
        padding = max(2, fontSize // 8)
        label_bboxes = []

        for z, eq in self.__equations:
            label_text = _format_contour_level(z, self.a, self.b, self.steps)
            polylines = trace_contour_polylines(eq.dotsPosAbstract, parent)
            polylines = sorted(
                polylines,
                key=lambda polyline: _polyline_arc_length(_simplify_polyline(polyline)),
                reverse=True,
            )
            polylines = [
                polyline
                for polyline in polylines
                if _polyline_arc_length(_simplify_polyline(polyline)) >= self.labelSpacing
            ][:3]

            for polyline in polylines:
                for point, index in _label_positions(polyline, self.labelSpacing):
                    angle = contour_label_angle(polyline, index)
                    text = Text(
                        label_text,
                        int(point[0]),
                        int(point[1]),
                        fontSize=fontSize,
                        color=self.labelColor,
                        rotate=int(angle),
                        anchor_x='center',
                        anchor_y='center',
                    )

                    left, top = text.getLeftTopPos()
                    shapes.Rectangle(
                        left - padding,
                        top - padding,
                        text.width + 2 * padding,
                        text.height + 2 * padding,
                        color=WHITE,
                        batch=self.batch,
                    )
                    text.batch = self.batch
                    self.batch.add(text)

                    label_bboxes.append(text.getBoundingBox())

        if not label_bboxes:
            return

        suppress_padding = max(4, fontSize // 4)
        for _, eq in self.__equations:
            for dot in eq.dots:
                for bbox in label_bboxes:
                    if _point_in_expanded_bbox(dot.x, dot.y, bbox, suppress_padding):
                        dot.hide()
                        break

    
    def push(self, x, y):
        for _, eq in self.__equations:
            eq.push(x, y)
        self.batch.push(x, y)

    
    def draw(self, surface):
        for _, eq in self.__equations:
            eq.draw(surface)
        self.batch.draw(surface)


    def legend(self, text:str, symbol=symbols.LINE, color=None):
        """
        Adds a legend
        
        Parameters
        ----------
        text : str
            The text to be displayed in the legend.
        symbol : symbols, optional
            The symbol to be used in the legend.
        color : optional
            The color to be used for the legend text. If not provided, the default color will be used.
        
        Returns
        -------
        self : object
            Returns the instance of the arrow object with the updated legend.        
        """

        self.legendText = text
        self.legendSymbol = symbol
        if color:
            self.legendColor = to_rgba(color)
        return self
