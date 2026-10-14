"""Rewrite relative Markdown links after files and directories moved.

``LinkRelocation`` says where things went; ``relocate_links`` points the relative links of the given files at
the new locations and reports every change. It never raises for a link or a file: a link into a moved-away
path with no new location, and a file that cannot be read or written, become ``UnresolvedLink`` entries.

All paths are absolute, or relative to the ``root`` passed to ``relocate_links``; they are compared after
``os.path.normpath``, never resolved through symbolic links. A destination is taken as written (no
percent-decoding or escape removal), so it is relocated only when its spelling names the moved path.
"""

from __future__ import annotations

import os
import posixpath
import re
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from devkit.core import atomic_write_text
from devkit.rules.workspace.markdown import extract_links

StrPath = str | os.PathLike[str]

_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class UnresolvedReason(StrEnum):
    """Why a link or a file was left as it was (stable values, also in ``to_dict``)."""

    UNMAPPED = "unmapped"  # the link points into a moved-away path that no mapping covers
    UNREADABLE = "unreadable"  # the file cannot be read as UTF-8 (``line`` 0, empty ``target``)
    UNWRITABLE = "unwritable"  # the rewritten file cannot be written (``line`` 0, empty ``target``)


@dataclass(frozen=True)
class LinkRelocation[K: StrPath]:
    """Where moved paths went, and where moved files were written for; ``K`` is the key type of the maps
    (``str`` or ``Path``), inferred from the arguments, since ``Mapping`` keys are invariant.

    - ``files``: old path to new path, exactly. A directory linked to as a whole is mapped here too.
    - ``directories``: old directory to new directory, for every path strictly beneath it (the deepest
      matching directory wins); a link to the directory itself goes through ``files`` only.
    - ``removed``: old paths (files or directories) that are gone. A link to one of them, or beneath one,
      that neither map covers is ``unmapped``. The keys of ``files`` and ``directories`` (with everything
      beneath a ``directories`` key) count as gone too.
    - ``file_origins``: new file to the old file it was written as; its relative links resolve from the
      old file's directory and are rewritten to work from the new one.
    - ``directory_origins``: new directory to the old directory its files were written for (the deepest
      matching directory wins); the same for every file beneath it without a ``file_origins`` entry.
    """

    files: Mapping[K, StrPath] = field(default_factory=dict)
    directories: Mapping[K, StrPath] = field(default_factory=dict)
    removed: Collection[StrPath] = ()
    file_origins: Mapping[K, StrPath] = field(default_factory=dict)
    directory_origins: Mapping[K, StrPath] = field(default_factory=dict)


@dataclass(frozen=True)
class RelocatedLink:
    """One rewritten link destination at ``path:line`` (``path`` relative to ``root``, POSIX separators)."""

    path: str
    line: int
    old: str
    new: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "line": self.line, "from": self.old, "to": self.new}


@dataclass(frozen=True)
class UnresolvedLink:
    """A link (``target`` as written) or a whole file (``line`` 0, ``target`` empty) left as it was."""

    path: str
    line: int
    target: str
    reason: UnresolvedReason

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "line": self.line, "target": self.target, "reason": str(self.reason)}


@dataclass
class LinkRelocationReport:
    """``files``: the files rewritten (relative to ``root``), in the order given; ``rewritten`` and
    ``unresolved`` in file, then document order."""

    files: list[str] = field(default_factory=list)
    rewritten: list[RelocatedLink] = field(default_factory=list)
    unresolved: list[UnresolvedLink] = field(default_factory=list)


def _under(path: str, directory: str) -> bool:
    return path.startswith(directory + os.sep)


def _deepest(path: str, directories: Mapping[str, str], *, inclusive: bool) -> tuple[str, str] | None:
    found = [(old, new) for old, new in directories.items() if (inclusive and path == old) or _under(path, old)]
    return max(found, key=lambda item: len(item[0]), default=None)


class _Plan:
    def __init__(self, root: Path, relocation: LinkRelocation[Any]) -> None:
        def norm(path: StrPath) -> str:
            return os.path.normpath(os.path.join(root, os.fspath(path)))

        self.files = {norm(old): norm(new) for old, new in relocation.files.items()}
        self.directories = {norm(old): norm(new) for old, new in relocation.directories.items()}
        self.removed = [norm(path) for path in relocation.removed]
        self.file_origins = {norm(new): norm(old) for new, old in relocation.file_origins.items()}
        self.directory_origins = {norm(new): norm(old) for new, old in relocation.directory_origins.items()}
        self.norm = norm

    def gone(self, target: str) -> bool:
        """Whether ``target`` is a path that moved away (so a link to it must change or is unresolved)."""
        return (
            target in self.files
            or any(target == old or _under(target, old) for old in self.directories)
            or any(target == old or _under(target, old) for old in self.removed)
        )

    def new_location(self, target: str) -> str | None:
        if target in self.files:
            return self.files[target]
        match = _deepest(target, self.directories, inclusive=False)
        return match[1] + target[len(match[0]) :] if match else None

    def base(self, file: str) -> str:
        """The directory ``file``'s relative links were written against."""
        if file in self.file_origins:
            return os.path.dirname(self.file_origins[file])
        here = os.path.dirname(file)
        match = _deepest(here, self.directory_origins, inclusive=True)
        return match[1] + here[len(match[0]) :] if match else here


def _read(path: str) -> str:
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


def relocate_links[K: StrPath](
    root: Path, files: Iterable[StrPath], relocation: LinkRelocation[K]
) -> LinkRelocationReport:
    """Rewrite the relative inline Markdown links of ``files`` (``extract_links``) for ``relocation``.

    A destination with a scheme (``https:``, ``mailto:``), a root-relative one (``/x``) and a fragment- or
    query-only one are left alone. The rest resolve against the file's directory, or against its origin
    (``file_origins``, ``directory_origins``). A link into a moved-away path goes to its new location; a
    link of a file written for another location is rewritten to reach the same target from where the file
    is now. The ``#fragment`` and ``?query`` are kept, and a destination that already names the target
    from the file's directory keeps the author's spelling (``./a.md`` stays). A link into a moved-away
    path with no new location is ``unmapped`` and stays as written.

    Changed files are replaced with ``atomic_write_text`` (a symbolic link is written through to its
    target); line endings and every other byte are kept. Returns the report; nothing is raised for a file.
    """
    plan = _Plan(root, relocation)
    report = LinkRelocationReport()
    for file in map(plan.norm, files):
        display = Path(os.path.relpath(file, root)).as_posix()
        try:
            text = _read(file)
        except (OSError, UnicodeDecodeError):
            report.unresolved.append(UnresolvedLink(display, 0, "", UnresolvedReason.UNREADABLE))
            continue
        here = os.path.dirname(file)
        base = plan.base(file)
        edits: list[tuple[int, int, int, str]] = []
        rewritten: list[RelocatedLink] = []
        for link in extract_links(text):
            target = link.target
            cut = min((i for i in (target.find("#"), target.find("?")) if i >= 0), default=len(target))
            path_part, suffix = target[:cut], target[cut:]
            if not path_part or path_part.startswith("/") or _SCHEME.match(path_part):
                continue
            resolved = os.path.normpath(os.path.join(base, path_part))
            gone = plan.gone(resolved)
            if not gone and base == here:
                continue
            new_abs = plan.new_location(resolved) if gone else resolved
            if new_abs is None:
                report.unresolved.append(UnresolvedLink(display, link.line, target, UnresolvedReason.UNMAPPED))
                continue
            new_rel = Path(os.path.relpath(new_abs, here)).as_posix()
            if new_rel == posixpath.normpath(path_part):
                continue  # the same target from the file's directory: keep the author's spelling
            edits.append((link.line - 1, link.target_start, link.target_end, new_rel + suffix))
            rewritten.append(RelocatedLink(display, link.line, target, new_rel + suffix))
        if not edits:
            continue
        lines = text.split("\n")
        for index, start, end, replacement in sorted(edits, reverse=True):
            lines[index] = lines[index][:start] + replacement + lines[index][end:]
        try:
            atomic_write_text(Path(os.path.realpath(file)), "\n".join(lines))
        except OSError:
            report.unresolved.append(UnresolvedLink(display, 0, "", UnresolvedReason.UNWRITABLE))
            continue
        report.rewritten.extend(rewritten)
        report.files.append(display)
    return report
