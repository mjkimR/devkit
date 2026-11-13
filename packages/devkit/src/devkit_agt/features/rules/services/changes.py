"""Pure change-range and bounded excerpt calculations."""

from __future__ import annotations

import difflib
import hashlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from devkit_agt.features.rules.models.contracts import RuleContext

from devkit_agt.features.rules.models.changes import ChangeHunk, FileChange, LineRange


def file_change(path: str, before: bytes, after: bytes, *, mode: str, base: str, status: str) -> FileChange:
    if b"\0" in before or b"\0" in after:
        raise ValueError("binary content has no textual change evidence")
    old, new = before.decode("utf-8"), after.decode("utf-8")
    hunks = tuple(
        ChangeHunk(LineRange(i + 1, j + 1), LineRange(k + 1, end + 1))
        for tag, i, j, k, end in difflib.SequenceMatcher(
            None, old.splitlines(keepends=True), new.splitlines(keepends=True), autojunk=False
        ).get_opcodes()
        if tag != "equal"
    )

    def digest(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    return FileChange(path, status, mode, base, digest(before), digest(after), old, new, hunks)


def excerpts(change: FileChange) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """At most 20 hunks, 20 lines per side/hunk, 8192 bytes of source text."""
    result: list[dict[str, Any]] = []
    omitted = {"hunks": max(0, len(change.hunks) - 20), "lines": 0, "bytes": 0}
    budget = 8192
    texts = {"before": change.before.splitlines(keepends=True), "after": change.after.splitlines(keepends=True)}
    for index, hunk in enumerate(change.hunks):
        item: dict[str, Any] = hunk.to_dict()
        for side in ("before", "after"):
            span = getattr(hunk, side)
            lines = texts[side][span.start - 1 : span.end - 1]
            if index >= 20:
                omitted["lines"] += len(lines)
                omitted["bytes"] += len("".join(lines).encode())
                continue
            selected = "".join(lines[:20]).encode()
            tail = "".join(lines[20:]).encode()
            shown = selected[:budget].decode("utf-8", errors="ignore")
            used = len(shown.encode())
            budget -= used
            omitted["bytes"] += len(selected) + len(tail) - used
            omitted["lines"] += len(lines) - len(shown.splitlines())
            item[side + "_text"] = shown
        if index < 20:
            result.append(item)
    return result, omitted


def refresh_context_changes(ctx: RuleContext) -> None:
    """Capture a new immutable pass against the original before-side identity."""
    from types import MappingProxyType

    from devkit_agt.features.rules.repositories.workspace.changes import capture_changes

    captured = capture_changes(
        ctx.workspace_root,
        ctx.cache,
        snapshot=ctx.snapshot,
        base=ctx.change_base or None,
        explicit=tuple(ctx.changed_files),
    )
    evidence: dict[str, FileChange] = {}
    for raw in captured.files:
        selected = ctx.change_targets
        if (
            ctx.has_targets
            and not (ctx.snapshot is not None and raw.path in ctx.snapshot.deleted)
            and not any(t == "." or raw.path == t or raw.path.startswith(t.rstrip("/") + "/") for t in selected)
        ):
            continue
        if ctx._excluded(raw.path):
            continue
        try:
            if not raw.available:
                raise ValueError("unavailable source bytes")
            evidence[raw.path] = file_change(
                raw.path, raw.before, raw.after, mode=captured.mode, base=captured.base, status=raw.status
            )
        except (ValueError, UnicodeError):
            evidence[raw.path] = FileChange(
                raw.path, "unavailable", captured.mode, captured.base, "", "", "", "", (), False
            )
    ctx.changes = MappingProxyType(evidence)
    ctx.change_base = captured.base
    ctx.change_available = captured.available
