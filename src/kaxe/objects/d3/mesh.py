

from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Triangle, Line3D, Point3D
from ...core.d3.render import Render
from ...core.d3.helper import rc
from ...core.color import Colormaps, Colormap

# other
import numpy as np
import math

STLLIBIMPORTED = False
try:
    from stl import mesh as stlmesh
    STLLIBIMPORTED = True
except ImportError:
    pass


class Mesh(Base3DObject):
    """
    A class used to represent a 3D Mesh object.
    
    Parameters
    ----------
    mesh: list or array-like
        The mesh object containing the 3D geometry. Contains all verticies data as three points. 
    color: Colormap, optional
        Colormap to display based on average vertices z-value for each triangle.

    Examples
    --------
    >>> mesh = kaxe.Mesh( meshlist )
    >>> plt.add(mesh)
    
    >>> mesh = kaxe.Mesh.open( 'path/to/mesh.stl' )
    >>> plt.add(mesh)

    """
    
    def __init__(self, mesh, color:Colormap=None):
        super().__init__()

        self.mesh = mesh
        self.color = color

        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.RECTANGLE
        self.legendColor = rc()

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

    
    def open(fpath, color:Colormap=None):
        """
        Reads a STL file and creates a Mesh object
        
        Parameters
        ----------
        fpath: str
            file to STL-file. This method relies on the numpy-stl library.
        color: Colormap, optional
            Colormap to display based on average vertices z-value for each triangle.
        
        Returns
        -------
        kaxe.Mesh

        Examples
        --------
        >>> mesh = kaxe.Mesh.open( 'path/to/mesh.stl' )
        >>> plt.add(mesh)

        """

        if not STLLIBIMPORTED:
            raise ImportError('Please ensure that the numpy-stl library is installed')

        return Mesh(stlmesh.Mesh.from_file(fpath), color=color)


    def finalize(self, parent):

        render:Render = parent.render

        for p1, p2, p3 in self.mesh.vectors:
            avgZ = (p1[2] + p2[2] + p3[2]) / 3
            
            if not(parent.inside(*p1) and parent.inside(*p2) and parent.inside(*p3)):
                continue

            color = self.cmap.getColor(avgZ, parent.windowAxis[4], parent.windowAxis[5])
            render.add3DObject(Triangle(parent.pixel(*p1), parent.pixel(*p2), parent.pixel(*p3), color=color))

        del self.mesh
        

    def legend(self, text:str, color=None, symbol=None):
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


        if symbol:
            self.legendSymbol = symbol

        return self


    def getBoundingBox(self):
        """
        gets the bounding box of the mesh

        Returns
        -------
        bbox: list
            [x0, x1, y0, y1, z0, z1]

        """

        bbox = [math.inf, -math.inf, math.inf, -math.inf, math.inf, -math.inf]

        for p1, p2, p3 in self.mesh.vectors:
            bbox = [
                min(bbox[0], p1[0], p2[0], p3[0]),
                max(bbox[1], p1[0], p2[0], p3[0]),
                min(bbox[2], p1[1], p2[1], p3[1]),
                max(bbox[3], p1[1], p2[1], p3[1]),
                min(bbox[4], p1[2], p2[2], p3[2]),
                max(bbox[5], p1[2], p2[2], p3[2]),
            ]
        
        return bbox