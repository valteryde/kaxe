
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject
from ...core.helper import isRealNumber

# 3d
from ...core.d3.objects import Point3D, Line3D
from ...core.d3.helper import rc
from ..color import Colormaps

# packages
import numpy as np
from scipy.spatial import Delaunay


class Points3D(Base3DObject):
    def __init__(self, x, y, z, color:tuple=None, size:int=None, connect:bool=False):
        super().__init__()

        cx, cy, cz = [], [], []
        for i in range(len(x)):

            if isRealNumber(x[i]) and isRealNumber(y[i]):
                cx.append(x[i])
                cy.append(y[i])
                cz.append(y[i])

        self.x = cx
        self.y = cy
        self.z = cz
        
        self.supports = [identities.XYZPLOT]
        self.legendColor = rc()

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

    
    def finalize(self, parent):

        render = parent.render

        for i in range(len(self.x)):
            if not parent.inside3D(self.x[i], self.y[i], self.z[i]):
                continue
            
            render.add3DObject(
                Point3D(*parent.pixel(self.x[i], self.y[i], self.z[i]), 5, self.cmap.getColor(self.z[i], parent.windowAxis[4], parent.windowAxis[5]))
            )


    def legend(self, text:str, color=None, symbol=symbols.CIRCLE):
        self.legendText = text

        if color:
            self.legendColor = color

        self.legendSymbol = symbol

        return self
