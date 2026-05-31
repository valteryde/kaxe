"""Export/import context for project serialization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ExportContext:
    window: Any
    sample_count: int = 2000

    def plot_identity(self) -> Optional[str]:
        return getattr(self.window, "identity", None)

    def plot_window_axis(self):
        return getattr(self.window, "windowAxis", None)


@dataclass
class ImportContext:
    """Placeholder for future blob deduplication and path resolution."""
    pass
