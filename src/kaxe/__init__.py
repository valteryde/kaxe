
import logging

from .plot import *
from .chart import *
from .data import data
from .objects import *
from .core import koundTeX

try:
    ipy_str = str(type(get_ipython()))
    if 'zmqshell' in ipy_str:
        logging.basicConfig(level=logging.CRITICAL)
    if 'terminal' in ipy_str:
        logging.basicConfig(level=logging.CRITICAL)
except:
    logging.basicConfig(level=logging.INFO)

