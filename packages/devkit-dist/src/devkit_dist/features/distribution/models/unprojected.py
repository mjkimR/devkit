"""Unavailable agent projections reported by installation operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Unprojected:
    """A subagent with ``variants`` that has no file for a selected agent."""

    bundle: str
    asset: str
    agent: str

    def to_dict(self) -> dict[str, str]:
        return {"bundle": self.bundle, "asset": self.asset, "agent": self.agent}
