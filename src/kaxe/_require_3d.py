_MSG = "3D features require optional dependencies. Install with: pip install kaxe[3d]"


def require_3d():
    try:
        import OpenGL  # noqa: F401
        import sdl2  # noqa: F401
    except ImportError as exc:
        raise ImportError(_MSG) from exc
