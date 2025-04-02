
from ..plot.box import BoxedPlot
import numpy as np
import statistics
from ..objects.point import Points2D
from ..objects.function import Function2D
from ..core.styles import getRandomColor
from ..core.symbol import symbol


class QQPlot(BoxedPlot):
    """
    Initialize a QQPlot instance.
    
    Parameters
    ----------
    data : list
        The data points to be plotted on the QQ plot.
    quantiles : list, optional
        The theoretical quantiles to compare against. If not provided, 
        standard normal quantiles are calculated based on the length of `data`.
    color : list, optional
        A list containing two color values for the plot. Defaults to [None, None].
        If None, a random color is generated.
    size : int, optional
        The size of the points in the plot. Default is 50.
        
    Attributes
    ----------
    points : Points2D
        The 2D points object representing the data and quantiles.
    line : Function2D
        The 2D function represeting an line
            
    Notes
    -----
    A linear fit is applied to the data and quantiles, and the resulting line is added to the plot.
    """

    def __init__(self, data, quantiles:list=None, color:list=[None, None], size=50):
        
        self.size = size

        self.color = color
        if color[0] is None:
            self.color[0] = getRandomColor()
        if color[1] is None:
            self.color[1] = getRandomColor()

        data = sorted(data)

        self.quantiles = quantiles
        if not quantiles:
            self.quantiles = statistics.NormalDist(0, 1).quantiles(len(data)+1)

        self.data = data.copy()

        super().__init__()

        points = self.points = self.add(Points2D(
            self.quantiles, 
            self.data, 
            color=self.color[0],
            size=self.size,
            symbol=symbol.DONUT
        ))

        oldx = points.farLeft, points.farRight

        spreadval = -.1

        diff = (points.farTop - points.farBottom)
        points.farBottom = points.farBottom + diff*spreadval
        points.farTop = points.farTop - diff*spreadval
        
        diff = (points.farRight - points.farLeft)
        points.farLeft = points.farLeft + diff*spreadval
        points.farRight = points.farRight - diff*spreadval

        a, b = np.polyfit(self.quantiles, self.data, deg=1)

        def f(x):
            if not (oldx[0] < x < oldx[1]):
                return

            return a*x+b

        self.line = self.add(Function2D(f, width=self.size//2, color=self.color[1]))


    def __prepare__(self):
        # finish making plot
        # fit "plot" into window

        numberOnAxisGoal = self.getAttr('xNumbers')
        if not numberOnAxisGoal:
            self.attrmap.style(xNumbers = self.getAttr('fontSize')//10)


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


