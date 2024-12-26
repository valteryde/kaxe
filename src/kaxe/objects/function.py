
from .d2.function import Function2D
from .d3.function import Function3D
from typing import Union, Callable
from inspect import signature

class Function:
    """
    Function to be added to any plot type
    
    Parameters
    ----------
    f : Callable
        The function to be plotted. Should accept one parameter for 2D functions and two parameters for 3D functions.
    color : tuple, optional
        The color of the function plot. Default is None.
    width : int, optional
        The width of the function plot line for 2D functions. Default is 10.
    numPoints : int, optional
        The number of points to plot for 3D functions. Default is None.
    fill : bool, optional
        Whether to fill the area under the function plot for 3D functions. Default is True.
    *args : tuple
        Additional positional arguments to pass to the function f.
    **kwargs : dict
        Additional keyword arguments to pass to the function f. 

    Returns
    -------
    Object : Function2D|Function3D
        Correct Function class based on the parameters
    
    See also
    --------
    kaxe.Function2D
    kaxe.Function3D
    """

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

