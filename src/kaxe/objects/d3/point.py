
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject
from ...core.helper import isRealNumber

# 3d
from ...core.d3.objects import Point3D, Line3D
from ...core.d3.helper import rc
from ...core.color import Colormaps

# packages
import numpy as np
from scipy.spatial import Delaunay


class Points3D(Base3DObject):
    """
    Create 3D points
        
    Parameters
    ----------
    x : list
        List of x-coordinates.
    y : list
        List of y-coordinates.
    z : list
        List of z-coordinates.
    color : Colormap, optional
        ColorMap for colors
    size : int, optional
        Size of the point. Default is 5.
    connect : bool, optional
        Whether the points should be connected. Default is False.
        
    """

    def __init__(self, x, y, z, color:tuple=None, size:int=5, connect:bool=False):
        super().__init__()

        cx, cy, cz = [], [], []
        for i in range(len(x)):

            if isRealNumber(x[i]) and isRealNumber(y[i]):
                cx.append(x[i])
                cy.append(y[i])
                cz.append(z[i])

        self.x = cx
        self.y = cy
        self.z = cz
        
        self.supports = [identities.XYZPLOT]
        self.legendColor = rc()
        self.size = size

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

    
    def finalize(self, parent):

        render = parent.render

        for i in range(len(self.x)):
            if not parent.inside3D(self.x[i], self.y[i], self.z[i]):
                continue
            
            render.add3DObject(
                Point3D(*parent.pixel(self.x[i], self.y[i], self.z[i]), self.size, self.cmap.getColor(self.z[i], parent.windowAxis[4], parent.windowAxis[5]))
            )


    def legend(self, text:str, color=None, symbol=symbols.CIRCLE):
        """
        Adds a legend
        
        Parameters
        ----------
        text : str
            The text to be displayed in the legend.
        symbol : symbols, optional
            The symbol to be used in the legend.
        color : optional
            The color to be used for the legend text. If not provided, the default color will be used.
        
        Returns
        -------
        self : object
            Returns the instance of the arrow object with the updated legend.        
        """
        

        self.legendText = text

        if color:
            self.legendColor = color

        self.legendSymbol = symbol

        return self
