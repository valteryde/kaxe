"""Kaxe project document (.kaxe JSON) encode/decode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

from .context import ImportContext
from .window import build_document, import_window

KAXE_VERSION = 1


class ProjectDocument:
    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def from_window(cls, window) -> "ProjectDocument":
        payload = build_document(window)
        payload["kaxe_version"] = KAXE_VERSION
        return cls(payload)

    def to_window(self):
        version = self.data.get("kaxe_version", 1)
        if version != KAXE_VERSION:
            raise ValueError(
                f"Unsupported kaxe_version {version} (this Kaxe supports version {KAXE_VERSION})"
            )
        return import_window(self.data, ImportContext())

    def encode(self, indent: int = 2) -> str:
        return json.dumps(self.data, indent=indent, ensure_ascii=False)

    @classmethod
    def decode(cls, text: str) -> "ProjectDocument":
        return cls(json.loads(text))

    def write(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.write_text(self.encode(), encoding="utf-8")

    @classmethod
    def read(cls, path: Union[str, Path]) -> "ProjectDocument":
        path = Path(path)
        return cls.decode(path.read_text(encoding="utf-8"))
