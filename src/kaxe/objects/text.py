

from ..core.styles import *
from ..core.shapes import shapes
from ..core.symbol import makeSymbolShapes
from ..core.symbol import symbol as symbols
from ..core.helper import *
from ..plot import identities
from ..core.d3.objects import Triangle, Line3D
import numpy as np

class Text:
    """
    
    """
    
    def __init__(self, text, center, color:tuple=None):
        
        self.text = text
        self.center = center
    
        # color
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color
    
        self.legendColor = self.color
        self.supports = [identities.XYPLOT, identities.POLAR, identities.XYZPLOT]

    
    def finalize(self, parent):
        if parent == identities.XYZPLOT:
            self.finalize3D(parent)
        else:
            self.finalize2D(parent)


    def finalize2D(self, parent):
        pass


    def finalize3D(self, parent):
        pass