
from typing import Callable
from .point import Points
from ..plot.styles import getRandomColor
from ..plot.helper import *
from ..plot.shapes import shapes
from ..plot.symbol import symbol
import numbers

class Function:

    def __init__(self, f:Callable, switchAxis:bool=False, stepSize:int=10, color:tuple=None, width:int=2, *args, **kwargs):
        self.__call__ = f
        self.function = f
        self.switchAxis = switchAxis
        self.stepSize = stepSize
        self.batch = shapes.Batch()
        self.legendSymbol = symbol.LINE

        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color

        self.thickness = width

        self.otherArgs = args
        self.otherKwargs = kwargs


    def finalize(self, parent):

        lastPoint = None
        # lastPointOutside = True
        lastPointInside = True
        self.lineSegments = []
        
        for n in range(0, parent.windowBox[2], 2):

            x, _ = parent.inversepixel(n,0)

            try:
                y = self.function(x, *self.otherArgs, **self.otherKwargs)
            except Exception as e:
                continue

            if not isinstance(x, numbers.Real) or not isinstance(y, numbers.Real):
                continue
            if math.isnan(x) or math.isnan(y):
                continue

            x,y = parent.pixel(x,y)
            # print(x,y)

            if not lastPoint:
                lastPoint = [x, y]
                continue

            inside = parent.inside(x,y)
            
            # last is inside but plot heading out
            if lastPointInside and not inside:
                lastPointInside = False

            # last is out but plot is heading in
            elif not lastPointInside and inside:
                lastPointInside = True
            
            # both points is inside
            elif inside:
                lastPointInside = True

            else:
                lastPointInside = False
                lastPoint = [x,y]
                continue

            if (not parent.inside(*lastPoint) and not parent.inside(x,y)):
                continue

            line = shapes.Line(lastPoint[0], lastPoint[1], x, y, color=self.color, width=self.thickness*2, batch=self.batch, center=True)
            self.lineSegments.append(line)
            lastPoint = [x, y]


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str):
        self.legendText = text
        return self