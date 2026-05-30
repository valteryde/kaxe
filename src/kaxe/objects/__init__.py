from typing import TYPE_CHECKING

from .d2 import *
from .function import Function
from .point import Points
from .legend import GhostLegend

if TYPE_CHECKING:
    from .d3 import Points3D, Function3D, Mesh, Potato, SolidOfRotation


def __getattr__(name):
    from ._lazy import lazy_getattr
    return lazy_getattr(globals(), name)