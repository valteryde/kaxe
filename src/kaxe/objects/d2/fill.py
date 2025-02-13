
from ...core.styles import *
from ...core.symbol import symbol as symbols
from ...plot import identities
from ...core.shapes import shapes
from types import FunctionType
from typing import Union


class Fill:
    """
    A class used to represent a Fill between two functions.
    
    Parameters
    ----------
    f : FunctionType
        First function to fill between
    g : FunctionType, optional
        Second function to fill between. If None is given `g(x)=0` is used.
    color : Union[list, tuple], optional
        Color of the fill. If None, a random color with transparency is used.
            
    Examples
    --------
    >>> f = lambda x: x**2
    >>> g = lambda x: x
    >>> fill = kaxe.Fill(f, g)
    >>> plt.add( fill )
    
    See also
    --------
    `kaxe.Function2D().fill()`

    Notes
    -----
    When a fill is not wanted set create f(x) and g(x) so `f(x)=g(x)` in the wished interval
    This object can also be used to fill between discrete points but the user will have to create the function. This could be achived through Zero-order-hold, interpolation or regression.
    
    """
    
    def __init__(self, f:FunctionType, g:FunctionType=None, color:Union[list, tuple]=None):
        self.batch = shapes.Batch()
    
        self.f = f
        
        if g is None:
            g = lambda x: 0

        self.g = g

        # color
        if color is None:
            self.color = list(getRandomColor())
            if len(self.color) > 3:
                self.color[3] = 100
            else:
                self.color.append(100)
            self.color = tuple(self.color)
        else:
            self.color = color
    
        self.legendColor = self.color

        self.supports = [identities.XYPLOT]

    
    def finalize(self, parent):

        fills = []

        buffer = []

        isfOverg = None

        for n in range(parent.windowBox[0], parent.windowBox[2]):
        
            x, _ = parent.inversepixel(n,0)
            
            try:
                yf = self.f(x)
                yg = self.g(x)
            except Exception:
                continue

            if yf == yg:
                continue
            
            # kører kun første gang loopet starter
            if isfOverg is None:
                isfOverg = yf > yg

            buffer.append((x, yf, yg))

            # skifter de rolle
            if (yf < yg) == isfOverg:
                fills.append([i for i in buffer]) # shallow copy
                buffer = []
                isfOverg = not isfOverg
        
        fills.append(buffer)

        for fill in fills:

            top = [parent.clamp(*parent.pixel(x, yf)) for x, yf, yg in fill]
            bottom = [parent.clamp(*parent.pixel(x, yg)) for x, yf, yg in fill]

            bottom.reverse()

            shapes.Polygon(*top, *bottom, color=self.color, batch=self.batch)

    
    def push(self, x, y):
        self.batch.push(x, y)

    
    def draw(self, surface):
        self.batch.draw(surface)


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





