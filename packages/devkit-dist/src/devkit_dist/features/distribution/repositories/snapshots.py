"""Bounded source reads and coherent local snapshot directory replacement."""

from __future__ import annotations

import fcntl
import os
import shutil
import tempfile
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, suppress
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git
from devkit_dist.features.distribution.models.content import Content, is_by_product, normal_mode
from devkit_dist.features.distribution.models.snapshots import (
    SnapshotConflictError,
    SnapshotInvalidError,
    SnapshotWriteError,
)
from devkit_dist.features.project.repositories.invocation import guard_execution


def read_content(path: Path) -> Content:
    """Read a regular file without following a symbolic-link component."""
    if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file():
        raise SnapshotInvalidError(f"expected a regular, unlinked source file: {path}")
    try:
        return Content(path.read_bytes(), normal_mode(path.stat().st_mode))
    except OSError as exc:
        raise SnapshotInvalidError(f"cannot read source file: {path}: {exc}") from exc


def symlinked_ancestor(path: Path) -> Path | None:
    """The outermost symbolic-link component above ``path``, if any."""
    for ancestor in reversed(path.parents):
        if ancestor.is_symlink():
            return ancestor
    return None


def read_tree(root: Path) -> dict[str, Content]:
    """Read a tree; derived bytecode and Finder metadata are not drift or distributable content."""
    if not root.is_dir() or root.is_symlink():
        raise SnapshotInvalidError(f"expected a snapshot directory: {root}")
    found: dict[str, Content] = {}
    try:
        for entry in sorted(root.rglob("*")):
            rel = entry.relative_to(root)
            if is_by_product(rel):
                continue
            if entry.is_symlink() or not (entry.is_file() or entry.is_dir()):
                raise SnapshotInvalidError(f"nonregular snapshot source: {rel.as_posix()}")
            if entry.is_file():
                found[rel.as_posix()] = read_content(entry)
    except OSError as exc:
        raise SnapshotInvalidError(f"cannot enumerate snapshot files: {exc}") from exc
    return found


def source_commit(root: Path, originals: Mapping[Path, Content]) -> str | None:
    """Return HEAD only when every copied input's bytes/mode matches its committed blob.

    ``None`` when the source is not in a Git repository or a Git command fails or runs past 10 seconds.
    """

    def git(*args: str) -> bytes:
        return run_git(root, *args, timeout=10)

    try:
        repository = Path(git("rev-parse", "--show-toplevel").decode().strip())
        captured_head = git("rev-parse", "HEAD").decode().strip()
        for path, content in originals.items():
            rel = path.relative_to(repository).as_posix()
            fields = git("ls-tree", captured_head, "--", rel).split(b"\t", 1)[0].split()
            if len(fields) != 3 or fields[1] != b"blob":
                return None
            if git("cat-file", "blob", fields[2].decode()) != content.data:
                return None
            if (fields[0] == b"100755") != (content.mode == 0o755):
                return None
        return captured_head
    except (GitError, OSError, ValueError, UnicodeError):
        return None


@contextmanager
def snapshot_lock(root: Path) -> Iterator[None]:
    """Serialize snapshot commands on the consumer directory without creating project state."""
    try:
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as exc:
        raise SnapshotWriteError(f"cannot lock consumer directory: {exc}") from exc
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SnapshotConflictError("another snapshot operation holds the consumer directory lock") from exc
        yield
    finally:
        os.close(fd)


def replace_snapshot(
    destination: Path,
    files: Mapping[str, Content],
    validate: Callable[[Path], None],
    *,
    creating: bool,
    previous_files: Mapping[str, Content] | None = None,
) -> None:
    """Stage and validate before replacing; restore the previous tree on a reported failure."""
    guard_execution()
    stage: Path | None = None
    backup: Path | None = None
    installed = False
    completed = False
    created_parents: list[Path] = []
    try:
        parent = destination.parent
        missing = parent
        while not missing.exists():
            created_parents.append(missing)
            missing = missing.parent
        parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.snapshot-", dir=parent))
        for rel, content in sorted(files.items()):
            path = stage / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.data)
            path.chmod(content.mode)
        validate(stage)
        if creating:
            if destination.exists():
                raise SnapshotConflictError("snapshot destination already exists")
        else:
            backup = Path(tempfile.mkdtemp(prefix=f".{destination.name}.previous-", dir=parent))
            backup.rmdir()
            destination.rename(backup)
            try:
                previous = read_tree(backup)
            except SnapshotInvalidError as changed:
                raise SnapshotConflictError("snapshot changed while refresh was preparing; preview again") from changed
            if previous_files is None or previous != previous_files:
                raise SnapshotConflictError("snapshot changed while refresh was preparing; preview again")
        stage.rename(destination)
        stage = None
        installed = True
        validate(destination)
        completed = True
    except BaseException as exc:
        try:
            if installed:
                shutil.rmtree(destination)
            if backup is not None and backup.exists():
                backup.rename(destination)
                backup = None
        except OSError as rollback:
            raise SnapshotWriteError(
                f"snapshot write and rollback failed: {exc}; {rollback}",
                f"Preserve recovery backup: {backup}",
            ) from exc
        if isinstance(exc, SnapshotConflictError):
            raise
        if not isinstance(exc, Exception):
            raise
        raise SnapshotWriteError(f"snapshot write failed; prior package preserved: {exc}") from exc
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        if backup is not None and backup.exists() and completed:
            shutil.rmtree(backup)
        for parent in created_parents:
            with suppress(OSError):
                parent.rmdir()
