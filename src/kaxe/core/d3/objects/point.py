
from numpy import array
from ..helper import magnitude
import math
from numba import jit, njit

@njit
def drawCircle(zbuffer, abuffer, radius, p_proj, p, R, w, index):

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

            if zbuffer[y][x] > z:
                abuffer[y][x] = index
                zbuffer[y][x] = z



class Point3D:

    def __init__(self, x, y, z, radius, color=(0,0,0,255)):
        self.radius = radius
        self.pos = array((x, y, z))
        self.looks = 0
        self.color = color

    def drawTozBuffer(self, render, index):
        
        drawCircle(
            zbuffer = render.zbuffer, 
            abuffer = render.abuffer, 
            radius  = self.radius, 
            p_proj  = render.pixel(*self.pos), 
            p       = array([float(i) for i in self.pos]), 
            R       = render.camera.R, 
            w       = render.camera.w, 
            index   = index
        )
    
    def getColor(self, render, x, y):
        return self.color