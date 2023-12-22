
#22.1285s

from ..plot.shapes import shapes
from ..plot.styles import getRandomColor
from ..plot.symbol import symbol
from sympy import solve
import math


class Equation:

    def __init__(self, left, right, color:tuple=None, width=2):
        self.batch = shapes.Batch()

        self.left = left
        self.right = right
        
        self.legendSymbol = symbol.LINE
        self.width = width
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color
        
        self.dots = []

        self.steps = [1, 10, 100]


    def __getPointsInBox__(self, box, step, parent):
        if step == -1:
            return
        
        delta = self.steps[step]

        xtot = int((box[1] - box[0]) / delta)
        ytot = int((box[3] - box[2]) / delta)
        
        grid = set()

        for i in range(xtot):
            px = (i * delta) + box[0]
            
            for j in range(ytot):
                py = (j * delta) + box[2]

                x0, y0 = parent.inversepixel(px, py)
                x1, y1 = parent.inversepixel(px, py+delta)
                x2, y2 = parent.inversepixel(px+delta, py)
                x3, y3 = parent.inversepixel(px+delta, py+delta)

                d1 = self.left(x0, y0) - self.right(x0, y0)
                d2 = self.left(x1,y1) - self.right(x1, y1)
                d3 = self.left(x2,y2) - self.right(x2, y2)
                d4 = self.left(x3,y3) - self.right(x3, y3)

                # er nul imellem?
                if max(d1, d2, d3, d4) >= 0 and min(d1, d2, d3, d4) <= 0:
                    
                    grid.add((i,j))
                    grid.add((i-1,j))
                    grid.add((i-1,j-1))
                    grid.add((i+1,j))
                    grid.add((i+1,j+1))
        

        for i,j in grid:
            px = (i * delta) + box[0]
            py = (j * delta) + box[2]

            if (not parent.inside(px, py)) or (not parent.inside(px+delta, py+delta)):
                continue

            if step == 0:
                self.dots.append(shapes.Circle(px, py, color=self.color, batch=self.batch, radius=self.width))

            #shapes.Rectangle(px, py, delta, delta, (255,0,0,100), batch=self.batch, radius=2)

            self.__getPointsInBox__([
                px,
                px+delta,
                py,
                py+delta
            ], step-1, parent)


    def finalize(self, parent):
        box = parent.windowAxis
        p1 = parent.pixel(box[0], box[2])
        p2 = parent.pixel(box[1], box[3])
        box = (
            p1[0],
            p2[0],
            p1[1],
            p2[1]
        )
        self.__getPointsInBox__(box, len(self.steps)-1, parent)


    def push(self, x, y):
        self.batch.push(x,y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def legend(self, text:str):
        self.legendText = text
        return self
