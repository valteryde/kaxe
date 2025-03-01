
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
