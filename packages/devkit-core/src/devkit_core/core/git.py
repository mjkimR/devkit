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

from devkit_core.base.errors import GitError
from devkit_core.core.deadline import Deadline

DEFAULT_TIMEOUT = 60.0  # seconds; the one Git timeout every devkit area uses
# The index of the commit being made, which the ``verify-commands`` gate passes to the commands it runs, and the
# ``rules-check`` gate sets while it runs, after removing Git's own ``GIT_INDEX_FILE`` (see ``commit_index``).
COMMIT_INDEX_VARIABLE = "DEVKIT_GIT_INDEX_FILE"


def run_git(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
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
    ``index`` sets ``GIT_INDEX_FILE`` for this call.

    ``deadline`` bounds the call by a shared ``Deadline`` instead of ``timeout``; passing a ``timeout`` other
    than ``DEFAULT_TIMEOUT`` with it is a programming error (``ValueError``), as it is for ``file_lock``. An
    expired deadline starts no Git, Git gets the time left on it, and a Git still running when it runs out is killed.
    Both raise ``deadline.exceeded("git <subcommand>")`` (``DeadlineExceededError`` unless the deadline
    has an error factory); every other failure is still ``GitError``.
    """
    command = ("git", "-C", str(cwd), *args)
    label = f"git {args[0]}" if args else "git"
    if deadline is not None:
        if timeout != DEFAULT_TIMEOUT:
            raise ValueError("run_git takes a timeout or a deadline, not both")
        deadline.check(label)
        timeout = max(deadline.remaining(), 0.001)
    env = {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}
    if index is not None:
        env["GIT_INDEX_FILE"] = index
    stdin = subprocess.DEVNULL if input is None else None
    try:
        completed = subprocess.run(
            command, input=input, stdin=stdin, capture_output=True, check=False, timeout=timeout, env=env
        )
    except subprocess.TimeoutExpired as exc:
        if deadline is not None:
            raise deadline.exceeded(label) from exc
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


def commit_index(root: Path) -> str | None:
    """The index of the commit a hook is making when devkit runs from the ``verify-commands`` or ``rules-check`` gate.

    Both gates remove Git's ``GIT_INDEX_FILE`` from the environment the check runs in (so Git run in another
    repository, a test suite's or a materialized snapshot's, is not pointed at it) and pass it as
    ``DEVKIT_GIT_INDEX_FILE`` instead. It applies only
    while ``GIT_INDEX_FILE`` is unset and only to the repository whose Git directory holds that index, so
    ``git commit -a`` and ``git commit <paths>``, which commit a temporary index, are evaluated as committed.
    ``None`` otherwise: Git's own ``GIT_INDEX_FILE``, or the default index, applies.
    """
    value = os.environ.get(COMMIT_INDEX_VARIABLE)
    if not value or "GIT_INDEX_FILE" in os.environ:
        return None
    index = Path(value)
    if not index.is_absolute():
        return None
    git_dir = Path(os.fsdecode(run_git(root, "rev-parse", "--absolute-git-dir").rstrip(b"\n")))
    return value if index.parent.resolve() == git_dir.resolve() else None
