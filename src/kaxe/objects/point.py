

from .d2.point import Points2D
from .d3.point import Points3D
from typing import Union, Callable
from inspect import signature
from ..core.symbol import symbol as symbols
from ..core.color import Colormap

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
    **kwargs
        Additional keyword arguments. For the appropiate keyworks see arguments for Points2D and Points3D.

    Returns
    -------
    Object : Points2D|Points3D
        Correct points class based on the parameters
    
    See also
    --------
    kaxe.Points2D
    kaxe.Points3D
    """

    def __new__(self, x, y, z = None, **kwargs) -> Union[Points2D, Points3D]:
    
        if z:
            return Points3D(x, y, z, **kwargs)
        return Points2D(x, y, **kwargs)
