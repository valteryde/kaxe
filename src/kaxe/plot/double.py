

# special cases of base plot
from .standard import Plot, XYPLOT
from ..core.axis import Axis
from typing import Union

class MiddleManPlot(Plot):

    def __init__(self, parent:Plot, y_:callable, iy_:callable):
        super().__init__()

        self.parent = parent
        self.y_ = y_
        self.iy_ = iy_

        self.pixel = lambda x,y: self.parent.pixel(x,y_(y))
        self.translate = lambda x,y: self.parent.translate(x,y_(y))
        self.inside = lambda x,y: self.parent.inside(x,y)
        self.clamp = lambda x,y: self.parent.clamp(x,y)
        self.scaled = lambda x,y: self.parent.scaled(x,y_(y))
        # NOTE: This could be a problem if n is not changed
        self.pointOnWindowBorderFromLine = lambda pos, n: self.parent.pointOnWindowBorderFromLine((pos[0], y_(pos[1])),n)
        self.getAttr = parent.getAttr
        
        self.copyAttributesFromParent()

        # self.addFunc = parent.addFunc

    def inversepixel(self, x, y):
        x, y = self.parent.inversepixel(x,y)
        return x, self.iy_(y)
    
    def inversetranslate(self, x, y):
        x, y = self.parent.inversetranslate(x,y)
        return x, self.iy_(y)



    def copyAttributesFromParent(self):
        self.__dict__.update(self.parent.__dict__)


class DoubleAxisPlot(Plot):
    """
    A plotting window with two y-axis placed on each end of axis

    Attributes
    ----------
    firstAxis : Kaxe.Axis
        The first axis of the plot.
    secondAxis : Kaxe.Axis
        The second axis of the plot.

    Parameters
    ----------
    window: list|tuple|None
        [x0, x1, ya0, ya1, yb0, yb1],
        A list or tuple defining the window for the plot
        The first two values are the x-axis window, the next two are the first y-axis window, and the last two are the second y-axis window.

    """

    def __init__(self, window:Union[list, tuple, None]):
        super().__init__(window)
        
        self.thirdAxis = Axis((0,1), (1,0), 'yNumbers')
        self.thirdTitle = None
        self.offset.append(0)
        

    def __prepare__(self):
        # finish making plot
        # fit "plot" into window

        xLength = self.windowAxis[1] - self.windowAxis[0]
        yaLength = self.windowAxis[3] - self.windowAxis[2]
        ybLength = self.windowAxis[4] - self.windowAxis[5]
        self.scale = [self.width/xLength,self.height/yaLength, self.height/ybLength]

        # position axis
        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3])
        self.thirdAxis.addStartAndEnd(self.windowAxis[4], self.windowAxis[5])
        self.offset[0] += self.windowAxis[0] * self.scale[0]
        self.offset[1] += self.windowAxis[2] * self.scale[1]
        self.offset[2] += self.windowAxis[4] * self.scale[2]

        self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[2]))
        self.firstAxis.finalize(self)

        self.secondAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[0],self.windowAxis[3]))
        self.secondAxis.finalize(self)

        self.thirdAxis.setPos(self.pixel(self.windowAxis[1],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[3]))
        self.thirdAxis.finalize(self)

        self.firstAxis.autoAddMarkers(self)
        self.secondAxis.autoAddMarkers(self)
        self.thirdAxis.autoAddMarkers(self)

        self.firstAxis.checkCrossOvers(self,self.secondAxis)
        self.secondAxis.checkCrossOvers(self, self.firstAxis)
        self.thirdAxis.checkCrossOvers(self, self.firstAxis)

        if self.firstTitle: self.firstAxis.addTitle(self.firstTitle, self)
        if self.secondTitle: self.secondAxis.addTitle(self.secondTitle, self)
        if self.thirdTitle: self.thirdAxis.addTitle(self.thirdTitle, self)

        self.secondAxisPlot = MiddleManPlot(self, lambda y: y, lambda y: y)
        
        secondLength = self.windowAxis[3] - self.windowAxis[2]
        thirdLength = self.windowAxis[5] - self.windowAxis[4]

        y_ = lambda y: (y - ( self.windowAxis[4] - self.windowAxis[2] )) * (secondLength/thirdLength)
        iy_ = lambda y: y/(secondLength/thirdLength) + ( self.windowAxis[4] - self.windowAxis[2] )
        self.thirdAxisPlot = MiddleManPlot(self, y_, iy_)


    def __callFinalizeObject__(self, obj):

        if obj.__usedAxis == 1:
            return obj.finalize(self.secondAxisPlot)
        
        elif obj.__usedAxis == 2:
            return obj.finalize(self.thirdAxisPlot)

        else:
            return obj.finalize(self)


    def add1(self, obj):
        """
        Adds to the first Axis

        Parameters
        ----------
        object : Object
            The object to add to the left axis

        """

        obj.__usedAxis = 1
        self.add(obj)


    def add2(self, obj):
        """
        Adds to the first Axis

        Parameters
        ----------
        object : Object
            The object to add to the second axis

        """

        obj.__usedAxis = 2
        self.add(obj)


    def title(self, first=None, second=None, third=None):
        """
        Adds title to the plot.
        
        Parameters
        ----------
        first : str, optional
            Title for the first axis.
        second : str, optional
            Title for the second axis.
        third : str, optional
            Title for the second second axis. Called the third axis

        Returns
        -------
        Kaxe.Plot
            The active plotting window
        
        """

        self.firstTitle = first
        self.secondTitle = second
        self.thirdTitle = third
        return self
