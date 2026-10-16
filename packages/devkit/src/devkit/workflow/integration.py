"""The integration guard: a branch whose units are held by their envelopes is not merged.

``devkit worktree finish --merge`` calls every ``devkit.finish_guard`` extension before its first change; this one
(registered by devkit-agt) refuses a branch whose tip holds an unresolved problem or an unanswered question in a
unit the branch changed. It reads the committed tip through Git, not the worktree's files, so uncommitted
envelopes neither block nor clear the merge. See ``docs/workflow/envelopes.md``.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path, PurePosixPath

from devkit.core.errors import GitError
from devkit.core.git import run_git
from devkit.workflow.unit.envelope import ENVELOPES_DIR, collect_envelopes, is_envelope_name


def _git(cwd: Path, *args: str) -> str:
    return os.fsdecode(run_git(cwd, *args))


def changed_units(base: Path, merge_base: str, tip: str) -> list[str]:
    """The repository-relative unit directories (``.`` at the top) whose ``envelopes/`` files changed between
    ``merge_base`` and ``tip``."""
    changed = _git(base, "diff", "--name-only", "-z", "--no-renames", merge_base, tip, "--").split("\0")
    units = set()
    for name in filter(None, changed):
        path = PurePosixPath(name)
        if path.parent.name == ENVELOPES_DIR and is_envelope_name(path.name):
            units.add(path.parent.parent.as_posix())
    return sorted(units)


def unit_hold_reasons(base: Path, tip: str, unit: str) -> list[str]:
    """Why the unit ``unit`` is held at ``tip``: one line per unresolved problem and unanswered question."""
    directory = f"{unit}/{ENVELOPES_DIR}" if unit != "." else ENVELOPES_DIR
    try:
        listed = _git(base, "ls-tree", "-z", "--name-only", f"{tip}:{directory}").split("\0")
    except GitError:  # the branch deleted the directory: nothing holds it
        return []

    def reader(name: str) -> Callable[[], str]:
        return lambda: _git(base, "show", f"{tip}:{directory}/{name}")

    envelopes = collect_envelopes((name, reader(name)) for name in listed if name and is_envelope_name(name))
    return envelopes.hold().reasons("" if unit == "." else f"{unit}/")


def finish_guard(base: Path, branch: str, merge_base: str, tip: str) -> list[str]:
    """The ``devkit.finish_guard`` extension: the hold reasons of every unit ``branch`` changed, at its ``tip``."""
    del branch  # the units are found from the changes, whatever the branch is called
    return [reason for unit in changed_units(base, merge_base, tip) for reason in unit_hold_reasons(base, tip, unit)]
