"""Type registry for project export/import."""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

_EXPORTERS: Dict[str, Callable] = {}
_IMPORTERS: Dict[str, Callable] = {}


def register_type(type_name: str, export_fn: Callable, import_fn: Callable) -> None:
    _EXPORTERS[type_name] = export_fn
    _IMPORTERS[type_name] = import_fn


def export_object(obj, ctx) -> dict:
    type_name = type(obj).__name__
    if type_name in _EXPORTERS:
        return _EXPORTERS[type_name](obj, ctx)
    raise TypeError(
        f"Object type {type_name!r} cannot be exported to a .kaxe project (v1)"
    )


def import_object(data: dict, ctx):
    type_name = data.get("type")
    if not type_name or type_name not in _IMPORTERS:
        raise ValueError(f"Unknown or missing object type in project: {type_name!r}")
    return _IMPORTERS[type_name](data, ctx)


def has_exporter(type_name: str) -> bool:
    return type_name in _EXPORTERS
