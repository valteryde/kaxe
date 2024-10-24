
from .d2.function import Function2D
from .d3.function import Function3D
from typing import Union, Callable
from inspect import signature

class Function:

    def __new__(self, 
                 f:Callable, # both
                 color:tuple=None, # both
                 width:int=10, # 2d
                 numPoints:int=None, # 3d
                 fill:bool=True, # 3d
                 *args, 
                 **kwargs
                ) -> Union[Function2D, Function3D]:
        
        sig = signature(f)
        n = len(sig.parameters) - len(kwargs) - len(args)         

        if n == 1:
            return Function2D(f, color=color, width=width, *args, **kwargs)

        if n == 2:
            return Function3D(f, color=color, numPoints=numPoints, fill=fill)

