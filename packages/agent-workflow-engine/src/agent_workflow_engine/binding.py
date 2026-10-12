"""The binding recorded in a unit's anchor: which workflow it follows and the schema hash."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_workflow_engine import frontmatter

WORKFLOW_KEY = "workflow"
HASH_KEY = "workflow_hash"


@dataclass(frozen=True)
class Binding:
    workflow: str = ""
    hash: str = ""

    @property
    def bound(self) -> bool:
        return bool(self.workflow and self.hash)

    def to_dict(self) -> dict[str, Any]:
        return {"workflow": self.workflow or None, "workflow_hash": self.hash or None}


def read_binding(anchor_path: Path) -> Binding:
    """Binding from the anchor's frontmatter; an anchor without the keys is unbound."""
    data = frontmatter.read(anchor_path)
    return Binding(workflow=frontmatter.field(data, WORKFLOW_KEY), hash=frontmatter.field(data, HASH_KEY))


def write_binding(anchor_path: Path, binding: Binding) -> None:
    """Record the binding, replacing existing keys and preserving every other byte."""
    text = anchor_path.read_text("utf-8")
    updated = frontmatter.update(text, {WORKFLOW_KEY: binding.workflow, HASH_KEY: binding.hash})
    anchor_path.write_text(updated, "utf-8")
