"""The integration guard: a branch whose units are held by their envelopes is not merged.

``devkit worktree finish --merge`` calls every ``devkit.finish_guard`` extension before its first change; this one
(registered by devkit-agt) refuses a branch whose tip holds an unresolved problem, an unanswered question or a
malformed worker envelope in a unit the branch changed. It reads the committed tip through Git, not the worktree's
files, so uncommitted envelopes neither block nor clear the merge. Envelope files are never removed one by one: a
file the branch deleted from a unit that still exists still counts, read at the merge base, so deleting a problem
does not clear it. A Git failure propagates, and the guard runner then refuses the merge (fail closed). See
``docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md``.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path, PurePosixPath

from devkit_core.core.git import run_git, run_git_text

from devkit_agt.features.workflow.services.envelope import ENVELOPES_DIR, collect_envelopes, is_envelope_name

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # what a branch without a merge base is compared with


def changed_units(base: Path, merge_base: str, tip: str) -> list[str]:
    """The repository-relative unit directories (``.`` at the top) whose ``envelopes/`` files changed between
    ``merge_base`` (the empty tree when there is none) and ``tip``."""
    changed = run_git_text(
        base, "diff", "--name-only", "-z", "--no-renames", merge_base or EMPTY_TREE, tip, "--"
    ).split("\0")
    units = set()
    for name in filter(None, changed):
        path = PurePosixPath(name)
        if path.parent.name == ENVELOPES_DIR and is_envelope_name(path.name):
            units.add(path.parent.parent.as_posix())
    return sorted(units)


def _names(base: Path, rev: str, directory: str) -> list[str]:
    """The entries of ``directory`` at ``rev``; none when it does not exist there. Other failures raise."""
    listed = run_git_text(base, "ls-tree", "-z", "--name-only", rev, "--", f"{directory}/").split("\0")
    return [PurePosixPath(entry).name for entry in listed if entry]


def unit_hold_reasons(base: Path, tip: str, unit: str, merge_base: str = "") -> list[str]:
    """Why the unit ``unit`` is held at ``tip``: one line per unresolved problem, unanswered question and malformed
    worker envelope. A unit the branch removed holds nothing; envelope files it removed from a unit it kept are
    read at ``merge_base``."""
    directory = f"{unit}/{ENVELOPES_DIR}" if unit != "." else ENVELOPES_DIR
    if unit != "." and not _names(base, tip, unit):
        return []  # the branch removed the unit (a handoff or a close): nothing of it is merged
    at_tip = [name for name in _names(base, tip, directory) if is_envelope_name(name)]
    deleted = []
    if merge_base:
        deleted = [n for n in _names(base, merge_base, directory) if is_envelope_name(n) and n not in at_tip]

    def reader(rev: str, name: str) -> Callable[[], str]:
        return lambda: os.fsdecode(run_git(base, "show", f"{rev}:{directory}/{name}"))

    files = [(name, reader(tip, name)) for name in at_tip] + [(name, reader(merge_base, name)) for name in deleted]
    return collect_envelopes(files).hold().reasons("" if unit == "." else f"{unit}/")


def finish_guard(base: Path, branch: str, merge_base: str, tip: str) -> list[str]:
    """The ``devkit.finish_guard`` extension: the hold reasons of every unit ``branch`` changed, at its ``tip``."""
    del branch  # the units are found from the changes, whatever the branch is called
    return [
        reason
        for unit in changed_units(base, merge_base, tip)
        for reason in unit_hold_reasons(base, tip, unit, merge_base)
    ]
