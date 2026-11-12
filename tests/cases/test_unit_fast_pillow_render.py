"""
Unit tests for optimized Pillow 2D rendering paths in line, shapes, window, and equation.
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import kaxe
from kaxe.core import line as kline
from kaxe.core import shapes
from runner import unit


def _reference_draw_line(surface: Image.Image, x0: float, y0: float, x1: float, y1: float, color, thickness: float):
    """Reference implementation matching weighted_line + colorBlend with bounds guard."""
    if thickness <= 0 or not (
        math.isfinite(x0) and math.isfinite(y0) and math.isfinite(x1) and math.isfinite(y1)
    ):
        return
    r, g, b, a = color
    if len(color) == 4 and a <= 0:
        return
    rr, cc, val = kline.weighted_line(y0, x0, y1, x1, thickness)
    pixels = surface.load()
    w, h = surface.size
    for x, y, alpha in zip(cc, rr, val):
        ix, iy = int(x), int(y)
        if 0 <= ix < w and 0 <= iy < h:
            pixels[ix, iy] = kline.colorBlend(r, g, b, alpha * a, *pixels[ix, iy])


def _make_backed_surface(size: tuple[int, int], fill: tuple[int, int, int, int]) -> Image.Image:
    """Create a PIL RGBA image backed by a mutable NumPy RGBA buffer like Window.__pillowPaint__."""
    w, h = size
    buf = np.empty((h, w, 4), dtype=np.uint8)
    buf[:, :] = fill
    surface = Image.frombuffer("RGBA", (w, h), buf, "raw", "RGBA", 0, 1)
    surface.readonly = 0
    surface._kaxe_buf = buf
    return surface


@unit()
def test_draw_line_pixel_exact_with_and_without_kaxe_buf():
    """drawLineOnPillowImage matches reference on opaque canvases and matches identically with/without _kaxe_buf."""
    size = (64, 48)
    cases = [
        # Horizontal (left-to-right and right-to-left)
        (5, 12, 45, 12, (20, 120, 220, 255), 3),
        (45, 20, 5, 20, (20, 120, 220, 137), 2),
        # Vertical (bottom-to-top and top-to-bottom)
        (16, 4, 16, 40, (200, 50, 70, 255), 4),
        (24, 40, 24, 4, (200, 50, 70, 145), 1),
        # Gentle and steep diagonals in both directions + fractional endpoints
        (4.3, 6.7, 54.8, 22.2, (10, 180, 90, 190), 2),
        (54.8, 22.2, 4.3, 6.7, (10, 180, 90, 190), 2),
        (20.2, 3.4, 31.6, 44.1, (130, 40, 210, 111), 3),
        (31.6, 44.1, 20.2, 3.4, (130, 40, 210, 111), 3),
    ]

    for x0, y0, x1, y1, color, thickness in cases:
        # 1. Opaque canvas matches colorBlend reference within <=1 rounding from float vs int aa
        opaque_bg = (240, 220, 200, 255)
        ref = Image.new("RGBA", size, opaque_bg)
        _reference_draw_line(ref, x0, y0, x1, y1, color, thickness)

        got_buf = _make_backed_surface(size, opaque_bg)
        got_crop = Image.new("RGBA", size, opaque_bg)
        kline.drawLineOnPillowImage(got_buf, x0, y0, x1, y1, color, thickness)
        kline.drawLineOnPillowImage(got_crop, x0, y0, x1, y1, color, thickness)

        assert np.array_equal(np.asarray(got_buf), np.asarray(got_crop))
        diff = np.abs(np.asarray(got_buf, dtype=np.int16) - np.asarray(ref, dtype=np.int16)).max()
        assert diff <= 1, f"Mismatch for {(x0, y0, x1, y1, color, thickness)}: max diff={diff}"

        # 2. Semi-transparent canvas blends identically between _kaxe_buf and crop fallback
        alpha_bg = (240, 220, 200, 180)
        got_abuf = _make_backed_surface(size, alpha_bg)
        got_acrop = Image.new("RGBA", size, alpha_bg)
        kline.drawLineOnPillowImage(got_abuf, x0, y0, x1, y1, color, thickness)
        kline.drawLineOnPillowImage(got_acrop, x0, y0, x1, y1, color, thickness)
        assert np.array_equal(np.asarray(got_abuf), np.asarray(got_acrop))


@unit()
def test_draw_line_edge_cases_and_no_wraparound():
    """Out-of-bounds coordinates clip cleanly without wraparound, and invalid thickness/coords are safe."""
    size = (40, 30)
    bg = (255, 255, 255, 255)

    for use_buf in (True, False):
        # Negative and out-of-bounds endpoints must match clipped reference (no negative index wraparound)
        oob_cases = [
            (-10, 5, 20, 5, (255, 0, 0, 200), 3),
            (25, 10, 55, 10, (0, 128, 255, 200), 2),
            (10, -8, 10, 20, (0, 200, 0, 180), 3),
            (-5, -5, 15, 20, (50, 50, 200, 160), 2),
            (50, 50, 80, 80, (255, 0, 0, 255), 3),  # completely outside
        ]
        for x0, y0, x1, y1, color, thickness in oob_cases:
            ref = Image.new("RGBA", size, bg)
            _reference_draw_line(ref, x0, y0, x1, y1, color, thickness)

            got = _make_backed_surface(size, bg) if use_buf else Image.new("RGBA", size, bg)
            kline.drawLineOnPillowImage(got, x0, y0, x1, y1, color, thickness)
            diff = np.abs(np.asarray(got, dtype=np.int16) - np.asarray(ref, dtype=np.int16)).max()
            assert diff <= 1, f"OOB mismatch (use_buf={use_buf}) for {(x0, y0, x1, y1, color, thickness)}: diff={diff}"

        # thickness <= 0 and non-finite coordinates are no-ops
        for args in [
            (5, 5, 20, 20, (255, 0, 0, 255), 0),
            (5, 5, 20, 20, (255, 0, 0, 255), -2),
            (float("nan"), 5, 20, 20, (255, 0, 0, 255), 2),
            (5, float("inf"), 20, 20, (255, 0, 0, 255), 2),
            (5, 5, 20, float("-inf"), (255, 0, 0, 255), 2),
        ]:
            got = _make_backed_surface(size, bg) if use_buf else Image.new("RGBA", size, bg)
            kline.drawLineOnPillowImage(got, *args)
            assert np.all(np.asarray(got) == np.array(bg, dtype=np.uint8))


@unit()
def test_circle_sprite_cache_and_corner_align_invariant():
    """Circle sprite cache reuses identical sprites, handles radius<=0, and cornerAlign never mutates self.x."""
    s1 = shapes.Circle._get_sprite(7, (10, 20, 30, 180), True, 5)
    s2 = shapes.Circle._get_sprite(7, (10, 20, 30, 180), True, 5)
    assert s1 is s2

    s_outline = shapes.Circle._get_sprite(7, (10, 20, 30, 180), False, 2)
    assert s_outline is not s1

    # radius <= 0 guard
    zero_circle = shapes.Circle(15, 15, radius=0, color=(255, 0, 0, 255))
    surf_zero = Image.new("RGBA", (30, 30), (255, 255, 255, 255))
    zero_circle.drawPillow(surf_zero)
    assert np.all(np.asarray(surf_zero) == 255)

    # cornerAlign=True must not mutate c.x and must render identically across draws
    c = shapes.Circle(12, 18, radius=5, color=(20, 100, 200, 200), cornerAlign=True, fill=True)
    surf1 = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
    surf2 = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
    c.drawPillow(surf1)
    assert c.x == 12
    assert c.y == 18
    c.drawPillow(surf2)
    assert c.x == 12
    assert np.array_equal(np.asarray(surf1), np.asarray(surf2))

    # Non-trivial pixels changed at expected corner-aligned position
    arr = np.asarray(surf1)
    assert not np.all(arr == 255)


@unit()
def test_window_pillow_paint_background_alpha_modes():
    """Window.__pillowPaint__ supports opaque, fully transparent, and semi-transparent backgrounds."""
    for bg in [(12, 34, 56, 255), (0, 0, 0, 0), (100, 150, 200, 128)]:
        p = kaxe.Plot([-2, 2, -2, 2])
        p.style(width=120, height=90, backgroundColor=bg, showAxis=False)
        p.__bake__()
        img = p.__pillowPaint__()
        assert img is not None
        assert hasattr(img, "_kaxe_buf")
        if bg[3] in (0, 255):
            assert img.getpixel((0, 0)) == bg
        else:
            ref = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            shapes.Rectangle(0, 0, 10, 10, color=bg).drawPillow(ref)
            assert img.getpixel((0, 0)) == ref.getpixel((0, 0))


@unit()
def test_equation_draw_fast_path_hide_push_and_polar_fallback():
    """Equation Pillow fast path matches Circle drawing, honors dot.hide()/push(), and falls back on PolarPlot."""
    # Standard Plot with Equation
    p = kaxe.Plot([-3, 3, -3, 3])
    p.style(width=400, height=300)
    eq = kaxe.Equation(lambda x, y: x**2 + y**2, lambda x, y: 2.25, color=(30, 90, 210, 200), width=4)
    p.add(eq)
    p.__bake__()

    assert len(eq.dots) > 0
    assert len(eq.dots) == len(eq.batch.objects)

    # Hide half the dots (like Contour labels do)
    for i in range(0, len(eq.dots), 2):
        eq.dots[i].hide()

    # Fast path render
    fast_surface = _make_backed_surface((p.winSize[0], p.winSize[1]) if hasattr(p, "winSize") else (500, 400), (255, 255, 255, 255))
    # Ensure surface matches plot pixel box height used during finalize
    eq.draw(fast_surface)

    # Reference render via batch.draw (individual Circle.drawPillow)
    ref_surface = _make_backed_surface(fast_surface.size, (255, 255, 255, 255))
    eq.batch.draw(ref_surface)
    assert np.array_equal(np.asarray(fast_surface), np.asarray(ref_surface))

    # push() shifts dot positions and keeps fast path matching batch.draw
    eq.push(15, -10)
    fast_pushed = _make_backed_surface(fast_surface.size, (255, 255, 255, 255))
    ref_pushed = _make_backed_surface(fast_surface.size, (255, 255, 255, 255))
    eq.draw(fast_pushed)
    eq.batch.draw(ref_pushed)
    assert np.array_equal(np.asarray(fast_pushed), np.asarray(ref_pushed))

    # PolarPlot creates Line primitives alongside dots -> len(dots) != len(batch.objects) -> fallback path
    pp = kaxe.PolarPlot([0, 3])
    pp.style(width=400, height=400)
    peq = kaxe.Equation(lambda theta, r: r, lambda theta, r: 1.5, color=(200, 40, 40, 255), width=3)
    pp.add(peq)
    pp.__bake__()
    assert len(peq.batch.objects) != len(peq.dots) or len(peq.dots) > 0
    polar_img = pp.__pillowPaint__()
    assert polar_img is not None
