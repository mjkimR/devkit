"""Workspace transactions: the project lock, the write-ahead journal and atomic file replacement.

POSIX only (``fcntl.flock`` through ``devkit_core.core.file_lock``, directory ``fsync``).
"""

from __future__ import annotations

import base64
import errno
import json
import logging
import os
from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path

from devkit_core.core import LockHeldError as CoreLockHeldError
from devkit_core.core import UnsafePathError, atomic_write_bytes, file_lock

from devkit_dist.features.distribution.models.content import Content, json_content
from devkit_dist.features.distribution.models.errors import (
    LockHeldError,
    PendingTransactionError,
    RecoveryError,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.services.installation.workspace import (
    JOURNAL,
    LOCK,
    checked_path,
    directory_at,
    owned_prefix,
    project_path,
    snapshot,
)
from devkit_dist.features.project.repositories.invocation import guard_execution

logger = logging.getLogger(__name__)

# A reader that meets one of these while taking the lock reads without it: the file system is read-only for it.
_READ_ONLY = frozenset({errno.EROFS, errno.EACCES, errno.EPERM})

# How long a reader waits for a writer to release the lock before giving up.
READ_LOCK_TIMEOUT = 10.0


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
            guard_execution()
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


def missing_directories(root: Path, names: Iterable[str], removed: frozenset[str] = frozenset()) -> list[str]:
    """The workspace-relative directories that writing ``names`` would create, parents first.

    A path in ``removed`` (a managed file the same change set deletes) counts as missing.
    """
    missing: dict[str, None] = {}
    for name in names:
        parts = name.split("/")[:-1]
        for depth in range(1, len(parts) + 1):
            directory = "/".join(parts[:depth])
            if directory not in missing and (directory in removed or not os.path.lexists(root / directory)):
                missing[directory] = None
    return list(missing)


def blocked_parent(root: Path, name: str, removed: frozenset[str] = frozenset()) -> str | None:
    """The first existing ancestor of ``name`` that is not a directory (a file stands where a directory must be).

    An ancestor in ``removed`` (a managed file the same change set deletes first) blocks nothing.
    """
    parts = name.split("/")[:-1]
    for depth in range(1, len(parts) + 1):
        directory = "/".join(parts[:depth])
        path = root / directory
        if directory in removed or not os.path.lexists(path):
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


def _removed_owned(changes: dict[str, Content | None]) -> frozenset[str]:
    """The owned destinations (managed or projected files) that ``changes`` delete."""
    return frozenset(name for name, content in changes.items() if content is None and owned_prefix(name) is not None)


def _ordered(changes: dict[str, Content | None]) -> list[tuple[str, Content | None]]:
    """``changes`` with the deletions first, so a deleted file frees its path for a directory written in its place,
    and the files of a deleted directory free its path for a file."""
    return sorted(changes.items(), key=lambda item: item[1] is not None)


def _emptied(root: Path, name: str, removed: frozenset[str]) -> bool:
    """Whether every file under the directory ``name`` is in ``removed`` and it holds nothing else (no symlink)."""
    for current, directories, files in os.walk(root / name):
        relative = Path(current).relative_to(root).as_posix()
        if any((Path(current) / entry).is_symlink() for entry in directories):
            return False
        if any(f"{relative}/{entry}" not in removed for entry in files):
            return False
    return True


def require_writable(root: Path, changes: dict[str, Content | None]) -> list[str]:
    """``UnsafeWorkspaceError`` when a file stands where a directory of a path to write must be, or a directory where
    a file is written; otherwise the directories the written files replace.

    A managed or projected file that the same ``changes`` delete is no obstacle (an upstream asset whose file became
    a directory): the transaction deletes it before it writes. Any other file, a project file above all, is. Likewise
    an owned directory whose files the same ``changes`` all delete (an upstream asset whose directory became a file)
    is removed once they are; one that holds anything else is never replaced.
    """
    removed = _removed_owned(changes)
    replaced = []
    for name, content in changes.items():
        if content is None:
            continue
        parent = blocked_parent(root, name, removed)
        if parent is not None:
            raise blocked_parent_error(name, parent)
        if directory_at(root, name):
            if not _emptied(root, name, removed):
                raise UnsafeWorkspaceError(
                    f"{name} is a directory that holds files devkit does not remove, so devkit cannot write the file"
                    f" {name}",
                    target_files=[name],
                    what_to_report=f"Whether {name} may be moved so devkit can write the file; devkit never removes"
                    " a file it does not own",
                    fix=f"Move {name} out of the way (or delete it), then run the command again",
                )
            replaced.append(name)
    return replaced


def _remove_emptied(root: Path, name: str) -> None:
    """Remove the directory ``name`` that a file replaces, its deletions applied: only empty directories are left."""
    for current, _, _ in os.walk(root / name, topdown=False):
        guard_execution()
        os.rmdir(current)
    _fsync_directory((root / name).parent)


def _prune_created(root: Path, directories: list[str]) -> None:
    """Remove the directories a rolled-back transaction created, deepest first, while they are empty."""
    for directory in sorted(directories, key=lambda name: name.count("/"), reverse=True):
        parts = directory.split("/")
        if any(root.joinpath(*parts[:depth]).is_symlink() for depth in range(1, len(parts) + 1)):
            continue
        try:
            guard_execution()
            root.joinpath(*parts).rmdir()
        except OSError:
            continue


def replace_file(path: Path, content: Content | None) -> None:
    """Atomically replace (``devkit_core.core.atomic_write_bytes``) or, with ``None``, delete one already validated file.

    Either way the directory entry is ``fsync``ed before this returns.
    """
    guard_execution()
    if content is not None:
        atomic_write_bytes(path, content.data, mode=content.mode)
        return
    path.unlink(missing_ok=True)
    if path.parent.exists():
        _fsync_directory(path.parent)


def atomic_write(root: Path, name: str, content: Content | None) -> None:
    replace_file(project_path(root, name), content)


@contextmanager
def project_lock(root: Path, *, shared: bool = False) -> Iterator[None]:
    """Hold the project lock at ``.devkit/transient/lock`` (``devkit_core.core.file_lock``).

    Writers take it exclusively and fail at once when it is held. Readers
    (``shared=True``) share it with each other and wait up to
    ``READ_LOCK_TIMEOUT`` seconds for a writer to finish. A reader of a
    project without ``.devkit/`` takes no lock: there is nothing to read yet,
    and taking it would create the directory. A reader that cannot create or
    open the lock file because the file system is read-only for it (a
    read-only review sandbox) reads without the lock; a writer never does.
    """
    devkit_dir = root / LOCK.split("/", 1)[0]
    if shared and not devkit_dir.exists() and not devkit_dir.is_symlink():
        yield
        return
    path = checked_path(root, LOCK)
    with ExitStack() as stack:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            stack.enter_context(file_lock(path, shared=shared, timeout=READ_LOCK_TIMEOUT if shared else 0.0))
        except UnsafePathError as exc:
            raise UnsafeWorkspaceError(f"unsafe lock file: {LOCK}", target_files=[LOCK]) from exc
        except CoreLockHeldError as exc:
            raise LockHeldError(
                "another devkit operation holds the project lock",
                target_files=[LOCK],
                what=exc.what,
                seconds=exc.seconds,
            ) from exc
        except OSError as exc:
            if not shared or exc.errno not in _READ_ONLY:
                raise
            logger.info("reading without the project lock: %s is not writable here (%s)", LOCK, exc.strerror)
        yield


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


def _swapped_directory(root: Path, name: str, directories: list[str]) -> bool:
    """Whether ``name`` is a directory the transaction swaps with a file: one it created where it deleted the file
    ``name`` (its ``after``), or one it is replacing with the file ``name`` (its ``before``, emptied or not yet)."""
    path = root / name
    return name in directories and path.is_dir() and not path.is_symlink()


LEGACY_JOURNAL_FIX = (
    f"Run `devkit recover` with the devkit version that wrote {JOURNAL}; without it, restore by hand: for each path"
    " under `changes` whose file equals its base64 `before` or `after` content, write back the `before` content"
    " (delete the file when `before` is null); a file that equals neither was edited after the sync, so decide"
    f" which content to keep; then delete {JOURNAL} and run `devkit sync`"
)


def _legacy_journal_error() -> RecoveryError:
    """The refusal of a journal an earlier devkit wrote (no ``directories`` entry), which this devkit does not read."""
    return RecoveryError(
        f"recovery journal written by an earlier devkit (it has no `directories` entry): {JOURNAL}",
        target_files=[JOURNAL],
        fix=LEGACY_JOURNAL_FIX,
        what_to_report=f"{JOURNAL} is from an earlier devkit; roll it back with that version or by hand",
    )


def recover_locked(root: Path) -> int:
    guard_execution()
    journal = read_json(root, JOURNAL)
    if journal is None:
        return 0
    if set(journal) == {"schema", "changes"}:
        raise _legacy_journal_error()
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
        # Only a journaled path or its ancestor: recovery never removes anything else.
        if not isinstance(directory, str) or not any(
            name == directory or name.startswith(f"{directory}/") for name in journal["changes"]
        ):
            raise RecoveryError("invalid recovery directory", target_files=[JOURNAL])
    changes = {}
    for name, values in journal["changes"].items():
        if name == JOURNAL or not isinstance(values, dict) or set(values) != {"before", "after"}:
            raise RecoveryError("invalid recovery entry", target_files=[JOURNAL])
        before, after = _decode(values["before"]), _decode(values["after"])
        if not _swapped_directory(root, name, directories) and snapshot(root, name) not in (before, after):
            raise RecoveryError(
                f"recovery blocked by subsequent edit: {name}",
                target_files=[name, JOURNAL],
                what_to_report=f"{name} changed after the interrupted synchronization; decide which content to keep, "
                f"then delete {JOURNAL}",
            )
        changes[name] = before
    # What the transaction created goes before anything is restored: the journal's keys are sorted, and either can
    # free the path the other needs (a file and a directory that swapped places).
    for name, before in sorted(reversed(list(changes.items())), key=lambda item: item[1] is not None):
        if before is None and _swapped_directory(root, name, directories):
            continue  # the directory a file was to replace: its files are restored into it below
        atomic_write(root, name, before)
        if before is None:
            prune_empty_parents(root, name)
    # Directories the transaction created (a seeded target's too) go once they are empty again.
    _prune_created(root, directories)
    atomic_write(root, JOURNAL, None)
    return len(changes)


def apply_changes(root: Path, changes: dict[str, Content | None]) -> None:
    """Write ``changes`` (``None`` deletes) all or nothing, through the journal.

    The journal also records the directories the writes create, so a rollback removes them again once empty, and
    those a written file replaces, so a rollback restores their files in place of it. A file standing where a
    directory must be, or a directory holding anything else where a file goes, is ``UnsafeWorkspaceError``, before
    anything is written.
    """
    if not changes:
        return
    replaced = require_writable(root, changes)
    # Deletions first: a deleted file frees its path for a directory, a directory's deleted files free it for a file.
    ordered = _ordered(changes)
    journal = {
        "schema": 1,
        "changes": {
            name: {"before": _encode(None if name in replaced else snapshot(root, name)), "after": _encode(content)}
            for name, content in ordered
        },
        "directories": [
            *missing_directories(
                root, [name for name, content in ordered if content is not None], _removed_owned(changes)
            ),
            *replaced,
        ],
    }
    atomic_write(root, JOURNAL, Content(json_content(journal).data, 0o600))
    try:
        for name, content in ordered:
            guard_execution()
            if name in replaced:
                _remove_emptied(root, name)
            atomic_write(root, name, content)
    except Exception:
        recover_locked(root)
        raise
    atomic_write(root, JOURNAL, None)
    for name, content in changes.items():
        if content is None:
            prune_empty_parents(root, name)
