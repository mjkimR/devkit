"""The safe path and envelope rules shared by the fingerprinted memos under ``.devkit/transient/``.

A fingerprinted memo is disposable derived state: a JSON object of exactly ``version``, ``fingerprint`` and
``entries`` kept below an existing ``<root>/.devkit/transient/``. This module decides only whether a memo path may be
used and whether a parsed memo has that envelope; reading, parsing, fingerprints, entries, writes and logging stay
with each memo. Nothing here logs, and every refusal is a value, never an exception.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path

TRANSIENT_PARTS = (".devkit", "transient")


class PathRefusal(StrEnum):
    """Why a memo path is not used; the value is a short English reason."""

    NO_TRANSIENT = "no .devkit/transient/ directory"
    MISSING = "a missing directory"
    SYMLINK = "a symbolic link"
    NOT_DIRECTORY = "a non-directory on the way"
    MOVED = "a directory that resolves elsewhere"
    NOT_REGULAR = "not a regular file"


class EnvelopeProblem(StrEnum):
    """Why a parsed memo is discarded; the value is a short English reason."""

    SHAPE = "not the expected shape"
    VERSION = "another version"
    FINGERPRINT = "another fingerprint"


def _directory_refusal(path: Path) -> PathRefusal | None:
    if path.is_symlink():
        return PathRefusal.SYMLINK
    if not path.is_dir():
        return PathRefusal.NOT_DIRECTORY
    try:
        moved = path.resolve() != path
    except (OSError, RuntimeError):
        moved = True
    return PathRefusal.MOVED if moved else None


def safe_memo_path(root: Path, parts: Sequence[str], *, create: bool) -> Path | PathRefusal:
    """The memo at ``parts`` below ``<root>/.devkit/transient/``, or why it is not used.

    ``root`` is resolved and ``parts`` ends with the file name. ``.devkit/`` and ``transient/`` must exist; any
    problem there is ``NO_TRANSIENT``. Every directory component, from ``.devkit/`` down, must be a real directory
    that resolves to itself; a missing one below ``transient/`` is ``MISSING``, or is created when ``create`` is set.
    The file may be absent; when present it must be a regular file, not a symbolic link. An ``OSError`` from creating
    a directory or reading a component's status propagates.
    """
    if not parts:
        raise ValueError("a memo path needs a file name")
    here = root
    for part in TRANSIENT_PARTS:
        here = here / part
        if not here.exists() and not here.is_symlink():
            return PathRefusal.NO_TRANSIENT
        if _directory_refusal(here) is not None:
            return PathRefusal.NO_TRANSIENT
    for part in parts[:-1]:
        here = here / part
        if not here.exists() and not here.is_symlink():
            if not create:
                return PathRefusal.MISSING
            here.mkdir(exist_ok=True)  # another process may create it at the same time
        refusal = _directory_refusal(here)
        if refusal is not None:
            return refusal
    path = here / parts[-1]
    if path.is_symlink():
        return PathRefusal.SYMLINK
    if path.exists() and not path.is_file():
        return PathRefusal.NOT_REGULAR
    return path


def envelope_problem(loaded: object, version: int, fingerprint: str) -> EnvelopeProblem | None:
    """``None`` when ``loaded`` is exactly ``{version, fingerprint, entries}`` with this integer ``version`` and
    ``fingerprint`` and a mapping of entries; else the first problem, in the order shape, version, fingerprint, and
    an ``entries`` that is not a mapping last, as ``SHAPE``."""
    if type(loaded) is not dict or set(loaded) != {"version", "fingerprint", "entries"}:
        return EnvelopeProblem.SHAPE
    if type(loaded["version"]) is not int or loaded["version"] != version:
        return EnvelopeProblem.VERSION
    if loaded["fingerprint"] != fingerprint:
        return EnvelopeProblem.FINGERPRINT
    if type(loaded["entries"]) is not dict:
        return EnvelopeProblem.SHAPE
    return None
