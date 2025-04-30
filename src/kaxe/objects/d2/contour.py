

from ...core.styles import *
from ...core.shapes import shapes
# from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities
from .equation import Equation
from types import FunctionType
from typing import Union
from ...core.color import Colormaps, Colormap


class Contour:
    """
    A class used to represent a Contour.
    
    Parameters
    ----------
    func3D : FunctionType
        A function that represents the 3D function to be contoured.
    a : Union[int, float], optional
        The starting value for the contour range (default is -20).
    b : Union[int, float], optional
        The ending value for the contour range (default is 20).
    steps : Union[int, float], optional
        The number of steps in the contour (default is 15).
    colorMap : Colormap, optional
        The colormap to be used for the contour (default is None, which uses the standard colormap).
    lineThickness : int, optional
        The thickness of the contour lines (default is 10).
    computePadding: int, optional
        When generating the contour equations some padding can be needed to include the edges properly (default is 50).
        
    Examples
    --------
    >>> def example_func(x, y):
    >>>     return x**2 + y**2
    >>> contour = Contour(example_func)
    >>> plt.add(contour)

    """
    
    def __init__(self, func3D:FunctionType, a:Union[int, float]=-20, b:Union[int, float]=20, steps:Union[int, float]=15, colorMap:Colormap=None, lineThickness:int=2, computePadding:int=50):
        self.batch = shapes.Batch()
    
        self.func = func3D
        self.a = a
        self.b = b
        self.steps = steps

        self.lineThickness = lineThickness
    
        # color
        if colorMap is None:
            self.color = Colormaps.standard
        else:
            self.color = colorMap
    
        self.legendColor = self.color.getColor(5, -10, 10)

        self.supports = [identities.XYPLOT, identities.POLAR, identities.XYZPLOT]

        self.__equations = []

        self.computePadding = computePadding

    
    def finalize(self, parent):

        for i in range(self.steps):
            z = self.a + (self.b - self.a) * i/self.steps

            eq = Equation(lambda *args: z, self.func, color=self.color.getColor(z, self.a, self.b), width=self.lineThickness, computePadding=self.computePadding)
            eq.finalize(parent)
            self.__equations.append(eq)

    
    def push(self, x, y):
        for eq in self.__equations:
            eq.push(x, y)

    
    def draw(self, surface):
        for eq in self.__equations:
            eq.draw(surface)


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
