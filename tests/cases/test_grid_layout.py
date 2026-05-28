"""
Grid layout tests: stacked subplots must not overlap at shared boundaries.
"""

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from PIL import Image
from runner import unit
from scipy.signal import TransferFunction, bode


def _make_stacked_bode_grid(width=3000, height=800):
    num = [1, 3, 3]
    den = [1, 2, 1, 1]
    tf = TransferFunction(num, den)
    w, mag, phase = bode(tf, n=1000)

    grid = kaxe.Grid()
    grid.style(width=width, height=height)
    grid.showProgressBar = False
    grid.printDebugInfo = False

    plt1 = kaxe.BoxedLogPlot(firstAxisLog=True, secondAxisLog=False)
    plt1.add(kaxe.Points2D(w, mag, connect=True))

    plt2 = kaxe.BoxedLogPlot(firstAxisLog=True, secondAxisLog=False)
    plt2.add(kaxe.Points2D(w, phase, connect=True, color=(109, 69, 76, 255)))

    grid.addColumn(plt1, plt2)
    return grid


@unit()
def test_grid_stacked_log_no_overlap():
    grid = _make_stacked_bode_grid()
    layout = grid._prepare_cells(vector=False)

    cell_height = layout["cellHeight"]
    gaprows = layout["gaprows"]
    toppadding = layout["toppadding"]
    bottompadding = layout["bottompadding"]
    outer = grid.getAttr("outerPadding")

    min_height = (
        2 * cell_height
        + sum(gaprows)
        + toppadding
        + bottompadding
        + outer[1]
        + outer[3]
    )
    assert layout["size"][1] >= min_height
    assert len(gaprows) == 1
    assert gaprows[0] >= grid.gridGap[1]

    buf = BytesIO()
    grid.save(buf, format="png")
    buf.seek(0)
    image = Image.open(buf).convert("RGBA")
    bg = grid.getAttr("backgroundColor")

    gap_start = toppadding + outer[1] + cell_height
    gap_end = gap_start + gaprows[0]
    sample_y = int((gap_start + gap_end) / 2)
    sample_x_start = int(image.width * 0.25)
    sample_x_end = int(image.width * 0.75)

    dark_pixels = 0
    sampled = 0
    for x in range(sample_x_start, sample_x_end, 8):
        pixel = image.getpixel((x, sample_y))
        sampled += 1
        if pixel[:3] != bg[:3]:
            dark_pixels += 1

    assert sampled > 0
    assert dark_pixels == 0, (
        f"expected clear gap between stacked cells at y={sample_y}, "
        f"found {dark_pixels}/{sampled} non-background pixels"
    )


@unit()
def test_grid_rebakes_resized_cell():
    plot = kaxe.Plot([-3, 3, -3, 3])
    plot.add(kaxe.Function2D(lambda x: x**2 - 2))
    plot.style(width=1200, height=600)
    plot.showProgressBar = False
    plot.printDebugInfo = False
    plot.save(BytesIO())

    standalone_size = plot.getSize()

    grid = kaxe.Grid()
    grid.style(width=1200, height=600)
    grid.showProgressBar = False
    grid.printDebugInfo = False
    grid.addRow(plot)

    grid._prepare_cells(vector=False)
    cell_size = plot.getSize()

    assert cell_size != standalone_size
    assert plot.getAttr("width") == 1200
