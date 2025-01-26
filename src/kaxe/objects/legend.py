
from ..plot import identities

class GhostLegend:
    """
    Adds a legend
        
    Parameters
    ----------
    text : str
        The text to be displayed in the legend.
    symbol : symbols
        The symbol to be used in the legend.
    color : tuple
        The color to be used for the legend text. If not provided, the default color will be used.
        
    """

    def __init__(self, text:str, color:tuple, symbol:str):
        
        self.supports = [identities.POLAR, identities.XYPLOT, identities.XYZPLOT, identities.LOGPLOT]

        self.legendText = text
        self.legendColor = color
        self.legendSymbol = symbol

    
    def finalize(self, *args, **kwargs):
        pass

    def push(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        pass