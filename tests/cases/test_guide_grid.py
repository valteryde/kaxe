"""
Tests for PolarGuideGrid overlay on Cartesian plots.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke, unit


@smoke()
@sanity()
@judge(
    elements=["Cartesian axes", "circular arcs", "radial guide lines", "guide labels"],
    focus="polar guide grid overlay legibility",
    min_score=5,
)
def test_splane_guide_grid():
    """S-plane style plot with polar guide overlay on Cartesian axes."""
    plt = kaxe.Plot([-10, 2, -5, 5])
    plt.title("Real Axis", "Imag Axis")
    plt.add(kaxe.PolarGuideGrid(
        center=(0, 0),
        radii=[2, 4, 6, 8, 10],
        angles=[120, 135, 150, 160, 170, 175, 178, 179],
        arc_span=(90, 270),
        radius_labels=True,
        angle_labels=[0.2, 0.4, 0.56, 0.7, 0.81, 0.9, 0.955, 0.988],
        dashed=True,
        color=(128, 128, 128, 180),
    ))
    return plt


@unit()
def test_guide_grid_shape_counts():
    """PolarGuideGrid finalize produces expected guide geometry."""
    plt = kaxe.Plot([-10, 2, -5, 5])
    grid = kaxe.PolarGuideGrid(
        center=(0, 0),
        radii=[2, 4, 6],
        angles=[120, 150],
        arc_span=(90, 270),
        radius_labels=True,
        angle_labels=True,
        symmetric=True,
    )
    plt.add(grid)
    plt.__bake__()

    # 3 arcs + 3 radius labels + 4 radials (2 angles x symmetric) + 4 angle labels
    assert grid._shape_count >= 10


@unit()
def test_guide_grid_full_circles():
    """PolarGuideGrid draws full circles without arc_span."""
    plt = kaxe.Plot([-5, 5, -5, 5])
    grid = kaxe.PolarGuideGrid(
        center=(0, 0),
        radii=[1, 2, 3],
        angles=[0, 90],
        symmetric=False,
    )
    plt.add(grid)
    plt.__bake__()
    assert grid._shape_count >= 5
