"""
Unit tests for SDL cleanup when the 3D viewer closes in Jupyter.
"""

import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from runner import unit


@unit()
def test_release_sdl_window_skips_quit_in_jupyter():
    from kaxe.core.d3 import openglrender as ogl

    window = object()
    gl_context = object()

    with mock.patch.object(ogl, "sdl2") as mock_sdl, mock.patch.object(
        ogl, "_should_quit_sdl_subsystem", return_value=False
    ):
        ogl._release_sdl_window(window, gl_context)

    mock_sdl.SDL_GL_DeleteContext.assert_called_once_with(gl_context)
    mock_sdl.SDL_DestroyWindow.assert_called_once_with(window)
    mock_sdl.SDL_Quit.assert_not_called()


@unit()
def test_release_sdl_window_quits_outside_jupyter():
    from kaxe.core.d3 import openglrender as ogl

    window = object()
    gl_context = object()

    with mock.patch.object(ogl, "sdl2") as mock_sdl, mock.patch.object(
        ogl, "_should_quit_sdl_subsystem", return_value=True
    ):
        ogl._release_sdl_window(window, gl_context)

    mock_sdl.SDL_Quit.assert_called_once()


@unit()
def test_should_quit_sdl_subsystem_false_in_jupyter():
    from kaxe.core import window as win
    from kaxe.core.d3 import openglrender as ogl

    with mock.patch.object(win, "terminaltype", "jupyter"):
        assert ogl._should_quit_sdl_subsystem() is False


@unit()
def test_should_quit_sdl_subsystem_true_in_terminal():
    from kaxe.core import window as win
    from kaxe.core.d3 import openglrender as ogl

    with mock.patch.object(win, "terminaltype", "terminal"):
        assert ogl._should_quit_sdl_subsystem() is True
