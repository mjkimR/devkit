"""Git queries the workflow engine needs, built on ``devkit.core.git.run_git``."""

from __future__ import annotations

import re
from pathlib import Path

from devkit.core.errors import GitError
from devkit.core.git import run_git

__all__ = ["REVISION", "is_ancestor", "is_revision"]

REVISION = re.compile(r"[0-9a-f]{7,64}")


def is_revision(value: str) -> bool:
    """Whether ``value`` is a hexadecimal revision of 7 to 64 digits, in full."""
    return REVISION.fullmatch(value) is not None


def is_ancestor(workspace_root: Path, ancestor: str, descendant: str) -> bool:
    """True when ``ancestor`` is an ancestor of, or equal to, ``descendant``.

    Both must be hexadecimal revisions (``is_revision``). Raises ``GitError`` when
    Git cannot answer: not a repository, an unknown revision (as in a shallow
    clone), Git missing, or Git's timeout expiring.
    """
    for revision in (ancestor, descendant):
        if not is_revision(revision):
            raise GitError(f"{revision!r} is not a hexadecimal revision", input_error=True)
    try:
        run_git(workspace_root, "merge-base", "--is-ancestor", ancestor, descendant)
    except GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True
