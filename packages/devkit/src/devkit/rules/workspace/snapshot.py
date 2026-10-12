"""Exact Git trees for gate evaluation.

``devkit rules check --staged`` evaluates the index (what a commit would
contain) and ``--ci --base <ref>`` evaluates ``HEAD`` against its merge base
with ``<ref>``. Both read the tree from Git rather than the working directory,
so unstaged edits, ignored files and local-only configuration cannot change the
result. The tree is materialized into a temporary directory, which becomes the
workspace root for the run: ``.devkit/config.toml``, the installation receipt
and synchronized rules are therefore taken from the same snapshot. Managed rule
copies are usually Git-ignored and absent from the tree; the rule engine then
reads them from the working tree only when they match the hash recorded in the
snapshot's receipt (see ``engine.discovery``).

The snapshot root must be the top level of the Git work tree: Git reports tree
and diff paths relative to it, and a snapshot of a subdirectory would silently
check nothing.

Materialization writes regular and executable files, recreates symlinks whose
target stays inside the tree (others are skipped) and creates an empty
directory for each submodule, so a link to a tracked symlink or into a
submodule resolves as it does in the working tree. Only regular files are
evaluation targets.
"""

from __future__ import annotations

import contextlib
import os
import posixpath
import subprocess
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import IO

from devkit.core import GitError, is_safe_relpath, run_git
from devkit.core.git import DEFAULT_TIMEOUT
from devkit.rules.engine.errors import SnapshotError

REGULAR_MODES = {"100644", "100755"}
SYMLINK_MODE = "120000"
GITLINK_MODE = "160000"
_CHUNK = 1 << 20


@dataclass(frozen=True)
class Snapshot:
    root: Path
    mode: str  # "staged" or "ci"
    tree: str
    base: str
    changed: tuple[str, ...]  # changed regular files present in ``tree``
    deleted: tuple[str, ...]
    files: tuple[tuple[str, str, str], ...]  # (path, object sha, mode) of every regular file, symlink and submodule

    def describe(self) -> str:
        return (
            f"[SNAPSHOT: mode={self.mode} tree={self.tree[:12]} base={self.base[:12]} "
            f"changed={len(self.changed)} deleted={len(self.deleted)}]"
        )


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return run_git(root, *args, input=stdin)
    except GitError as exc:
        raise SnapshotError(str(exc)) from exc


def _decode(name: bytes) -> str:
    return name.decode("utf-8", errors="surrogateescape")


def _require_toplevel(root: Path) -> None:
    try:
        toplevel_raw = _git(root, "rev-parse", "--show-toplevel").rstrip(b"\n")
    except SnapshotError as exc:
        raise SnapshotError(
            f"{root} is not inside a Git work tree ({exc})",
            input_error=True,
            target_files=["--workspace-root"],
            fix="Run from inside the repository or pass --workspace-root <repository top level>",
        ) from exc
    toplevel = Path(os.fsdecode(toplevel_raw)).resolve()
    if toplevel != root:
        raise SnapshotError(
            f"a Git snapshot must be taken at the work tree top level {toplevel}, not {root}; "
            f"run from the repository root or pass --workspace-root {toplevel}",
            input_error=True,
            target_files=["--workspace-root"],
            fix=f"Pass --workspace-root {toplevel}",
        )


def _changes(root: Path, prior: str, tree: str) -> tuple[list[str], list[str]]:
    """Changed and deleted paths between two trees, from one ``--name-status`` diff."""
    output = _git(root, "diff", "--name-status", "-z", "--no-renames", prior, tree, "--")
    parts = [part for part in output.split(b"\0") if part]
    changed: list[str] = []
    deleted: list[str] = []
    for status, name in zip(parts[0::2], parts[1::2], strict=True):
        path = _decode(name)
        changed.append(path)
        if status.startswith(b"D"):
            deleted.append(path)
    return changed, deleted


def git_snapshot(root: Path, *, staged: bool, base: str = "origin/main") -> Snapshot:
    """Capture the staged index or the ``HEAD`` tree with its merge base against ``base``.

    ``root`` must be the top level of the Git work tree.
    """
    root = root.resolve()
    _require_toplevel(root)
    if staged:
        tree = _git(root, "write-tree").decode().strip()
        try:
            prior = _git(root, "rev-parse", "--verify", "--quiet", "HEAD^{tree}").decode().strip()
        except SnapshotError:
            # Unborn branch: compare against the empty tree.
            prior = _git(root, "hash-object", "-t", "tree", "--stdin", stdin=b"").decode().strip()
        mode = "staged"
    else:
        tree = _git(root, "rev-parse", "--verify", "--quiet", "HEAD^{tree}").decode().strip()
        try:
            prior = _git(root, "merge-base", "--", base, "HEAD").decode().strip()
        except SnapshotError as exc:
            raise SnapshotError(
                f"no merge base between {base} and HEAD: {exc}",
                input_error=True,
                target_files=["--base"],
                fix="Pass --base a ref that shares history with HEAD (fetch it first in a shallow CI clone)",
            ) from exc
        mode = "ci"
    changed, deleted = _changes(root, prior, tree)
    files: list[tuple[str, str, str]] = []
    regular: set[str] = set()
    for entry in _git(root, "ls-tree", "-r", "--full-tree", "-z", tree).split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        file_mode, _kind, sha = meta.decode().split(" ")
        name = _decode(path)
        if file_mode not in REGULAR_MODES | {SYMLINK_MODE, GITLINK_MODE} or not is_safe_relpath(name, canonical=True):
            continue
        files.append((name, sha, file_mode))
        if file_mode in REGULAR_MODES:
            regular.add(name)
    return Snapshot(
        root=root,
        mode=mode,
        tree=tree,
        base=prior,
        changed=tuple(p for p in changed if p in regular),
        deleted=tuple(deleted),
        files=tuple(files),
    )


def _inside_tree(name: str, link_target: str) -> bool:
    """Whether a symlink at ``name`` pointing to ``link_target`` resolves inside the tree, lexically."""
    if not link_target or link_target.startswith("/") or "\0" in link_target:
        return False
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(name), link_target))
    return joined != ".." and not joined.startswith("../") and joined != "."


def _target(directory: Path, name: str) -> Path:
    target = directory / Path(*PurePosixPath(name).parts)
    if target.exists() or target.is_symlink():
        raise SnapshotError(
            f"cannot materialize {name}: another path in the tree has the same name on this file system "
            "(paths that differ only by case)"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


class _BlobReader:
    """Stream blobs from one ``git cat-file --batch`` process, one object at a time.

    Object names are written to Git's standard input by a writer thread while
    the caller reads, so neither pipe can fill up and block the other side.
    Each object is read as its ``<sha> <type> <size>`` header followed by
    exactly ``size`` bytes and a newline; memory never holds more than one
    chunk of a regular file or one symlink target. The process is killed after
    ``timeout`` seconds.
    """

    def __init__(self, root: Path, shas: list[str], timeout: float | None = DEFAULT_TIMEOUT) -> None:
        self._command = ("git", "-C", str(root), "cat-file", "--batch")
        try:
            self._process = subprocess.Popen(
                self._command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except OSError as exc:
            raise SnapshotError(f"git is not available: {exc}") from exc
        self._stderr = bytearray()
        self._timed_out = False
        request = "".join(f"{sha}\n" for sha in shas).encode()
        self._threads = [
            threading.Thread(target=self._write, args=(request,), daemon=True),
            threading.Thread(target=self._drain_stderr, daemon=True),
        ]
        for thread in self._threads:
            thread.start()
        self._timer = threading.Timer(timeout, self._kill) if timeout is not None else None
        if self._timer is not None:
            self._timer.daemon = True
            self._timer.start()
        self._timeout = timeout

    @property
    def _stdout(self) -> IO[bytes]:
        assert self._process.stdout is not None
        return self._process.stdout

    def _write(self, request: bytes) -> None:
        stdin = self._process.stdin
        assert stdin is not None
        with contextlib.suppress(OSError):  # the process ended early; the reader reports it
            stdin.write(request)
        with contextlib.suppress(OSError):
            stdin.close()

    def _drain_stderr(self) -> None:
        assert self._process.stderr is not None
        self._stderr.extend(self._process.stderr.read())

    def _kill(self) -> None:
        self._timed_out = True
        self._process.kill()

    def _failure(self, problem: str) -> SnapshotError:
        self.close()
        if self._timed_out:
            return SnapshotError(f"git cat-file timed out after {self._timeout}s in {self._command[2]}")
        stderr = self._stderr.decode("utf-8", errors="replace").strip()
        return SnapshotError(f"git cat-file failed in {self._command[2]}: {stderr or problem}")

    def header(self, name: str, sha: str) -> int:
        """Read the next object's header and return its size; it must be the blob ``sha``."""
        line = self._stdout.readline()
        if not line.endswith(b"\n"):
            raise self._failure(f"output ended before {name}")
        parts = line.decode("utf-8", errors="replace").split()
        if parts[:2] == [sha, "missing"]:
            raise SnapshotError(f"object {sha} of {name} is missing from the repository")
        if len(parts) != 3 or parts[0] != sha or parts[1] != "blob" or not parts[2].isdigit():
            raise self._failure(f"unexpected cat-file header for {name}: {line!r}")
        return int(parts[2])

    def chunks(self, name: str, size: int) -> Iterator[bytes]:
        """The ``size`` content bytes of the current object, then its trailing newline is consumed."""
        remaining = size
        while remaining:
            chunk = self._stdout.read(min(remaining, _CHUNK))
            if not chunk:
                raise self._failure(f"output ended inside {name}")
            remaining -= len(chunk)
            yield chunk
        if self._stdout.read(1) != b"\n":
            raise self._failure(f"missing object terminator after {name}")

    def read(self, name: str, size: int) -> bytes:
        return b"".join(self.chunks(name, size))

    def finish(self) -> None:
        """Wait for Git to exit; a nonzero status is an error even after every object was read."""
        self._stdout.close()
        returncode = self._process.wait()
        for thread in self._threads:
            thread.join()
        if self._timer is not None:
            self._timer.cancel()
        if self._timed_out or returncode != 0:
            raise self._failure(f"exit status {returncode}")

    def close(self) -> None:
        """Stop the process and its helper threads (idempotent)."""
        if self._timer is not None:
            self._timer.cancel()
        if self._process.poll() is None:
            self._process.kill()
        self._process.wait()
        for thread in self._threads:
            thread.join()
        self._stdout.close()


def materialize(snapshot: Snapshot, directory: Path) -> None:
    """Write the snapshot's files, in-tree symlinks and submodule placeholders under ``directory``.

    Blobs are streamed from one ``git cat-file --batch`` process and written
    as they arrive, so memory is bounded by a chunk of the largest file.
    """
    blobs = [(name, sha, mode) for name, sha, mode in snapshot.files if mode != GITLINK_MODE]
    for name, _, mode in snapshot.files:
        if mode == GITLINK_MODE:
            _target(directory, name).mkdir()
    if not blobs:
        return
    links: list[tuple[str, str]] = []
    reader = _BlobReader(snapshot.root, [sha for _, sha, _ in blobs])
    try:
        for name, sha, file_mode in blobs:
            size = reader.header(name, sha)
            if file_mode == SYMLINK_MODE:
                links.append((name, os.fsdecode(reader.read(name, size))))
                continue
            target = _target(directory, name)
            with target.open("wb") as handle:
                for chunk in reader.chunks(name, size):
                    handle.write(chunk)
            if file_mode == "100755":
                target.chmod(0o755)
        reader.finish()
    finally:
        reader.close()
    # Symlinks last, so a link never redirects where a later regular file is written.
    for name, link_target in links:
        if _inside_tree(name, link_target):
            _target(directory, name).symlink_to(link_target)
