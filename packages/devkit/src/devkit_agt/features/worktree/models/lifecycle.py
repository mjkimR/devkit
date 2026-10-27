"""Worktree positions, lifecycle outcomes and read-only status values."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError


@dataclass(frozen=True)
class Position:
    """The checkout a command runs in."""

    root: Path  # top level of this checkout
    base: Path  # top level of the base checkout (whose Git directory is the common one)
    branch: str | None  # this checkout's branch; None when detached
    linked: bool  # True inside a linked worktree


@dataclass(frozen=True)
class StartResult:
    branch: str
    path: Path
    base: Path
    created: bool  # False when the existing worktree was reused
    setup: str | None = None  # the setup command that ran, if any
    synced: bool | None = None  # whether `devkit sync --locked` restored the project; None when it did not run
    notices: list[AdvisoryError] = field(default_factory=list)
    existing: bool = False  # the branch existed before (`attach`)
    unit: str | None = None  # the unit `attach` was given, relative to the repository root

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "slug": self.slug,
            "path": str(self.path),
            "base": str(self.base),
            "created": self.created,
            "existing": self.existing,
            "unit": self.unit,
            "setup": self.setup,
            "synced": self.synced,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass(frozen=True)
class BranchStartResult:
    """``start_branch``: the branch was created at ``checkout``'s HEAD and ``checkout`` switched to it."""

    branch: str
    checkout: Path
    started_from: str  # the branch the checkout was on, recorded as ``devkitBase``
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "slug": self.slug,
            "checkout": str(self.checkout),
            "from": self.started_from,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass
class FinishResult:
    """How far ``finish`` got; ``push`` is ``pushed``, ``rejected``, ``failed`` or ``no-upstream``, ``None`` without
    a merge. ``removed`` is also ``True`` when there was no worktree to remove (a rerun after it was removed, or a
    branch ``start_branch`` created, whose ``path`` is the checkout it was started in). ``discarded`` is ``True`` for
    ``discard``: the branch was deleted unmerged."""

    branch: str
    path: Path
    merged: bool = False
    push: str | None = None
    removed: bool | None = False  # None: the branch never had a worktree (``start_branch``, made by hand)
    branch_deleted: bool = False
    discarded: bool = False
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        value = {"branch": self.branch, "slug": self.slug} | dataclasses.asdict(self) | {"path": str(self.path)}
        value["notices"] = [notice.to_dict() for notice in self.notices]
        return value


@dataclass(frozen=True)
class WorktreeStatus:
    path: Path
    branch: str | None  # None when detached
    head: str | None  # short commit id; None before the first commit
    role: str  # base | linked
    merged: bool | None  # into the base HEAD; None for the base itself
    dirty: bool | None  # None when the directory is missing or unreadable
    prunable: bool  # Git reports the worktree directory missing

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self) | {"path": str(self.path)}


@dataclass(frozen=True)
class BranchStatus:
    """A local branch that no worktree checks out and the base HEAD does not contain."""

    name: str
    head: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class StatusResult:
    base: Path
    base_branch: str | None
    worktrees: list[WorktreeStatus]
    branches: list[BranchStatus]

    def to_dict(self) -> dict[str, Any]:
        return {
            "base": str(self.base),
            "base_branch": self.base_branch,
            "worktrees": [item.to_dict() for item in self.worktrees],
            "branches": [item.to_dict() for item in self.branches],
        }


def slug_of(branch: str) -> str:
    """The slug of an activity branch: its name without the activity prefix."""
    return branch.split("-", 1)[1] if "-" in branch else branch
