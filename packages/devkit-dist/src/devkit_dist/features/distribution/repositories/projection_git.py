"""Read-only Git diagnostics restricted to installation-owned native projection files."""

from __future__ import annotations

import os
import shlex
from collections.abc import Iterable
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import GitError
from devkit_core.core.git import ignored_paths, run_git, tracked_paths
from devkit_dist.features.distribution.models.errors import (
    ProjectionGitCheckFailedNotice,
    ProjectionNotIgnoredNotice,
    ProjectionTrackedNotice,
)
from devkit_dist.features.distribution.models.settings import NATIVE_ROOTS

LIMIT = 10
# Where native projections live: the files these diagnostics inspect.
PROJECTION_PREFIXES = tuple(f"{native}/" for native in NATIVE_ROOTS)


def _ignore_pattern(name: str) -> str:
    # An anchored file pattern, not a directory-wide exclusion or a Git glob.
    return "/" + "".join("\\" + char if char in "\\*?[] " else char for char in name)


def projection_git_notices(root: Path, desired: Iterable[str], previous: Iterable[str]) -> list[AdvisoryError]:
    """Inspect desired ignore coverage and current/previous tracking, never changing the index or ignores."""
    wanted = {name for name in desired if name.startswith(PROJECTION_PREFIXES)}
    owned = wanted | {name for name in previous if name.startswith(PROJECTION_PREFIXES)}
    if not owned:
        return []
    try:
        # Ignore patterns are anchored at the repository root, so a devkit root below it needs its prefix.
        prefix = os.fsdecode(run_git(root, "rev-parse", "--show-toplevel", "--show-prefix")).split("\n")[1]
        tracked = tracked_paths(root, sorted(owned))
        candidates = sorted(wanted - tracked)
        ignored = ignored_paths(root, candidates, no_index=True)
    except GitError as exc:
        # Git has no distinct exit code for nonrepository vs access/discovery failures.
        # The shared runner fixes LC_ALL=C; only this explicit nonrepository response is a skip.
        if exc.returncode == 128 and exc.stderr.startswith("fatal: not a git repository"):
            return []
        return [
            ProjectionGitCheckFailedNotice(
                "Git could not inspect native projection tracking and ignore coverage",
                fix="Check Git access and repository health, then rerun uv run devkit sync",
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
            command = (
                "git -C "
                + shlex.quote(str(root.resolve()))
                + " rm --cached -- "
                + " ".join(shlex.quote(":(literal)" + name) for name in shown)
            )
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
            patterns = [f"ignore pattern: {_ignore_pattern(prefix + name)}" for name in shown]
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
