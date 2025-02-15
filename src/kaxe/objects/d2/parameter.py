
from typing import Callable
from .point import Points2D
from ...core.styles import getRandomColor
from ...core.color import Colormap
from ...core.helper import *
from ...core.shapes import shapes
from ...core.symbol import symbol
from ...plot import identities
import numbers
from random import randint
from .function import Function2D
from typing import Union
from ...core.d3.objects import Line3D, Point3D
from ...core.d3.render import Render

class ParametricEquation:
    """
    A class to represent a parametric equation.
    
    Supports classical plots, polar plot is experimential

    Parameters
    ----------
    f : Callable
        The parametric function.
    interval : Union[tuple, list]
        The interval over which the function is defined.
    color : tuple | kaxe.Colormap, optional
        The color of the parametric equation, by default None. ColorMap only works in 3D plots.
    width : int, optional
        The width of the line representing the parametric equation, by default 10.
    dotted : int, optional
        If greater than 0, the function plot line will be dotted with the specified distance between dots. Default is 0.
    dashed : int, optional
        If greater than 0, the function plot line will be dashed with the specified distance between dashes. Default is 0.
    *args : tuple
        Additional positional arguments.
    **kwargs : dict
        Additional keyword arguments.
    """


    def __init__(self, 
                 f:Callable, 
                 interval:Union[tuple, list],
                 color:tuple=None, 
                 width:int=10,
                 dashed:int=0,
                 dotted:int=0,
                 *args, 
                 **kwargs
                ):
        
        self.function = f
        self.interval = interval
        self.batch = shapes.Batch()
        
        self.dashed = dashed
        self.dotted = dotted

        self.tangentFunctions = []

        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        
        self.legendColor = self.color
        if type(self.color) is Colormap:
            self.legendColor = self.color.getColor(0, 1, 2)

        self.thickness = width

        self.otherArgs = args
        self.otherKwargs = kwargs

        self.supports = [identities.XYPLOT, identities.XYZPLOT]


    def __call__(self, x):
        return self.function(x)


    def __half__(self, t0, t1, parent, fidelity):

        p0 = self.function(t0)
        p1 = self.function(t1)

        pixel0 = parent.pixel(*p0)
        pixel1 = parent.pixel(*p1)

        diff = vlen(vdiff(pixel0, pixel1)) * fidelity

        if diff > 10:
            badPoints = not parent.inside(*pixel0) or not parent.inside(*pixel1)
            half = (t0 + t1) / 2
            
            if badPoints:
                return self.__half__(t0, half, parent, fidelity) + [None] + self.__half__(half, t1, parent, fidelity)
            else:
                return self.__half__(t0, half, parent, fidelity) + self.__half__(half, t1, parent, fidelity)

        else:
            return [list(pixel0) + [t0], list(pixel1) + [t1]]


    def finalize(self, parent):

        self.lineSegments = [[]]
        self.__lastPoint__ = []

        lineSegments = [[]]

        fidelity = 1
        if parent == identities.XYZPLOT:
            fidelity = 2000

        for i in self.__half__(*self.interval, parent, fidelity=fidelity):
            if i:lineSegments[-1].append(i)
            elif len(lineSegments[-1]) > 0: lineSegments.append([])

        if parent == identities.XYPLOT:
                
            # piece together linesegments
            for ls in lineSegments:
                shapes.LineSegment(
                    [(i[0], i[1]) for i in ls], 
                    color=self.color, 
                    width=self.thickness, 
                    batch=self.batch, 
                    dotted=self.dotted > 0,
                    dashed=self.dashed > 0,
                    dashedDist=self.dashed,
                    dottedDist=self.dotted
                )

            # add tangent
            for tf in self.tangentFunctions:
                parent.add(tf)

        elif parent == identities.XYZPLOT:
            render:Render = parent.render

            for ls in lineSegments:

                for i in range(len(ls)-1):
                    color = self.color
                    if type(self.color) is Colormap:
                        color = self.color.getColor(ls[i][3], *self.interval)

                    render.add3DObject( Line3D(
                        (ls[i][0], ls[i][1], ls[i][2]), 
                        (ls[i+1][0], ls[i+1][1], ls[i+1][2]), 
                        color=color, 
                        width=self.thickness, 
                    ))
                    render.add3DObject( Point3D(
                        ls[i][0], ls[i][1], ls[i][2], 
                        color=color, 
                        radius=self.thickness/2, 
                    ))


    def tangent(self, t, dt=10**(-5)):
        """
        Creates an tangent using central diffrence quotient
        Does not work on 3D plots
        
        Parameters
        ----------
        t : int|float
            t-value where tangent will be placed
        dt : int|float, optional
            Step size for CFDM
        """

        # central diff quo
        x, y = self.function(t)
        dx, dy = vdiff((x,y), self.function(t+dt))
        
        a = dy/dx
 
        self.tangentFunctions.append(Function2D(
            lambda x, a, x0, y0: a*(x - x0) + y0, a=a, x0=x, y0=y,
            width=self.thickness,
            color=self.color,
            dotted=True
        ))

    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str, symbol=symbol.LINE, color=None):
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