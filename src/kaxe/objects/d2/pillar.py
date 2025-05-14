
from typing import Union
from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities
import numpy as np

class Pillars:
    """
    Different pillars in plots

    This is different from the Bar charts and Group Bar charts. This Object can be 
    inserted into classical plots.
        
    Parameters
    ----------
    x : list or array-like
        The x-coordinates of the center of the pillar.
    heights : list or array-like
        The heights of the pillar at each x-coordinate. 
        If this list contains multiple lists inside, each pillar will consist of 
        multiple colors; This feature is not supported in polar plot.
    color : tuple, optional
        The RGB color of the pillar. If None, a random color is assigned. Default is None.
    width : int, optional
        The width of the pillar. Default is None.
    outlineWidth : int, optional
        The width of the outline around the pillar. Default is 5.
    outlineColor : tuple, optional
        The RGBA color of the outline around the pillar. Default is (0, 0, 0, 255).
        
    See also
    --------
    Bar
    GroupBar
    Histogram

    """

    def __init__(self, x, heights, colors:Union[tuple, list[tuple]]=None, width:int=None, outlineWidth=5, outlineColor:tuple=(0,0,0,255)) -> None:
    
        self.outlineWidth = outlineWidth
        self.outlineColor = outlineColor

        self.x = x
        
        for i in range(len(heights)):
            if type(heights[i]) in [list, tuple]:
                continue
            
            heights[i] = [heights[i]]

        self.heights = heights
        self.width = width

        self.batch = shapes.Batch()
        self.rects = []
        
        # color
        self.randomColor = False
        if colors is None:
            maxColors = max([len(i) for i in heights])
            self.color = [getRandomColor() for i in range(maxColors)]
            self.randomColor = True
        else:
            if not (type(colors[0]) in [list, tuple]):
                colors = [colors]
            self.color = colors

        self.legendColor = self.color[0]
        
        xcopy = list(self.x).copy()
        xcopy.sort()
        try:
            self.farLeft = xcopy[0] - (xcopy[1] - xcopy[0])/2
            self.farRight = xcopy[-1] + (xcopy[-1] - xcopy[-2])/2
        except IndexError:
            pass
        
        self.farTop = 0
        for height in self.heights:
            self.farTop = max(self.farTop, sum(height))
        
        self.farBottom = 0

        self.supports = [identities.XYPLOT, identities.POLAR]

    
    def finalize(self, parent):
        
        if parent.identity == identities.XYPLOT:
            self.finalizeXYPLOT(parent)
        
        elif parent.identity == identities.POLAR:
            self.finalizePOLAR(parent)


    def finalizePOLAR(self, parent):
        
        assert not(list in [type(i[0]) for i in self.heights] or tuple in [type(i[0]) for i in self.heights])

        if self.width is None:
            self.width = 5

        if self.randomColor:
            self.color = list(self.color[0])
            self.color[-1] = 150
            self.color = tuple(self.color)

        for i, angle in enumerate(self.x):
            h = self.heights[i][0]

            shapes.Arc(math.degrees(angle)-90-self.width/2, self.width, parent.pixel(0,0), vlen(vdiff(parent.pixel(0,0), parent.pixel(0, h))), batch=self.batch, color=self.color)


    def finalizeXYPLOT(self, parent):
        
        altwidth, _ = parent.scaled(self.x[1] - self.x[0], 0)
        altwidth += 1

        for i in range(len(self.x)):

            heights = self.heights[i]
            if type(heights) not in [list, tuple]:
                heights = [heights]

            pos = 0
            for j, h in enumerate(heights):
                _, y0 = parent.pixel(0, pos)
                x, y1 = parent.pixel(self.x[i], pos+h)
                height = y1 - y0
                pos += h

                if not parent.inside(x, y1):
                    continue

                options = {'height':height, 'batch':self.batch, 'color':self.color[j], 'outlineWidth':self.outlineWidth, 'outlineColor':self.outlineColor}

                if self.width:
                    self.rects.append(shapes.Rectangle(x - self.width/2, y0, self.width, **options))
                else:
                    self.rects.append(shapes.Rectangle(x - altwidth/2, y0, altwidth, **options))


    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x, y)


    def legend(self, text:str, symbol=symbols.RECTANGLE, color=None):
        """
        Adds a legend
        
        Parameters
        ----------
        text : str
            The text to be displayed in the legend.
        symbol : symbols, optional
            The symbol to be used in the legend.
        color : optional
            The color to be used for the legend text. If not provided, the default color will be used.
        
        Returns
        -------
        self : object
            Returns the instance of the arrow object with the updated legend.        
        
        """
        
        self.legendText = text
        self.legendSymbol = symbol
        if color:
            self.legendColor = color
        return self



class Histogram:

    def __new__(self, data:list, bins:int=5, color:list=None, width:int=None, outlineColor:tuple=(0,0,0,255), outlineWidth=5):
        """
        Create a new instance of the Pillars object with histogram data.
        
        Parameters
        ----------
        data : list
            A list of numerical data to generate the histogram from.
        bins : int, optional
            The number of bins to use for the histogram (default is 5).
        color : list, optional
            A list specifying the color for each pillar (default is None).
        
        Returns
        -------
        Pillars
            A new instance of the Pillars object containing the histogram data.
        
        Notes
        -----
        The method calculates the histogram of the input data using `numpy.histogram`.
        The bin centers are computed as the average of the bin edges.
        """
        
        hist, bin = np.histogram(data, bins=bins, density=True)
        bin = [(bin[i]+bin[i+1])/2 for i in range(len(bin)-1)]
        return Pillars(bin, list(hist), colors=color, width=width, outlineColor=outlineColor, outlineWidth=outlineWidth)
