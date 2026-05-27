
from random import randint
import numpy as np
from ..color import to_rgba


def rc() -> tuple:
    """random color"""
    return (randint(0,255), randint(0,255), randint(0,255), 255)

def magnitude(x):
    return np.sqrt(np.dot(x, x))

def clamp(v, a, b):
    return min(max(v, a), b)

def formatColor(color):
    return np.array([np.uint8(i) for i in to_rgba(color)], dtype=np.int32)
