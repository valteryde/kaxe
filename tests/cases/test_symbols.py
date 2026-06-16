"""Unit and smoke tests for procedural kaxe symbols."""

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import kaxe
from kaxe.core.shapes import ImageShape
from kaxe.core.symbol import SymbolGroup, makeSymbolShapes, symbol
from runner import sanity, smoke, unit

ALL_SYMBOLS = (
    symbol.CIRCLE,
    symbol.LINE,
    symbol.THICKLINE,
    symbol.RECTANGLE,
    symbol.TRIANGLE,
    symbol.STAR,
    symbol.LOLLIPOP,
    symbol.CROSS,
    symbol.DONUT,
)


@unit()
def test_make_symbol_shapes_returns_shape_for_all_constants():
    """Every documented symbol constant produces a drawable shape."""
    for sym in ALL_SYMBOLS:
        shape = makeSymbolShapes(sym, 24, (10, 20, 30, 255), batch=None)
        assert shape is not None, sym
        width, height = shape.getBoundingBox()
        assert width > 0, sym
        assert height > 0, sym


@unit()
def test_procedural_symbols_do_not_use_image_shape():
    """Previously PNG-backed symbols are built from vector primitives."""
    for sym in (symbol.TRIANGLE, symbol.STAR, symbol.CROSS, symbol.LOLLIPOP, symbol.DONUT):
        shape = makeSymbolShapes(sym, 24, (10, 20, 30, 255), batch=None)
        assert not isinstance(shape, ImageShape), sym
        if isinstance(shape, SymbolGroup):
            for part in shape.parts:
                assert not isinstance(part, ImageShape), sym


@unit()
def test_star_symbol_was_missing():
    """STAR is implemented and was previously absent."""
    assert makeSymbolShapes(symbol.STAR, 16, (0, 0, 0, 255), batch=None) is not None


def _plot_with_all_symbols():
    plot = kaxe.Plot([0, 10, 0, 10])
    plot.showProgressBar = False
    plot.printDebugInfo = False
    colors = [
        (200, 0, 0, 255),
        (0, 114, 178, 255),
        (0, 128, 0, 255),
        (222, 107, 72, 255),
    ]
    for i, sym in enumerate(ALL_SYMBOLS):
        plot.add(
            kaxe.Points2D([1 + i * 0.5], [1 + i * 0.5], symbol=sym, color=colors[i % len(colors)])
            .legend(sym, symbol=sym, color=colors[i % len(colors)])
        )
    return plot


@smoke()
@sanity()
def test_all_symbols_render_png():
    """All symbols render on points and in the legend without error."""
    return _plot_with_all_symbols()


@unit()
def test_all_symbols_render_svg():
    """SVG export path works for all procedural symbols."""
    plot = _plot_with_all_symbols()
    buf = BytesIO()
    plot.save(buf, format="svg")
    content = buf.getvalue().decode("utf-8")
    assert "<svg" in content
