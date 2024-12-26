

from .d2.point import Points2D
from .d3.point import Points3D
from typing import Union, Callable
from inspect import signature
from ..core.symbol import symbol as symbols
from .color import Colormap

# 2d
# self, x, y, color:tuple=None, size:int=None, symbol:str=symbols.CIRCLE, connect:bool=False
# 3d har ikke symbol

class Points:
    """
    Points to be added to any plot type
    
    Parameters
    ----------
    x : array-like
        X coordinates of the points.
    y : array-like
        Y coordinates of the points.
    z : array-like, optional
        Z coordinates of the points for 3D plots. Default is None.
    color : Union[tuple, Colormap], optional
        Color of the points. Default is None.
    size : int, optional
        Size of the points. Default is None.
    symbol : str, optional
        Symbol used for the points. Default is symbols.CIRCLE.
    connect : bool, optional
        Whether to connect the points with lines. Default is False.

    Returns
    -------
    Object : Points2D|Points3D
        Correct points class based on the parameters
    
    See also
    --------
    kaxe.Points2D
    kaxe.Points3D
    """

    def __new__(self, 
                 x, y, 
                 z = None,
                 color:Union[tuple, Colormap]=None, 
                 size:int=None, 
                 symbol:str=symbols.CIRCLE, 
                 connect:bool=False                 
                ) -> Union[Points2D, Points3D]:
    
        if z:
            return Points3D(x, y, z, color=color, size=size, connect=connect)
        return Points2D(x, y, color=color, size=size, symbol=symbol, connect=connect)
