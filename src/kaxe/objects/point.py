

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



