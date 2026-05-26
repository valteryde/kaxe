
from random import randint
import numpy as np


def rc() -> tuple:
    """random color"""
    return (randint(0,255), randint(0,255), randint(0,255), 255)

def magnitude(x):
    return np.sqrt(np.dot(x, x))

def clamp(v, a, b):
    return min(max(v, a), b)

def formatColor(color):
    if len(color) == 3:
        color = [*color, 255]

    return np.array([np.uint8(i) for i in color], dtype=np.int32)
