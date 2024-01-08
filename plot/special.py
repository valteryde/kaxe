
# special cases of base plot
from .plot import Plot
from .core.axis import Axis
import math

class LogPlot:
    
    def __init__(self, window, firstAxisLog=False, secondAxisLog=True):
        self.plot = Plot(window, None)
        
        if firstAxisLog:
            firstAxis = Axis((1,0), func=math.log10, invfunc=lambda x: math.pow(10, x))
        else:
            firstAxis = Axis((1,0))

        if secondAxisLog:
            secondAxis = Axis((0,1), func=math.log10, invfunc=lambda x: math.pow(10, x))
        else:
            secondAxis = Axis((0,1))

        self.plot.setAxis(firstAxis, secondAxis)

        self.add = self.plot.add
        self.save = self.plot.save
