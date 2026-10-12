"""The one subprocess runner for Git.

Output is returned as bytes: Git paths are arbitrary bytes, so callers decode
them themselves (``data.decode("utf-8", errors="surrogateescape")`` keeps every
name round-trippable). Package-specific queries live in their packages and are
built on ``run_git``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from devkit.core.errors import GitError

DEFAULT_TIMEOUT = 60.0


def run_git(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> bytes:
    """Run ``git -C <cwd> <args...>`` and return its standard output.

    ``input`` is written to Git's standard input. ``timeout`` is in seconds;
    ``None`` waits indefinitely. The process inherits the environment, so the
    ``GIT_DIR`` / ``GIT_INDEX_FILE`` set by Git for hooks are honored.

    Raises ``GitError`` when Git cannot be started, does not finish within
    ``timeout``, or exits nonzero; the error carries the command, the exit
    status (``None`` if there is none) and Git's decoded standard error.
    """
    command = ("git", "-C", str(cwd), *args)
    label = f"git {args[0]}" if args else "git"
    try:
        completed = subprocess.run(command, input=input, capture_output=True, check=False, timeout=timeout)
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
