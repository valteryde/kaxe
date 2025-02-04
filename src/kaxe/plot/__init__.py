
from .themes import Themes
from .log import LogPlot, BoxedLogPlot, LOGPLOT
from .standard import Plot, XYPLOT
from .polar import PolarPlot, POLARPLOT
from .box import BoxedPlot
from .empty import EmptyPlot, EmptyWindow
from .d3 import Plot3D, PlotCenter3D, PlotFrame3D, PlotEmpty3D, XYZPLOT
from .double import DoubleAxisPlot
from .grid import Grid


class identities:
    XYPLOT = XYPLOT
    POLAR = POLARPLOT
    XYZPLOT = XYZPLOT
    LOGPLOT = LOGPLOT