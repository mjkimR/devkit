"""The one subprocess runner for Git.

Output is returned as bytes: Git paths are arbitrary bytes, so callers decode
them themselves (``data.decode("utf-8", errors="surrogateescape")`` keeps every
name round-trippable). Package-specific queries live in their packages and are
built on ``run_git``.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from devkit.core.errors import GitError

DEFAULT_TIMEOUT = 60.0  # seconds; the one Git timeout every devkit area uses


def run_git(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> bytes:
    """Run ``git -C <cwd> <args...>`` and return its standard output.

    ``input`` is written to Git's standard input; without it Git's standard
    input is ``/dev/null``, so Git never consumes the caller's input (a hook's
    ref list) or waits on a prompt. ``timeout`` is in seconds; ``None`` waits
    indefinitely. The process inherits the environment, so the ``GIT_DIR`` /
    ``GIT_INDEX_FILE`` set by Git for hooks are honored, with ``LC_ALL=C``
    (Git's messages are never localized) and ``GIT_TERMINAL_PROMPT=0`` (Git
    fails instead of prompting for credentials) on top.

    Raises ``GitError`` when Git cannot be started, does not finish within
    ``timeout``, or exits nonzero; the error carries the command, the exit
    status (``None`` if there is none) and Git's decoded standard error.
    """
    command = ("git", "-C", str(cwd), *args)
    label = f"git {args[0]}" if args else "git"
    env = {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}
    stdin = subprocess.DEVNULL if input is None else None
    try:
        completed = subprocess.run(
            command, input=input, stdin=stdin, capture_output=True, check=False, timeout=timeout, env=env
        )
    except subprocess.TimeoutExpired as exc:
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise GitError(f"{label} timed out after {timeout}s in {cwd}", command=command, stderr=stderr) from exc
    except OSError as exc:
        raise GitError(f"git is not available: {exc}", command=command) from exc
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(
            f"{label} failed in {cwd}: {stderr or f'exit status {completed.returncode}'}",
            command=command,
            returncode=completed.returncode,
            stderr=stderr,
        )
    return completed.stdout
