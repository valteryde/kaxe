
from PIL import ImageColor
import math
import numpy as np
from typing import Union


class Colormap:
    def __init__(self, colorGradientSteps:Union[list, tuple]):
        self.colorGradientSteps = colorGradientSteps
        for i, phex in enumerate(colorGradientSteps):
            if type(phex) is str:
                self.colorGradientSteps[i] = np.array(ImageColor.getcolor(phex, "RGBA"))

    
    def getColor(self, value:Union[int, float], start:Union[int, float], end:Union[int, float]):
        
        if value < start:
            return self.colorGradientSteps[0]
        if value > end:
            return self.colorGradientSteps[-1]

        x = ((value - start) / (end - start)) * (len(self.colorGradientSteps) - 1)
        x0 = math.floor(x)
        x1 = math.ceil(x)

        x -= x0
        return (1 - x) * self.colorGradientSteps[x0] + (x) * self.colorGradientSteps[x1]


class SingleColormap(Colormap):
    def __init__(self, color, diff=[0.3, 0.7]):

        if type(color) is str:
            color = np.array(ImageColor.getcolor(hex, "RGBA"))

        if len(color) == 3:
            color = np.array((*color, 255))
        
        self.color = color
        self.diff = diff
        len_ = self.diff[1] - self.diff[0]

        n = 10

        arr = [np.array((*(color*(self.diff[0]+len_*(i/n)))[:3], 255)) for i in range(n+1)]
        arr.reverse()

        super().__init__(arr)



class Colormaps:
    standard = Colormap([
        "#AFE3C0",
        "#90C290",
        "#FF5154",
        "#91A6FF",
        "#FAFF7F",
        "#ED7D3A",
    ])
    green = Colormap([
        "#004b23",
        "#006400",
        "#007200",
        "#008000",
        "#38b000",
        "#70e000",
        "#9ef01a",
        "#ccff33"
    ])

    brown = Colormap([
        "#6f1d1b",
        "#bb9457",
        "#432818",
        "#99582a",
        "#ffe6a7"
    ])

    blue = Colormap([
        "#7400b8",
        "#6930c3",
        "#5e60ce",
        "#5390d9",
        "#4ea8de",
        "#48bfe3",
        "#56cfe1",
        "#64dfdf",
        "#72efdd",
        "#80ffdb"
    ])

    yellow = Colormap([
        "#ff7b00",
        "#ff8800",
        "#ff9500",
        "#ffa200",
        "#ffaa00",
        "#ffb700",
        "#ffc300",
        "#ffd000",
        "#ffdd00",
        "#ffea00"
    ])

    cream = Colormap([
        "#780000",
        "#c1121f",
        "#fdf0d5",
        "#003049",
        "#669bbc"
    ])

    red = SingleColormap((255, 0, 0))
