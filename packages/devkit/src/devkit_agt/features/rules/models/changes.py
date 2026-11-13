"""Immutable source-pair evidence shared by change-scoped rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class LineRange:
    """One-based half-open lines; start == end is an insertion/deletion anchor."""

    start: int
    end: int

    def intersects(self, start: int, end: int) -> bool:
        if start < 1 or end <= start:
            return False
        return start <= self.start < end if self.start == self.end else start < self.end and self.start < end

    def to_dict(self) -> dict[str, int]:
        return {"start": self.start, "end": self.end}


@dataclass(frozen=True)
class ChangeHunk:
    before: LineRange
    after: LineRange

    def to_dict(self) -> dict[str, Any]:
        return {"before": self.before.to_dict(), "after": self.after.to_dict()}


@dataclass(frozen=True)
class ChangeSpan:
    """The affected construct on one side of one exact source pair."""

    path: str
    side: Literal["before", "after"]
    start: int
    end: int
    content_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "side": self.side,
            "start": self.start,
            "end": self.end,
            "content_id": self.content_id,
        }


@dataclass(frozen=True)
class FileChange:
    path: str
    status: str
    mode: str
    base: str
    before_id: str
    after_id: str
    before: str
    after: str
    hunks: tuple[ChangeHunk, ...]
    available: bool = True

    def span(self, side: Literal["before", "after"], start: int, end: int) -> ChangeSpan:
        return ChangeSpan(self.path, side, start, end, self.before_id if side == "before" else self.after_id)

    def affects(self, span: ChangeSpan) -> bool:
        text = self.before if span.side == "before" else self.after
        identity = self.before_id if span.side == "before" else self.after_id
        return (
            self.available
            and span.path == self.path
            and span.side in ("before", "after")
            and span.content_id == identity
            and 1 <= span.start < span.end <= len(text.splitlines()) + 1
            and any(getattr(h, span.side).intersects(span.start, span.end) for h in self.hunks)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "status": self.status,
            "mode": self.mode,
            "base": self.base,
            "old_path": self.path if self.status != "added" else None,
            "new_path": self.path if self.status != "deleted" else None,
            "before_id": self.before_id,
            "after_id": self.after_id,
            "hunks": [h.to_dict() for h in self.hunks],
        }
