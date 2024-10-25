
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Triangle, Line3D, Point3D
from ...core.d3.helper import rc
from ..color import Colormaps, Colormap

# other
import numpy as np
import math
import time

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

        badPoints = []

        # get points
        for xn in range(self.numPoints):
            x = xlen * (xn / self.numPoints) + parent.window[0]

            for yn in range(self.numPoints):
                y = ylen * (yn / self.numPoints) + parent.window[2]

                try:
                    z = self.f(x,y)
                except Exception:
                    badPoints.append((xn,yn))
                    continue
                
                if type(z) not in [int, float]:
                    badPoints.append((xn,yn))
                    continue

                if not parent.inside3D(x,y,z):
                    badPoints.append((xn,yn))
                    continue

                matrix[xn][yn] = parent.pixel(x,y,z)
                zmap[xn][yn] = z

        # draw
        for xn in range(self.numPoints-1):
            for yn in range(self.numPoints-1):
                if matrix[xn][yn][0] is None:
                    continue

                color = self.cmap.getColor(zmap[xn][yn], parent.windowAxis[4], parent.windowAxis[5])
                
                if self.fill:
                    self.__fill__(render, matrix, xn, yn, color)
                else:
                    self.__outline__(render, matrix, xn, yn, color)

        # draw ends
        # NOTE: der er en del punkter der måske kan sorteres fra
        for xn, yn in badPoints:
            p1 = xn-1, yn-1
            p2 = xn-1, yn
            p3 = xn-1, yn+1
            p4 = xn  , yn+1
            p6 = xn  , yn-1
            p7 = xn+1, yn-1
            p8 = xn+1, yn
            p9 = xn+1, yn+1

            p = [p1, p2, p3, p4, p6, p7, p8, p9]
            for i in p:
                for j in p:
                    if i == j: continue
                    for k in p:
                        if i == k or j == k: continue
                        
                        # behøver ikke være en funktion, men gør bare det hele så meget pænere
                        self.__createTriangleAtEnd__(parent, matrix, zmap, *i, *j, *k)


    def __createTriangleAtEnd__(self, parent, matrix, zmap, x0, y0, x1, y1, x2, y2):
        if x0 < 0 or y0 < 0 or x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            return

        render = parent.render

        try:
            if matrix[x0][y0][0] is not None and matrix[x1][y1][0] is not None and matrix[x2][y2][0] is not None:
                color = self.cmap.getColor(zmap[x0][y0], parent.windowAxis[4], parent.windowAxis[5])
                if self.fill:
                    render.add3DObject(Triangle(matrix[x0][y0], matrix[x1][y1], matrix[x2][y2], color=color))
                else:
                    render.add3DObject(Line3D(matrix[x0][y0], matrix[x1][y1], color=color))
                    render.add3DObject(Line3D(matrix[x0][y0], matrix[x2][y2], color=color))
                    render.add3DObject(Line3D(matrix[x1][y1], matrix[x2][y2], color=color))
                                                
        except IndexError:
            pass


    def legend(self, text:str, color=None, symbol=None):
        self.legendText = text

        if color:
            self.legendColor = color

        if symbol:
            self.legendSymbol = symbol

        return self
