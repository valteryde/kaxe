"""Default color palettes for Kaxe figures.

Series colors follow the Okabe–Ito palette (colorblind-safe, common in
publication figures). See: https://jfly.uni-koeln.de/color/

Pure black is omitted from the series cycle; it remains reserved for axes,
ticks, and text ink.
"""

from __future__ import annotations

from .color import to_rgba

# Okabe–Ito categorical series (7 colors; black excluded from data series).
OKABE_ITO_SERIES = [
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
]

# Sequential ramp for heatmaps, contours, and color scales (blue → green).
DEFAULT_SEQUENTIAL_STEPS = [
    "#0072B2",
    "#2088A8",
    "#329E96",
    "#009E73",
    "#3CB371",
    "#56B4E9",
]

DEFAULT_SERIES_COLORS = [to_rgba(c) for c in OKABE_ITO_SERIES]


def apply_series_palette(color_list: list | None = None) -> list[tuple[int, int, int, int]]:
    """Normalize a color list to RGBA tuples, or return the default series palette."""
    if color_list is None:
        return list(DEFAULT_SERIES_COLORS)
    return [to_rgba(c) for c in color_list]
