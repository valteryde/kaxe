"""
Unit tests for zoom inset connector placement logic.

Tests the math that determines which selection-box corners connect to which
inset corners based on relative position (above, below, left, right).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from kaxe.plot.zoom_connector import connector_placement
from runner import unit


@unit()
def test_connector_placement_inset_right():
    """Inset to the right of selection -> mode 'right'."""
    # Selection: (100, 200) to (200, 400) -> sel_left=100, sel_right=200, sel_bottom=200, sel_top=400
    # Inset to the right: inset_x=250, so inset_x > sel_right
    mode = connector_placement(
        inset_x=250, inset_y=250, surf_w=100, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(300, 300),
    )
    assert mode == "right"


@unit()
def test_connector_placement_inset_left():
    """Inset to the left of selection -> mode 'left'."""
    # Inset left: inset_x + surf_w < sel_left
    mode = connector_placement(
        inset_x=10, inset_y=250, surf_w=80, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(50, 300),
    )
    assert mode == "left"


@unit()
def test_connector_placement_inset_below():
    """Inset below selection -> mode 'vertical' (top-to-top, bottom-to-bottom)."""
    # Inset below: inset_y + surf_h < sel_bottom
    # Selection bottom at 200, inset top at inset_y+surf_h = 50+100 = 150 < 200
    mode = connector_placement(
        inset_x=120, inset_y=50, surf_w=80, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(150, 10),
    )
    assert mode == "vertical"


@unit()
def test_connector_placement_inset_above():
    """Inset above selection -> mode 'vertical'."""
    # Inset above: inset_y > sel_top
    mode = connector_placement(
        inset_x=120, inset_y=450, surf_w=80, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(150, 500),
    )
    assert mode == "vertical"


@unit()
def test_connector_placement_named_pos_top_right():
    """Named position 'top-right' -> mode 'right'."""
    mode = connector_placement(
        inset_x=300, inset_y=100, surf_w=100, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos="top-right",
    )
    assert mode == "right"


@unit()
def test_connector_placement_named_pos_bottom_left():
    """Named position 'bottom-left' with inset to the left -> mode 'left'."""
    mode = connector_placement(
        inset_x=50, inset_y=50, surf_w=100, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos="bottom-left",
    )
    assert mode == "left"


@unit()
def test_connector_placement_named_pos_top_left():
    """Named position 'top-left' with inset to the left -> mode 'left'."""
    mode = connector_placement(
        inset_x=50, inset_y=450, surf_w=100, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos="top-left",
    )
    assert mode == "left"


@unit()
def test_connector_placement_fallback_left_right():
    """When inset overlaps or is diagonal, fallback to 'left-right'."""
    # Inset overlaps selection (e.g. centered): not right, not left, not above, not below
    mode = connector_placement(
        inset_x=130, inset_y=250, surf_w=80, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(150, 300),
    )
    assert mode == "left-right"


@unit()
def test_connector_placement_inset_below_by_coords():
    """Inset below selection when pos is (x,y) data coords: inset_y + surf_h < sel_bottom."""
    # Simulate: selection in middle of plot, inset at bottom. Pixel coords:
    # sel_bottom=300, inset at y=50, surf_h=200 -> inset top = 250 < 300
    mode = connector_placement(
        inset_x=400, inset_y=50, surf_w=200, surf_h=200,
        sel_left=300, sel_right=500, sel_bottom=300, sel_top=500,
        pos=(70, 5),  # data coords - pixel conversion would put inset below
    )
    # With pos as tuple, we use geometry: inset_y+surf_h=250 < sel_bottom=300
    assert mode == "vertical"


@unit()
def test_connector_placement_boundary_right():
    """Inset exactly at sel_right boundary -> not right (inset_x must be > sel_right)."""
    mode = connector_placement(
        inset_x=200, inset_y=250, surf_w=80, surf_h=100,
        sel_left=100, sel_right=200, sel_bottom=200, sel_top=400,
        pos=(250, 300),
    )
    # inset_x=200 is NOT > sel_right=200, so not "right"
    assert mode != "right"
