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
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..errors import LockHeldError, PendingTransactionError, RecoveryError, UnsafeWorkspaceError
from .workspace import JOURNAL, LOCK, Content, checked_path, owned_prefix, project_path, snapshot

# How long a reader waits for a writer to release the lock before giving up.
READ_LOCK_TIMEOUT = 10.0
_POLL = 0.05


def json_content(value: object) -> Content:
    return Content((json.dumps(value, sort_keys=True, indent=2) + "\n").encode(), 0o644)


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


def prune_empty_parents(root: Path, name: str) -> None:
    """Remove directories left empty by deleting ``name``, up to (not including) its owned prefix.

    Only owned destinations are pruned (``.claude/skills/<id>/`` goes,
    ``.claude/skills/`` stays); a seeded target's directories belong to the project.
    """
    prefix = owned_prefix(name)
    if prefix is None:
        return
    stop = root / prefix.rstrip("/")
    parent = (root / name).parent
    while parent != stop and parent.is_relative_to(stop):
        try:
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


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
    ``READ_LOCK_TIMEOUT`` seconds for a writer to finish.
    """
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
        raise PendingTransactionError("an interrupted synchronization left its journal; run devkit recover first")


def recover_locked(root: Path) -> int:
    journal = read_json(root, JOURNAL)
    if journal is None:
        return 0
    if (
        set(journal) != {"schema", "changes"}
        or type(journal["schema"]) is not int
        or journal["schema"] != 1
        or not isinstance(journal["changes"], dict)
    ):
        raise RecoveryError("invalid recovery journal", target_files=[JOURNAL])
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
    atomic_write(root, JOURNAL, None)
    return len(changes)


def apply_changes(root: Path, changes: dict[str, Content | None]) -> None:
    """Write ``changes`` (``None`` deletes) all or nothing, through the journal."""
    if not changes:
        return
    journal = {
        "schema": 1,
        "changes": {
            name: {"before": _encode(snapshot(root, name)), "after": _encode(content)}
            for name, content in changes.items()
        },
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
