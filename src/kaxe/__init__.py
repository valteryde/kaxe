"""
Kaxe is free software: you can redistribute it and/or modify under the terms of 
the GNU General Public License as published by the Free Software Foundation, 
version 3 of the License on 29. June 2007.

Maintainer:
Valter Yde Daugberg, valteryde@hotmail.com

Kaxe is a versatile data visualization library designed to simplify the process of creating complex charts and plots. 
It provides a wide range of tools and utilities for handling data, customizing visual elements, and integrating with 
interactive environments like Jupyter notebooks. The library includes modules for plotting, charting, data manipulation, 
and object management, making it a comprehensive solution for data visualization needs.

Modules:
- plot: Contains functions and classes for creating various types of plots.
- chart: Provides tools for generating different chart formats.
- data: Includes utilities for data handling and manipulation.
- objects: Manages graphical objects used in visualizations.
- core: Core functionalities including color settings, symbol management, and window handling.
- core.window: Contains classes for window management and attribute mapping.

Example:
>>> import kaxe
>>> plt = kaxe.Plot()
>>> plt.add( ... )
>>> plt.show()
"""


import logging

from .plot import *
from .chart import *
from .data import data
from .objects import *
from .core import koundTeX, setDefaultColors
from .core import getRandomColor
from .core import resetColor
from .core import symbol as Symbol
from .core import symbol
from .core import Colormaps, SingleColormap, Colormap
from .core.window import Window, AttrObject, AttrMap
from .core import Axis

try:
    ipy_str = str(type(get_ipython()))
    if 'zmqshell' in ipy_str:
        logging.basicConfig(level=logging.CRITICAL)
    if 'terminal' in ipy_str:
        logging.basicConfig(level=logging.CRITICAL)
except:
    logging.basicConfig(level=logging.INFO)

