
from .mesh import Mesh
from ...core.color import Colormap
import random
from scipy.interpolate import CubicSpline
import math


class Potato(Mesh):
    """
    A class used ...
    
    Parameters
    ----------
    

    Examples
    --------
    

    """
    
    def __init__(self, seed=None, color:Colormap=None):
        """
        from circle down, radius and offset
        spline between two 
        """

        numPointsHorisontal = 10
        spreadHorisontal = 10
        
        numPointsHorisontalRadius = 20
        spreadRadius = 10
        
        height = 10

        x, y = [], []
        for i in range(numPointsHorisontal):
            x.append(i/numPointsHorisontal*height)
            y.append(random.random()*spreadHorisontal - spreadHorisontal/2)
        
        splinetrans = CubicSpline(x, y)

        x, y = [], []
        for i in range(numPointsHorisontalRadius):
            x.append(i/numPointsHorisontalRadius*height)
            y.append(max(random.random()*spreadRadius, spreadRadius//4))

        splineradius = CubicSpline(x, y)
        
        vectors = []

        numPointsHeight = 1000
        dz = height/numPointsHeight
        for i in range(numPointsHeight):
            z = i/numPointsHeight * height

            # create a ring
            numRing = 360
            for i in range(numRing):
                angle = i/numRing * 2*math.pi
                r = splineradius(z)

                x, y = math.sin(angle)*r, math.cos(angle)*r

                x += splinetrans(z)

                dx = .1
                dy = 0

                vectors.append([[x, y, z], [x+dx, y,z], [x+dx,y,z+dz]])

        mesh = Mesh.fromVectors(vectors).mesh

        super().__init__(mesh, color)
    