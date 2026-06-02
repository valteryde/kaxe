"""Jupyter / IPython inline display helpers."""

from io import BytesIO


def is_notebook():
    from .window import terminaltype

    return terminaltype in ("jupyter", "ipython")


def jupyter_display_width():
    from .window import settings

    return settings.get("jupyterDisplayWidth", 800)


def to_png_bytes(plot):
    """Render a plot or grid to PNG bytes in memory."""
    buf = BytesIO()
    plot.save(buf)
    return buf.getvalue()


def display_png_bytes(data, width=None):
    """Display PNG bytes inline in a Jupyter or IPython session."""
    from IPython import display  # pyright: ignore[reportMissingModuleSource]

    if width is None:
        width = jupyter_display_width()
    image = display.Image(data=data, width=width, unconfined=True)
    display.display(image)
