
from PIL import ImageColor
import math
import numpy as np
from typing import Union


class Colormap:
    def __init__(self, colorGradientSteps:Union[list, tuple]):
        self.colorGradientSteps = colorGradientSteps
        for i, hex in enumerate(colorGradientSteps):
            self.colorGradientSteps[i] = np.array(ImageColor.getcolor(hex, "RGBA"))

    
    def getColor(self, value:Union[int, float], start:Union[int, float], end:Union[int, float]):
        
        x = (value / (end - start)) * (len(self.colorGradientSteps) - 1)
        x0 = math.floor(x)
        x1 = math.ceil(x)

        x -= x0
        return (1 - x) * self.colorGradientSteps[x0] + (x) * self.colorGradientSteps[x1]



class Colormaps:
    standard = Colormap([
        # "#BB7E8C",
        "#AFE3C0",
        "#90C290",
        "#FF5154",
        "#91A6FF",
        # "#FF88DC",
        "#FAFF7F",
        "#ED7D3A",
    ])
