
from typing import Callable
from .point import Points2D
from ...core.styles import getRandomColor
from ...core.helper import *
from ...core.shapes import shapes
from ...core.symbol import symbol
from ...core.helper import isRealNumber
from ...plot import identities
from random import randint
from typing import Union
from ...core.d3.translator import translate2DTo3DObjects, getEquivalent2DPlot, has3DReference

class Function2D:
    """
    A class to represent a 2D function for plotting

    Supports classical plots, polar plots and logarithmic plot

    Parameters
    ----------
    f : callable
        The function to be plotted. It should take a single argument and return a value y.
        The function is not contained to a domain.
    color : tuple, optional
        The color of the function plot. If not provided, a random color will be used.
    width : int, optional
        The thickness of the function plot line. Default is 10.
    dotted : int, optional
        If greater than 0, the function plot line will be dotted with the specified distance between dots. Default is 0.
    dashed : int, optional
        If greater than 0, the function plot line will be dashed with the specified distance between dashes. Default is 0.
    args : tuple, optional
        Additional positional arguments to be passed to the function f.
    kwargs : dict, optional
        Additional keyword arguments to be passed to the function f.

    Methods
    -------
    __call__(x)
        Evaluates the function at a given x value.
    
    Examples
    --------
    >>> def f(x):
    ...     return 2*x
    >>> func = kaxe.Function2D(f(x))
    >>> func(2)
    4
    >>> plt.add(func)
    """

    def __init__(self, 
                 f:Callable, 
                 color:tuple=None, 
                 width:int=10,
                 dotted:int=0,
                 dashed:int=0,
                 *args, 
                 **kwargs
                ):

        self.function = f
        self.batch = shapes.Batch()
        self.fillbatch = shapes.Batch()
        self.tangentFunctions = []
        self.fillAreasBorders = []
        self.fillAreas = []
        self.fills = []

        self.dotted = dotted
        self.dashed = dashed

        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color

        self.legendSymbol = symbol.LINE
        if self.dotted:
            self.legendSymbol = symbol.CIRCLE

        self.thickness = width
        if len(self.color) > 3:
            self.fillcolor = (*self.color[:3], int(self.color[3]*0.5))
        else:
            self.fillcolor = (*self.color, 175)

        self.otherArgs = args
        self.otherKwargs = kwargs

        self.supports = [identities.XYPLOT, identities.POLAR, identities.LOGPLOT]


    def __call__(self, x):
        return self.function(x, *self.otherArgs, **self.otherKwargs)


    def __setPoint__(self, x, parent, firstaxisy:Union[int, None]=None, fills:Union[list, None]=None):
        try:
            y = self.function(x, *self.otherArgs, **self.otherKwargs)
        except Exception as e:
            #print('Bad value:', x, e)
            return

        if not (isRealNumber(x) and isRealNumber(y)):
            #print('Bad value:', x)
            return

        px, py = parent.pixel(x,y)

        if not px or not py:
            return

        if not self.__lastPoint__:
            self.__lastPoint__ = [px, py]
            return

        if fills != None:
            # add fill areas under curve
            for x0, x1 in self.fillAreasBorders:
                if x0 <= x <= x1:
                    fills.append(
                        (
                            firstaxisy < py, 
                            (px, parent.clamp(y=py)[1]), 
                            (self.__lastPoint__[0], parent.clamp(y=self.__lastPoint__[1])[1])
                        )
                    )

        if parent.inside(px, py) or parent.inside(*self.__lastPoint__):
            self.lineSegments[-1].append(parent.clamp(self.__lastPoint__[0], self.__lastPoint__[1]))
            self.lineSegments[-1].append(parent.clamp(px, py))
        else:
            self.lineSegments.append([])

        self.__lastPoint__ = [px, py]


    def finalize(self, parent):

        self.lineSegments = [[]]
        fills = []
        self.__lastPoint__ = []

        # translate xyz
        if parent == identities.XYZPLOT:
            parent = getEquivalent2DPlot(parent)


        if parent == identities.XYPLOT:
        
            firstaxisy = parent.pixel(0,0)[1]
            for n in range(0, parent.windowBox[2]):
                x, _ = parent.inversepixel(n,0)
                self.__setPoint__(x, parent, firstaxisy, fills)
        
        
        elif parent == identities.LOGPLOT:
            # avoid clustering

            for n in range(0, parent.windowBox[2]):
                try:
                    x, _ = parent.inversepixel(n,1)
                except Exception as e:
                    continue
                self.__setPoint__(x, parent, fills)
        

        elif parent == identities.POLAR:
        
            fidelity = 100 # burde kunne vælges som værdi
            for angle in range(0, 360*fidelity, 5):
                angle = math.radians(angle / fidelity)
                self.__setPoint__(angle, parent)

        # piece together linesegments
        for segment in self.lineSegments:
            shapes.LineSegment(
                segment, 
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

        # new fills
        fillAreas = []
        last = None
        for top, p1, p2 in fills:

            if top != last:                
                fillAreas.append({"top":top,"points":[]})
                last = top

            fillAreas[-1]["points"].append(p1)
            fillAreas[-1]["points"].append(p2)

        for area in fillAreas:
            area["points"].append((area["points"][len(area["points"])-1][0], firstaxisy))
            area["points"].insert(0, (area["points"][0][0], firstaxisy))

        for area in fillAreas:
            shapes.Polygon(*area["points"], color=self.fillcolor, batch=self.fillbatch)


        # translate fully to xyz
        if has3DReference(parent):
            translate2DTo3DObjects(parent, self.batch)
            # translate2DTo3DObjects(parent, self.fillbatch)


    def tangent(self, x, dx=10**(-5)):
        """
        Creates an tangent using central diffrence quotient

        Parameters
        ----------
        x : int|float
            x-value where tangent will be placed
        dx : int|float, optional
            Step size for CFDM
        """


        # central diff quo
        dy = self.function(x+dx/2) - self.function(x-dx/2)
        
        a = dy/dx
 
        self.tangentFunctions.append(Function2D(
            lambda x, a, x0, y0: a*(x - x0) + y0, a=a, x0=x, y0=self.function(x),
            width=self.thickness,
            color=self.color,
        ))

    
    def fill(self, x0, x1): 
        """
        Fills the area in the graph between x0 and x1

        Parameters
        ----------
        x0 : int|float
            Left first axis value to start the fill
        x1 : int|float
            Right first axis value to end the fill
        """
        
        self.fillAreasBorders.append((x0,x1))
        

    def draw(self, *args, **kwargs):
        self.fillbatch.draw(*args, **kwargs)
        self.batch.draw(*args, **kwargs)


    def push(self, *args, **kwargs):
        self.fillbatch.push(*args, **kwargs)
        self.batch.push(*args, **kwargs)
    

    def legend(self, text:str, symbol=None, color=None):
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
        if symbol:
            self.legendSymbol = symbol
        if color:
            self.legendColor = color
        return self