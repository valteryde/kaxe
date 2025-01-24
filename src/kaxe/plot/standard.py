
# a simple xy plot
# faster than the true plot

from ..core.helper import *
import logging
from ..core.axis import *
from ..core.window import Window

XYPLOT = 'xy'

class Plot(Window):
    """
    A simple plotting window for cartesian coordinates
    
    Attributes
    ----------
    firstAxis : Kaxe.Axis
        The first axis of the plot.
    secondAxis : Kaxe.Axis
        The second axis of the plot.

    Parameters
    ----------
    window : list
        A list representing the axis window [x0, x1, y0, y1].
    
    Examples
    --------
    >>> import kaxe
    >>> plt = kaxe.Plot()
    >>> plt.add( ... )
    >>> plt.show( )

    """
    
    # en måde at gøre den nemmer at ændre på er at dele tingene op i flere
    # delfunktioner. fx __setAxisPos__ ændres af BoxPlot til altid at have 
    # akserne i nederste hjørne

    def __init__(self,  window:list=None): # |
        super().__init__()
        self.identity = XYPLOT

        """
        window:tuple [x0, x1, y0, y1] axis
        """
        
        # NOTE: Does not really fit into the whole idea of styles
        # but does serve a quality of life function
        self.attrmap.default(attr='xNumbers', value=None)
        self.attrmap.default(attr='yNumbers', value=None)

        self.firstAxis = Axis((1,0), (0,-1), 'xNumbers')
        self.secondAxis = Axis((0,1), (-1,0), 'yNumbers')

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.firstTitle = None
        self.secondTitle = None

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)


    def __setAxisPos__(self):
        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3])
        self.offset[0] += self.windowAxis[0] * self.scale[0]
        self.offset[1] += self.windowAxis[2] * self.scale[1]

        if self.secondAxis.hasNull:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],0), self.pixel(self.windowAxis[1],0))

        elif self.secondAxis.endNumber < 0:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[3]), self.pixel(self.windowAxis[1],self.windowAxis[3]))

        else:
            self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[2]))

        self.firstAxis.finalize(self)

        if self.firstAxis.hasNull:
            self.secondAxis.setPos(self.pixel(0,self.windowAxis[2]), self.pixel(0,self.windowAxis[3]))

        elif self.firstAxis.endNumber < 0:
            self.secondAxis.setPos(self.pixel(self.windowAxis[1],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[3]))

        else:
            self.secondAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[0],self.windowAxis[3]))

        self.secondAxis.finalize(self)

    def __prepare__(self):
        # finish making plot
        # fit "plot" into window

        xLength = self.windowAxis[1] - self.windowAxis[0]
        yLength = self.windowAxis[3] - self.windowAxis[2]
        self.scale = [self.width/xLength,self.height/yLength]

        self.__setAxisPos__()

        self.firstAxis.autoAddMarkers(self)
        self.secondAxis.autoAddMarkers(self)

        self.firstAxis.checkCrossOvers(self,self.secondAxis)
        self.secondAxis.checkCrossOvers(self, self.firstAxis)

        if self.firstTitle: self.firstAxis.addTitle(self.firstTitle, self)
        if self.secondTitle: self.secondAxis.addTitle(self.secondTitle, self)


    # special api
    def title(self, first=None, second=None):
        """
        Adds title to the plot.
        
        Parameters
        ----------
        first : str, optional
            Title for the first axis.
        second : str, optional
            Title for the second axis.

        Returns
        -------
        Kaxe.Plot
            The active plotting window
        
        """

        self.firstTitle = first
        self.secondTitle = second
        return self


    # more translations
    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        # x -= self.firstAxis.offset
        # y -= self.secondAxis.offset

        return self.translate(x,y)


    def inversepixel(self, x:int, y:int):
        """
        para: pixel values according to axis
        return abstract value
        """
        return self.inversetranslate(x,y)
