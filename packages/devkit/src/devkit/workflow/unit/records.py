"""Helpers shared by the numbered record files of a unit: ``decisions/NN-*.yaml`` and ``envelopes/<kind>-NN.yaml``.

POSIX only (``fcntl.flock``), like the installation transaction.
"""

from __future__ import annotations

import fcntl
import os
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

TEMPORARY_SUFFIX = ".tmp"


def as_text(value: Any) -> str:
    """``value`` as a string; ``None`` is ``""``."""
    return "" if value is None else str(value)


@contextmanager
def _locked(directory: Path) -> Iterator[None]:
    """Hold an exclusive ``flock`` on ``directory`` itself; the lock dies with the process, so none goes stale."""
    fd = os.open(directory, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def is_temporary(name: str) -> bool:
    """Whether ``name`` is the temporary file of a ``write_new_file`` in progress (or interrupted)."""
    return name.startswith(".") and name.endswith(TEMPORARY_SUFFIX)


def write_new_file(path: Path, body: str) -> bool:
    """Create ``path`` holding ``body`` completely or not at all; ``False`` when ``path`` already exists.

    ``body`` goes to a hidden temporary file in the same directory first, which
    is then hard-linked to ``path``: the link fails instead of replacing an
    existing file, and an interrupted write leaves no partial ``path``. The
    file gets the mode a plain ``open`` would give it (``0o666`` less the umask).
    """
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}{TEMPORARY_SUFFIX}")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            return False
        return True
    finally:
        temporary.unlink(missing_ok=True)


def write_numbered(
    directory: Path,
    seq: int,
    name_for: Callable[[int], str],
    sequence_of: Callable[[str], int | None],
    body: str,
) -> tuple[Path, int]:
    """Write ``body`` as ``directory / name_for(n)`` under a sequence number ``n`` no other file holds.

    ``sequence_of`` gives the number a file name already holds in this
    numbering (``None`` for a file outside it), so the number is reserved
    itself, not only the file name: ``n`` is ``seq`` or, when that is not above
    every number taken, the next one above them. Writers serialize on a lock
    of ``directory``; the file is created whole (``write_new_file``) and never
    replaces one. Returns the path written and its sequence number.
    """
    directory.mkdir(parents=True, exist_ok=True)
    with _locked(directory):
        taken = [n for entry in os.listdir(directory) if (n := sequence_of(entry)) is not None]
        n = max(seq, max(taken, default=0) + 1)
        while not write_new_file(directory / name_for(n), body):
            n += 1
    return directory / name_for(n), n
