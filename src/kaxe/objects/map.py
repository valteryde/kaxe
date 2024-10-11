
import numpy as np
from .mapdata import heatcolormap
import math
from ..core.shapes import shapes
from ..core.text import Text
from ..core.round import koundTeX
from ..plot import identities
from typing import Union

def mapTempToColor(col, minColor:Union[float, int], maxColor:Union[float, int], colors:list=heatcolormap):

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
        self.digits = 2

        # max, min
        self.minValue = min([min(row) for row in self.data])
        self.maxValue = max([max(row) for row in self.data])

        self.farLeft = len(data[0])
        self.farRight = 0
        self.farTop = len(data)
        self.farBottom = 0
        
        self.supports = [identities.XYPLOT]

    
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
            
        # scale
        windowHeight = (parent.windowBox[3] - parent.windowBox[1])
        height = int(windowHeight * 0.85)
        
        fontsize = parent.getAttr('fontSize')

        width = fontsize*3
        scaleLeftMargin = fontsize
        scaleStartPos = parent.windowBox[2]+scaleLeftMargin, parent.windowBox[1] + 1/2*windowHeight - height//2

        # spild af CPU her, men nemmere at læse, 
        # altså det ville jo være bedre at lave et billed og bare loade det hver gang
        arr = [[mapTempToColor(self.maxValue - (i / height) * (self.maxValue - self.minValue), self.minValue, self.maxValue) for _ in range(width)] for i in range(height)]

        # bottom text
        self.topText = Text(
            str(koundTeX(round(self.minValue, self.digits))), 
            scaleStartPos[0]+width/2, 
            scaleStartPos[1]-fontsize/4, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='',
            fontSize=fontsize
        )
        
        # top text
        self.bottomText = Text(
            str(koundTeX(round(self.maxValue, self.digits))),
            scaleStartPos[0]+width/2, 
            scaleStartPos[1]+height, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='',
            fontSize=fontsize
        )
        
        self.bottomText.y += self.bottomText.height + fontsize/4

        self.img = shapes.ImageArray(np.array(arr, np.uint8), *scaleStartPos, batch=self.batch)
        parent.addPaddingCondition(right=width+scaleLeftMargin)
        #parent.hasColorScale = True 

    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)