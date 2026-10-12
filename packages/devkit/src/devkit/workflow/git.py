"""Git queries the workflow engine needs, built on ``devkit.core.git.run_git``."""

from __future__ import annotations

import re
from pathlib import Path

from devkit.core.errors import GitError
from devkit.core.git import run_git

__all__ = ["REVISION", "TIMEOUT", "GitError", "is_ancestor"]

REVISION = re.compile(r"^[0-9a-f]{7,64}$")
TIMEOUT = 30.0


def is_ancestor(workspace_root: Path, ancestor: str, descendant: str, *, timeout: float = TIMEOUT) -> bool:
    """True when ``ancestor`` is an ancestor of, or equal to, ``descendant``.

    Both must be hexadecimal revisions (``REVISION``). Raises ``GitError`` when
    Git cannot answer: not a repository, an unknown revision (as in a shallow
    clone), Git missing, or the timeout expiring.
    """
    for revision in (ancestor, descendant):
        if not REVISION.match(revision):
            raise GitError(f"{revision!r} is not a hexadecimal revision", input_error=True)
    try:
        run_git(workspace_root, "merge-base", "--is-ancestor", ancestor, descendant, timeout=timeout)
    except GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True
