"""Upstream drift of a project-owned override."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Drift:
    bundle: str
    asset: str
    path: str

    @property
    def message(self) -> str:
        return f"upstream drift detected for {self.bundle}:{self.asset}"

    def to_dict(self) -> dict[str, str]:
        return {"bundle": self.bundle, "asset": self.asset, "path": self.path, "message": self.message}
