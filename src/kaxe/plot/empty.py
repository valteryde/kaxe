
# special cases of base plot
from .standard import Plot, XYPLOT
from ..core.axis import Axis
import math
from ..core.styles import ComputedAttribute
from typing import Union

class EmptyPlot(Plot):
    """
    A almost empty plotting window. Axis have no numbers

    Parameters
    ----------
    window : Union[list, tuple, None], optional
        The window configuration for the plot. Default is None.
    """
    
    def __init__(self, window:Union[list, tuple, None]=None):
        super().__init__(window)
        self.style({'marker.showNumber': False, 'axis.showArrow':True})

class EmptyWindow(Plot):
    """
    A completely empty plotting window.

    Parameters
    ----------
    window : Union[list, tuple, None], optional
        The window configuration for the plot. Default is None.
    """

    def __init__(self, window:Union[list, tuple, None]=None):

        super().__init__(window)
        self.style({'marker.showNumber': False, 'axis.width':0})
