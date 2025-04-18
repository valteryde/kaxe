
from numpy import array
from ..helper import magnitude, formatColor
import math
from numba import njit
from .color import addColorToBuffers

@njit
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



class Point3D:

    def __init__(self, x, y, z, radius, color=(0,0,0,255)):
        self.radius = radius
        self.pos = array((x, y, z))
        self.looks = 0
        self.color = formatColor(color)

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
    