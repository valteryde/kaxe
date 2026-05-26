"""
Zoom inset connector placement logic.

Extracted for testability. Determines which selection-box corners connect
to which inset corners based on relative position.
"""

from typing import Literal, Union, Tuple, List

ConnectorMode = Literal["right", "left", "vertical", "left-right"]


def connector_placement(
    inset_x: float,
    inset_y: float,
    surf_w: float,
    surf_h: float,
    sel_left: float,
    sel_right: float,
    sel_bottom: float,
    sel_top: float,
    pos: Union[str, Tuple[float, float], List[float]],
) -> ConnectorMode:
    """
    Determine connector line placement based on inset position relative to selection box.

    Parameters
    ----------
    inset_x, inset_y : float
        Bottom-left corner of inset in pixel coordinates.
    surf_w, surf_h : float
        Width and height of inset surface.
    sel_left, sel_right, sel_bottom, sel_top : float
        Selection box bounds in pixel coordinates.
    pos : str or tuple
        Position: 'top-left', 'top-right', 'bottom-left', 'bottom-right',
        or (x, y) in data coordinates.

    Returns
    -------
    str
        One of: 'right', 'left', 'vertical', 'left-right'
        - 'right': Inset to the right of selection (2 lines: tr->tr, bl->bl)
        - 'left': Inset to the left of selection (2 lines: tr->tl, br->bl)
        - 'vertical': Inset above or below (4 lines: all corners)
        - 'left-right': Fallback (2 lines: tl->tr, bl->br)
    """
    if isinstance(pos, (tuple, list)) and len(pos) >= 2:
        inset_right_of_sel = inset_x > sel_right
        inset_left_of_sel = (inset_x + surf_w) < sel_left
        inset_below_sel = (inset_y + surf_h) < sel_bottom
        inset_above_sel = inset_y > sel_top
    else:
        inset_right_of_sel = pos in ("top-right", "bottom-right")
        inset_left_of_sel = pos in ("top-left", "bottom-left")
        inset_below_sel = pos in ("bottom-left", "bottom-right")
        inset_above_sel = pos in ("top-left", "top-right")

    if inset_right_of_sel:
        return "right"
    if inset_left_of_sel:
        return "left"
    if inset_below_sel or inset_above_sel:
        return "vertical"
    return "left-right"


def compute_boxplot_whiskers(
    data: list,
) -> Tuple[float, float]:
    """
    Compute whisker endpoints using Tukey convention.

    Whiskers extend to min/max of data within fence [Q1-1.5*IQR, Q3+1.5*IQR].

    Returns
    -------
    tuple
        (leftwhisker, rightwhisker)
    """
    import numpy as np

    leftbox = float(np.quantile(data, 0.25))
    rightbox = float(np.quantile(data, 0.75))
    IQR = rightbox - leftbox
    lower_fence = leftbox - 1.5 * IQR
    upper_fence = rightbox + 1.5 * IQR

    data_arr = np.array(data)
    within_fence = data_arr[(data_arr >= lower_fence) & (data_arr <= upper_fence)]
    if len(within_fence) > 0:
        leftwhisker = float(np.min(within_fence))
        rightwhisker = float(np.max(within_fence))
    else:
        leftwhisker = lower_fence
        rightwhisker = upper_fence

    return (leftwhisker, rightwhisker)


def compute_render_scale(
    main_width: float,
    main_height: float,
    main_x_range: float,
    main_y_range: float,
    inset_w: float,
    inset_h: float,
    zoom_x_range: float,
    zoom_y_range: float,
) -> float:
    """
    Compute visual scale factor for zoom inset (magnification).

    Returns scale >= 1.0 when zoom has more pixels per data unit than main.
    """
    import math

    zoom_ppu_x = inset_w / zoom_x_range if zoom_x_range else 1
    zoom_ppu_y = inset_h / zoom_y_range if zoom_y_range else 1
    main_ppu_x = main_width / main_x_range if main_x_range else 1
    main_ppu_y = main_height / main_y_range if main_y_range else 1
    scale_x = zoom_ppu_x / main_ppu_x
    scale_y = zoom_ppu_y / main_ppu_y
    return max(1.0, math.sqrt(scale_x * scale_y))
