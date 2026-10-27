"""The one subprocess runner for Git.

``run_git`` returns bytes: Git paths are arbitrary bytes, so they are decoded with
``data.decode("utf-8", errors="surrogateescape")``, which keeps every name
round-trippable. ``run_git_text`` applies that rule for callers that want text, and
``is_ancestor`` is the shared ``merge-base --is-ancestor`` test. These generic
primitives live here; queries that encode one package's policy live in that package
and are built on them.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.deadline import Deadline

DEFAULT_TIMEOUT = 60.0  # seconds; the one Git timeout every devkit area uses


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


def run_git_text(
    cwd: Path,
    *args: str,
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
) -> str:
    """``run_git`` with its output decoded as UTF-8 with ``surrogateescape`` and one trailing newline removed.

    Only a single ``\\n`` is removed, so a one-line answer (a commit id, a path) comes back bare while leading and
    other trailing whitespace, which a path may carry, is kept. A caller that needs the output byte for byte (a file's
    content from ``git show``) uses ``run_git``. Raises as ``run_git`` does.
    """
    output = run_git(cwd, *args, input=input, timeout=timeout, index=index, deadline=deadline)
    return output.decode("utf-8", errors="surrogateescape").removesuffix("\n")


def is_ancestor(cwd: Path, ancestor: str, descendant: str) -> bool:
    """Whether commit ``ancestor`` is contained in ``descendant`` (a commit is its own ancestor).

    Git's exit status 1 is the answer no; any other failure (an unknown revision, as in a shallow clone, or not a
    repository) raises ``GitError``. Both revisions are passed to Git as given; a caller taking them from input
    validates them first.
    """
    try:
        run_git(cwd, "merge-base", "--is-ancestor", ancestor, descendant)
    except GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True
