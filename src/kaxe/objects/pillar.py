
from ..core.styles import *
from ..core.shapes import shapes
from ..core.symbol import makeSymbolShapes
from ..core.symbol import symbol as symbols
from ..core.helper import *
from ..plot import identities

class Pillars:

    def __init__(self, x, heights, color:tuple=None, width:int=None) -> None:
        
        self.x = x
        self.heights = heights
        self.width = width

        self.batch = shapes.Batch()
        self.rects = []
        
        # color
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color

        #self.size = size

        self.symbol = symbols.RECTANGLE
        self.legendSymbol = self.symbol
        self.legendColor = self.color
        
        self.farLeft = min(self.x) - 1
        self.farRight = max(self.x) + 1
        self.farTop = max(self.heights)
        self.farBottom = 0

        self.supports = [identities.XYPLOT]

    
    def finalize(self, parent):

        x0, y0 = parent.pixel(0, 0)
        x1, _ = parent.pixel(len(self.x) / (self.farRight - self.farLeft), 0)
        width = (x1 - x0) * 0.75

        for i in range(len(self.x)):

            x, y1 = parent.pixel(self.x[i], self.heights[i])
            height = y1 - y0

            if not parent.inside(x, y1):
                continue

            if self.width:
                self.rects.append(shapes.Rectangle(x - width/2, y0, self.width, height, batch=self.batch, color=self.color))
            else:
                self.rects.append(shapes.Rectangle(x - width/2, y0, width, height, batch=self.batch, color=self.color))

    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x, y)


    def legend(self, text:str):
        self.legendText = text
        return self
    