
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Triangle, Line3D, Point3D
from ...core.d3.helper import rc
from ...core.color import Colormaps, Colormap

# other
import numpy as np
import math
import numbers
from numba import njit
import time



### OPTIMIZING
@njit
def getTriangleNormal(p1, p2, p3):

    Ax, Ay, Az = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    Bx, By, Bz = p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]

    Nx = Ay * Bz - Az * By
    Ny = Az * Bx - Ax * Bz
    Nz = Ax * By - Ay * Bx

    return (Nx, Ny, Nz)

@njit
def isHorizontalTriangle(dependantVariable, p1, p2, p3):
    normal = getTriangleNormal(p1, p2, p3)

    if dependantVariable == "z":
        return (
            np.isclose(normal[0], 0) and 
            np.isclose(normal[1], 0) and 
            (not np.isclose(normal[2], 0))
        )
    elif dependantVariable == "y":
        return (
            np.isclose(normal[0], 0) and 
            (not np.isclose(normal[1], 0)) and 
            np.isclose(normal[2], 0)
        )
    elif dependantVariable == "x":
        return (
            (not np.isclose(normal[0], 0)) and 
            np.isclose(normal[1], 0) and 
            np.isclose(normal[2], 0)
        )










class Function3D(Base3DObject):
    """
    Create a Function in 3D given .. math:: z=f(x,y)
    
    Parameters
    ----------
    f : callable
        The function to be plotted.
    color : Colormap, optional
        The colormap to be used for plotting. If None, the standard colormap is used.
    numPoints : int, optional
        The number of points to be used for plotting. If None, defaults to 500 if `fill` is True, otherwise 25.
    fill : bool
        Whether to fill the plot. default is True
    drawDiagonalLines: bool
        Whether to draw diagonal lines in triangles when fill is False. default is False
    excludeLight : bool, optional
        Whether to exclude lighting effects. Default is True.
    
    Methods
    -------
    __call__(x)
        Evaluates the function at a given x value.

    """
    
    def __init__(self, 
                 f, 
                 color:Colormap=None, 
                 numPoints:int=None, 
                 fill:bool=True, 
                 drawDiagonalLines:bool=False, 
                 axis="xy", 
                 excludeLight=True,
                 *args, 
                 **kwargs
        ):
        
        super().__init__()

        self.f = f
        self.axis = ''.join(sorted(axis)) #xy, xz, yz
        self.dependantVariable = "xyz".replace(self.axis[0], '').replace(self.axis[1], '')
        self.otherArgs = args
        self.otherKwargs = kwargs
        self.excludeLight = excludeLight

        self.fill = fill
        self.drawDiagonalLines = drawDiagonalLines
        
        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.RECTANGLE
        self.legendColor = rc()

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

        self.numPoints = numPoints
        if numPoints is None and fill:
            self.numPoints = 500
        elif numPoints is None:
            self.numPoints = 25


    

    def __addTriangle__(self, render, p1, p2, p3, color, isRealpoint):
        
        # dont draw vertical vertices
        if isHorizontalTriangle(self.dependantVariable, p1, p2, p3) and not isRealpoint:
            return

        render.add3DObject(
            Triangle(
                p1,
                p2,
                p3,
                color=color,
                ableToUseLight=not self.excludeLight
            )
        )


    def __fill__(self, render, matrix, xn, yn, color, isRealpoint):
        
        if all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):
            
            self.__addTriangle__(render, matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1], color, isRealpoint)

        if all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    
            self.__addTriangle__(render, matrix[xn+1][yn], matrix[xn+1][yn+1], matrix[xn][yn+1], color, isRealpoint)
        

    def __addTriangleOutline__(self, render, p1, p2, p3, color, isRealpoint, xn, yn):
        
        # dont draw vertical vertices
        if isHorizontalTriangle(self.dependantVariable, p1, p2, p3) and not isRealpoint:
            return

        render.add3DObject(Line3D(p1,p2,color=color))
        
        if self.drawDiagonalLines:
            render.add3DObject(Line3D(p1,p3,color=color))
            render.add3DObject(Line3D(p2,p3,color=color))
            return
        
        # Correcting for not drawing diagonals
        # Here the parrallel lines will have an perpendicalur lines at the end at x=len(self.numPoints) and so on
        if xn == self.numPoints-1:
            render.add3DObject(Line3D(p2,p3,color=color))
        
        if yn == 0:
            render.add3DObject(Line3D(p1,p3,color=color))


    def __outline__(self, render, matrix, xn, yn, color, isRealpoint):
        if all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):

            self.__addTriangleOutline__(render, matrix[xn][yn], matrix[xn][yn+1],matrix[xn+1][yn], color, isRealpoint, -1, yn)
        
        if all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
            
            self.__addTriangleOutline__(render, matrix[xn][yn+1], matrix[xn+1][yn+1], matrix[xn+1][yn], color, isRealpoint, xn, -1)


    def finalize(self, parent):

        render = parent.render

        self.points = []
        xlen = parent.window[1] - parent.window[0]
        ylen = parent.window[3] - parent.window[2]
        zlen = parent.window[5] - parent.window[4]

        matrix = np.empty((self.numPoints+1, self.numPoints+1), dtype=tuple)
        matrix.fill(np.array((None, None, None)))
        
        zmap = np.empty((self.numPoints+1, self.numPoints+1), dtype=float)
        zmap.fill(-math.inf)

        realpoint = np.empty((self.numPoints+1, self.numPoints+1), dtype=bool)
        realpoint.fill(True)
        
        # get points in plane
        if self.dependantVariable == "z":
            gx = lambda xn: xlen * (xn / self.numPoints) + parent.window[0]
            gy = lambda yn: ylen * (yn / self.numPoints) + parent.window[2]
        elif self.dependantVariable == "y":
            gx = lambda xn: xlen * (xn / self.numPoints) + parent.window[0]
            gy = lambda yn: zlen * (yn / self.numPoints) + parent.window[4]
        else:
            gx = lambda yn: zlen * (yn / self.numPoints) + parent.window[4]
            gy = lambda xn: ylen * (xn / self.numPoints) + parent.window[2]

        for xn in range(self.numPoints+1):
            x = gx(xn)

            for yn in range(self.numPoints+1):
                y = gy(yn)

                try:
                    z = self.f(x,y, *self.otherArgs, **self.otherKwargs)
                except Exception:
                    continue
                                
                if not isinstance(z, numbers.Number):
                    continue

                # Check if point is outside maximum z value
                if self.dependantVariable == "z": #xy
                    if z > parent.window[5]:
                        z = parent.window[5]
                        realpoint[xn][yn] = False

                    if z < parent.window[4]:
                        z = parent.window[4]
                        realpoint[xn][yn] = False
                    
                    matrix[xn][yn] = parent.pixel(x,y,z)
                    zmap[xn][yn] = z
                
                elif self.dependantVariable == "y": #xz
                    if z > parent.window[3]:
                        z = parent.window[3]
                        realpoint[xn][yn] = False

                    if z < parent.window[2]:
                        z = parent.window[2]
                        realpoint[xn][yn] = False

                    matrix[xn][yn] = parent.pixel(x,z,y)
                    zmap[xn][yn] = y
                
                elif self.dependantVariable == "x": #yz
                    if z > parent.window[1]:
                        z = parent.window[1]
                        realpoint[xn][yn] = False

                    if z < parent.window[0]:
                        z = parent.window[0]
                        realpoint[xn][yn] = False
                
                    matrix[xn][yn] = parent.pixel(z, y, x)
                    zmap[xn][yn] = x

        # draw
        for xn in range(self.numPoints):
            for yn in range(self.numPoints):
                if matrix[xn][yn][0] is None:
                    continue
                
                color = self.cmap.getColor(zmap[xn][yn], parent.windowAxis[4], parent.windowAxis[5])

                if self.fill:
                    self.__fill__(render, matrix, xn, yn, color, realpoint[xn][yn])
                else:
                    self.__outline__(render, matrix, xn, yn, color, realpoint[xn][yn])

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


    def __call__(self, x, y):
        return self.f(x, y, *self.otherArgs, **self.otherKwargs)