
from numpy import array, dot, linalg
from ..helper import magnitude
import math
from numba import jit, njit

@njit
def drawLine(zbuffer, abuffer, p1_proj, p2_proj, p1, p2, R, w, halfwidth:int, index):

    # calculate normal vector
    v = p2_proj - p1_proj
    nx, ny = -v[1], v[0]
    c = -p1_proj[0] * nx - p1_proj[1] * ny

    line_len = magnitude(p2_proj - p1_proj)
    r_line_len = 1/line_len
    d = 1/magnitude(array((nx, ny)))

    rp1 = R @ p1
    rp2 = R @ p2

    x1 = math.floor(min(p1_proj[0], p2_proj[0])) - halfwidth
    x2 = math.ceil(max(p1_proj[0], p2_proj[0])) + halfwidth

    y1 = math.floor(min(p1_proj[1], p2_proj[1])) - halfwidth
    y2 = math.ceil(max(p1_proj[1], p2_proj[1])) + halfwidth

    p1_proj_x, p1_proj_y = p1_proj
    p2_proj_x, p2_proj_y = p2_proj

    AB = p2_proj - p1_proj
    AB_x, AB_y = AB

    BA = p1_proj - p2_proj
    BA_x, BA_y = BA

    d = 1/magnitude(array((nx, ny)))

    for x in range(x1, x2):

        for y in range(y1, y2):

            dot_a = AB_x * (x - p1_proj_x) + AB_y * (y - p1_proj_y)
            dot_b = BA_x * (x - p2_proj_x) + BA_y * (y - p2_proj_y)
            #1.1156

            if dot_a > 0 and dot_b > 0:
            
                dist = abs(nx * x + ny * y + c) * d
                if dist > halfwidth:
                    continue    
                        
                # draw
                alpha = linalg.norm(array((x,y)) - p1_proj) * r_line_len

                if not(-0.25 <= alpha <= 1.25):
                    continue
                    #raise ValueError

                p = rp2 * alpha + rp1 * (1 - alpha)

                z = w - p[2]

                if zbuffer[y][x] > z:
                    abuffer[y][x] = index
                    zbuffer[y][x] = z


            else:

                # possible rounding
                continue


class Line3D:
    def __init__(self, p1, p2, color=(0,0,0,255), width=5):
        self.p1 = array([float(i) for i in p1])
        self.p2 = array([float(i) for i in p2])
        self.width = width
        self.color = color
        self.hidden = False


    def drawTozBuffer(self, render, index):
        if self.hidden: return
        
        drawLine(
            zbuffer=render.zbuffer,
            abuffer=render.abuffer,
            p1_proj=render.pixel(*self.p1), 
            p2_proj=render.pixel(*self.p2), 
            p1=self.p1, 
            p2=self.p2, 
            R=render.camera.R, 
            w=render.camera.w,
            halfwidth=round(self.width/2),
            index=index
        )
    
    def getColor(self, render, x, y):
        return self.color


    def hide(self):
        self.hidden = True