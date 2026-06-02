"""
Unit tests for Jupyter inline display and deferred progress.
"""

import sys
from io import BytesIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from runner import unit


def _small_plot():
    import kaxe

    plt = kaxe.Plot([-5, 5, -5, 5])
    plt.style(width=200, height=200, fontSize=20)
    plt.add(kaxe.Function2D(lambda x: x))
    return plt


@unit()
def test_to_png_bytes_returns_png_magic():
    from kaxe.core.ipython_display import to_png_bytes

    data = to_png_bytes(_small_plot())
    assert data[:4] == b"\x89PNG"
    assert len(data) > 100


@unit()
def test_show_uses_in_memory_display_in_notebook():
    from kaxe.core import window as win

    plt = _small_plot()
    png = b"\x89PNGfake"

    with mock.patch.object(win, "terminaltype", "jupyter"), mock.patch.object(
        win, "to_png_bytes", return_value=png
    ) as mock_to_bytes, mock.patch.object(win, "display_png_bytes") as mock_display, mock.patch.object(
        win, "is_notebook", return_value=True
    ):
        plt.show()

    mock_to_bytes.assert_called_once_with(plt)
    mock_display.assert_called_once_with(png)


@unit()
def test_show_opens_pillow_viewer_in_terminal():
    from kaxe.core import window as win
    from PIL import Image

    plt = _small_plot()

    with mock.patch.object(win, "terminaltype", "terminal"), mock.patch.object(
        Image.Image, "show"
    ) as mock_show:
        plt.show()

    mock_show.assert_called_once()


@unit()
def test_repr_png_returns_bytes_in_notebook():
    from kaxe.core import window as win

    plt = _small_plot()

    with mock.patch.object(win, "terminaltype", "jupyter"):
        data = plt._repr_png_()

    assert data is not None
    assert data[:4] == b"\x89PNG"


@unit()
def test_repr_png_returns_none_in_terminal():
    from kaxe.core import window as win

    plt = _small_plot()

    with mock.patch.object(win, "terminaltype", "terminal"):
        assert plt._repr_png_() is None


@unit()
def test_grid_repr_png_returns_bytes_in_notebook():
    import kaxe
    from kaxe.core import window as win

    grid = kaxe.Grid()
    grid.style(width=200, height=200, fontSize=20)
    grid.addRow(_small_plot())

    with mock.patch.object(win, "terminaltype", "jupyter"):
        data = grid._repr_png_()

    assert data is not None
    assert data[:4] == b"\x89PNG"


@unit()
def test_deferred_progress_waits_for_threshold():
    from kaxe.core.progress import _DeferredProgress

    times = iter([0.0, 0.5, 0.9, 1.1, 1.2])

    with mock.patch("kaxe.core.progress.time.time", side_effect=lambda: next(times)), mock.patch(
        "kaxe.core.progress.tqdm.tqdm"
    ) as mock_tqdm:
        mock_bar = mock.Mock()
        mock_tqdm.return_value = mock_bar
        progress = _DeferredProgress(3, "Baking", threshold=1.0)
        progress.update()
        progress.update()
        mock_tqdm.assert_not_called()
        progress.update()
        mock_tqdm.assert_called_once_with(total=3, desc="Baking", initial=3)
        mock_bar.update.assert_called_once_with(1)
        progress.close()
        mock_bar.close.assert_called_once()


@unit()
def test_make_progress_bar_suppressed_when_show_false():
    from kaxe.core.progress import _NoProgress, make_progress_bar

    bar = make_progress_bar(False, 5, "Baking")
    assert isinstance(bar, _NoProgress)


@unit()
def test_make_progress_bar_deferred_in_jupyter():
    from kaxe.core import window as win
    from kaxe.core.progress import _DeferredProgress, make_progress_bar

    with mock.patch.object(win, "terminaltype", "jupyter"):
        bar = make_progress_bar(True, 5, "Baking")

    assert isinstance(bar, _DeferredProgress)


@unit()
def test_remove_info_disables_progress_on_new_window():
    import kaxe
    from kaxe.core import window as win
    from kaxe.core.progress import _NoProgress, make_progress_bar

    win.setSetting(removeInfo=True)
    try:
        plt = kaxe.Plot([-5, 5, -5, 5])
        assert plt.showProgressBar is False
        bar = make_progress_bar(plt.showProgressBar, 3, "Baking")
        assert isinstance(bar, _NoProgress)
    finally:
        win.setSetting(removeInfo=False)


@unit()
def test_display_png_bytes_uses_data_not_filename():
    from kaxe.core.ipython_display import display_png_bytes

    png = b"\x89PNGtest"

    with mock.patch("IPython.display.Image") as mock_image_cls, mock.patch(
        "IPython.display.display"
    ) as mock_display:
        mock_image_cls.return_value = "image-object"
        display_png_bytes(png, width=640)

    mock_image_cls.assert_called_once_with(data=png, width=640, unconfined=True)
    mock_display.assert_called_once_with("image-object")
    call_kwargs = mock_image_cls.call_args.kwargs
    assert "filename" not in call_kwargs
