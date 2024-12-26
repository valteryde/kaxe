
from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities

class Pillars:
    """
    Diffrent pillars in plots

    This is diffrent from the Bar charts and Group Bar charts. This Object can be 
    inserted into classical plots.
        
    Parameters
    ----------
    x : list or array-like
        The x-coordinates of the pillar.
    heights : list or array-like
        The heights of the pillar at each x-coordinate.
    color : tuple, optional
        The RGB color of the pillar. If None, a random color is assigned. Default is None.
    width : int, optional
        The width of the pillar. Default is None.
    
    See also
    --------
    Bar
    GroupBar

    """

    def __init__(self, x, heights, color:tuple=None, width:int=None) -> None:
    

        self.x = x
        self.heights = heights
        self.width = width

        self.batch = shapes.Batch()
        self.rects = []
        
        # color
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color

        #self.size = size

        self.legendColor = self.color
        
        self.farLeft = min(self.x) - 1
        self.farRight = max(self.x) + 1
        self.farTop = max(self.heights)
        self.farBottom = 0

        self.supports = [identities.XYPLOT]

    
    def finalize(self, parent):

        x0, y0 = parent.pixel(0, 0)
        x1, _ = parent.pixel(len(self.x) / (self.farRight - self.farLeft), 0)
        width = (x1 - x0) * 0.75

        for i in range(len(self.x)):

            x, y1 = parent.pixel(self.x[i], self.heights[i])
            height = y1 - y0

            if not parent.inside(x, y1):
                continue

            if self.width:
                self.rects.append(shapes.Rectangle(x - width/2, y0, self.width, height, batch=self.batch, color=self.color))
            else:
                self.rects.append(shapes.Rectangle(x - width/2, y0, width, height, batch=self.batch, color=self.color))

    
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