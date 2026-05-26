
"""Lazy attribute loading for plot submodules with heavy dependencies."""

_D3_EXPORTS = frozenset({
    'Plot3D',
    'PlotCenter3D',
    'PlotFrame3D',
    'PlotEmpty3D',
})


def lazy_getattr(module_globals, name):
    if name in _D3_EXPORTS:
        from . import d3 as _d3
        value = getattr(_d3, name)
        module_globals[name] = value
        return value
    raise AttributeError(f"module {module_globals['__name__']!r} has no attribute {name!r}")
