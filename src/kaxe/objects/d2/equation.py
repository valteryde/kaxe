
#22.1285s

from ...core.shapes import shapes
from ...core.styles import getRandomColor
from ...core.symbol import symbol
from ...plot import identities
from ...core.helper import vdiff, vlen
from sympy import solve
import math

from ...core.d3.translator import translate2DTo3DObjects, getEquivalent2DPlot, has3DReference


class Equation:
    """
    A class to represent a mathematical equation from left and right side of equation.
    
    Supported in classical plots, polar plot and 3D plots as a 2D object with `z=0`

    Parameters
    ----------
    left : callable
        Left side of the equation
    right : callable
        Right side of the equation
    color : tuple|list, optional
        Color to display the equation , if default is None a random color will be assigned
    width : int
        Line thickness, default is 2
    
    Examples
    --------
    >>> def left(x, y):
    ...     return x**2 + y**2
    >>> def right(x, y):
    ...     return 1
    >>> eq = Equation(left, right)
    >>> eq.legend("Circle", color=(255, 0, 0, 255))
    >>> plt.add(eq)
    """
    

    def __init__(self, left, right, color:tuple=None, width:int=2, computePadding=50):
        self.batch = shapes.Batch()

        self.left = left
        self.right = right
        self.computePadding = computePadding
        
        self.width = width
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
        self.legendColor = self.color # default
        
        self.dots = []
        self.dotsPosAbstract = set()

        self.steps = [1, 10, 100]

        self.supports = [identities.XYPLOT, identities.POLAR, identities.XYZPLOT]


    def __getPointsInBox__(self, box, step, parent):
        if step == -1:
            return
        
        delta = self.steps[step]

        xtot = int((box[1] - box[0]) / delta)
        ytot = int((box[3] - box[2]) / delta)
        
        grid = set()

        for i in range(xtot):
            px = (i * delta) + box[0]
            
            for j in range(ytot):
                py = (j * delta) + box[2]

                if parent == identities.XYPLOT:
                    x0, y0 = parent.inversepixel(px, py)
                    x1, y1 = parent.inversepixel(px, py+delta)
                    x2, y2 = parent.inversepixel(px+delta, py)
                    x3, y3 = parent.inversepixel(px+delta, py+delta)
                elif parent == identities.POLAR:
                    x0, y0 = parent.inversetranslate(px, py)
                    x1, y1 = parent.inversetranslate(px, py+delta)
                    x2, y2 = parent.inversetranslate(px+delta, py)
                    x3, y3 = parent.inversetranslate(px+delta, py+delta)
                    
                d1 = self.left(x0, y0) - self.right(x0, y0)
                d2 = self.left(x1,y1) - self.right(x1, y1)
                d3 = self.left(x2,y2) - self.right(x2, y2)
                d4 = self.left(x3,y3) - self.right(x3, y3)

                #shapes.Rectangle(px, py, delta, delta, (0,0,255,100), batch=self.batch, radius=2)
                
                # er nul imellem?
                if max(d1, d2, d3, d4) >= 0 and min(d1, d2, d3, d4) <= 0:

                    grid.add((i,j))
                    grid.add((i-1,j))
                    grid.add((i-1,j-1))
                    grid.add((i+1,j))
                    grid.add((i+1,j+1))
        
        
        for i,j in grid:
            px = (i * delta) + box[0]
            py = (j * delta) + box[2]
            
            if step == 0:
                
                if parent == identities.XYPLOT:
                    dpx, dpy = px, py
                elif parent == identities.POLAR:
                    x, y = parent.inversetranslate(px, py)
                    dpx, dpy = parent.pixel(x,y)

                if dpx is None or dpy is None:
                    continue
                
                if not parent.inside(dpx, dpy):
                    continue

                self.dotsPosAbstract.add((px,py))

                self.dots.append(shapes.Circle(
                    dpx, 
                    dpy, 
                    color=self.color, 
                    batch=self.batch,
                    radius=self.width)
                )

            # shapes.Rectangle(px, py, delta, delta, (255,0,0,100), batch=self.batch)

            self.__getPointsInBox__([
                px,
                px+delta,
                py,
                py+delta
            ], step-1, parent)


    def __connectToClosestNeighbour__(self, parent):

        connections = dict()
        for x,y in self.dotsPosAbstract:
            
            for otherPos in [
                    (x,y+1),
                    (x,y-1),
                    (x+1,y),
                    (x-1,y),
                    (x-1,y-1),
                    (x+1,y+1)
                ]:
                if otherPos in self.dotsPosAbstract:
                    
                    if (x,y) in connections:
                        connections[(x,y)].append(otherPos)
                    else:
                        connections[(x,y)] = [otherPos]

        
        for key in connections:
            # a -> b

            a = parent.inversetranslate(*key)
            a = parent.pixel(*a)

            # a og b skal inverses translate eller noget i den stil <3
            for b in connections[key]:
                
                b = parent.inversetranslate(*b)
                b = parent.pixel(*b)

                shapes.Line(
                    *a,
                    *b,
                    batch=self.batch,
                    width=self.width*2,
                    color=self.color
                )


    def finalize(self, parent):
        # Translate to 3D plot
        if parent == identities.XYZPLOT:
            parent = getEquivalent2DPlot(parent)
        box = parent.windowBox
        box = [
            box[0] - self.computePadding, box[2] + self.computePadding, 
            box[1] - self.computePadding , box[3] + self.computePadding
        ]
        self.__getPointsInBox__(box, len(self.steps)-1, parent)

        # Translate to 3D plot
        if has3DReference(parent):
            translate2DTo3DObjects(parent, self.batch)

        # algoritmen burde findes alle pixels hvor ligningen går op
        # for plots der ikke er standard XY skal pixelesne warpes rundt
        # der kan komme "huller" i plots hvor warpen ikke er ens med standard XY
        if parent != identities.XYPLOT:
            self.__connectToClosestNeighbour__(parent)


    def push(self, x, y):
        self.batch.push(x,y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


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
        computePadding: int, optional
            When generating the equation some padding can be needed to include the edges properly (default is 50).
            
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
