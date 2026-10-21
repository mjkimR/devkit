"""The binding recorded in a unit's anchor: the workflow it follows, the handoff history."""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from devkit_core.base.errors import FrontmatterError

import devkit_agt.features.workflow.repositories.unit.frontmatter as frontmatter
from devkit_agt.features.workflow.models.binding import AnchorState as AnchorState
from devkit_agt.features.workflow.models.binding import Binding as Binding
from devkit_agt.features.workflow.models.binding import HistoryEntry as HistoryEntry
from devkit_agt.features.workflow.models.errors import AnchorInvalidError
from devkit_agt.features.workflow.repositories.unit.records import temporary_path

WORKFLOW_KEY = "workflow"
HISTORY_KEY = "workflow_history"


def _history(value: Any) -> tuple[HistoryEntry, ...]:
    if not isinstance(value, list):
        return ()
    out: list[HistoryEntry] = []
    for item in value:
        if isinstance(item, dict) and isinstance(item.get("workflow"), str):
            last = item.get("last_decision")
            out.append(
                HistoryEntry(
                    workflow=item["workflow"],
                    completed=frontmatter.field(item, "completed"),
                    last_decision=last if isinstance(last, int) and not isinstance(last, bool) else 0,
                )
            )
    return tuple(out)


def binding_from(data: Mapping[str, Any]) -> Binding:
    """The binding recorded in an anchor's parsed frontmatter."""
    return Binding(
        workflow=frontmatter.field(data, WORKFLOW_KEY),
        history=_history(data.get(HISTORY_KEY)),
    )


def read_anchor(anchor_path: Path, display: str | None = None) -> AnchorState:
    """The status and binding recorded in the anchor's frontmatter.

    Raises ``AnchorInvalidError`` (``ANCHOR_INVALID``, targeting ``display``,
    default the path) when the file cannot be read or its frontmatter parsed.
    """
    target = display or anchor_path.as_posix()
    try:
        data = frontmatter.read(anchor_path)
    except (FrontmatterError, OSError, UnicodeError) as exc:
        raise AnchorInvalidError(f"{anchor_path.name}: {exc}", target_files=[target]) from exc
    return AnchorState(frontmatter.field(data, "status"), binding_from(data))


def read_binding(anchor_path: Path) -> Binding:
    """Binding from the anchor's frontmatter; an anchor without the keys is unbound.

    Raises ``AnchorInvalidError`` when the frontmatter cannot be read.
    """
    return read_anchor(anchor_path).binding


def render_binding(text: str, binding: Binding) -> str:
    """``text`` (an anchor) with the binding recorded, preserving every other byte.

    The history is written as a single flow-style YAML line so the anchor keeps
    one top-level line per key. An empty history leaves an existing one untouched.
    An anchor without frontmatter gets a block holding the binding.
    """
    updates = {WORKFLOW_KEY: binding.workflow}
    if binding.history:
        flow = yaml.safe_dump(
            [h.to_dict() for h in binding.history], default_flow_style=True, sort_keys=False, width=10**6
        ).strip()
        updates[HISTORY_KEY] = flow
    return frontmatter.update(text, updates)


def replace_text(path: Path, text: str) -> None:
    """Replace the file at ``path`` (or the file a link there points to) with ``text`` atomically.

    The text goes to a temporary file in the same directory (``temporary_path``,
    which loaders and ``lint-clean`` skip), which takes the original's
    permission bits and then replaces it, so an interrupted or failed write
    leaves the original intact.
    """
    target = path.resolve()
    mode = stat.S_IMODE(target.stat().st_mode)
    temporary = temporary_path(target)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.chmod(temporary, mode)
        os.replace(temporary, target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def write_binding(anchor_path: Path, binding: Binding) -> None:
    """Record the binding in the anchor (``render_binding``), replacing the file atomically (``replace_text``)."""
    replace_text(anchor_path, render_binding(anchor_path.read_text("utf-8"), binding))
