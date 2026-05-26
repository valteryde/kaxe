"""
Zoom inset (magnifying glass) feature for Kaxe plots.
"""

from typing import List, Tuple, Union


class ZoomInset:
    """
    A linked subplot that displays a magnified view of a region.
    Objects added via zoom.add() appear only in the inset, not on the main plot.

    Parameters
    ----------
    parent : Plot
        The parent plot this inset belongs to.
    x0, x1, y0, y1 : float
        Data coordinates of the zoom region [x0, x1, y0, y1].
    position : str or tuple, optional
        Position of the inset. Either a preset string ('top-left', 'top-right',
        'bottom-left', 'bottom-right') or a tuple (x, y) in data coordinates
        for the bottom-left corner of the inset. Default is 'top-left'.
    size : tuple, optional
        (width, height) of the inset in pixels. Default is (400, 300).
    showAxes : bool, optional
        Whether to show axes in the inset. Default is True.
    connectorLines : bool, optional
        Whether to draw lines connecting the selection box to the inset. Default is True.
    """

    def __init__(
        self,
        parent,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        position: Union[str, Tuple[float, float]] = "top-left",
        size: Tuple[int, int] = (400, 300),
        showAxes: bool = True,
        connectorLines: bool = True,
        connectorCorners: str = "auto",
        includeMain: bool = True,
        margin: int = 20,
        selectionBoxWidth: int = 3,
        selectionBoxColor: Tuple[int, int, int, int] = (0, 0, 0, 255),
        connectorWidth: int = 2,
        connectorColor: Tuple[int, int, int, int] = (0, 0, 0, 255),
    ):
        self.parent = parent
        self.windowAxis = [x0, x1, y0, y1]
        self.objects: List = []
        self.position = position
        self.size = size
        self.showAxes = showAxes
        self.connectorLines = connectorLines
        self.connectorCorners = connectorCorners  # "auto" | "left-right" | "right-left" | "left-left" | "right-right"
        self.includeMain = includeMain
        self.margin = margin
        self.selectionBoxWidth = selectionBoxWidth
        self.selectionBoxColor = selectionBoxColor
        self.connectorWidth = connectorWidth
        self.connectorColor = connectorColor
        self.firstTitle = None
        self.secondTitle = None

    def add(self, obj):
        """
        Add an object to the zoom inset. The object appears only in the inset,
        not on the main plot.

        Parameters
        ----------
        obj
            Object to add (Function2D, Points2D, etc.)

        Returns
        -------
        The added object
        """
        if self.parent.identity in obj.supports:
            self.objects.append(obj)
        else:
            import logging
            logging.error(f"{obj} is not supported in zoom inset for {self.parent}")
        return obj

    def title(self, first=None, second=None):
        """
        Set axis titles for the inset.

        Parameters
        ----------
        first : str, optional
            Title for the first (x) axis.
        second : str, optional
            Title for the second (y) axis.

        Returns
        -------
        self
        """

        self.firstTitle = first
        self.secondTitle = second
        return self
