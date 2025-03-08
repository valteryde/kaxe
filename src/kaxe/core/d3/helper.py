
from random import randint
from numba import jit, njit
import numpy as np

def rc() -> tuple:
    """random color"""
    return (randint(0,255), randint(0,255), randint(0,255), 255)

@jit
def magnitude(x):
    return np.sqrt(np.dot(x, x))

@njit
def clamp(v, a, b):
    return min(max(v, a), b)

# @jit
# def isPointInTriangle(v1, v2, v3, pt):
#     d1 = sign(pt, v1, v2)
#     d2 = sign(pt, v2, v3)
#     d3 = sign(pt, v3, v1)
#     has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
#     has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
#     return not(has_neg and has_pos)


#### RENDER IMAGE

from numba import njit
import bisect 
import numpy as np


@njit
def blend_rgba(color1, color2):
    
    r1 = color1[0]
    g1 = color1[1]
    b1 = color1[2]
    a1 = color1[3]
    
    r2 = color2[0]
    g2 = color2[1]
    b2 = color2[2]
    a2 = color2[3]
    
    # Normalize alpha values to [0,1]
    a1 /= 255.0
    a2 /= 255.0
    
    # Compute the output alpha
    out_a = a1 + a2 * (1 - a1)
    
    # Compute the output RGB values
    if out_a == 0:
        return (0, 0, 0, 0)
    
    out_r = (r1 * a1 + r2 * a2 * (1 - a1)) / out_a
    out_g = (g1 * a1 + g2 * a2 * (1 - a1)) / out_a
    out_b = (b1 * a1 + b2 * a2 * (1 - a1)) / out_a
    
    return int(out_r), int(out_g), int(out_b), int(out_a * 255)


# @njit
def addColorToBuffer(zbuffer, colorbuffer, color, x, y, z):
    # 2. Depth Peeling (Order-Independent Transparency)

    # a = [1, 2, 4, 5] 
    # bisect.insort(a, 3) 
    # print(a)

    colorbuffer[y][x] = np.concatenate((colorbuffer[y][x],[color]),axis=0)
    zbuffer[y][x] = np.concatenate((zbuffer[y][x],[z]),axis=0)


# @njit
def renderImage(width, height, colorbuffer, zbuffer, image):
    for y in range(height):
        for x in range(width):
            
            z = np.array(zbuffer[y][x])
            p = z.argsort()
            color = colorbuffer[y][x][p[0]]
            p = z.argsort()[1:]

            for i in p:
                
                color = blend_rgba(color, colorbuffer[y][x][i])
            
            image[y][x] = color
