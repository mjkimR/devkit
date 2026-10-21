"""Immutable Git snapshot metadata for a rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Snapshot:
    root: Path
    mode: str  # "staged" or "ci"
    tree: str
    base: str
    changed: tuple[str, ...]  # changed regular files present in ``tree``
    deleted: tuple[str, ...]
    files: tuple[tuple[str, str, str], ...]  # (path, object sha, mode) of every regular file, symlink and submodule

    def describe(self) -> str:
        return (
            f"[SNAPSHOT: mode={self.mode} tree={self.tree[:12]} base={self.base[:12]} "
            f"changed={len(self.changed)} deleted={len(self.deleted)}]"
        )
