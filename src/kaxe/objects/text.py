
from ..core.styles import *
from ..core.shapes import shapes
from ..core.symbol import makeSymbolShapes
from ..core.symbol import symbol as symbols
from ..core.helper import *
from ..plot import identities
import numpy as np

class Text:
    """Place a text label at a data coordinate on a plot.

    Parameters
    ----------
    text : str
        Label text. LaTeX math is supported when wrapped in ``$...$``.
    center : tuple
        ``(x, y)`` or ``(x, y, z)`` position in data coordinates.
    color : tuple, optional
        RGBA color. A random cycle color is used when omitted.

    Examples
    --------
    >>> import kaxe
    >>> plt = kaxe.Plot([-1, 1, -1, 1])
    >>> plt.add(kaxe.objects.text.Text("$\\alpha$", (0, 0)))
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
