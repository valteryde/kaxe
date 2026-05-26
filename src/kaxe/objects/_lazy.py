
"""Lazy attribute loading for 3D object exports."""

_D3_EXPORTS = frozenset({
    'Points3D',
    'Function3D',
    'Mesh',
    'Potato',
    'SolidOfRotation',
})


def lazy_getattr(module_globals, name):
    if name in _D3_EXPORTS:
        from . import d3 as _d3
        value = getattr(_d3, name)
        module_globals[name] = value
        return value
    raise AttributeError(f"module {module_globals['__name__']!r} has no attribute {name!r}")
