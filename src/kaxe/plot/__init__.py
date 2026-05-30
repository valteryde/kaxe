from typing import TYPE_CHECKING

from .themes import Themes
from .log import LogPlot, BoxedLogPlot, LOGPLOT
from .standard import Plot, XYPLOT
from .polar import PolarPlot, POLARPLOT
from .box import BoxedPlot
from .empty import EmptyPlot, EmptyWindow
from .double import DoubleAxisPlot
from .constants import XYZPLOT
from .grid import Grid
from .zoom import ZoomInset

__all__ = [
    'Themes', 'LogPlot', 'BoxedLogPlot', 'LOGPLOT',
    'Plot', 'XYPLOT', 'PolarPlot', 'POLARPLOT',
    'BoxedPlot', 'EmptyPlot', 'EmptyWindow',
    'DoubleAxisPlot', 'Grid', 'XYZPLOT', 'identities',
    'Plot3D', 'PlotCenter3D', 'PlotFrame3D', 'PlotEmpty3D',
]

if TYPE_CHECKING:
    from .d3 import Plot3D, PlotCenter3D, PlotFrame3D, PlotEmpty3D


class identities:
    XYPLOT = XYPLOT
    POLAR = POLARPLOT
    XYZPLOT = XYZPLOT
    LOGPLOT = LOGPLOT


def __getattr__(name):
    from ._lazy import lazy_getattr
    return lazy_getattr(globals(), name)