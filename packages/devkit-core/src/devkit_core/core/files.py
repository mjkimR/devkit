"""Atomic file replacement (a reader sees the old content or the new, never a partial write) and empty-tree removal.

POSIX only (directory ``fsync``, ``dir_fd``). The data goes to a temporary file in the
target's directory, is flushed to disk, takes its permission bits, and then
replaces the target with ``os.replace``; the directory is then synced, best
effort, so the rename survives a crash. An interrupted or failed write leaves
the target as it was and removes the temporary file. A symlink at ``path`` is
replaced by the new file, never written through: a caller that means the link's
target resolves the path first (and confines it, ``devkit_core.core.resolve_within``).
Replacing creates a new inode, so a hard link to the old file keeps the old
content, and the owner, ACLs and extended attributes are the new file's (the
writing user's), not the old one's.
"""

from __future__ import annotations

import contextlib
import errno
import os
import secrets
import stat
from pathlib import Path

NEW_FILE_MODE = 0o666
"""Requested for a new file; the kernel applies the process umask (``022`` gives ``0o644``, ``077`` ``0o600``)."""

_TEMPORARY_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_DIRECTORY_FLAGS = (
    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _create_temporary(directory: Path, name: str) -> tuple[int, Path]:
    """A new file next to the target, created with ``NEW_FILE_MODE`` so the kernel applies the umask."""
    while True:
        temporary = directory / f".{name}.devkit-{secrets.token_hex(6)}.tmp"
        try:
            return os.open(temporary, _TEMPORARY_FLAGS, NEW_FILE_MODE), temporary
        except FileExistsError:
            continue


def atomic_write_bytes(path: Path, data: bytes, *, mode: int | None = None) -> None:
    """Replace the file at ``path`` with ``data`` atomically, creating missing parent directories.

    ``mode`` sets the permission bits; ``None`` keeps those of the regular file
    at ``path``, or, when there is none, gives ``0o666`` less the process umask
    (the bits ``open`` would give a new file). Raises ``OSError`` when the file
    cannot be written; the target is then unchanged. Syncing the directory after
    the replacement is best effort: its failure is not raised, since the target
    has already changed.
    """
    if mode is None:
        try:
            current = path.lstat()
        except FileNotFoundError:
            current = None
        if current is not None and stat.S_ISREG(current.st_mode):
            mode = stat.S_IMODE(current.st_mode)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = _create_temporary(path.parent, path.name)
    try:
        with os.fdopen(fd, "wb") as stream:
            if mode is not None:
                os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    with contextlib.suppress(OSError):
        _fsync_directory(path.parent)


def atomic_write_text(path: Path, text: str, *, mode: int | None = None) -> None:
    """``atomic_write_bytes`` of ``text`` encoded as UTF-8, exactly (no newline translation)."""
    atomic_write_bytes(path, text.encode("utf-8"), mode=mode)


def _raise(error: OSError) -> None:
    raise error


def _remove_below(fd: int, children: dict[Path, list[str]], here: Path, removed: list[Path]) -> None:
    """Remove the directories listed beneath ``here`` (open as ``fd``), deepest first, never following a link."""
    for name in children.get(here, ()):
        child = os.open(name, _DIRECTORY_FLAGS, dir_fd=fd)
        try:
            _remove_below(child, children, here / name, removed)
        finally:
            os.close(child)
        os.rmdir(name, dir_fd=fd)
        removed.append(here / name)


def remove_empty_tree(path: Path) -> list[Path]:
    """Remove the directory ``path`` when it and every directory beneath it hold no file; return what went.

    All or nothing: any file at any depth keeps the whole tree, and a symbolic link counts as a file (it is
    never followed, never removed). The removed directories are returned deepest first, ``path`` last; the
    list is empty when ``path`` is missing, a symbolic link, not a directory, or holds a file. A directory
    that cannot be listed raises ``OSError`` before anything is removed; one that cannot be removed (a file
    appeared meanwhile) raises ``OSError`` too, leaving its parents in place.

    The tree is listed first and then removed through directory descriptors opened without following links,
    only the directories the listing found: a directory swapped for a symbolic link between the two passes
    is never followed (``OSError``), and when ``path`` itself is no longer the directory that was listed
    nothing is removed. Only the parent components of ``path`` are trusted.
    """
    try:
        top = path.lstat()
    except FileNotFoundError:
        return []
    if not stat.S_ISDIR(top.st_mode):
        return []
    children: dict[Path, list[str]] = {}
    for current, dirnames, filenames in os.walk(path, onerror=_raise, followlinks=False):
        here = Path(current)
        if filenames or any((here / name).is_symlink() for name in dirnames):
            return []
        children[here] = list(dirnames)
    try:
        fd = os.open(path, _DIRECTORY_FLAGS)
    except OSError as error:
        if error.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
            return []
        raise
    removed: list[Path] = []
    try:
        opened = os.fstat(fd)
        if (opened.st_dev, opened.st_ino) != (top.st_dev, top.st_ino):
            return []
        _remove_below(fd, children, path, removed)
    finally:
        os.close(fd)
    path.rmdir()
    removed.append(path)
    return removed
