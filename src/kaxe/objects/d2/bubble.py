

from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.text import Text
from ...core.helper import *
from ...plot import identities

class Bubble:
    """
    A class to represent a bubble with text and a line pointing to it.

    Parameters
    ----------
    text : str
        The text to be displayed inside the bubble.
    centerPos : tuple
        The (x, y) coordinates of the center position of the bubble.
    lineEndPos : tuple
        The (x, y) coordinates of the end position of the line pointing to the bubble.
    color : tuple, optional
        The color of the bubble in RGB format, by default BLACK.
    lineThickness : int, optional
        The thickness of the line pointing to the bubble, by default 5.
    fontSize : int, optional
        The font size of the text inside the bubble, by default 32.

    Examples
    --------
    >>> plt.add( Bubble("kaxe is cool", (0,1), (2, 5)) )
    """
    
    def __init__(self, text:str, centerPos, lineEndPos, color:tuple=BLACK, lineThickness:int=5, fontSize:int=32):

        self.batch = shapes.Batch()
    
        self.centerPos = centerPos
        self.lineEndPos = lineEndPos
        self.text = str(text)
        self.fontSize = fontSize

        self.lineThickness = lineThickness

        self.color = color

        self.legendColor = self.color
        self.supports = [identities.XYPLOT, identities.POLAR]

    
    def finalize(self, parent):
        
        centerpos = parent.pixel(*self.centerPos)

        text = Text(self.text, *centerpos, self.fontSize)
        size = max(text.width, text.height) / 2

        line = shapes.Line(*centerpos, *parent.pixel(*self.lineEndPos), color=self.color, batch=self.batch, width=self.lineThickness*2)
        outerCircle = shapes.Circle(*centerpos, size+2*self.lineThickness, color=self.color, batch=self.batch)
        innerCircle = shapes.Circle(*centerpos, size+self.lineThickness, color=WHITE, batch=self.batch)

        # instead of draw and push
        parent.addDrawingFunction(self.batch)
        parent.addDrawingFunction(text)



    def draw(self, *args, **kwargs):
        pass#self.batch.draw(*args, **kwargs)

    def push(self, x, y):
        pass#self.batch.push(x, y)


    def legend(self, text:str, symbol=symbols.LINE, color=None):
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

