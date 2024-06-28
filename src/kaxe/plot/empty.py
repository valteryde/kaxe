
# special cases of base plot
from .standard import Plot, XYPLOT
from ..core.axis import Axis
import math
from ..core.styles import ComputedAttribute


class EmptyPlot(Plot):
    
    def __init__(self, window:list|tuple|None=None):
        super().__init__(window)
        self.style({'marker.showNumber': False, 'axis.showArrow':True})

class EmptyWindow(Plot):
    
    def __init__(self, window:list|tuple|None=None):
        super().__init__(window)
        self.style({'marker.showNumber': False, 'axis.width':0})
