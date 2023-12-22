
from .mapdata import heatcolormap
import math
from ..plot.styles import getRandomColor
# from ..plot.helper import *
from ..plot.shapes import shapes
# from ..plot.symbol import symbol

def mapTempToColor(col, minColor:float|int, maxColor:float|int, colors:list=heatcolormap):

    if -0.005 < minColor - maxColor < 0.005:
        return [*colors[-1], 255]

    n = (col - minColor) / (maxColor - minColor)
    n = (len(colors)-1) * n

    upper = min(math.ceil(n), len(colors)-1)
    lower = max(math.floor(n), 0)

    r = n - lower
    if r < 0:
        return [*colors[lower], 255]

    try:
        c = [
            round(colors[lower][0] + (colors[upper][0] - colors[lower][0])*r),
            round(colors[lower][1] + (colors[upper][1] - colors[lower][1])*r),
            round(colors[lower][2] + (colors[upper][2] - colors[lower][2])*r),
            255
        ]

    except IndexError:
        return [*colors[-1], 255]

    return c


class ColorMap:
    def __init__(self, data):
        self.batch = shapes.Batch()
        
        self.data = data

        # max, min
        self.minValue = min([min(row) for row in self.data])
        self.maxValue = max([max(row) for row in self.data])

        self.farLeft = len(data[0])
        self.farRight = 0
        self.farTop = len(data)
        self.farBottom = 0

    
    def finalize(self, parent):
        
        width, height = parent.scaled(1, 1)
        width, height = math.ceil(width), math.ceil(height)
        for rowNum, row in enumerate(self.data):

            for cellNum, cell in enumerate(row):
                
                shapes.Rectangle(
                    *parent.pixel(cellNum, rowNum), 
                    width, height,
                    color=tuple(mapTempToColor(cell, self.minValue, self.maxValue)), 
                    batch=self.batch
                )


    def push(self, x, y):
        self.batch.push(x, y)

    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)