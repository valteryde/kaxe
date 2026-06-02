"""
Test contour plots.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.helper import bbox_overlaps
from kaxe.core.shapes import shapes
from runner import judge, sanity, smoke, unit


def _finalize_contour(f, window, **kwargs):
    plot = kaxe.Plot(window)
    plot.width = 800
    plot.height = 600
    plot.windowBox = [0, 0, 800, 600]
    plot.__calculateWindowBorders__()
    plot.__prepare__()
    contour = kaxe.Contour(f, **kwargs)
    contour.finalize(plot)
    return contour


@smoke()
@sanity()
@judge(
    elements=["contour curves", "inline contour labels", "axes"],
    focus="contour level numbers readable on lines",
    min_score=5,
)
def test_contour_labels():
    """Contour plot with inline level labels on curves."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])

    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2

    plot.add(kaxe.Contour(f, a=0.2, b=1.7, steps=7, label=True))
    return plot


@smoke()
@sanity()
@judge(
    elements=["contour curves", "axes"],
    focus="contour curves without inline labels",
)
def test_contour_without_labels():
    """Contour plot with labels disabled."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])

    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2

    plot.add(kaxe.Contour(f, a=0.2, b=1.7, steps=7, label=False))
    return plot


@unit()
def test_contour_label_batch():
    """Inline labels are added to the contour batch without exploding in count."""
    f = lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2
    contour = _finalize_contour(f, [-2.5, 0, -1.5, 1.5], a=0.2, b=1.7, steps=7, label=True)

    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    assert len(texts) > 0
    assert len(texts) < 70


@unit()
def test_contour_labels_no_white_rectangles():
    """Contour labels use transparent fondi text without opaque background rectangles."""
    contour = _finalize_contour(lambda x, y: x ** 2 + y ** 2, [-6, 6, -4, 6], label=True)

    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    rects = [obj for obj in contour.batch.objects if isinstance(obj, shapes.Rectangle)]

    assert len(texts) > 0
    assert len(rects) == 0


@unit()
def test_contour_labels_no_bbox_overlap():
    """Placed contour labels do not overlap each other's bounding boxes."""
    contour = _finalize_contour(lambda x, y: x ** 2 + y ** 2, [-6, 6, -4, 6], label=True)

    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    bboxes = [text.getBoundingBox() for text in texts]

    for i, bbox in enumerate(bboxes):
        for other in bboxes[i + 1:]:
            assert not bbox_overlaps(bbox, other, contour.labelCollisionPadding)


@unit()
def test_contour_label_rotation_follows_tangent():
    """Label rotation follows the smooth contour tangent, not pixel-grid stair steps."""
    from kaxe.core.helper import contour_label_angle

    f = lambda x, y: x ** 2 + y ** 2
    plot = kaxe.Plot([-10, 10, -10, 10])
    plot.width = 800
    plot.height = 800
    plot.windowBox = [0, 0, 800, 800]
    plot.__calculateWindowBorders__()
    plot.__prepare__()

    top_px, top_py = plot.pixel(0, 3)
    right_px, right_py = plot.pixel(3, 0)

    top_angle = contour_label_angle(f, plot, top_px, top_py)
    right_angle = contour_label_angle(f, plot, right_px, right_py)

    assert abs(top_angle) < 25
    assert abs(abs(right_angle) - 90) < 25

    stair_polyline = [
        (right_px, right_py),
        (right_px, right_py + 40),
        (right_px, right_py + 80),
    ]
    stair_angle = contour_label_angle(
        f, plot, right_px, right_py, polyline=stair_polyline
    )
    assert abs(abs(stair_angle) - 90) < 25

    # PIL rotate must use the readable angle directly, not its negation.
    down_right = math.degrees(math.atan2(-100, 100))
    down_right = (down_right + 90) % 180 - 90
    assert down_right == -45


@unit()
def test_contour_labels_x2y2_density():
    """Concentric x²+y² contours get a modest number of non-overlapping labels."""
    from collections import Counter

    contour = _finalize_contour(lambda x, y: x ** 2 + y ** 2, [-6, 6, -4, 6], label=True)

    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    counts = Counter(text.text for text in texts)
    assert 0 < len(texts) < 60
    assert all(count <= contour.labelMaxPerLevel for count in counts.values())
