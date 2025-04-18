
import math
from numpy import array, sqrt, dot, uint8, cross
from numba import njit
from ..helper import clamp, formatColor
from .color import addColorToBuffers


@njit
def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


@njit
def barycentricWeights(a,b,c,p):
    bottom = sign(a,b,c)

    if bottom == 0:
        return -1, -1, -1

    w1 = ((b[1] - c[1])*(p[0] - c[0]) + (c[0] - b[0])*(p[1] - c[1])) / bottom
    w2 = ((c[1] - a[1])*(p[0] - c[0]) + (a[0] - c[0])*(p[1] - c[1])) / bottom

    return w1, w2, 1 - w1 - w2


@njit
def drawTriangle(zbuffer, 
                 colorbuffer, 
                 R, 
                 w, 
                 p1, 
                 p2, 
                 p3, 
                 p1_proj,
                 p2_proj,
                 p3_proj,
                 color,
                 lightDirection,
                 useLight
                 ):

    rp1 = R @ p1
    rp2 = R @ p2
    rp3 = R @ p3

    if useLight:
        v1, v2 = rp2 - rp1, rp3 - rp1

        # Compute and normalize the normal vector
        normal = cross(v1, v2)
        normal = normal / sqrt(dot(normal, normal))

        # Compute view direction
        view_dir = array([0,0, w]) - rp1
        view_dir = view_dir / sqrt(dot(view_dir, view_dir))

        # Return the normal that faces the camera
         
        if dot(normal, view_dir) < 0:
            normal = -normal
        
        intensity = dot(normal, lightDirection)
        intensity = 2.559523810*intensity**3 - 5.232142857*intensity**2 + 3.672619048*intensity
        intensity = clamp(intensity, 0, 1)

        color = array([
            uint8(clamp(color[0] * intensity, 0, 255)),
            uint8(clamp(color[1] * intensity, 0, 255)),
            uint8(clamp(color[2] * intensity, 0, 255)),
            uint8(color[3])
        ])

    min_ = (math.floor(min(p1_proj[0], p2_proj[0], p3_proj[0])), math.floor(min(p1_proj[1], p2_proj[1], p3_proj[1])))
    max_ = (math.ceil(max(p1_proj[0], p2_proj[0], p3_proj[0])), math.ceil(max(p1_proj[1], p2_proj[1], p3_proj[1])))

    min_ = (clamp(min_[0], 0, len(colorbuffer[0])), clamp(min_[1], 0, len(colorbuffer)))
    max_ = (clamp(max_[0], 0, len(colorbuffer[0])), clamp(max_[1], 0, len(colorbuffer)))

    for x in range(min_[0], max_[0]):

        for y in range(min_[1], max_[1]):
                
            k1, k2, k3 = barycentricWeights(p1_proj, p2_proj, p3_proj, (x,y))

            if k1 < 0 or k2 < 0 or k3 < 0:
                continue

            # skal være afstand fra kamera til position
            # påfør rotationsmatrix på positionen
            # self.__calcRotatedVector__()
            
            z = rp1[2] * k1 + rp2[2] * k2 + rp3[2] * k3

            z = w - z

            addColorToBuffers(zbuffer, colorbuffer, y, x, z, color)


class Triangle:
    def __init__(self, p1, p2, p3, color=(0,0,0,255), ableToUseLight=True):
        self.p1 = array([float(i) for i in p1])
        self.p2 = array([float(i) for i in p2])
        self.p3 = array([float(i) for i in p3])
        self.color = formatColor(color)
        self.ableToUseLight = ableToUseLight
        self.__hidden__ = False


    def hide(self):
        self.__hidden__ = True

    def show(self):
        self.__hidden__ = False


    def getZ(self, R):
        return ((R @ self.p1)[2] + (R @ self.p2)[2] + (R @ self.p3)[2]) / 3

    def draw(self, render):
        if self.__hidden__: return

        self.p1_proj = render.pixel(*self.p1)
        self.p2_proj = render.pixel(*self.p2)
        self.p3_proj = render.pixel(*self.p3)
        drawTriangle(
            zbuffer        = render.zbuffer,
            colorbuffer    = render.image,
            R              = render.camera.R,
            w              = render.camera.w,
            p1             = self.p1,
            p2             = self.p2,
            p3             = self.p3,
            p1_proj        = self.p1_proj,
            p2_proj        = self.p2_proj,
            p3_proj        = self.p3_proj,
            color          = self.color,
            lightDirection = render.lightDirection,
            useLight       = render.useLight and self.ableToUseLight
        )
    