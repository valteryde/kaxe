"""
Test zoom inset (magnifying glass) feature.
"""

import kaxe
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runner import fingerprint, judge, smoke


@smoke()
@fingerprint(reference="zoom_inset.png")
@judge(
    elements=["zoom inset", "connector lines", "main plot", "sine curve"],
    focus="zoom feature correctness and legibility",
)
def test_zoom_inset():
    """Zoom inset with main plot and inset-only points."""
    plot = kaxe.Plot([0, 4 * np.pi, -1, 1])
    plot.add(kaxe.Function2D(lambda x: np.sin(x)))

    zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5))
    zoom.add(
        kaxe.Points2D(
            [3.2], [-0.2],
            symbol=kaxe.symbol.CIRCLE,
            color=(255, 0, 0, 255),
        )
    )
    return plot
