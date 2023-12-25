
from typing import Callable
from .point import Points
from ..plot.styles import getRandomColor
from ..plot.helper import *
from ..plot.shapes import shapes
from ..plot.symbol import symbol
import numbers


class Function:

    def __init__(self, 
                 f:Callable, 
                 color:tuple=None, 
                 width:int=2, 
                 dotted:bool=False,
                 *args, 
                 **kwargs
                ):
        
        self.function = f
        self.batch = shapes.Batch()
        self.legendSymbol = symbol.LINE
        self.tangentFunction = None
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


    def __call__(self, x):
        return self.function(x)

    def finalize(self, parent):

        lastPoint = None
        # lastPointOutside = True
        lastPointInside = True
        self.lineSegments = []
        fills = []

        firstaxisy = parent.pixel(0,0)[1]
        for n in range(0, parent.windowBox[2]):

            x, _ = parent.inversepixel(n,0)

            try:
                y = self.function(x, *self.otherArgs, **self.otherKwargs)
            except Exception as e:
                continue

            if not isinstance(x, numbers.Real) or not isinstance(y, numbers.Real):
                continue
            if math.isnan(x) or math.isnan(y):
                continue

            px, py = parent.pixel(x,y)

            if not lastPoint:
                lastPoint = [px, py]
                continue
                        
            # add fill areas under curve
            for x0, x1 in self.fillAreasBorders:
                if x0 <= x <= x1:
                    fills.append(
                        (
                            firstaxisy < py, 
                            (px, parent.clamp(y=py)[1]), 
                            (lastPoint[0], parent.clamp(y=lastPoint[1])[1])
                        )
                    )

            if parent.inside(px, py) or parent.inside(*lastPoint):
                line = shapes.Line(
                    *parent.clamp(lastPoint[0], lastPoint[1]), 
                    *parent.clamp(px, py), 
                    color=self.color, 
                    width=self.thickness*2, 
                    batch=self.batch, 
                    center=True
                )
                self.lineSegments.append(line)
        
            lastPoint = [px, py]

        # add tangent
        if self.tangentFunction: parent.add(self.tangentFunction)

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
            shapes.Polygon(*area["points"], color=self.fillcolor, batch=self.batch)


    def tangent(self, x, dx=10**(-5)):
         
        # central diff quo
        dy = self.function(x+dx/2) - self.function(x-dx/2)
        
        a = dy/dx
 
        self.tangentFunction = Function(
            lambda x, a, x0, y0: a*(x - x0) + y0, a=a, x0=x, y0=self.function(x),
            width=self.thickness,
            color=self.color,
            dotted=True
        )

    
    def fill(self, x0, x1): 
        self.fillAreasBorders.append((x0,x1))
        

    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str):
        self.legendText = text
        return self
