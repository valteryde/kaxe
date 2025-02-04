

from ..core.helper import *
import logging
from ..core.axis import *
from ..core.styles import getRandomColor, isLightOrDark
from ..core.symbol import symbol as symbols
from ..core.symbol import makeSymbolShapes
from ..core.window import Window

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

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        self.axis = Axis((1,0), (0, -1), 'axisNumbers')

        self.maxNumber = 0
        self.maxNumberAmount = 0
        self.boxplots = []
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
            IQR = rightbox - leftbox
            leftwhisker = leftbox - 3/2*IQR
            rightwhisker = rightbox + 3/2*IQR

            min_ = min(min_, *boxplot["data"], leftwhisker, rightwhisker)
            max_ = max(max_, *boxplot["data"], leftwhisker, rightwhisker)

            boxplot["whiskers"] = (leftwhisker, rightwhisker)
            boxplot["quantile"] = (leftbox, rightbox)

        # important styles
        boxHeight = (self.getAttr('height')-self.getAttr('boxGap')*(len(self.boxplots)+1))/len(self.boxplots)
        lineWidth = self.getAttr('lineWidth')
        fill = self.getAttr('fill')


        self.axis.addStartAndEnd(min_, max_)

        topPoint = (self.windowBox[0], self.windowBox[3]-self.windowBox[1])
        
        self.axis.setPos(
            (self.windowBox[0], self.windowBox[1]),
            (self.windowBox[2]-self.windowBox[0], self.windowBox[1])
        )

        self.axis.finalize(self)        
        self.axis.autoAddMarkers(self)

        for i, label in enumerate(self.legendsLabels):
            if label: self.legendbox.add(label, color=self.boxplots[i]["color"], symbol=self.boxplots[i]["symbol"])

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
            
            for i in data:
                
                if not(leftwhisker < i < rightwhisker):
                    height = self.getAttr('symbolHeight')
                    symbol = makeSymbolShapes(boxplot["symbol"], height, color=boxplot["color"], batch=self.boxbatch)
                    symbol.x = self.axis.get(i)[0]
                    symbol.y = centerLine - height/2



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
            color = getRandomColor()

        self.boxplots.append({"data": data, "color": color, "symbol": symbol})

    
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



