"""The ``branch.<branch>.devkit*`` keys ``devkit worktree`` records in the common Git configuration.

``start`` and ``attach`` write them with ``git config --local``; ``branch_marker`` reads them the same way, so a
value set globally or system-wide never counts as a marker.
"""

from __future__ import annotations

from pathlib import Path

from devkit_core.core import GitError, run_git_text

# Recorded on every branch ``start`` creates or attaches; only a marked branch is deleted without its worktree, so
# ``finish`` never deletes an ordinary branch that happens to share the name.
MARKER = "devkitWorktree"
BASE_KEY = "devkitBase"  # the branch ``start_branch`` started from, where the base checkout returns to
UNIT_KEY = "devkitUnit"  # the unit directory ``attach`` was given, for the stale-branch report


def marker_key(branch: str, key: str = MARKER) -> str:
    """The configuration key ``branch.<branch>.<key>``."""
    return f"branch.{branch}.{key}"


def branch_marker(root: Path, branch: str, key: str = MARKER) -> str:
    """``branch.<branch>.<key>`` from the local configuration of the repository at ``root``; ``""`` when unset.

    Any Git failure other than an unset key (exit ``1``) raises ``GitError``.
    """
    try:
        return run_git_text(root, "config", "--local", "--get", marker_key(branch, key))
    except GitError as exc:
        if exc.returncode == 1:
            return ""
        raise
