
# special cases of plot
from .plot import Plot
from .axis import Axis
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


"""
NOTE:
For logPlot skal der tjekkes automatisk justering, altså farLeft og farRight

Funktion og equation skal laves om hvis de skal virke med et polært plot
Jeg tror måske en løsning ville være at lave en helt ny plot fra bunden.
Det kan også være at Plot lige skal kigges igennem for underlige ting.
Skære det ned til benene

"""

class PolarPlot:
    
    def __init__(self, window):
        window = [-10,10,-10,10]
        self.plot = Plot(window, None)
        
        self.plot.setTranslateFunction(lambda r, angle: (math.cos(angle)*r+10, math.sin(angle)*r+10))

        self.add = self.plot.add
        self.save = self.plot.save
