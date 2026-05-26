"""Plot3D style variants."""

from typing import Union

from .plot3d import Plot3D

class PlotCenter3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot with axis placed correctly 
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [60, -70]).
    drawBackground: bool, optional
        Draw background with gridlines
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self, 
                 window:list=None, 
                 rotation=[60, -70], 
                 size:Union[bool, list, tuple]=None, 
                 light:list=[0,0,0],
                 addMarkers:bool=True,
        ):
        super().__init__(window, rotation, size=size, light=light, addMarkers=addMarkers)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = True


class PlotFrame3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot with only x-, y- and z-axis drawn
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self,  
                 window:list=None, 
                 rotation=[60, -70], 
                 drawBackground=True, 
                 size:Union[bool, list, tuple]=None, 
                 light:list=[0,0,0],
        ):
        super().__init__(window, rotation, size=size, drawBackground=drawBackground, light=light)
        self.__boxed__ = True
        self.__frame__ = True
        self.__normal__ = False


class PlotEmpty3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot without axis drawn
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self,  
                window:list=None, 
                rotation=[60, -70], 
                size:Union[bool, list, tuple]=None, 
                light:list=[0,0,0],
        ):
        super().__init__(window, rotation, size=size, light=light)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = False
