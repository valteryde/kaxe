
import math

from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import symbol as symbols
from ...core.helper import bbox_intersects_box, bbox_overlaps, contour_label_angle
from ...core.text import Text
from ...core.round import koundTeX
from ...plot import identities
from .equation import Equation, trace_contour_polylines
from types import FunctionType
from typing import Optional, Union
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


def _polyline_is_closed(polyline, tolerance=2.0):
    if len(polyline) < 3:
        return False
    dx = polyline[0][0] - polyline[-1][0]
    dy = polyline[0][1] - polyline[-1][1]
    return math.hypot(dx, dy) <= tolerance


def _polyline_total_arc(polyline, closed):
    arc = _polyline_arc_length(polyline)
    if closed:
        dx = polyline[0][0] - polyline[-1][0]
        dy = polyline[0][1] - polyline[-1][1]
        arc += math.hypot(dx, dy)
    return arc


def _point_at_arc_length(polyline, target, closed=False):
    if not polyline:
        return 0, (0, 0)

    total = _polyline_total_arc(polyline, closed)
    if total <= 0:
        return 0, polyline[0]

    if closed:
        target = target % total
    elif target >= total:
        return len(polyline) - 1, polyline[-1]

    walked = 0.0
    segment_count = len(polyline) - 1 + (1 if closed else 0)

    for seg in range(segment_count):
        i = seg if seg < len(polyline) - 1 else len(polyline) - 1
        j = (seg + 1) if seg < len(polyline) - 1 else 0
        dx = polyline[j][0] - polyline[i][0]
        dy = polyline[j][1] - polyline[i][1]
        seg_len = math.hypot(dx, dy)
        if seg_len == 0:
            continue
        if walked + seg_len >= target:
            t = (target - walked) / seg_len
            point = (polyline[i][0] + t * dx, polyline[i][1] + t * dy)
            return i, point
        walked += seg_len

    return len(polyline) - 1, polyline[-1]


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


_LABEL_PHASE_GOLDEN = 0.618033988749895


def _label_candidates(polyline, spacing, max_candidates=None, phase=0.0):
    polyline = _simplify_polyline(polyline)
    if len(polyline) < 2:
        return []

    closed = _polyline_is_closed(polyline)
    arc = _polyline_total_arc(polyline, closed)
    if arc < spacing:
        return []

    num_labels = max(1, int(arc / spacing))
    if max_candidates is not None:
        num_labels = min(num_labels, max_candidates)

    candidates = []
    for k in range(num_labels):
        fraction = (k + 0.5 + phase) / num_labels
        if closed:
            fraction = fraction % 1.0
        elif fraction > 1.0:
            continue
        target = fraction * arc
        index, point = _point_at_arc_length(polyline, target, closed)
        candidates.append((point, index, arc))

    return candidates


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
        Minimum pixel spacing between label candidates along a contour (default is 80).
    labelCollisionPadding : int, optional
        Extra pixel gap required between placed label bounding boxes (default is 4).
    labelMinArc : int, optional
        Minimum polyline arc length to consider for labels (default is labelSpacing).
    labelMaxBranches : int, optional
        Maximum number of polylines per level to label (default is 1).
    labelMaxPerLevel : int, optional
        Maximum labels per contour level (default is 8).
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
        labelSpacing: int = 80,
        labelCollisionPadding: int = 4,
        labelMinArc: Optional[int] = None,
        labelMaxBranches: int = 1,
        labelMaxPerLevel: int = 8,
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
        self.labelCollisionPadding = labelCollisionPadding
        self.labelMinArc = labelSpacing if labelMinArc is None else labelMinArc
        self.labelMaxBranches = labelMaxBranches
        self.labelMaxPerLevel = labelMaxPerLevel
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

    def __collectCandidates__(self, parent):
        candidates = []

        for level_index, (z, eq) in enumerate(self.__equations):
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
                if _polyline_arc_length(_simplify_polyline(polyline)) >= self.labelMinArc
            ][: self.labelMaxBranches]

            for branch_index, polyline in enumerate(polylines):
                simplified = _simplify_polyline(polyline)
                arc = _polyline_arc_length(simplified)
                for candidate_index, (point, index, _) in enumerate(
                    _label_candidates(
                        polyline,
                        self.labelSpacing,
                        max_candidates=self.labelMaxPerLevel,
                        phase=(
                            level_index / max(self.steps, 1)
                            + (level_index * _LABEL_PHASE_GOLDEN) % 1.0
                        ) % 1.0,
                    )
                ):
                    candidates.append({
                        "z": z,
                        "level_index": level_index,
                        "branch_index": branch_index,
                        "candidate_index": candidate_index,
                        "arc": arc,
                        "polyline": polyline,
                        "point": point,
                        "index": index,
                        "label_text": label_text,
                    })

        candidates.sort(
            key=lambda item: (-item["arc"], item["level_index"], item["branch_index"], item["candidate_index"])
        )
        return candidates

    def __finalizeLabels__(self, parent):
        fontSize = parent.getAttr('fontSize')
        collision_padding = max(self.labelCollisionPadding, fontSize // 2)
        placed_bboxes = []
        label_bboxes = []
        placed_per_level = {}

        for candidate in self.__collectCandidates__(parent):
            level_index = candidate["level_index"]
            if placed_per_level.get(level_index, 0) >= self.labelMaxPerLevel:
                continue

            px, py = candidate["point"]
            angle = contour_label_angle(self.func, parent, px, py)
            text = Text(
                candidate["label_text"],
                int(px),
                int(py),
                fontSize=fontSize,
                color=self.labelColor,
                rotate=round(angle),
                anchor_x='center',
                anchor_y='center',
                clip_box=list(parent.windowBox),
            )
            bbox = text.getBoundingBox()
            if not bbox_intersects_box(bbox, parent.windowBox):
                continue

            label_padding = max(
                collision_padding,
                int(max(bbox[2], bbox[3]) * 0.15),
            )

            if any(
                bbox_overlaps(bbox, placed_bbox, label_padding)
                for placed_bbox in placed_bboxes
            ):
                continue

            text.batch = self.batch
            self.batch.add(text)
            placed_bboxes.append(bbox)
            label_bboxes.append(bbox)
            placed_per_level[level_index] = placed_per_level.get(level_index, 0) + 1

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
