"""Read-only Git diagnostics restricted to installation-owned native projection files."""

from __future__ import annotations

import os
import shlex
from collections.abc import Iterable
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git, run_git_result
from devkit_dist.features.distribution.models.errors import (
    ProjectionGitCheckFailedNotice,
    ProjectionNotIgnoredNotice,
    ProjectionTrackedNotice,
)
from devkit_dist.features.project.repositories.project import git_toplevel

LIMIT = 10
NATIVE_ROOTS = (".agents/", ".claude/", ".codex/")


def _paths(raw: bytes) -> set[str]:
    return {os.fsdecode(name) for name in raw.split(b"\0") if name}


def _ignore_pattern(name: str) -> str:
    # An anchored file pattern, not a directory-wide exclusion or a Git glob.
    return "/" + "".join("\\" + char if char in "\\*?[] " else char for char in name)


def projection_git_notices(root: Path, desired: Iterable[str], previous: Iterable[str]) -> list[AdvisoryError]:
    """Inspect desired ignore coverage and current/previous tracking, never changing the index or ignores."""
    wanted = {name for name in desired if name.startswith(NATIVE_ROOTS)}
    owned = wanted | {name for name in previous if name.startswith(NATIVE_ROOTS)}
    if not owned or git_toplevel(root) is None:
        return []
    try:
        tracked = _paths(run_git(root, "ls-files", "-z", "--", ".")) & owned
        candidates = sorted(wanted - tracked)
        ignored = (
            _paths(
                run_git_result(
                    root,
                    "check-ignore",
                    "--no-index",
                    "--stdin",
                    "-z",
                    input=b"".join(os.fsencode(name) + b"\0" for name in candidates),
                    ok_returncodes=(0, 1),
                ).stdout
            )
            if candidates
            else set()
        )
    except GitError:
        return [
            ProjectionGitCheckFailedNotice(
                "Git could not inspect native projection tracking and ignore coverage",
                fix="Check Git access and repository health, then rerun devkit sync",
            )
        ]
    notices: list[AdvisoryError] = []
    for paths, kind in ((tracked, ProjectionTrackedNotice), (set(candidates) - ignored, ProjectionNotIgnoredNotice)):
        if not paths:
            continue
        shown = sorted(paths)[:LIMIT]
        more = (
            [f"{len(paths) - LIMIT} more paths omitted; rerun sync after repairing the listed paths"]
            if len(paths) > LIMIT
            else []
        )
        if kind is ProjectionTrackedNotice:
            command = "git rm --cached -- " + " ".join(shlex.quote(":(literal)" + name) for name in shown)
            notices.append(
                kind(
                    f"{len(paths)} native projection file(s) are tracked by Git",
                    *more,
                    target_files=shown,
                    fix=command,
                    what_to_report="Confirm these generated files should leave Git tracking; the command preserves working files",
                )
            )
        else:
            patterns = [f"ignore pattern: {_ignore_pattern(name)}" for name in shown]
            notices.append(
                kind(
                    f"{len(paths)} native projection file(s) lack effective Git ignore coverage",
                    *patterns,
                    *more,
                    target_files=shown,
                    fix="Add the listed exact-file patterns to the repository root .gitignore; resolve overriding negations, then rerun sync",
                )
            )
    return notices
