
# polar plot
from .window import Window
from .shapes import shapes
from .axis import Axis
from .helper import *
import logging
from math import sin, cos, acos, asin

POLARPLOT = 'polar'

class PolarPlot(Window):
    """
    polarplot er en del mere stringent end plot og kan en del mindre
    """

    def __init__(self,  window:list=None): # |
        super().__init__()
        self.identity = POLARPLOT
        
        self.axis = [lambda: self.radiusAxis]

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.scale = (1,1)
        self.radiusTitle = None
        self.radiusAxis = Axis((1,0))

        self.angleAxis = PolarAxis()

        self.style(__overwrite__=False, 
                   markerStepSizeBand=[100, 30], 
                   windowWidth=1500, 
                   windowHeight=1500
        )


    # creating plotting window
    def __calculateWindowBorders__(self):
        pass


    def __prepare__(self):
        # finish making plot
        # fit "plot" into window 

        assert self.height == self.width

        self.radiusAxis.addStartAndEnd(0, 100)
        xLength = 100
        yLength = xLength
        self.scale = ((self.width/2) / xLength, (self.height/2) / yLength)
        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])

        y = halfWay([self.windowBox[1]], [self.windowBox[3]])[0]
        self.center = (halfWay([self.windowBox[0]], [self.windowBox[2]])[0], y)
        self.radiusAxis.finalize(self, poss=(*self.center, self.windowBox[2] + self.windowBox[0], y))
        
        self.radiusAxis.addMarkersToAxis(self)

        self.radiusAxis.addTitle('hejsa', self)
        
        self.angleAxis.finalize(self)

    # special api
    def title(self, first=None, second=None):
        self.firstTitle = first
        self.secondTitle = second
        return self


    def setAxis(self, axis:Axis):
        self.radiusAxis = axis


    # translations
    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return (
            self.center[0] + x * self.scale[0] - self.offset[0] + self.padding[0],
            self.center[1] + y * self.scale[1] - self.offset[1] + self.padding[1]
        )


    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0] - self.center[0])/self.scale[0]
        if not y is None: p[1] = (x+self.offset[1]-self.padding[1] - self.center[1])/self.scale[1]

        return p


    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def pixel(self, angle:int|float, radius:int|float) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        x, y = math.cos(angle)*radius, math.sin(angle)*radius

        return self.translate(x,y)


    def inversepixel(self, angle:int|float, radius:int|float):
        
        x, y = math.acos(angle)/radius, math.asin(angle)/radius

        return self.inversetranslate(x, y)


    # SKAL SKRIVES OM
    def pointOnWindowBorderFromLine(self, pos, n): # -> former def line(...)
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))


class PolarAxis:

    def __init__(self):
        self.batch = shapes.Batch()


    def finalize(self, parent:PolarPlot): #virker kun til polarplot
        self.circle = shapes.Circle(*parent.center, parent.height/2, fill=False, batch=self.batch, width=2)
        parent.addDrawingFunction(self.batch, 2)