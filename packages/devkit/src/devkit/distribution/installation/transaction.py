"""Workspace transactions: the project lock, the write-ahead journal and atomic file replacement.

POSIX only (``fcntl.flock``, directory ``fsync``).
"""

from __future__ import annotations

import base64
import errno
import fcntl
import json
import os
import stat
import tempfile
import time
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit.distribution.content import Content, json_content
from devkit.distribution.errors import LockHeldError, PendingTransactionError, RecoveryError, UnsafeWorkspaceError
from devkit.distribution.installation.workspace import JOURNAL, LOCK, checked_path, owned_prefix, project_path, snapshot

# How long a reader waits for a writer to release the lock before giving up.
READ_LOCK_TIMEOUT = 10.0
_POLL = 0.05


def read_json(root: Path, name: str) -> dict | None:
    """A JSON object file; ``None`` when absent. Duplicate keys and non-objects are errors."""
    content = snapshot(root, name)
    if content is None:
        return None

    def unique(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise RecoveryError(f"{name}: duplicate JSON key {key}", target_files=[name])
            result[key] = value
        return result

    try:
        value = json.loads(content.data, object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        raise RecoveryError(f"invalid {name}: {exc}", target_files=[name]) from exc
    if not isinstance(value, dict):
        raise RecoveryError(f"invalid {name}: expected object", target_files=[name])
    return value


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def prune_empty_parents(root: Path, name: str, *, stop: str | None = None) -> None:
    """Remove directories left empty by deleting ``name``, up to (not including) ``stop``.

    ``stop`` is a workspace-relative directory; by default it is the owned
    prefix of ``name``, so only owned destinations are pruned
    (``.claude/skills/<id>/`` goes, ``.claude/skills/`` stays) and a seeded
    target's directories, which belong to the project, are never touched.
    """
    if stop is None:
        prefix = owned_prefix(name)
        if prefix is None:
            return
        stop = prefix.rstrip("/")
    boundary = root / stop
    parent = (root / name).parent
    while parent != boundary and parent.is_relative_to(boundary):
        try:
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


def missing_directories(root: Path, names: Iterable[str]) -> list[str]:
    """The workspace-relative directories that writing ``names`` would create, parents first."""
    missing: dict[str, None] = {}
    for name in names:
        parts = name.split("/")[:-1]
        for depth in range(1, len(parts) + 1):
            directory = "/".join(parts[:depth])
            if directory not in missing and not os.path.lexists(root / directory):
                missing[directory] = None
    return list(missing)


def blocked_parent(root: Path, name: str) -> str | None:
    """The first existing ancestor of ``name`` that is not a directory (a file stands where a directory must be)."""
    parts = name.split("/")[:-1]
    for depth in range(1, len(parts) + 1):
        directory = "/".join(parts[:depth])
        path = root / directory
        if not os.path.lexists(path):
            return None
        if not path.is_dir():
            return directory
    return None


def blocked_parent_error(name: str, parent: str) -> UnsafeWorkspaceError:
    return UnsafeWorkspaceError(
        f"{parent} is not a directory, so devkit cannot write {name}",
        target_files=[parent, name],
        what_to_report=f"Whether {parent} may be moved so devkit can write {name}; devkit never replaces a project file",
        fix=f"Move {parent} out of the way (or delete it), then run the command again",
    )


def require_writable(root: Path, changes: dict[str, Content | None]) -> None:
    """``UnsafeWorkspaceError`` when a file stands where a directory of a path to write must be."""
    for name, content in changes.items():
        parent = None if content is None else blocked_parent(root, name)
        if parent is not None:
            raise blocked_parent_error(name, parent)


def _prune_created(root: Path, directories: list[str]) -> None:
    """Remove the directories a rolled-back transaction created, deepest first, while they are empty."""
    for directory in sorted(directories, key=lambda name: name.count("/"), reverse=True):
        parts = directory.split("/")
        if any(root.joinpath(*parts[:depth]).is_symlink() for depth in range(1, len(parts) + 1)):
            continue
        try:
            root.joinpath(*parts).rmdir()
        except OSError:
            continue


def replace_file(path: Path, content: Content | None) -> None:
    """Atomically replace (or, with ``None``, delete) one already validated file path."""
    if content is None:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".devkit-write-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                os.fchmod(stream.fileno(), content.mode)
                stream.write(content.data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)
    if path.parent.exists():
        _fsync_directory(path.parent)


def atomic_write(root: Path, name: str, content: Content | None) -> None:
    replace_file(project_path(root, name), content)


@contextmanager
def project_lock(root: Path, *, shared: bool = False) -> Iterator[None]:
    """Hold the project lock at ``.devkit/transient/lock``.

    Writers take it exclusively and fail at once when it is held. Readers
    (``shared=True``) share it with each other and wait up to
    ``READ_LOCK_TIMEOUT`` seconds for a writer to finish. A reader of a
    project without ``.devkit/`` takes no lock: there is nothing to read yet,
    and taking it would create the directory.
    """
    devkit_dir = root / LOCK.split("/", 1)[0]
    if shared and not devkit_dir.exists() and not devkit_dir.is_symlink():
        yield
        return
    path = checked_path(root, LOCK)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise UnsafeWorkspaceError(f"unsafe lock file: {LOCK}", target_files=[LOCK]) from exc
        raise
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise UnsafeWorkspaceError(f"unsafe lock file: {LOCK}", target_files=[LOCK])
        deadline = time.monotonic() + (READ_LOCK_TIMEOUT if shared else 0.0)
        while True:
            try:
                fcntl.flock(fd, (fcntl.LOCK_SH if shared else fcntl.LOCK_EX) | fcntl.LOCK_NB)
                break
            except BlockingIOError as exc:
                if time.monotonic() >= deadline:
                    raise LockHeldError("another devkit operation holds the project lock", target_files=[LOCK]) from exc
                time.sleep(_POLL)
        yield
    finally:
        os.close(fd)


def _encode(content: Content | None) -> dict | None:
    return None if content is None else {"data": base64.b64encode(content.data).decode(), "mode": content.mode}


def _decode(value: object) -> Content | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"data", "mode"}:
        raise RecoveryError("invalid journal content", target_files=[JOURNAL])
    if not isinstance(value["data"], str) or type(value["mode"]) is not int or not 0 <= value["mode"] <= 0o777:
        raise RecoveryError("invalid journal content types", target_files=[JOURNAL])
    try:
        return Content(base64.b64decode(value["data"], validate=True), value["mode"])
    except ValueError as exc:
        raise RecoveryError("invalid journal bytes", target_files=[JOURNAL]) from exc


def pending_journal(root: Path) -> bool:
    return snapshot(root, JOURNAL) is not None


def require_no_journal(root: Path) -> None:
    if pending_journal(root):
        raise PendingTransactionError("an interrupted synchronization left its journal")


def recover_locked(root: Path) -> int:
    journal = read_json(root, JOURNAL)
    if journal is None:
        return 0
    if (
        set(journal) != {"schema", "changes", "directories"}
        or type(journal["schema"]) is not int
        or journal["schema"] != 1
        or not isinstance(journal["changes"], dict)
        or not isinstance(journal["directories"], list)
    ):
        raise RecoveryError("invalid recovery journal", target_files=[JOURNAL])
    directories = journal["directories"]
    for directory in directories:
        # Only an ancestor of a journaled path: recovery never removes anything else.
        if not isinstance(directory, str) or not any(name.startswith(f"{directory}/") for name in journal["changes"]):
            raise RecoveryError("invalid recovery directory", target_files=[JOURNAL])
    changes = {}
    for name, values in journal["changes"].items():
        if name == JOURNAL or not isinstance(values, dict) or set(values) != {"before", "after"}:
            raise RecoveryError("invalid recovery entry", target_files=[JOURNAL])
        before, after = _decode(values["before"]), _decode(values["after"])
        if snapshot(root, name) not in (before, after):
            raise RecoveryError(
                f"recovery blocked by subsequent edit: {name}",
                target_files=[name, JOURNAL],
                what_to_report=f"{name} changed after the interrupted synchronization; decide which content to keep, "
                f"then delete {JOURNAL}",
            )
        changes[name] = before
    for name, before in reversed(list(changes.items())):
        atomic_write(root, name, before)
        if before is None:
            prune_empty_parents(root, name)
    # Directories the transaction created (a seeded target's too) go once they are empty again.
    _prune_created(root, directories)
    atomic_write(root, JOURNAL, None)
    return len(changes)


def apply_changes(root: Path, changes: dict[str, Content | None]) -> None:
    """Write ``changes`` (``None`` deletes) all or nothing, through the journal.

    The journal also records the directories the writes create, so a rollback removes them again once empty.
    A file standing where a directory must be is ``UnsafeWorkspaceError``, before anything is written.
    """
    if not changes:
        return
    require_writable(root, changes)
    journal = {
        "schema": 1,
        "changes": {
            name: {"before": _encode(snapshot(root, name)), "after": _encode(content)}
            for name, content in changes.items()
        },
        "directories": missing_directories(root, [name for name, content in changes.items() if content is not None]),
    }
    atomic_write(root, JOURNAL, Content(json_content(journal).data, 0o600))
    try:
        for name, content in changes.items():
            atomic_write(root, name, content)
    except Exception:
        recover_locked(root)
        raise
    atomic_write(root, JOURNAL, None)
    for name, content in changes.items():
        if content is None:
            prune_empty_parents(root, name)
