
from typing import Callable
from .point import Points
from ..core.styles import getRandomColor
from ..core.helper import *
from ..core.shapes import shapes
from ..core.symbol import symbol
from ..plot import identities
import numbers
from random import randint
from .function import Function
from typing import Union

class ParametricEquation:

    def __init__(self, 
                 f:Callable, 
                 interval:Union[tuple, list],
                 color:tuple=None, 
                 width:int=10,
                 dotted:bool=False,
                 *args, 
                 **kwargs
                ):
        
        self.function = f
        self.interval = interval
        self.batch = shapes.Batch()
        
        self.legendSymbol = symbol.LINE
        self.tangentFunctions = []
        self.dotted = dotted
        self.fidelity = 100

        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color

        self.thickness = width

        self.otherArgs = args
        self.otherKwargs = kwargs

        self.supports = [identities.XYPLOT, identities.POLAR]


    def __call__(self, x):
        return self.function(x)


    def __half__(self, t0, t1, parent):

        p0 = self.function(t0)
        p1 = self.function(t1)

        pixel0 = parent.pixel(*p0)
        pixel1 = parent.pixel(*p1)

        diff = vlen(vdiff(pixel0, pixel1))

        if diff > 10:
            badPoints = not parent.inside(*pixel0) or not parent.inside(*pixel1)
            half = (t0 + t1) / 2
            
            if badPoints:
                return self.__half__(t0, half, parent) + [None] + self.__half__(half, t1, parent)
            else:
                return self.__half__(t0, half, parent) + self.__half__(half, t1, parent)

        else:
            return [pixel0, pixel1]


    def finalize(self, parent):

        self.lineSegments = [[]]
        self.__lastPoint__ = []

        if parent == identities.XYPLOT:
        

            lineSegments = [[]]

            for i in self.__half__(*self.interval, parent):
                if i:lineSegments[-1].append(i)
                elif len(lineSegments[-1]) > 0: lineSegments.append([])
        
        # elif parent == identities.POLAR:
        #     for angle in range(0, 360*fidelity, 5):
        #         angle = math.radians(angle / fidelity)
        #         self.__setPoint__(angle, parent)

        # piece together linesegments
        for ls in lineSegments:
            shapes.LineSegment(
                ls, 
                color=self.color, 
                width=self.thickness, 
                batch=self.batch, 
            )

        # add tangent
        for tf in self.tangentFunctions:
            parent.add(tf)


    def tangent(self, t, dt=10**(-5)):
         
        # central diff quo
        x, y = self.function(t)
        dx, dy = vdiff((x,y), self.function(t+dt))
        
        a = dy/dx
 
        self.tangentFunctions.append(Function(
            lambda x, a, x0, y0: a*(x - x0) + y0, a=a, x0=x, y0=y,
            width=self.thickness,
            color=self.color,
            dotted=True
        ))

    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str):
        self.legendText = text
        return self
