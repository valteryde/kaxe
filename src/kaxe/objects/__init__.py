from .d2 import *
from .function import Function
from .point import Points
from .legend import GhostLegend


def __getattr__(name):
    from ._lazy import lazy_getattr
    return lazy_getattr(globals(), name)