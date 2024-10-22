
from PIL import ImageColor
import math
import numpy as np

colorGradientSteps = [
    # "#BB7E8C",
    "#AFE3C0",
    "#90C290",
    "#FF5154",
    "#91A6FF",
    # "#FF88DC",
    "#FAFF7F",
    "#ED7D3A",
]

for i, hex in enumerate(colorGradientSteps):
    colorGradientSteps[i] = np.array(ImageColor.getcolor(hex, "RGBA"))

def getColor(v, a, b):
    """
    v value
    a start point
    b end point
    """
    
    x = (v / (b - a)) * (len(colorGradientSteps) - 1)
    x0 = math.floor(x)
    x1 = math.ceil(x)

    x -= x0
    return (1 - x) * colorGradientSteps[x0] + (x) * colorGradientSteps[x1]
