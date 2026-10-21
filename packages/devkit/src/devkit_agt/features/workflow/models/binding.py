"""Workflow binding value contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HistoryEntry:
    """A workflow segment the unit completed before handing off to the next one.

    ``last_decision`` is the highest decision sequence number when the segment
    ended; decision records up to it belong to finished segments.
    """

    workflow: str
    completed: str  # ISO date
    last_decision: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "completed": self.completed,
            "last_decision": self.last_decision,
        }


@dataclass(frozen=True)
class Binding:
    workflow: str = ""
    history: tuple[HistoryEntry, ...] = ()

    @property
    def bound(self) -> bool:
        return bool(self.workflow)

    @property
    def segment(self) -> int:
        """The index of the current segment: the number of finished segments in the history."""
        return len(self.history)

    @property
    def segment_start(self) -> int:
        """Decision records with a sequence above this belong to the current segment."""
        return self.history[-1].last_decision if self.history else 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow or None,
            "workflow_history": [h.to_dict() for h in self.history],
        }


@dataclass(frozen=True)
class AnchorState:
    """What the engine reads from a unit's anchor: its ``status`` and its binding."""

    status: str
    binding: Binding
