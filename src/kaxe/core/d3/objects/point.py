
from numpy import array
from ..helper import magnitude, formatColor
import math
from numba import njit, int32, float64
from numba.experimental import jitclass
from .color import addColorToBuffers
import numpy as np
from numba.typed import List
from numba.types import ListType
from .pointer import pointer_type

@njit(cache=True)
def drawCircle(zbuffer, colorbuffer, radius, p_proj, p, R, w, color):

    rp = R @ p
    
    x1 = math.floor(p_proj[0] - radius)
    y1 = math.floor(p_proj[1] - radius)
    x2 = math.ceil(p_proj[0] + radius)
    y2 = math.ceil(p_proj[1] + radius)

    for x in range(x1, x2):

        for y in range(y1, y2):
            pass

            if magnitude(array((x,y)) - p_proj) > radius:
                continue

            z = w - rp[2]

            addColorToBuffers(zbuffer, colorbuffer, y, x, z, color)


@jitclass()
class Point3DNumba:
    x : float64
    y : float64
    z : float64
    radius : float64
    color : int32[:]
    pos : float64[:]
    ableToUseLight : bool
    tp : str
    hidden : bool
    _triangles : ListType(pointer_type)

    def __init__(self, x, y, z, radius, color=np.array((0,0,0,255))):
        self.radius = radius
        self.pos = np.array((x, y, z))
        # self.looks = 0
        self.color = color
        self.ableToUseLight = False
        self._triangles = List.empty_list(pointer_type)
        self.tp = "point3d"
        self.hidden = False
    
    def getRemovableTriangles(self):
        res = []
        for tri in self._triangles:
            res.append(tri.pos)
        self._triangles.clear()
        return res

    def getZ(self, R):
        return (self.pos @ R)[2]

    def draw(self, render):
        
        drawCircle(
            zbuffer     = render.zbuffer, 
            colorbuffer = render.image, 
            radius      = self.radius, 
            p_proj      = render.pixel(*self.pos), 
            p           = array([float(i) for i in self.pos]), 
            R           = render.camera.R, 
            w           = render.camera.w, 
            color       = self.color
        )
    

def Point3D(x, y, z, radius=1, color=(0,0,0,255)):
    """
    Create a 3D point object
    """
    return Point3DNumba(x, y, z, radius, formatColor(color))