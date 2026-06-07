"""
Test contour plots.
"""

import math
import sys
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.helper import bbox_intersects_box, bbox_overlaps, intersect_bbox_with_box
from kaxe.core.shapes import shapes
from kaxe.core.text import Text
from runner import judge, sanity, smoke, unit

SVG_NS = "http://www.w3.org/2000/svg"


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


def _angular_span(angles):
    """Return the smallest arc (radians) covering all angles on a circle."""
    if len(angles) < 2:
        return 0.0
    angles = sorted(angles)
    max_gap = max(
        angles[i + 1] - angles[i] for i in range(len(angles) - 1)
    )
    wrap_gap = 2 * math.pi - (angles[-1] - angles[0])
    return 2 * math.pi - max(max_gap, wrap_gap)


@unit()
def test_contour_labels_angular_spread():
    """x²+y² labels on each level span at least 120° around the curve."""
    from collections import defaultdict

    plot = kaxe.Plot([-6, 6, -4, 6])
    plot.width = 800
    plot.height = 600
    plot.windowBox = [0, 0, 800, 600]
    plot.__calculateWindowBorders__()
    plot.__prepare__()
    contour = kaxe.Contour(lambda x, y: x ** 2 + y ** 2, label=True)
    contour.finalize(plot)

    center_x, center_y = plot.pixel(0, 0)
    by_level = defaultdict(list)
    for obj in contour.batch.objects:
        if hasattr(obj, "text"):
            cx, cy = obj.getCenterPos()
            angle = math.atan2(cy - center_y, cx - center_x)
            by_level[obj.text].append(angle)

    min_span = math.radians(120)
    for level, angles in by_level.items():
        if len(angles) >= 3:
            assert _angular_span(angles) >= min_span, (
                f"level {level} labels confined to {_angular_span(angles):.0f} rad"
            )


@unit()
def test_bbox_intersects_box_helpers():
    """bbox/window intersection helpers match axis-aligned expectations."""
    bbox = (10, 20, 30, 40)
    window = [0, 0, 100, 100]
    assert bbox_intersects_box(bbox, window)
    assert intersect_bbox_with_box(bbox, window) == bbox

    outside = (200, 200, 10, 10)
    assert not bbox_intersects_box(outside, window)
    assert intersect_bbox_with_box(outside, window) is None

    partial = (90, 90, 20, 20)
    assert bbox_intersects_box(partial, window)
    assert intersect_bbox_with_box(partial, window) == (90, 90, 10, 10)


@unit()
def test_contour_labels_skip_outside_window():
    """Labels fully outside windowBox are not placed in the batch."""
    contour = _finalize_contour(
        lambda x, y: x ** 2 + y ** 2,
        [-6, 6, -4, 6],
        label=True,
    )
    texts = [obj for obj in contour.batch.objects if hasattr(obj, "text")]
    assert len(texts) > 0

    plot = kaxe.Plot([-6, 6, -4, 6])
    plot.width = 800
    plot.height = 600
    plot.windowBox = [0, 0, 800, 600]

    for text in texts:
        assert bbox_intersects_box(text.getBoundingBox(), plot.windowBox)
        assert text.clip_box is not None


@unit()
def test_text_png_clip_at_window_edge():
    """Text with clip_box is cut off at the plot edge in PNG rendering."""
    surface = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
    text = Text("1.5", 340, 200, fontSize=40, clip_box=[0, 0, 350, 400])
    text.drawPillow(surface)

    arr = np.array(surface)
    bbox = text.getBoundingBox()
    clip_right = text.clip_box[2]
    ink_outside = (arr[:, clip_right + 1:, :3] < 250).any()
    ink_inside = (arr[:, max(0, clip_right - 20):clip_right + 1, :3] < 250).any()
    assert bbox[0] + bbox[2] > clip_right, "label should extend past clip edge"
    assert not ink_outside
    assert ink_inside


@unit()
def test_contour_labels_svg_clip_path():
    """Contour labels export SVG groups clipped to the plot window."""
    plot = kaxe.Plot([-2.5, 0, -1.5, 1.5])
    plot.add(kaxe.Contour(
        lambda x, y: (x + 1.5) ** 2 + 2 * y ** 2,
        a=0.2,
        b=1.7,
        steps=7,
        label=True,
    ))
    plot.showProgressBar = False
    plot.printDebugInfo = False

    buf = BytesIO()
    plot.save(buf, format="svg")
    root = ET.fromstring(buf.getvalue().decode("utf-8"))

    clip_paths = [
        el for el in root.iter()
        if el.tag == f"{{{SVG_NS}}}clipPath" or el.tag.endswith("clipPath")
    ]
    clipped_groups = [
        el for el in root.iter()
        if el.get("clip-path", "").startswith("url(#kaxe-clip-")
    ]
    assert len(clip_paths) > 0
    assert len(clipped_groups) > 0
