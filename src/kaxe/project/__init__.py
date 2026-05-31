"""Kaxe project file (.kaxe) save/load."""

from __future__ import annotations

from typing import Union
from pathlib import Path

from ..core.styles import resetColor
from . import serializers as _serializers  # noqa: F401 — register type handlers
from .document import ProjectDocument
from .window import assert_project_supported


def save_project(window, path: Union[str, Path]) -> None:
    """
    Save a plot window to a ``.kaxe`` JSON project file.

    The file stores styles, titles, numeric data, and sampled curves so the
    figure can be reopened and edited without the original script.
    """
    assert_project_supported(window)
    ProjectDocument.from_window(window).write(path)


def load_project(path: Union[str, Path]):
    """
    Load a plot window from a ``.kaxe`` project file.

    Returns a fresh, unbaked window ready for ``style()``, ``title()``, and ``save()``.
    """
    resetColor()
    return ProjectDocument.read(path).to_window()


__all__ = ["save_project", "load_project", "ProjectDocument"]
