
from typing import Callable
from .point import Points
from ..core.styles import getRandomColor
from ..core.helper import *
from ..core.shapes import shapes
from ..core.symbol import symbol
from ..plot import identities
import numbers
from random import randint
from typing import Union

class Function:

    def __init__(self, 
                 f:Callable, 
                 color:tuple=None, 
                 width:int=10,
                 dotted:bool=False,
                 *args, 
                 **kwargs
                ):
        
        self.function = f
        self.batch = shapes.Batch()
        self.fillbatch = shapes.Batch()
        self.legendSymbol = symbol.LINE
        self.tangentFunctions = []
        self.dotted = dotted
        self.fillAreasBorders = []
        self.fillAreas = []
        self.fills = []

        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color

        self.thickness = width
        if len(self.color) > 3:
            self.fillcolor = (*self.color[:3], int(self.color[3]*0.5))
        else:
            self.fillcolor = (*self.color, 175)

        self.otherArgs = args
        self.otherKwargs = kwargs

        self.supports = [identities.XYPLOT, identities.POLAR]


    def __call__(self, x):
        return self.function(x)


    def __setPoint__(self, x, parent, firstaxisy:Union[int, None]=None, fills:Union[list, None]=None):
        try:
            y = self.function(x, *self.otherArgs, **self.otherKwargs)
        except Exception as e:
            return

        if not isinstance(x, numbers.Real) or not isinstance(y, numbers.Real):
            return
        if math.isnan(x) or math.isnan(y):
            return

        px, py = parent.pixel(x,y)

        if not px or not py:
            return

        if not self.__lastPoint__:
            self.__lastPoint__ = [px, py]
            return
                        
        if fills != None:
            # add fill areas under curve
            for x0, x1 in self.fillAreasBorders:
                if x0 <= x <= x1:
                    fills.append(
                        (
                            firstaxisy < py, 
                            (px, parent.clamp(y=py)[1]), 
                            (self.__lastPoint__[0], parent.clamp(y=self.__lastPoint__[1])[1])
                        )
                    )

        if parent.inside(px, py) or parent.inside(*self.__lastPoint__):
            self.lineSegments[-1].append(parent.clamp(self.__lastPoint__[0], self.__lastPoint__[1]))
            self.lineSegments[-1].append(parent.clamp(px, py))
        else:
            self.lineSegments.append([])

        self.__lastPoint__ = [px, py]


    def finalize(self, parent):

        self.lineSegments = [[]]
        fills = []
        self.__lastPoint__ = []

        if parent == identities.XYPLOT:
        
            firstaxisy = parent.pixel(0,0)[1]
            for n in range(0, parent.windowBox[2]):
                x, _ = parent.inversepixel(n,0)
                self.__setPoint__(x, parent, firstaxisy, fills)
        
        elif parent == identities.POLAR:
        
            fidelity = 100
            for angle in range(0, 360*fidelity, 5):
                angle = math.radians(angle / fidelity)
                self.__setPoint__(angle, parent)

        # piece together linesegments
        for segment in self.lineSegments:
            shapes.LineSegment(
                segment, 
                color=self.color, 
                width=self.thickness, 
                batch=self.batch, 
            )

        # add tangent
        for tf in self.tangentFunctions:
            parent.add(tf)

        # new fills
        fillAreas = []
        last = None
        for top, p1, p2 in fills:

            if top != last:                
                fillAreas.append({"top":top,"points":[]})
                last = top

            fillAreas[-1]["points"].append(p1)
            fillAreas[-1]["points"].append(p2)

        for area in fillAreas:
            area["points"].append((area["points"][len(area["points"])-1][0], firstaxisy))
            area["points"].insert(0, (area["points"][0][0], firstaxisy))

        for area in fillAreas:
            shapes.Polygon(*area["points"], color=self.fillcolor, batch=self.fillbatch)


    def tangent(self, x, dx=10**(-5)):
         
        # central diff quo
        dy = self.function(x+dx/2) - self.function(x-dx/2)
        
        a = dy/dx
 
        self.tangentFunctions.append(Function(
            lambda x, a, x0, y0: a*(x - x0) + y0, a=a, x0=x, y0=self.function(x),
            width=self.thickness,
            color=self.color,
            dotted=True
        ))

    
    def fill(self, x0, x1): 
        self.fillAreasBorders.append((x0,x1))
        

    def draw(self, *args, **kwargs):
        self.fillbatch.draw(*args, **kwargs)
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.fillbatch.push(*args, **kwargs)
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str):
        self.legendText = text
        return self
