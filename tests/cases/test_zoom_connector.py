"""
Test zoom inset connector lines.

When the zoom inset is to the right of the selection:
- Top connector: selection top-right → inset top-right (right-right)
- Bottom connector: selection bottom-left → inset bottom-left (left-left)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
import numpy as np
from runner import judge, smoke


@smoke()
@judge(
    elements=[
        "top connector line connects from selection box top-right to zoom inset box top-right",
        "bottom connector line connects from selection box bottom-left to zoom inset box bottom-left",
        "zoom inset",
        "connector lines",
    ],
    focus="When the zoom inset is to the right of the selection, top connector uses right-right; bottom connector uses left-left to avoid crossing.",
)
def test_zoom_connector_right_right():
    """
    Zoom inset to the right of selection. Top: right-right, Bottom: left-left.
    """
    plot = kaxe.Plot([0, 4 * np.pi, -1, 1])
    plot.add(kaxe.Function2D(lambda x: np.sin(x)))

    # Inset at (5, -0.5) in data coords - to the RIGHT of selection [2.5, 4]
    zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5))
    zoom.add(
        kaxe.Points2D(
            [3.2], [-0.2],
            symbol=kaxe.symbol.CIRCLE,
            color=(255, 0, 0, 255),
        )
    )
    return plot
