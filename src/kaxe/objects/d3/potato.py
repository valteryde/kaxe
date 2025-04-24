
from .mesh import Mesh
from ...core.color import Colormap
import random
from scipy.interpolate import CubicSpline
import math
from types import FunctionType
from typing import Union


class Potato(Mesh):
    """
    A class used to generate a 3D potato-like mesh object by creating a series of rings 
    and interpolating their positions and radii using cubic splines.
    
    Parameters
    ----------
    xposfunc : FunctionType, optional
        A function to define the x-offset of the potato along its height. If None, a random spline is used.
    yposfunc : FunctionType, optional
        A function to define the y-offset of the potato along its height. If None, a random spline is used.
    radiusfunc : FunctionType, optional
        A function to define the radius of the potato along its height. If None, a random spline is used.
    color : Colormap, optional
        The color map to apply to the mesh.
    height : float or int, default=1
        The total height of the potato.
    middelRadius : float or int, default=10
        The average radius of the potato.
    spreadRadius : float or int, default=0.5
        The amount of randomness to apply to the radius.
    spreadHorisontal : float or int, default=10
        The amount of randomness to apply to the horizontal offsets.
    numPointsHeight : int, default=500
        The number of points to sample along the height of the potato.
    numRings : int, default=50
        The number of rings to generate around the potato at each height level.
    Create a potato mesh with default parameters:
    
    Examples
    --------
    >>> potato = kaxe.Potato()
    Create a potato mesh with custom radius and offset functions:

    >>> from scipy.interpolate import CubicSpline
    >>> import numpy as np
    >>> z = np.linspace(0, 1, 10)
    >>> x_offsets = np.sin(z * 2 * np.pi)
    >>> y_offsets = np.cos(z * 2 * np.pi)
    >>> radius = np.linspace(5, 10, 10)
    >>> xposfunc = CubicSpline(z, x_offsets)
    >>> yposfunc = CubicSpline(z, y_offsets)
    >>> radiusfunc = CubicSpline(z, radius)
    >>> potato = Potato(xposfunc=xposfunc, yposfunc=yposfunc, radiusfunc=radiusfunc)
    
    Notes
    -----
    - The mesh is constructed by creating triangular faces between consecutive rings.
    - Randomness is introduced to create an organic, irregular shape.

    """
    
    def __init__(self, 
                xposfunc:FunctionType=None, 
                yposfunc:FunctionType=None, 
                radiusfunc:FunctionType=None, 
                color:Colormap=None,
                height:Union[float, int]=1,
                middelRadius:Union[float, int]=10,
                spreadRadius:Union[float, int]=0.5,
                spreadHorisontal:Union[float, int]=10,
                numPointsHeight:int=500,
                numRings=50
        ):

        numPointsHorisontal = 5
        
        numPointsHorisontalRadius = 30
        crossoverPoints = 5
        
        x, y, z = [], [], []
        for i in range(-1, numPointsHorisontal+1):
            z.append(i/numPointsHorisontal*height)
            x.append(random.random()*spreadHorisontal - spreadHorisontal/2)
            y.append(random.random()*spreadHorisontal - spreadHorisontal/2)
        
        splinetransx = CubicSpline(z, x)
        splinetransy = CubicSpline(z, y)

        if xposfunc:
            splinetransx = xposfunc
        
        if yposfunc:
            splinetransy = yposfunc

        ### RADIUS FUNC
        if not radiusfunc:
            z, radius = [0], [0]
            for i in range(crossoverPoints, numPointsHorisontalRadius-crossoverPoints):
                z.append(i/numPointsHorisontalRadius*height)
                radius.append(middelRadius + (random.random()*spreadRadius - spreadRadius/2))
            
            z.append(height)
            radius.append(0)

            splineradius = CubicSpline(z, radius)
        else:
            splineradius = radiusfunc

        vectors = []

        for i in range(1, numPointsHeight+1):
            z = i/numPointsHeight * height

            # calculate last (previous) lz
            lz = z - 1/numPointsHeight * height

            # create a ring
            for i in range(numRings):
                angle = i/numRings * 2*math.pi
                
                # calculate last point
                # could also be storred but 
                # calculations are pretty quick
                lr = splineradius(lz)
                lx, ly = math.cos(angle)*lr, math.sin(angle)*lr
                lx += splinetransx(lz)
                ly += splinetransy(lz)

                # calculate x,y based on angle and z
                r = splineradius(z)
                if i >= numRings:
                    r = 0
                x, y = math.cos(angle)*r, math.sin(angle)*r
                x += splinetransx(z)
                y += splinetransy(z)

                # calculate next angle
                nangle = angle - 1/numRings * 2*math.pi
                nx, ny = math.cos(nangle)*r, math.sin(nangle)*r
                nx += splinetransx(z)
                ny += splinetransy(z)

                # last next
                lnx, lny = math.cos(nangle)*lr, math.sin(nangle)*lr
                lnx += splinetransx(lz)
                lny += splinetransy(lz)
                
                vectors.append([[lx, ly, lz], [x, y, z], [nx, ny, z]])
                vectors.append([[lx, ly, lz], [lnx, lny, lz], [nx, ny, z]])


        mesh = Mesh.fromVectors(vectors).mesh

        super().__init__(mesh, color)
    

class SolidOfRotation(Potato):
    """
    A class representing a solid of rotation, which is a 3D object generated by rotating 
    a 2D curve (defined by a function) around an axis.
    
    Parameters
    ----------
    func : FunctionType
        A function defining the radius of the solid at a given height.
    a : int or float
        The lower bound of the height range for the solid of rotation.
    b : int or float
        The upper bound of the height range for the solid of rotation.
    numPointsHeight : int, optional
        The number of points used to discretize the height of the solid (default is 1000).
    numRings : int, optional
        The number of rings used to approximate the solid of rotation (default is 180).
    axis : list of int, optional
        The axis of rotation, represented as a 3D vector (default is [0, -1, 0]).
    color : Colormap, optional
        The colormap used to color the solid of rotation (default is None).
    
    Attributes
    ----------
    mesh : Mesh
        The 3D mesh representation of the solid of rotation.
    
    Notes
    -----
    The solid is generated by rotating the given function `func` around the specified axis.
    The rotation is performed by rotating the mesh by 90 degrees around the given axis.
    Examples
    --------
    >>> from some_module import SolidOfRotation
    >>> import math
    >>> solid = SolidOfRotation(
    ...     func=lambda x: math.sin(x),
    ...     a=0,
    ...     b=math.pi,
    ...     numPointsHeight=500,
    ...     numRings=100,
    ...     axis=[0, -1, 0],
    ...     color=None
    ... )
    
    """


    def __init__(self, 
                func:FunctionType, 
                a:Union[int, float], 
                b:Union[int, float],
                numPointsHeight=1000,
                numRings=180,
                axis=[0,-1,0],
                color:Colormap=None
        ):
        
        super().__init__(
            xposfunc=lambda x: 0,
            yposfunc=lambda x: 0,
            radiusfunc=func,
            numPointsHeight=numPointsHeight,
            height=b-a,
            numRings=numRings,
            color=color
        )

        self.mesh.rotate(axis, math.radians(90))
