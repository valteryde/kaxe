
# special cases of base plot
#from .standard import Plot, XYPLOT
from .core.axis import Axis
import math
from .core.styles import ComputedAttribute

class BoxPlot:
    
    def __init__(self, window:list|tuple|None=None):
        self.plot = Plot(window, None)

        firstEndPos = ComputedAttribute(lambda am: (am.getAttr('width'), 0))
        secondEndPos = ComputedAttribute(lambda am: (0,am.getAttr('height')))    

        firstAxis = Axis((1,0))
        firstAxis.setAttr(startPos=(0,0))
        firstAxis.setAttr(endPos=firstEndPos)

        secondAxis = Axis((0,1))
        secondAxis.setAttr(startPos=(0,0))
        secondAxis.setAttr(endPos=secondEndPos)

        self.plot.setAxis(firstAxis, secondAxis)

        self.add = self.plot.add
        self.save = self.plot.save
