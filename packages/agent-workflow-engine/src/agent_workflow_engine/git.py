"""Git queries the engine needs; every call is a subprocess against the workspace."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REVISION = re.compile(r"^[0-9a-f]{7,64}$")


class GitError(RuntimeError):
    pass


def is_ancestor(workspace_root: Path, ancestor: str, descendant: str) -> bool:
    """True when ``ancestor`` is an ancestor of, or equal to, ``descendant``."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(workspace_root), "merge-base", "--is-ancestor", ancestor, descendant],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise GitError(str(exc)) from exc
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    raise GitError(proc.stderr.strip() or f"git exited with {proc.returncode}")
