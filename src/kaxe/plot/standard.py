
# a simple xy plot
# faster than the true plot

from io import BytesIO
from ..core.helper import *
from ..core.shapes import shapes
from ..core.window import Window
from PIL import Image
import logging
from ..core.axis import *
from .zoom import ZoomInset
from .zoom_connector import connector_placement, compute_render_scale

XYPLOT = 'xy'

class Plot(Window):
    """
    A simple plotting window for cartesian coordinates
    
    Attributes
    ----------
    firstAxis : Kaxe.Axis
        The first axis of the plot.
    secondAxis : Kaxe.Axis
        The second axis of the plot.

    Parameters
    ----------
    window : list
        A list representing the axis window [x0, x1, y0, y1].
    
    Examples
    --------
    >>> import kaxe
    >>> plt = kaxe.Plot()
    >>> plt.add( ... )
    >>> plt.show( )

    """
    
    # en måde at gøre den nemmer at ændre på er at dele tingene op i flere
    # delfunktioner. fx __setAxisPos__ ændres af BoxPlot til altid at have 
    # akserne i nederste hjørne

    def __init__(self,  window:list=None): # |
        super().__init__()
        self.identity = XYPLOT

        """
        window:tuple [x0, x1, y0, y1] axis
        """
        
        # NOTE: Does not really fit into the whole idea of styles
        # but does serve a quality of life function
        self.attrmap.default(attr='xNumbers', value=None)
        self.attrmap.default(attr='yNumbers', value=None)

        self.firstAxis = Axis((1,0), (0,-1), 'xNumbers')
        self.secondAxis = Axis((0,1), (-1,0), 'yNumbers')

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.firstTitle = None
        self.secondTitle = None

        self.zoom_insets = []

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        self._axis_pad_x = 0.0
        self._axis_pad_y = 0.0
        self._last_applied_pad_x = 0.0
        self._last_applied_pad_y = 0.0

        self._axis_pad_rel_x = 0.0
        self._axis_pad_rel_y = 0.0
        self._last_rel_x = 0.0
        self._last_rel_ya = 0.0
        self._last_rel_yb = 0.0

    def pad(self, x=0, y=None, *, relative=False, percent=False):
        """
        Expand the data window symmetrically on each axis (after bounds are resolved).

        Default is **absolute** padding in the same units as the axes. With ``relative=True``,
        ``x`` and ``y`` are fractions of each axis span: the amount added on the low and high
        side is ``fraction * (max - min)``, so ``pad(0.1, relative=True)`` widens x by 20% of
        the original x span (10% on each side). With ``percent=True``, the same rule applies
        but ``x``/``y`` are percents (``pad(10, percent=True)`` equals ``pad(0.1, relative=True)``).

        Relative padding is applied first, then absolute, if you set both.

        For :class:`~kaxe.DoubleAxisPlot`, ``y`` uses each y scale's own span when ``relative``.

        Parameters
        ----------
        x : float, optional
            Padding for x (absolute units, span fraction, or percent). Default 0.
        y : float, optional
            Padding for y (and both y scales on a double-axis plot). If omitted, uses ``x``.
        relative : bool, optional
            If True, ``x``/``y`` are fractions of the axis span(s). Default False.
        percent : bool, optional
            If True, ``x``/``y`` are percents of the span (implies ``relative``). Default False.

        Examples
        --------
        >>> plt.pad(0.05)
        >>> plt.pad(0.1, relative=True)
        >>> plt.pad(5, percent=True)
        """
        if y is None:
            y = x
        if percent:
            relative = True
            x, y = x / 100.0, y / 100.0
        if relative:
            self._axis_pad_rel_x = float(x)
            self._axis_pad_rel_y = float(y)
        else:
            self._axis_pad_x = float(x)
            self._axis_pad_y = float(y)

    def _reverse_relative_padding(self):
        lrx, lrya, lryb = self._last_rel_x, self._last_rel_ya, self._last_rel_yb
        if lrx == 0 and lrya == 0 and lryb == 0:
            return
        wa = self.windowAxis
        wa[0] += lrx
        wa[1] -= lrx
        wa[2] += lrya
        wa[3] -= lrya
        if len(wa) >= 6:
            wa[4] += lryb
            wa[5] -= lryb

    def _reverse_absolute_padding(self):
        lax, lay = self._last_applied_pad_x, self._last_applied_pad_y
        if lax == 0 and lay == 0:
            return
        wa = self.windowAxis
        wa[0] += lax
        wa[1] -= lax
        wa[2] += lay
        wa[3] -= lay
        if len(wa) >= 6:
            wa[4] += lay
            wa[5] -= lay

    def _reverse_axis_padding(self):
        self._reverse_absolute_padding()
        self._reverse_relative_padding()

    def _apply_relative_padding(self):
        wa = self.windowAxis
        rx_f, ry_f = self._axis_pad_rel_x, self._axis_pad_rel_y

        rx = rx_f * (wa[1] - wa[0]) if rx_f else 0.0
        rya = ry_f * (wa[3] - wa[2]) if ry_f else 0.0
        ryb = ry_f * (wa[5] - wa[4]) if ry_f and len(wa) >= 6 else 0.0

        if rx:
            wa[0] -= rx
            wa[1] += rx
        if rya:
            wa[2] -= rya
            wa[3] += rya
        if ryb:
            wa[4] -= ryb
            wa[5] += ryb

        self._last_rel_x = rx
        self._last_rel_ya = rya
        self._last_rel_yb = ryb

    def _apply_absolute_padding(self):
        px, py = self._axis_pad_x, self._axis_pad_y
        if px == 0 and py == 0:
            self._last_applied_pad_x = 0.0
            self._last_applied_pad_y = 0.0
            return
        wa = self.windowAxis
        wa[0] -= px
        wa[1] += px
        wa[2] -= py
        wa[3] += py
        if len(wa) >= 6:
            wa[4] -= py
            wa[5] += py
        self._last_applied_pad_x = px
        self._last_applied_pad_y = py

    def _apply_axis_padding(self):
        self._apply_relative_padding()
        self._apply_absolute_padding()

    def __calculateWindowBorders__(self):
        self._reverse_axis_padding()
        super().__calculateWindowBorders__()
        self._apply_axis_padding()

    def __setAxisPos__(self):
        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3])
        self.offset[0] += self.windowAxis[0] * self.scale[0]
        self.offset[1] += self.windowAxis[2] * self.scale[1]

        if self.secondAxis.hasNull:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],0), self.pixel(self.windowAxis[1],0))

        elif self.secondAxis.endNumber < 0:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[3]), self.pixel(self.windowAxis[1],self.windowAxis[3]))

        else:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[2]))

        self.firstAxis.finalize(self)

        if self.firstAxis.hasNull:
            self.secondAxis.setPos(self.pixel(0,self.windowAxis[2]), self.pixel(0,self.windowAxis[3]))

        elif self.firstAxis.endNumber < 0:
            self.secondAxis.setPos(self.pixel(self.windowAxis[1],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[3]))

        else:
            self.secondAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[0],self.windowAxis[3]))

        self.secondAxis.finalize(self)

    def __prepare__(self):
        # finish making plot
        # fit "plot" into window

        xLength = self.windowAxis[1] - self.windowAxis[0]
        yLength = self.windowAxis[3] - self.windowAxis[2]
        self.scale = [self.width/xLength,self.height/yLength]

        self.__setAxisPos__()

        self.firstAxis.autoAddMarkers(self)
        self.secondAxis.autoAddMarkers(self)

        self.firstAxis.checkCrossOvers(self,self.secondAxis)
        self.secondAxis.checkCrossOvers(self, self.firstAxis)

        if self.firstTitle: self.firstAxis.addTitle(self.firstTitle, self)
        if self.secondTitle: self.secondAxis.addTitle(self.secondTitle, self)

    def __addInnerContent__(self):
        """Bake zoom insets first (with main content when includeMain), then main content."""
        self.__zoom_surfaces__ = []
        for zoom in self.zoom_insets:
            surface = self.__bakeZoomInset__(zoom)
            self.__zoom_surfaces__.append((zoom, surface))
        # Clear batches of main objects before re-finalizing (zoom finalization polluted them)
        if self.zoom_insets and any(z.includeMain for z in self.zoom_insets):
            self.__clearObjectBatches__(self.objects)
        super().__addInnerContent__()

    def __clearObjectBatches__(self, objects):
        """Clear batch.objects and object state so they can be re-finalized cleanly."""
        for obj in objects:
            if hasattr(obj, 'batch') and hasattr(obj.batch, 'objects'):
                obj.batch.objects = []
            if hasattr(obj, 'fillbatch') and hasattr(obj.fillbatch, 'objects'):
                obj.fillbatch.objects = []
            if hasattr(obj, 'points'):
                obj.points = []
            if hasattr(obj, 'lines'):
                obj.lines = []
            if hasattr(obj, 'lineSegments'):
                obj.lineSegments = [[]]

    def __after__(self):
        """Add zoom overlay shapes (image, selection box, connectors)."""
        for zoom, surface in getattr(self, '__zoom_surfaces__', []):
            self.__addZoomOverlay__(zoom, surface)

    def __bakeZoomInset__(self, zoom):
        """Bake zoom plot and return rendered surface. Finalizes main objects with zoom view when includeMain."""
        from .empty import EmptyWindow, EmptyPlot

        inset_w, inset_h = zoom.size
        x0, x1, y0, y1 = zoom.windowAxis
        zoom_x_range = x1 - x0
        zoom_y_range = y1 - y0
        main_x_range = self.windowAxis[1] - self.windowAxis[0]
        main_y_range = self.windowAxis[3] - self.windowAxis[2]

        zoom_plot_render_scale = compute_render_scale(
            self.width, self.height, main_x_range, main_y_range,
            inset_w, inset_h, zoom_x_range, zoom_y_range,
        )

        zoom_plot = EmptyPlot(zoom.windowAxis) if zoom.showAxes else EmptyWindow(zoom.windowAxis)
        zoom_plot.renderScale = zoom_plot_render_scale
        zoom_plot.showProgressBar = False
        zoom_plot.printDebugInfo = False
        zoom_plot.showLegend = False
        zoom_plot.style({
            'axis.showArrow': False,
            'marker.showLine': True,
            'xNumbers': 5,
            'yNumbers': 5,
        })
        zoom_plot.attrmap.setAttr('width', inset_w)
        zoom_plot.attrmap.setAttr('height', inset_h)
        zoom_plot.attrmap.setAttr('outerPadding', (0, 0, 0, 0))
        zoom_plot.attrmap.setAttr('fontSize', max(1, int(self.getAttr('fontSize') * 0.6)))
        zoom_plot.attrmap.setAttr('backgroundColor', self.getAttr('backgroundColor'))
        zoom_plot.attrmap.setAttr('color', self.getAttr('color'))

        if zoom.includeMain:
            for obj in self.objects:
                zoom_plot.add(obj)
        for obj in zoom.objects:
            zoom_plot.add(obj)

        zoom_plot.__bake__()
        return zoom_plot.__paint__(BytesIO())

    def __addZoomOverlay__(self, zoom, zoom_surface):
        """Add overlay shapes for a zoom inset."""
        inset_w, inset_h = zoom.size
        surf_w = zoom_surface.width
        surf_h = zoom_surface.height
        margin = zoom.margin
        x0, x1, y0, y1 = zoom.windowAxis[:4]
        pos = zoom.position

        # Inset position (bottom-left corner in plot coords; ImageShape uses y as bottom)
        if isinstance(pos, (tuple, list)) and len(pos) >= 2:
            # Data coordinates: (x, y) for bottom-left corner of inset
            inset_x, inset_y = self.pixel(pos[0], pos[1])
        elif pos == 'top-left':
            inset_x = self.padding[0] + margin
            inset_y = self.padding[1] + self.height - surf_h - margin
        elif pos == 'top-right':
            inset_x = self.padding[0] + self.width - surf_w - margin
            inset_y = self.padding[1] + self.height - surf_h - margin
        elif pos == 'bottom-left':
            inset_x = self.padding[0] + margin
            inset_y = self.padding[1] + margin
        else:
            inset_x = self.padding[0] + self.width - surf_w - margin
            inset_y = self.padding[1] + margin

        # Selection box corners (data -> pixel)
        px0, py0 = self.pixel(x0, y0)
        px1, py1 = self.pixel(x1, y1)
        sel_left = min(px0, px1)
        sel_right = max(px0, px1)
        sel_bottom = min(py0, py1)
        sel_top = max(py0, py1)

        # Zoom overlay: draw on top of everything (z=1000)
        Z_ZOOM = 1000
        # Zoom image (y is bottom in plot coords)
        self.addDrawingFunction(shapes.Image(zoom_surface, int(inset_x), int(inset_y)), z=Z_ZOOM)

        # Inset border (frame)
        border = zoom.selectionBoxColor
        self.addDrawingFunction(shapes.Line(inset_x, inset_y, inset_x + surf_w, inset_y, color=border, width=2), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(inset_x + surf_w, inset_y, inset_x + surf_w, inset_y + surf_h, color=border, width=2), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(inset_x + surf_w, inset_y + surf_h, inset_x, inset_y + surf_h, color=border, width=2), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(inset_x, inset_y + surf_h, inset_x, inset_y, color=border, width=2), z=Z_ZOOM + 1)

        # Selection box outline
        w = zoom.selectionBoxWidth
        c = zoom.selectionBoxColor
        self.addDrawingFunction(shapes.Line(sel_left, sel_bottom, sel_right, sel_bottom, color=c, width=w), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(sel_right, sel_bottom, sel_right, sel_top, color=c, width=w), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(sel_right, sel_top, sel_left, sel_top, color=c, width=w), z=Z_ZOOM + 1)
        self.addDrawingFunction(shapes.Line(sel_left, sel_top, sel_left, sel_bottom, color=c, width=w), z=Z_ZOOM + 1)

        # Connector lines: 2 lines - connect the edge of selection that faces the inset
        # to the corresponding edge of the inset. Use connectorCorners to override: "left-right",
        # "right-left", "left-left", "right-right", or "auto" for automatic.
        if zoom.connectorLines:
            lc = zoom.connectorColor
            lw = zoom.connectorWidth
            sel_bl = (sel_left, sel_bottom)
            sel_br = (sel_right, sel_bottom)
            sel_tr = (sel_right, sel_top)
            sel_tl = (sel_left, sel_top)
            ins_bl = (inset_x, inset_y)
            ins_br = (inset_x + surf_w, inset_y)
            ins_tr = (inset_x + surf_w, inset_y + surf_h)
            ins_tl = (inset_x, inset_y + surf_h)
            corners = zoom.connectorCorners
            if corners == "auto":
                mode = connector_placement(
                    inset_x, inset_y, surf_w, surf_h,
                    sel_left, sel_right, sel_bottom, sel_top, pos
                )
                if mode == "right":
                    # Inset to the right: top right-right, bottom left-left (avoids crossing)
                    self.addDrawingFunction(shapes.Line(sel_tr[0], sel_tr[1], ins_tr[0], ins_tr[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    self.addDrawingFunction(shapes.Line(sel_bl[0], sel_bl[1], ins_bl[0], ins_bl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    corners = None  # already drawn
                elif mode == "left":
                    # Inset to the left: top right-left, bottom right-left (avoids crossing)
                    self.addDrawingFunction(shapes.Line(sel_tr[0], sel_tr[1], ins_tl[0], ins_tl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    self.addDrawingFunction(shapes.Line(sel_br[0], sel_br[1], ins_bl[0], ins_bl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    corners = None  # already drawn
                elif mode == "vertical":
                    # Inset above or below: connect corresponding corners (top-to-top, bottom-to-bottom)
                    self.addDrawingFunction(shapes.Line(sel_tl[0], sel_tl[1], ins_tl[0], ins_tl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    self.addDrawingFunction(shapes.Line(sel_tr[0], sel_tr[1], ins_tr[0], ins_tr[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    self.addDrawingFunction(shapes.Line(sel_bl[0], sel_bl[1], ins_bl[0], ins_bl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    self.addDrawingFunction(shapes.Line(sel_br[0], sel_br[1], ins_br[0], ins_br[1], color=lc, width=lw), z=Z_ZOOM + 1)
                    corners = None  # already drawn
                else:
                    corners = "left-right"  # mode == "left-right"
            if corners == "right-left":
                self.addDrawingFunction(shapes.Line(sel_tr[0], sel_tr[1], ins_tl[0], ins_tl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                self.addDrawingFunction(shapes.Line(sel_br[0], sel_br[1], ins_bl[0], ins_bl[1], color=lc, width=lw), z=Z_ZOOM + 1)
            elif corners == "left-right":
                self.addDrawingFunction(shapes.Line(sel_tl[0], sel_tl[1], ins_tr[0], ins_tr[1], color=lc, width=lw), z=Z_ZOOM + 1)
                self.addDrawingFunction(shapes.Line(sel_bl[0], sel_bl[1], ins_br[0], ins_br[1], color=lc, width=lw), z=Z_ZOOM + 1)
            elif corners == "left-left":
                self.addDrawingFunction(shapes.Line(sel_tl[0], sel_tl[1], ins_tl[0], ins_tl[1], color=lc, width=lw), z=Z_ZOOM + 1)
                self.addDrawingFunction(shapes.Line(sel_bl[0], sel_bl[1], ins_bl[0], ins_bl[1], color=lc, width=lw), z=Z_ZOOM + 1)
            elif corners == "right-right":
                self.addDrawingFunction(shapes.Line(sel_tr[0], sel_tr[1], ins_tr[0], ins_tr[1], color=lc, width=lw), z=Z_ZOOM + 1)
                self.addDrawingFunction(shapes.Line(sel_br[0], sel_br[1], ins_br[0], ins_br[1], color=lc, width=lw), z=Z_ZOOM + 1)

    def zoom(
        self,
        x0: float = None,
        x1: float = None,
        y0: float = None,
        y1: float = None,
        position: str = "top-left",
        size: tuple = (400, 300),
        showAxes: bool = True,
        connectorLines: bool = True,
        connectorCorners: str = "auto",
        includeMain: bool = True,
        margin: int = 20,
        selectionBoxWidth: int = 3,
        selectionBoxColor: tuple = (0, 0, 0, 255),
        connectorWidth: int = 2,
        connectorColor: tuple = (0, 0, 0, 255),
    ):
        """
        Create a zoom inset (magnifying glass) showing a magnified view of a region.
        Returns a linked subplot where objects added via zoom.add() appear only in the inset.

        Parameters
        ----------
        x0, x1, y0, y1 : float
            Data coordinates of the zoom region. Can also pass as zoom([x0, x1, y0, y1]).
        position : str or tuple, optional
            Preset: 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
            Or (x, y) in data coordinates for the bottom-left corner of the inset.
            Default 'top-left'.
        size : tuple, optional
            (width, height) of inset in pixels. Default (400, 300).
        showAxes : bool, optional
            Whether to show axes in the inset. Default True.
        connectorLines : bool, optional
            Whether to draw connector lines. Default True.

        Returns
        -------
        ZoomInset
            Plot-like object with .add() for inset-only content.

        Examples
        --------
        >>> zoom = plt.zoom(620, 740, 4.4, 5.2)
        >>> zoom.add(kaxe.Points2D([680], [4.8]))
        """
        if x1 is None and y0 is None and y1 is None and isinstance(x0, (list, tuple)):
            region = x0
            x0, x1, y0, y1 = region[0], region[1], region[2], region[3]
        inset = ZoomInset(
            self, x0, x1, y0, y1,
            position=position,
            size=size,
            showAxes=showAxes,
            connectorLines=connectorLines,
            connectorCorners=connectorCorners,
            includeMain=includeMain,
            margin=margin,
            selectionBoxWidth=selectionBoxWidth,
            selectionBoxColor=selectionBoxColor,
            connectorWidth=connectorWidth,
            connectorColor=connectorColor,
        )
        self.zoom_insets.append(inset)
        return inset

    # special api
    def title(self, first=None, second=None):
        """
        Adds title to the plot.
        
        Parameters
        ----------
        first : str, optional
            Title for the first axis.
        second : str, optional
            Title for the second axis.

        Returns
        -------
        Kaxe.Plot
            The active plotting window
        
        """

        self.firstTitle = first
        self.secondTitle = second
        return self


    # more translations
    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        # x -= self.firstAxis.offset
        # y -= self.secondAxis.offset

        return self.translate(x,y)


    def inversepixel(self, x:int, y:int):
        """
        para: pixel values according to axis
        return abstract value
        """
        return self.inversetranslate(x,y)
