
import numpy as np
from ..mapdata import heatcolormap
import math
from ...core.shapes import shapes
from ...core.text import Text
from ...core.round import koundTeX
from ...plot import identities
from typing import Union
from ...core.color import Colormaps


class ColorScale:
    """
    ColorScale to be added in the right middle of the window

    Supports all plots

    Parameters
    ----------
    lower : Union[float, int, tuple]
        The lower bound of the color scale. Can be a number or a tuple of length 2 with value and title as values.
    upper : Union[float, int, tuple]
        The upper bound of the color scale. Can be a number or a tuple of length 2 with value and title as values.
    cmap : Colormaps, optional
        The colormap to use for the color scale. Default is Colormaps.standard.
    width : Union[int, None], optional
        The width of the color scale. Default is None.

    """

    def __init__(self, lower:Union[float, int, tuple], upper:Union[float, int, tuple], cmap=Colormaps.standard, width:Union[int, None]=None):
        """
        lower and upper can both be a number or a tuple of length 2 with value and title as values
        """
        self.digits = 2

        if type(lower) in [list, tuple]:
            self.lower = lower[0]
            self.lowerTitle = lower[1]
        else:
            self.lower = lower
            self.lowerTitle = str(koundTeX(round(self.lower, self.digits)))

        if type(upper) in [list, tuple]:
            self.upper = upper[0]
            self.upperTitle = upper[1]
        else:
            self.upper = upper
            self.upperTitle = str(koundTeX(round(self.upper, self.digits)))

        self.cmap = cmap
        self.supports = [identities.XYPLOT, identities.XYZPLOT]
        self.batch = shapes.Batch()
        self.width = width


    def finalize(self, parent):
        fontsize = parent.getAttr('fontSize')
        leftMargin = fontsize # TODO: Style

        windowHeight = parent.windowBox[3] - parent.windowBox[1]
        height = int(windowHeight * 0.8)

        if not self.width:
            self.width = fontsize*2
        
        width = self.width # doven

        self.pos = (parent.windowBox[2], parent.padding[1] + windowHeight//2 - height//2)

        # spild af CPU her, men nemmere at læse, 
        # altså det ville jo være bedre at lave et billed og bare loade det hver gang
        arr = [self.cmap.getColor(self.upper - (i / height) * (self.upper - self.lower), self.lower, self.upper) for i in range(height)]
        arr = [[i]*width for i in arr]

        
        # bottom text
        self.lowerText = Text(
            self.lowerTitle, 
            0, 
            0, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='top',
            fontSize=fontsize
        )
        
        self.lowerText.setLeftTopPos(self.pos[0]+width/2-self.lowerText.width//2, self.pos[1])


        # top text
        self.upperText = Text(
            self.upperTitle,
            self.pos[0]+width/2, 
            self.pos[1]+height, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='',
            fontSize=fontsize
        )

        # add margin between text and axis        
        self.upperText.push(0, fontsize/8)
        self.lowerText.push(0, -fontsize/8)

        # parent.addPaddingCondition(right=width+scaleLeftMargin)

        self.img = shapes.ImageArray(np.array(arr, np.uint8), *self.pos, batch=self.batch)
        
        # add space
        lx, ly = self.lowerText.getLeftTopPos()
        ux, uy = self.upperText.getLeftTopPos()

        mx = min(lx, ux, self.pos[0])
        off = self.pos[0] - mx

        # add margin
        self.batch.push(leftMargin+off, 0)



        parent.include(self.pos[0]+width/2, self.pos[1]+height/2, width, height)
        parent.includeElement(self.upperText)
        parent.includeElement(self.lowerText)
        #parent.hasColorScale = True


    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


class HeatMap:
    """
    A class to represent a heatmap visualization.
    
    Parameters
    ----------
    data : list of list of float or int
        A 2D list containing the data values for the heatmap.
    cmap : Colormap, optional
        A colormap instance to map data values to colors (default is Colormaps.standard).
    """

    def __init__(self, data, cmap=Colormaps.standard):
        self.batch = shapes.Batch()
        self.cmap = cmap
        
        self.data = data

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
                    color=self.cmap.getColor(cell, self.minValue, self.maxValue), 
                    batch=self.batch
                )
        
    
    def addColorScale(self, parent):
        """
        Add a color scale to the parent
        """

        parent.add(ColorScale(self.minValue, self.maxValue, cmap=self.cmap))
        
        return self


    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)