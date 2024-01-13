
# a simple xy plot
# faster than the true plot

from .core.helper import *
import logging
from .core.axis import *
from .core.window import Window

XYPLOT = 'xy'

class Plot(Window):
    
    def __init__(self,  window:list=None): # |
        super().__init__()
        self.identity = XYPLOT

        """
        window:tuple [x0, x1, y0, y1] axis
        """
        
        self.firstAxis = Axis((1,0))
        self.secondAxis = Axis((0,1))

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.firstTitle = None
        self.secondTitle = None

        self.offset = [0,0]

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)


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

        # get styles
        self.width = self.getAttr('width')
        self.height = self.getAttr('height')

        xLength = self.windowAxis[1] - self.windowAxis[0]
        yLength = self.windowAxis[3] - self.windowAxis[2]
        self.scale = [self.width/xLength,self.height/yLength]

        self.__setAxisPos__()

        self.windowBox = (
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        )
        #self.nullInPlot = False

        self.firstAxis.autoAddMarkers(self)
        self.secondAxis.autoAddMarkers(self)


    # special api
    def title(self, first=None, second=None):
        self.firstTitle = first
        self.secondTitle = second
        return self


    # translations    
    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return (
            x * self.scale[0] - self.offset[0] + self.padding[0],
            y * self.scale[1] - self.offset[1] + self.padding[1]
        )

    
    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0])/self.scale[0]
        if not y is None: p[1] = (y+self.offset[1]-self.padding[1])/self.scale[1]

        return p


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


    def pointOnWindowBorderFromLine(self, pos, n): # -> former def line(...)
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))


    def inside(self, x, y):
        """
        para: translated
        (pixels)
        """
        return insideBox(self.windowBox, (x,y))

    
    def clamp(self, x:int=0, y:int=0):
        """
        clamps value to window max and min
        para: pixels
        """
        return (
            min(max(self.windowBox[0], x), self.windowBox[2]),
            min(max(self.windowBox[1], y), self.windowBox[3])
        )

