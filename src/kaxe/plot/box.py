
# special cases of base plot
from .standard import Plot, XYPLOT
from typing import Union

class BoxedPlot(Plot):
    """
    A class used to create a plot where the axis is always to the left and at the bottom.
    
    Attributes
    ----------
    firstAxis : Kaxe.Axis
        The first axis of the plot.
    secondAxis : Kaxe.Axis
        The second axis of the plot.


    Parameters
    ----------
    window : list|tuple|None, optional
        A list or tuple defining the window for the plot, by default None.
    """

    def __init__(self, window:Union[list, tuple, None]=None):
        super().__init__(window)

    def __setAxisPos__(self):
        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3])
        self.offset[0] += self.windowAxis[0] * self.scale[0]
        self.offset[1] += self.windowAxis[2] * self.scale[1]

        self.firstAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[1],self.windowAxis[2]))
        self.firstAxis.finalize(self)

        self.secondAxis.setPos(self.pixel(self.windowAxis[0],self.windowAxis[2]), self.pixel(self.windowAxis[0],self.windowAxis[3]))
        self.secondAxis.finalize(self)


