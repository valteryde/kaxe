
# special cases of base plot
from .plot import Plot
from .core.axis import Axis
import math
from .plot import XYPLOT

class Morten:
    
    def __init__(self, window:list|tuple|None=None):
        self.plot = Plot(window, None)
        
        firstAxis = Axis((1,0))
        firstAxis.style(
            head='>',
            tail='<'
        )

        secondAxis = Axis((0,1))
        secondAxis.style(
            head='>',
            tail='<'
        )

        self.plot.setAxis(firstAxis, secondAxis)

        self.add = self.plot.add
        self.save = self.plot.save
