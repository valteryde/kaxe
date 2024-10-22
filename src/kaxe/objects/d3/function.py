
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Point3D, Triangle
from ...core.d3.helper import rc
from .color import getColor

# other
import numpy as np


class Function3D(Base3DObject):
    def __init__(self, f, color:tuple=None, size:int=None):
        super().__init__()

        self.f = f
        
        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.RECTANGLE
        self.legendColor = rc()

        self.numPoints = 200


    def finalize(self, parent):

        render = parent.render

        self.points = []
        xlen = parent.window[1] - parent.window[0]
        ylen = parent.window[3] - parent.window[2]
        
        matrix = np.empty((self.numPoints, self.numPoints), dtype=tuple)
        matrix.fill(np.array((None, None, None)))
        for xn in range(self.numPoints):
            x = xlen * (xn / self.numPoints) + parent.window[0]

            for yn in range(self.numPoints):
                y = ylen * (yn / self.numPoints) + parent.window[2]

                z = self.f(x,y)
                if not parent.inside3D(x,y,z):
                    continue

                matrix[xn][yn] = parent.pixel(x,y,z)
                
        for xn in range(self.numPoints-1):
            for yn in range(self.numPoints-1):
                if matrix[xn][yn][0] is None:
                    continue

                color = getColor(matrix[xn][yn][2], parent.windowAxis[4], parent.windowAxis[5])
                
                if not all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    continue

                render.add3DObject(
                    Triangle(
                        matrix[xn][yn],
                        matrix[xn+1][yn],
                        matrix[xn][yn+1],
                        color=color
                    )
                )
                if not all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    continue

                render.add3DObject(
                    Triangle(
                        matrix[xn+1][yn+1],
                        matrix[xn+1][yn],
                        matrix[xn][yn+1],
                        color=color
                    )
                )


    def legend(self, text:str):
        self.legendText = text
        return self
