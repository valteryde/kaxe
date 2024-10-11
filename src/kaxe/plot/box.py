
# special cases of base plot
from .standard import Plot, XYPLOT
from ..core.axis import Axis
import math
from ..core.styles import ComputedAttribute
from typing import Union

class BoxPlot(Plot):
    
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
