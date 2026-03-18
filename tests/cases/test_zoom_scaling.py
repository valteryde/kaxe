"""
Test zoom inset scaling: points and function line width should scale up in the magnified view.
Also verifies zoom inset has no legend (legend only on main plot).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
import numpy as np
from runner import smoke, sanity, judge


@smoke()
@sanity()
@judge(
    elements=[
        "zoom inset with magnified sine curve",
        "main plot with sine curve",
        "main plot has legend",
        "zoom inset has NO legend",
    ],
    focus="Zoom inset shows scaled-up content (thicker lines, larger points) and has no duplicate legend.",
    strict_elements=False,
)
def test_zoom_inset_scaling():
    """
    Zoom inset with includeMain: function and points should be visually scaled up.
    Legend appears only on main plot, not in inset.
    """
    plot = kaxe.Plot([0, 4 * np.pi, -1, 1])
    plot.add(kaxe.Function2D(lambda x: np.sin(x), width=10).legend(r"$\theta$"))
    plot.add(kaxe.Points2D([3.2], [-0.2], symbol=kaxe.symbol.CIRCLE, color=(255, 0, 0, 255)))

    zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5), includeMain=True)
    zoom.add(
        kaxe.Points2D(
            [3.5], [-0.25],
            symbol=kaxe.symbol.CROSS,
            color=(0, 128, 0, 255),
        )
    )
    return plot
