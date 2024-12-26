
from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities

class Arrow:
    """
    A class to represent an arrow with customizable properties such as color, head size, and line thickness.
    
    Supported in the classical plots

    Parameters
    ----------
    p0 : tuple
        The starting point of the arrow.
    p1 : tuple
        The ending point of the arrow.
    color : tuple, optional
        The color of the arrow in RGBA format. If None, a random color is assigned (default is None).
    headSize : int, optional
        The size of the arrowhead (default is 42).
    lineThickness : int, optional
        The thickness of the arrow line (default is 10).
    
    Examples
    --------
    >> plt.add( kaxe.Arrow((0,0), (1,1)) )

    """
    
    def __init__(self, p0, p1, color:tuple=None, headSize:int=42, lineThickness:int=10):
        self.batch = shapes.Batch()
    
        self.p0 = p0
        self.p1 = p1

        self.lineThickness = lineThickness
        self.headSize = headSize
    
        # color
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
    
        self.legendColor = self.color

        self.supports = [identities.XYPLOT, identities.POLAR]

    
    def finalize(self, parent):

        pixel0 = parent.pixel(*self.p0)
        pixel1 = parent.pixel(*self.p1)
    
        v = vdiff(pixel1, pixel0)
        v = vectorScalar(v, 1/vlen(v))

        n = (-v[1], v[0])

        arrowSize = self.headSize * 0.75
        arrowDownHeight = self.headSize

        p1 = (pixel1[0] - 2 * arrowSize * v[0], pixel1[1] - 2 * arrowSize * v[1])
        p2 = (pixel1[0] + arrowSize * n[0] + arrowDownHeight * v[0], pixel1[1] + arrowSize * n[1] + arrowDownHeight * v[1])
        p3 = (pixel1[0] - arrowSize * n[0] + arrowDownHeight * v[0], pixel1[1] - arrowSize * n[1] + arrowDownHeight * v[1])

        offset = vdiff(pixel1, p1)

        pixel1 = vdiff(offset, pixel1)

        shapes.Triangle(
            vdiff(offset, p1), vdiff(offset, p2), pixel1,
            color=self.color, 
            batch=self.batch,
        )
        shapes.Triangle(
            vdiff(offset, p1), vdiff(offset, p3), pixel1,
            color=self.color, 
            batch=self.batch,
        )

        shapes.Line(*pixel0, *pixel1, width=self.lineThickness, color=self.color, batch=self.batch)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x, y)


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