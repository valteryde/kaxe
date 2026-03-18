"""
Unit tests for zoom inset render scale calculation.

The scale factor determines how much to magnify points/lines in the zoom view.
Scale >= 1 when zoom has more pixels per data unit than the main plot.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from kaxe.plot.zoom_connector import compute_render_scale
from runner import unit


@unit()
def test_render_scale_zoomed_in():
    """Zoom shows smaller data range in similar pixel area -> scale > 1."""
    # Main: 1000px for 10 units = 100 px/unit
    # Zoom: 400px for 2 units = 200 px/unit -> 2x magnification
    scale = compute_render_scale(
        main_width=1000, main_height=800,
        main_x_range=10, main_y_range=8,
        inset_w=400, inset_h=300,
        zoom_x_range=2, zoom_y_range=1.5,
    )
    assert scale >= 1.0
    # scale_x = 200/100 = 2, scale_y = 200/100 = 2, geom_mean = 2
    assert 1.9 <= scale <= 2.1


@unit()
def test_render_scale_same_as_main():
    """Zoom shows same data range as main -> scale ~= 1."""
    scale = compute_render_scale(
        main_width=1000, main_height=800,
        main_x_range=10, main_y_range=8,
        inset_w=1000, inset_h=800,
        zoom_x_range=10, zoom_y_range=8,
    )
    assert 0.99 <= scale <= 1.01


@unit()
def test_render_scale_zoomed_out():
    """Zoom shows larger data range in smaller area -> scale clamped to 1."""
    scale = compute_render_scale(
        main_width=1000, main_height=800,
        main_x_range=10, main_y_range=8,
        inset_w=200, inset_h=150,
        zoom_x_range=20, zoom_y_range=16,
    )
    assert scale == 1.0


@unit()
def test_render_scale_zero_range_protection():
    """Zero data range should not crash."""
    scale = compute_render_scale(
        main_width=1000, main_height=800,
        main_x_range=0, main_y_range=8,
        inset_w=400, inset_h=300,
        zoom_x_range=2, zoom_y_range=0,
    )
    assert scale >= 1.0


@unit()
def test_render_scale_asymmetric():
    """Different x and y magnification -> geometric mean."""
    # Main: 1000/10=100, 800/8=100 px/unit
    # Zoom x: 400/2=200 (2x), zoom y: 300/6=50 (0.5x)
    # scale_x=2, scale_y=0.5, geom_mean=sqrt(1)=1
    scale = compute_render_scale(
        main_width=1000, main_height=800,
        main_x_range=10, main_y_range=8,
        inset_w=400, inset_h=300,
        zoom_x_range=2, zoom_y_range=6,
    )
    assert 0.9 <= scale <= 1.1
