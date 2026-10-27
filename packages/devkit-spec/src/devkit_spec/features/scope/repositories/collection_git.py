"""Deadline- and byte-bounded Git reads, with no shell or implicit authentication prompts."""

from __future__ import annotations

import contextlib
import os
import selectors
import signal
import subprocess
from pathlib import Path

from devkit_core.core import GitError

from devkit_spec.features.scope.models.deadline import Deadline

MAX_GIT_BYTES = 16 * 1024 * 1024


class InputLimitError(Exception):
    """A bounded input was too large to collect."""


def git(root: Path, *args: str, deadline: Deadline, limit: int = MAX_GIT_BYTES) -> bytes:
    deadline.check("scope Git observation")
    command = ("git", "-C", str(root), "-c", "credential.interactive=false", *args)
    env = {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}
    # A caller's hook index must never redirect reads in another worktree.
    for key in ("GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_DIR"):
        env.pop(key, None)
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        raise GitError("Cannot start Git for scope observation", command=command) from exc
    completed = False
    output = bytearray()
    size = 0
    try:
        with selectors.DefaultSelector() as selector:
            assert process.stdout is not None and process.stderr is not None
            for pipe in (process.stdout, process.stderr):
                selector.register(pipe, selectors.EVENT_READ)
            while selector.get_map():
                deadline.check("scope Git observation")
                for key, _ in selector.select(max(0.001, min(deadline.remaining(), 0.05))):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    size += len(chunk)
                    if size > limit:
                        raise InputLimitError("Git output exceeds collection input limit")
                    if key.fileobj is process.stdout:
                        output.extend(chunk)
            process.wait(timeout=max(0.001, deadline.remaining()))
        if process.returncode:
            raise GitError("Git scope observation failed", command=command, returncode=process.returncode)
        completed = True
        return bytes(output)
    except subprocess.TimeoutExpired as exc:
        raise deadline.exceeded("scope Git observation") from exc
    finally:
        if not completed:
            # A child can hold pipes after Git's parent exits; kill the whole failed operation.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
        if process.poll() is None:
            process.wait()
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()


def text(root: Path, *args: str, deadline: Deadline) -> str:
    return git(root, *args, deadline=deadline).decode("utf-8", errors="surrogateescape").removesuffix("\n")


def optional(root: Path, *args: str, deadline: Deadline) -> str:
    try:
        return text(root, *args, deadline=deadline)
    except GitError as exc:
        if exc.returncode is None:
            raise
        return ""
