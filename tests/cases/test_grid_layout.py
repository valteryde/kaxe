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


def _make_simple_plot(legend_labels=()):
    plot = kaxe.Plot([-3, 3, -3, 3])
    for idx, label in enumerate(legend_labels):
        fn = kaxe.Function2D(lambda x, s=(1 if idx % 2 == 0 else -1): s * x)
        if label is not None:
            fn.legend(label)
        plot.add(fn)
    if not legend_labels:
        plot.add(kaxe.Function2D(lambda x: x))
    plot.showProgressBar = False
    plot.printDebugInfo = False
    return plot


@unit()
def test_grid_subplot_legend_in_second_column_not_clipped():
    """Subplot legends in column >= 1 must contribute to bottompadding and fit in PNG & SVG."""
    import xml.etree.ElementTree as ET

    def build_grid():
        grid = kaxe.Grid()
        grid.style(width=1200, height=1000)
        grid.showProgressBar = False
        grid.printDebugInfo = False

        p_tl = _make_simple_plot()
        p_tr = _make_simple_plot()
        p_bl = _make_simple_plot()
        p_br = _make_simple_plot(["Very long series name A", "Very long series name B"])

        grid.addRow(p_tl, p_tr)
        grid.addRow(p_bl, p_br)
        return grid, p_bl, p_br

    grid, p_bl, p_br = build_grid()
    png_buf = BytesIO()
    grid.save(png_buf, format="png")
    png_buf.seek(0)
    image = Image.open(png_buf).convert("RGBA")
    bg = grid.getAttr("backgroundColor")
    outer = grid.getAttr("outerPadding")
    assert p_br.padding[1] > p_bl.padding[1]

    # Legend pixels must appear in the extra bottompadding band and stay inside outerPadding[1].
    legend_band_top = image.height - outer[1] - (p_br.padding[1] - p_bl.padding[1])
    legend_band_bottom = image.height - outer[1]
    band_pixels = 0
    for y in range(legend_band_top, legend_band_bottom):
        for x in range(image.width // 2, image.width, 4):
            if image.getpixel((x, y))[:3] != bg[:3]:
                band_pixels += 1
    assert band_pixels > 0

    for y in range(image.height - outer[1], image.height):
        for x in range(0, image.width, 4):
            assert image.getpixel((x, y))[:3] == bg[:3]

    svg_grid, _, _ = build_grid()
    svg_buf = BytesIO()
    svg_grid.save(svg_buf, format="svg")
    root = ET.fromstring(svg_buf.getvalue().decode("utf-8"))
    assert (int(root.get("width")), int(root.get("height"))) == image.size


@unit()
def test_grid_subplot_legend_does_not_overwrite_grid_legend():
    """A column-1 subplot legend must not overlap or erase the shared grid legend."""
    grid = kaxe.Grid()
    grid.style(width=1200, height=500)
    grid.showProgressBar = False
    grid.printDebugInfo = False

    pa = _make_simple_plot()
    pb = _make_simple_plot(["Cell legend"])
    grid.addRow(pa, pb)
    grid.legends(("Grid Legend", kaxe.Symbol.CIRCLE, (200, 0, 0, 255)))

    buf = BytesIO()
    grid.save(buf, format="png")
    buf.seek(0)
    image = Image.open(buf).convert("RGBA")

    # Verify the red grid-legend circle marker and text below pb are intact at the bottom.
    red_pixels = 0
    dark_text_pixels = 0
    split_y = image.height - 90
    for y in range(split_y, image.height):
        for x in range(0, image.width, 2):
            r, g, b, _ = image.getpixel((x, y))
            if r > 150 and g < 50 and b < 50:
                red_pixels += 1
            elif r < 50 and g < 50 and b < 50:
                dark_text_pixels += 1
    assert red_pixels > 50
    assert dark_text_pixels > 50


@unit()
def test_grid_ragged_row_legend_not_clipped():
    """Ragged grids must keep overhanging cells in shorter columns inside the canvas."""
    grid = kaxe.Grid()
    grid.style(width=1000, height=600)
    grid.showProgressBar = False
    grid.printDebugInfo = False

    pa = _make_simple_plot()
    pb = _make_simple_plot([f"Long legend entry {i}" for i in range(6)])
    pc = _make_simple_plot()
    grid.addRow(pa, pb)
    grid.addRow(pc)

    layout = grid._prepare_cells(vector=False)
    expected_min_height = (
        layout["toppadding"]
        + layout["cellHeight"]
        + pb.padding[1]
        + grid.getAttr("outerPadding")[1]
        + grid.getAttr("outerPadding")[3]
    )
    assert layout["size"][1] >= expected_min_height


@unit()
def test_grid_asymmetric_outer_padding_legend_bottom_margin():
    """Shared grid legend must use outerPadding[1] (bottom), not outerPadding[3] (top)."""
    grid = kaxe.Grid()
    grid.style(width=1000, height=500, outerPadding=[10, 80, 10, 5])
    grid.showProgressBar = False
    grid.printDebugInfo = False

    p1 = _make_simple_plot()
    grid.addRow(p1)
    grid.legends(("Bottom margin check", kaxe.Symbol.CIRCLE, (200, 0, 0, 255)))

    buf = BytesIO()
    grid.save(buf, format="png")
    buf.seek(0)
    image = Image.open(buf).convert("RGBA")
    bg = grid.getAttr("backgroundColor")

    # Bottom 80px (outerPadding[1]) must remain pure background.
    for y in range(image.height - 80, image.height):
        for x in range(0, image.width, 4):
            assert image.getpixel((x, y))[:3] == bg[:3]

    # Legend content must be present just above the 80px bottom padding.
    legend_hits = 0
    for y in range(image.height - 130, image.height - 80):
        for x in range(0, image.width, 4):
            if image.getpixel((x, y))[:3] != bg[:3]:
                legend_hits += 1
    assert legend_hits > 0
