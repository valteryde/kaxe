

from ..core.helper import *
import logging
from ..core.axis import *
from ..plot.zoom_connector import compute_boxplot_whiskers
from ..core.styles import isLightOrDark
from ..core.symbol import symbol as symbols
from ..core.symbol import makeSymbolShapes
from ..core.window import Window


def _overlay_y_offset(index, count, box_height, jitter_frac):
    if count <= 1:
        return 0.0
    t = index / (count - 1)
    return (t - 0.5) * jitter_frac * box_height


class BoxPlot(Window):
    """
    Box plot for 1-d data 
    
    Examples
    --------
    >>> import kaxe
    >>> chart = kaxe.BoxPlot()
    >>> chart.add([1,2,3,4])
    >>> chart.add([4,1,6,1,6.3,1,6.2,7,9.1])
    >>> chart.legends('dataset 1', 'dataset 2')
    >>> chart.show()

    """

    def __init__(self): # |
        super().__init__()
        self.identity = 'boxplot'

        self.attrmap.default('titleFontSize', 100)
        self.attrmap.default('width', 3000)
        self.attrmap.default('height', 1500)
        self.attrmap.default('boxGap', ComputedAttribute(lambda m: m.getAttr('width')/100))
        self.attrmap.default('lineWidth', 6)
        self.attrmap.default('axisNumbers', None)
        self.attrmap.default('symbolHeight', ComputedAttribute(lambda m: m.getAttr('lineWidth')*4))
        self.attrmap.default('fill', True)
        self.attrmap.default('lineColor', (0,0,0,255))
        self.attrmap.default('overlayJitter', 0.8)
        self.attrmap.default('showOutliers', True)

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        self.axis = Axis((1,0), (0, -1), 'axisNumbers')

        self.maxNumber = 0
        self.maxNumberAmount = 0
        self.boxplots = []
        self.overlays = []
        self.numberAmount = 0

        self.legendsLabels = []

        self.titleText = None
        self.secondAxisTitle = None
        self.firstAxisTitle = None

   
    def __prepare__(self):

        # get maximum value
        min_, max_ = math.inf, -math.inf
        for boxplot in self.boxplots:
            
            data = boxplot["data"]

            leftbox = np.quantile(data, 0.25)
            rightbox = np.quantile(data, 0.75)
            leftwhisker, rightwhisker = compute_boxplot_whiskers(data)

            min_ = min(min_, *boxplot["data"], leftwhisker, rightwhisker)
            max_ = max(max_, *boxplot["data"], leftwhisker, rightwhisker)

            boxplot["whiskers"] = (leftwhisker, rightwhisker)
            boxplot["quantile"] = (leftbox, rightbox)

        n_boxes = len(self.boxplots)
        for overlay in self.overlays:
            box = overlay["box"]
            if box < 0 or box >= n_boxes:
                raise ValueError(
                    f"overlay box index {box} out of range; expected 0..{n_boxes - 1}"
                )
            if overlay["data"]:
                min_ = min(min_, *overlay["data"])
                max_ = max(max_, *overlay["data"])

        # important styles
        boxHeight = (self.getAttr('height')-self.getAttr('boxGap')*(len(self.boxplots)+1))/len(self.boxplots)
        lineWidth = self.getAttr('lineWidth')
        fill = self.getAttr('fill')
        overlayJitter = self.getAttr('overlayJitter')

        self.axis.addStartAndEnd(min_, max_)

        topPoint = (self.windowBox[0], self.windowBox[3]-self.windowBox[1])
        
        self.axis.setPos(
            (self.windowBox[0], self.windowBox[1]),
            (self.windowBox[2]-self.windowBox[0], self.windowBox[1])
        )

        self.axis.finalize(self)        
        self.axis.autoAddMarkers(self)

        box_geometry = {}
        for user_index, boxplot in enumerate(self.boxplots):
            render_index = n_boxes - 1 - user_index
            median = np.median(boxplot["data"])
            _, y = self.axis.get(median)
            y += self.getAttr('boxGap') * (render_index + 1)
            y0 = render_index * boxHeight + y
            y1 = (render_index + 1) * boxHeight + y
            box_geometry[user_index] = {"centerLine": (y0 + y1) / 2}

        for i, label in enumerate(self.legendsLabels):
            if label: self.legendbox.add(label, color=self.boxplots[i]["color"], symbol=self.boxplots[i]["symbol"])

        for overlay in self.overlays:
            if overlay["legend"]:
                self.legendbox.add(
                    overlay["legend"],
                    color=overlay["color"],
                    symbol=overlay["symbol"],
                )

        self.boxbatch = shapes.Batch()
        self.addDrawingFunction(self.boxbatch)
        
        self.boxplots.reverse()

        # add box plots to window
        for i, boxplot in enumerate(self.boxplots):

            data = boxplot["data"]

            median = np.median(data)
            leftwhisker, rightwhisker = boxplot["whiskers"]
            leftbox, rightbox = boxplot["quantile"]

            x, y = self.axis.get(median)

            y += self.getAttr('boxGap') * (i + 1)

            y0 = i*boxHeight + y
            y1 = (i+1)*boxHeight + y

            # whisker xpos left
            wxl = self.axis.get(leftwhisker)[0]
            
            # whisker xpos right
            wxr = self.axis.get(rightwhisker)[0]

            # connecting line
            centerLine = (y0+y1)/2

            if fill:
                lineColor = self.getAttr('lineColor')
            else: # temp overwrite
                lineColor = boxplot["color"]

            # box coord
            x0 = self.axis.get(leftbox)[0]
            x1 = self.axis.get(rightbox)[0]
            
            # center line
            shapes.Line(wxl, centerLine, x0, centerLine, width=lineWidth, batch=self.boxbatch, color=lineColor)
            shapes.Line(x1, centerLine, wxr, centerLine, width=lineWidth, batch=self.boxbatch, color=lineColor)
            
            if fill: shapes.Rectangle(x0, y0, x1-x0, boxHeight, color=boxplot["color"], batch=self.boxbatch)

            shapes.Line(x0, y0, x1, y0, width=lineWidth, batch=self.boxbatch, color=lineColor)
            shapes.Line(x0, y1, x1, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            shapes.Line(x0, y0, x0, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            shapes.Line(x1, y0, x1, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            
            # median
            shapes.Line(x, y0, x, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            
            # whiskers
            shapes.Line(wxl, y0, wxl, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            shapes.Line(wxr, y0, wxr, y1, width=lineWidth, batch=self.boxbatch, color=lineColor)
            
            for value in data:
                # Outliers: points outside the whisker range (beyond fence)
                if not self.getAttr('showOutliers'):
                    continue
                if value < leftwhisker or value > rightwhisker:
                    height = self.getAttr('symbolHeight')
                    symbol = makeSymbolShapes(boxplot["symbol"], height, color=boxplot["color"], batch=self.boxbatch)
                    symbol.x = self.axis.get(value)[0]
                    symbol.y = centerLine - height/2

        symbolHeight = self.getAttr('symbolHeight')
        for overlay in self.overlays:
            geom = box_geometry[overlay["box"]]
            centerLine = geom["centerLine"]
            data = overlay["data"]
            count = len(data)
            for j, value in enumerate(data):
                offset = _overlay_y_offset(j, count, boxHeight, overlayJitter)
                symbol = makeSymbolShapes(
                    overlay["symbol"],
                    symbolHeight,
                    color=overlay["color"],
                    batch=self.boxbatch,
                )
                symbol.x = self.axis.get(value)[0]
                symbol.y = centerLine + offset - symbolHeight / 2



        # title
        if self.titleText:
            
            title = Text(self.titleText, self.windowBox[0] + self.windowBox[2]/2, topPoint[1], fontSize=self.getAttr('titleFontSize'))
            title.push(0, title.height*1.5)
            self.addDrawingFunction(title)
            self.include(*title.getCenterPos(), title.width, title.height)

        if self.secondAxisTitle: self.axis.addTitle(self.secondAxisTitle, self)
        
        if self.firstAxisTitle:
            self.firstTitle = Text(self.firstAxisTitle, 0, self.windowBox[1]+self.windowBox[3]/2, fontSize=self.getAttr('fontSize'), rotate=90)
        
        if self.firstAxisTitle:
            self.include(*self.firstTitle.getCenterPos(), self.firstTitle.width, self.firstTitle.height)
            self.addDrawingFunction(self.firstTitle)


    
    def add(self, data:Union[list, tuple], color=None, symbol:str=symbols.CIRCLE):
        """
        Add a new box plot to the chart.
        
        Parameters
        ----------
        numbers : list of int or float
            The numerical values for the bar. If a single integer is provided, it will be converted to a list.
        color: None or list or tuple
            Color for the box plot
        symbol: str
            Symbol to be displayed at outliers
        """

        if color is None:
            color = self.nextSeriesColor()

        self.boxplots.append({"data": data, "color": color, "symbol": symbol})

    def overlay(
        self,
        data: Union[list, tuple],
        box: int = 0,
        color=None,
        symbol: str = symbols.CIRCLE,
        legend: str = None,
    ):
        """
        Overlay custom points on a box plot row.

        Use this to highlight subgroups within a box, each with its own color
        and symbol. Points are jittered vertically within the target box row.

        Parameters
        ----------
        data : list or tuple
            Numeric x-values to plot.
        box : int, optional
            Index of the target box in ``add()`` order (0 = first ``add()``).
        color : tuple, optional
            Point color. Defaults to the next series color.
        symbol : str, optional
            Marker symbol. Default is circle.
        legend : str, optional
            Legend label for this overlay series.

        Returns
        -------
        self
            Returns the chart instance for chaining.

        Examples
        --------
        >>> chart.add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> chart.overlay([2, 3, 4], box=0, color=(220, 50, 50, 255), legend="low")
        >>> chart.overlay([8, 9, 10], box=0, color=(50, 80, 220, 255), legend="high")
        """

        if color is None:
            color = self.nextSeriesColor()

        self.overlays.append(
            {
                "data": data,
                "box": box,
                "color": color,
                "symbol": symbol,
                "legend": legend,
            }
        )
        return self

    
    def legends(self, *legends):
        """
        Set the legends for the bar chart.
        
        Parameters
        ----------
        *legends : list
            Diffrent legends corresponding to the colors on the bar when supplying more values to the `add` method
        
        Examples
        --------
        >>> chart.legends("Legend for the datapoint 1", "Legend for the datapoint 2", ...)
        """
        
        self.legendsLabels = legends


    def title(self, firstAxis:str=None, secondAxis:str=None, title=None):
        """
        Set the titles for the chart and the charts axis
        
        Parameters
        ----------
        firstAxis : str, optional
            The title for the first axis. Default is None.
        secondAxis : str, optional
            The title for the second axis. Default is None.
        title : str, optional
            The main title of the chart. Default is None.
        
        Returns
        -------
        self : object
            Returns the instance of the chart
        """
    
        self.titleText = title
        self.firstAxisTitle=firstAxis
        self.secondAxisTitle=secondAxis
        return self



