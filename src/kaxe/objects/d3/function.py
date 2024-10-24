
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Triangle, Line3D
from ...core.d3.helper import rc
from ..color import Colormaps, Colormap

# other
import numpy as np
import math


class Function3D(Base3DObject):
    def __init__(self, f, color:Colormap=None, numPoints:int=None, fill:bool=True):
        super().__init__()

        self.f = f
        self.fill = fill
        
        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.RECTANGLE
        self.legendColor = rc()

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

        self.numPoints = numPoints
        if numPoints is None and fill:
            self.numPoints = 150
        elif numPoints is None:
            self.numPoints = 25


    def __fill__(self, render, matrix, xn, yn, color):
        if all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):
                
            render.add3DObject(
                Triangle(
                    matrix[xn][yn],
                    matrix[xn+1][yn],
                    matrix[xn][yn+1],
                    color=color
                )
            )

        if all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    
            render.add3DObject(
                Triangle(
                    matrix[xn+1][yn+1],
                    matrix[xn+1][yn],
                    matrix[xn][yn+1],
                    color=color
                )
            )
        

        return
        b = list(filter(lambda x: x[0] is not None, [matrix[xn+1][yn+1], matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]))

        if len(b) == 3:
            render.add3DObject(Triangle(
                *b
            ))
        elif len(b) == 2 and matrix[xn-1][yn][0] is not None:
            render.add3DObject(Triangle(
                *b, matrix[xn-1][yn]
            ))
        elif len(b) == 2 and matrix[xn][yn-1][0] is not None:
            render.add3DObject(Triangle(
                *b, matrix[xn][yn-1]
            ))
        elif len(b) == 2 and matrix[xn-1][yn-1][0] is not None:
            render.add3DObject(Triangle(
                *b, matrix[xn][yn-1]
            ))
        elif len(b) == 1:
            print(b)

    def __outline__(self, render, matrix, xn, yn, color):
        if all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):
                
            render.add3DObject(Line3D(matrix[xn][yn],matrix[xn][yn+1],color=color))
            render.add3DObject(Line3D(matrix[xn][yn],matrix[xn+1][yn],color=color))
            render.add3DObject(Line3D(matrix[xn][yn+1],matrix[xn+1][yn],color=color))
        
        if all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    
            render.add3DObject(Line3D(matrix[xn+1][yn+1],matrix[xn+1][yn],color=color))
            render.add3DObject(Line3D(matrix[xn+1][yn+1],matrix[xn][yn+1],color=color))


    def finalize(self, parent):

        render = parent.render

        self.points = []
        xlen = parent.window[1] - parent.window[0]
        ylen = parent.window[3] - parent.window[2]
        
        matrix = np.empty((self.numPoints, self.numPoints), dtype=tuple)
        matrix.fill(np.array((None, None, None)))
        zmap = np.empty((self.numPoints, self.numPoints), dtype=float)
        zmap.fill(-math.inf)

        for xn in range(self.numPoints):
            x = xlen * (xn / self.numPoints) + parent.window[0]

            for yn in range(self.numPoints):
                y = ylen * (yn / self.numPoints) + parent.window[2]

                try:
                    z = self.f(x,y)
                except Exception:
                    continue
                
                if type(z) not in [int, float]:
                    continue

                if not parent.inside3D(x,y,z):
                    continue

                matrix[xn][yn] = parent.pixel(x,y,z)
                zmap[xn][yn] = z

        
        for xn in range(self.numPoints-1):
            for yn in range(self.numPoints-1):
                if matrix[xn][yn][0] is None:
                    continue

                color = self.cmap.getColor(zmap[xn][yn], parent.windowAxis[4], parent.windowAxis[5])
                
                if self.fill:
                    self.__fill__(render, matrix, xn, yn, color)
                else:
                    self.__outline__(render, matrix, xn, yn, color)


    def legend(self, text:str, color=None, symbol=None):
        self.legendText = text

        if color:
            self.legendColor = color

        if symbol:
            self.legendSymbol = symbol

        return self
