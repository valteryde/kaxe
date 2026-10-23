_MSG = "Viewer features require optional dependencies. Install with: pip install kaxe[viewer]"


def require_viewer():
    try:
        import pyglet  # noqa: F401
    except ImportError as exc:
        raise ImportError(_MSG) from exc
