
# polar plot
from random import randint
from ..core.window import Window
from ..core.marker import Marker
from ..core.shapes import shapes
from ..core.axis import Axis
from ..core.helper import *
from ..core.text import Text
import logging
from math import sin, cos, acos, asin, radians, sqrt, pow
from typing import Union

POLARPLOT = 'polar'

class PolarPlot(Window):
    """
    A polar plot with radians on the radial axis

    Attributes
    ----------
    radiusAxis : Kaxe.Axis
        The radial axis of the polar plot.

    Note
    ----
    This plotting window supports fewer objects than that of the classical plotting windows
    
    """
    
    def __init__(self,  window:list=None, useDegrees:bool=False): # |
        super().__init__()
        self.identity = POLARPLOT

        self.useDegrees = useDegrees
        
        self.axis = [lambda: self.radiusAxis]

        self.attrmap.default('width', 2000)
        self.attrmap.default('height', 2000)

        self.attrmap.default(attr='rNumbers', value=None)

        self.setAttrMap(self.attrmap)

        self.attrmap.submit(Marker)
        self.attrmap.submit(Axis)
        self.attrmap.submit(PolarAxis)

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None]

        self.scale = (1,1)
        self.radiusTitle = None
        self.radiusAxis = Axis((1,0), (0,-1), 'rNumbers')

        self.angleAxis = PolarAxis(useDegrees)
        self.batch = shapes.Batch()


    # creating plotting window
    def __calculateWindowBorders__(self):
        if self.windowAxis[0] is None: self.windowAxis[0] = 0
        if self.windowAxis[1] is None: self.windowAxis[1] = 10


    def __addRoundLines__(self):
        """
        from markers of radius axis

        burde nok sendes til en ny klasse
        """

        for marker in self.radiusAxis.markers:
            
            if not marker.shown: continue

            shapes.Circle(*self.center, 
                          radius=self.translate(marker.x, 0)[0]-self.center[0], 
                          fill=False,
                          width=self.radiusAxis.getAttr('Marker.gridlineWidth'),
                          color=self.radiusAxis.getAttr('Marker.gridlineColor'),
                          batch=self.batch
                        )
        
        self.addDrawingFunction(self.batch)


    def __pre__(self):
        height = self.getAttr('height')
        width = self.getAttr('width')
        if width != height:
            largets = max(width, height)
            self.setAttr('width', largets)
            self.setAttr('height', largets)
            logging.info('Changed size of plot')


    def __prepare__(self):
        # finish making plot
        # fit "plot" into window     
        
        self.height = self.getAttr('height')
        self.width = self.getAttr('width')

        self.__calculateWindowBorders__()

        self.radius = self.height/2
        self.radiusAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        xLength = self.windowAxis[1] - self.windowAxis[0]
        yLength = xLength
        self.scale = ((self.width/2) / xLength, (self.height/2) / yLength)
        
        self.attrmap.setAttr('Marker.showLine', False)

        y = halfWay([self.windowBox[1]], [self.windowBox[3]])[0]
        self.center = (halfWay([self.windowBox[0]], [self.windowBox[2]])[0], y)
        self.radiusAxis.setPos(self.center, (self.windowBox[2] + self.windowBox[0], y))
        self.radiusAxis.finalize(self)
        
        self.radiusAxis.autoAddMarkers(self)
        self.__addRoundLines__()

        if self.radiusTitle: self.radiusAxis.addTitle(self.radiusTitle, self)
        
        self.angleAxis.finalize(self)


    # special api
    def title(self, title:str):
        """
        Adds title to the plot.
        
        Parameters
        ----------
        title : str
            Title for the axis.

        Returns
        -------
        Kaxe.Plot
            The active plotting window
        """

        self.radiusTitle = title
        return self


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
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0]-self.center[0])/self.scale[0]
        if not y is None: p[1] = (y+self.offset[1]-self.padding[1]-self.center[1])/self.scale[1]

        return p


    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def pixel(self, angle:Union[int, float], radius:Union[int, float]) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        if radius < 0:
            return None, None

        x, y = cos(angle)*radius, sin(angle)*radius

        return self.translate(x,y)


    def inversepixel(self, x:Union[int, float], y:Union[int, float]):
        
        x, y = self.inversetranslate(x, y)

        # special cases
        vl = vlen((x,y))
        if vl == 0:
            return 0, 0

        if -0.001 < y < 0.001:
            
            if x > 0:
                return x, 0

            else:
                return -x, math.pi

        # general cases
        if y > 0:
            angle = acos(x/vl)
        else:
            angle = acos(-x/vl)
            angle += radians(180)
        
        radius = max(x/cos(angle), y/sin(angle))
    
        # special case again
        if -0.001 < x < 0.001:
            return y/sin(angle), angle

        return angle, radius


    def inside(self, px:int, py:int):
        if px is None or py is None: return False

        return self.radius > vlen(vdiff((
            px-self.offset[0]-self.padding[0], 
            py-self.offset[1]-self.padding[1]
            ), self.center)
        )


    def clamp(self, x:int=0, y:int=0):
        """
        clamps value to window max and min
        para: pixels
        """
        return (
            min(max(self.windowBox[0], x), self.windowBox[2]),
            min(max(self.windowBox[1], y), self.windowBox[3])
        )


    # SKAL SKRIVES OM
    def pointOnWindowBorderFromLine(self, pos, n): # -> former def line(...)
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))


class PolarAxis(Axis):

    def __init__(self, degrees:bool=False):
        super().__init__((1,0), (0,1), '')
        
        self.batch = shapes.Batch()

        self.markers = [
            (0, '0'),
            (45, '$\\frac{\\pi}{4}$'),
            (90, '$\\frac{\\pi}{2}$'),
            (135, '$\\frac{3\\pi}{4}$'),
            (180, '$\\pi$'),
            (225, '$\\frac{5\\pi}{4}$'),
            (270, '$\\frac{3\\pi}{2}$'),
            (315, '$\\frac{7\\pi}{4}$'),
        ]
        if degrees:
            self.markers = [
                (0, '0'),
                (45, '45'),
                (90, '90'),
                (135, '135'),
                (180, '180'),
                (225, '225'),
                (270, '270'),
                (315, '315'),
            ]


    def finalize(self, parent:PolarPlot): #virker kun til polarplot
        self.setAttrMap(parent.attrmap)

        width = self.getAttr('Marker.gridlineWidth')

        self.radius = parent.getAttr('height')/2
        self.circle = shapes.Circle(*parent.center, self.radius, fill=False, width=width)
        self.texts = []
        fontsize = parent.getAttr('fontSize')

        # marker
        for angle, text in self.markers:
            v = (cos(radians(angle)), sin(radians(angle)))
            pos = addVector(parent.center, vectorScalar(v, self.radius))
            shapes.Line(*parent.center, 
                        *pos,
                        batch=self.batch,
                        width=width,
                        color=parent.getAttr('Marker.gridlineColor'),
                    )

            # check for overlap
            textShape = Text(
                text,
                *pos,
                batch=self.batch, 
                anchor_x="center", 
                anchor_y="center", 
                fontSize=int(fontsize), 
                color=parent.getAttr('color')
            )

            x, y = textShape.getCenterPos()

            poss = [
                (x+textShape.width/2, y),
                (x+textShape.width/2, y-textShape.height/2),
                (x-textShape.width/2, y),
                (x-textShape.width/2, y+textShape.height/2),
            ]

            maxDist = 0
            for p in poss:
                vn = (parent.center[0]-p[0], parent.center[1]-p[1])
                d = sqrt(pow(vn[0], 2)+pow(vn[1], 2))
                maxDist = max(d - self.radius, maxDist)

            maxDist += fontsize

            textShape.push(*vectorScalar(v, maxDist)) #= addVector(vectorScalar(v, maxDist), pos)
            self.texts.append(textShape)

        parent.addDrawingFunction(self.batch)
        parent.addDrawingFunction(self.circle, 2)
        for textShape in self.texts:
            parent.include(*textShape.getCenterPos(), textShape.width, textShape.height)
