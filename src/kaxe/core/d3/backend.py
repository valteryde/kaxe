"""
Protocol for 3D render backends used by Plot3D and objects/d3.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, Union

from numpy import ndarray
from PIL import Image


class RenderBackend(Protocol):
    width: int
    height: int
    guiWidth: int
    guiHeight: int
    SCL: float
    skipObjectUpdate: bool
    camera: Any
    profiler: Any

    def pixel(self, x: float, y: float, z: float) -> ndarray: ...

    def add3DObject(self, obj: Any) -> Any: ...

    def remove3DObject(self, obj: Any) -> None: ...

    def addMeshTriangles(
        self,
        p1s: ndarray,
        p2s: ndarray,
        p3s: ndarray,
        colors: ndarray,
        objs: Any,
    ) -> None: ...

    def render(self, overlay: Union[Callable[[], Image.Image], None] = None) -> Image.Image: ...

    def gui(self, overlay: Union[Callable[[], Image.Image], None] = None, plot: Any = None) -> Any: ...
