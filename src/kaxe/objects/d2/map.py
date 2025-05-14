
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
        self.digits = 200

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
    unitPerPixel : list of float, optional
        A list containing the width and height of each pixel in the heatmap in terms of the unit space (default is [1, 1]).
    position : list or tuple, optional
        The (x, y) position of the bottom-left corner of the heatmap in the unit space (default is (0, 0)).
    minValue : float or int, optional
        The minimum value for the heatmap. If not provided, it is calculated from the data.
    maxValue : float or int, optional
        The maximum value for the heatmap. If not provided, it is calculated from the data.
    """

    def __init__(self, 
                data,
                cmap=Colormaps.standard, 
                unitPerPixel:list[float]=[1,1],
                position:Union[list, tuple]=(0,0),
                minValue = None,
                maxValue = None
        ):
        
        self.batch = shapes.Batch()
        self.cmap = cmap
        
        self.data = data
        self.unitPerPixel = unitPerPixel
        self.position = position

        # max, min
        if minValue:
            self.minValue = minValue
        else:
            self.minValue = min([min(row) for row in self.data])

        if maxValue:
            self.maxValue = maxValue
        else:
            self.maxValue = max([max(row) for row in self.data])

        self.farLeft = len(data[0]) * self.unitPerPixel[0]
        self.farRight = position[0]
        self.farTop = len(data) * self.unitPerPixel[1]
        self.farBottom = position[1]
        
        self.supports = [identities.XYPLOT]

    
    def finalize(self, parent):

        # get size of one box
        width, height = parent.scaled(*self.unitPerPixel)
        width, height = math.ceil(width), math.ceil(height)

        for rowNum, row in enumerate(self.data):

            for cellNum, cell in enumerate(row):
                
                p = parent.pixel(
                    cellNum*self.unitPerPixel[0] + self.position[0], 
                    rowNum*self.unitPerPixel[1] + self.position[1]
                )
                if not parent.inside(*p): continue

                w, h = width, height
                p1 = parent.inversepixel(p[0]+w, p[1]+h)
                p1 = parent.pixel(p1[0], p1[1])
                if not parent.inside(*p1):
                    p1 = parent.clamp(*p1)
                    w = p1[0] - p[0]
                    h = p1[1] - p[1]

                    if w == 0 or h == 0:
                        continue
            
                shapes.Rectangle(
                    *p, math.ceil(w), math.ceil(h),
                    color=self.cmap.getColor(cell, self.minValue, self.maxValue), 
                    batch=self.batch
                )
        
    
    def addColorScale(self, parent, digits=64):
        """
        Adds a color scale to the specified parent object.

        This method creates a `ColorScale` object using the instance's minimum 
        and maximum values (`self.minValue` and `self.maxValue`) and colormap 
        (`self.cmap`), then adds it to the provided parent object.

        Parameters
        ----------
        parent : object
            The object to which the color scale will be added. It must 
            have an `add` method that accepts a `ColorScale` object.
        digits : int
            Number of digits to display

        Returns
        -------
        HeatMap
            The instance of the class, allowing for method chaining.
        """
        
        parent.add(ColorScale(round(self.minValue, digits), round(self.maxValue, digits), cmap=self.cmap))
        
        return self


    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)