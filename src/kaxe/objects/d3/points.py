
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Point3D
from ...core.d3.helper import rc
from .color import getColor


class Points3D(Base3DObject):
    def __init__(self, x, y, z, color:tuple=None, size:int=None, symbol:str=symbols.CIRCLE, connect:bool=False):
        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        
        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.CIRCLE
        self.legendColor = rc()

    
    def finalize(self, parent):

        render = parent.render

        for i in range(len(self.x)):
            render.add3DObject(
                Point3D(*parent.pixel(self.x[i], self.y[i], self.z[i]), 5, getColor(self.z[i], 0, 1))
            )


    def legend(self, text:str):
        self.legendText = text
        return self
