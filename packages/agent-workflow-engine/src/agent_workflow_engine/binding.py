"""The binding recorded in a unit's anchor: which workflow it follows, the schema hash and the handoff history."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agent_workflow_engine import frontmatter

WORKFLOW_KEY = "workflow"
HASH_KEY = "workflow_hash"
HISTORY_KEY = "workflow_history"


@dataclass(frozen=True)
class HistoryEntry:
    """A workflow the unit completed before handing off to the next one."""

    workflow: str
    hash: str
    completed: str  # ISO date

    def to_dict(self) -> dict[str, str]:
        return {"workflow": self.workflow, "hash": self.hash, "completed": self.completed}


@dataclass(frozen=True)
class Binding:
    workflow: str = ""
    hash: str = ""
    history: tuple[HistoryEntry, ...] = ()

    @property
    def bound(self) -> bool:
        return bool(self.workflow and self.hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow or None,
            "workflow_hash": self.hash or None,
            "workflow_history": [h.to_dict() for h in self.history],
        }


def _history(value: Any) -> tuple[HistoryEntry, ...]:
    if not isinstance(value, list):
        return ()
    out: list[HistoryEntry] = []
    for item in value:
        if isinstance(item, dict) and isinstance(item.get("workflow"), str):
            out.append(
                HistoryEntry(
                    workflow=item["workflow"],
                    hash=frontmatter.field(item, "hash"),
                    completed=frontmatter.field(item, "completed"),
                )
            )
    return tuple(out)


def read_binding(anchor_path: Path) -> Binding:
    """Binding from the anchor's frontmatter; an anchor without the keys is unbound."""
    data = frontmatter.read(anchor_path)
    return Binding(
        workflow=frontmatter.field(data, WORKFLOW_KEY),
        hash=frontmatter.field(data, HASH_KEY),
        history=_history(data.get(HISTORY_KEY)),
    )


def write_binding(anchor_path: Path, binding: Binding) -> None:
    """Record the binding, replacing existing keys and preserving every other byte.

    The history is written as a single flow-style YAML line so the anchor keeps
    one top-level line per key.
    """
    text = anchor_path.read_text("utf-8")
    updates = {WORKFLOW_KEY: binding.workflow, HASH_KEY: binding.hash}
    if binding.history:
        flow = yaml.safe_dump(
            [h.to_dict() for h in binding.history], default_flow_style=True, sort_keys=False, width=10**6
        ).strip()
        updates[HISTORY_KEY] = flow
    updated = frontmatter.update(text, updates)
    anchor_path.write_text(updated, "utf-8")
