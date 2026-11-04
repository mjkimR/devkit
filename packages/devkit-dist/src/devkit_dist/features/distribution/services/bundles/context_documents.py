"""A bundle's context documents: the Markdown files of the workspace directory its manifest declares, and of the
directories the installed ``devkit.context_documents`` providers add for the working directory.

``devkit get-context`` lists each file's ``title`` and ``summary`` so every agent context sees what the directory
covers; bodies are read on demand (``ADR-bundle-context-lists-project-documents``). The files are project-owned, so
they are read from the workspace at run time without a receipt hash, and a file that cannot be read never fails the
context load: each value it cannot provide is ``None``.

Read rules: only regular, non-symlink ``*.md`` files other than ``README.md`` directly inside the directory, which
must itself be reached without a symlink; at most ``HEADER_LIMIT`` bytes of each file are read, so frontmatter that
does not close within them is unreadable. The list is sorted by path.

Providers (``ADR-namespace-steering-directories``): a callable registered under the ``PROVIDER_GROUP`` entry-point
group is called with the project root, the working directory (both absolute) and the declared directory
(workspace-relative) and returns a pair of sequences of workspace-relative directories: the first to list beside the
declared one, the second only to mention with a file count (``documents_elsewhere``). Each directory must satisfy
the seeded ``target`` grammar (``manifest.seed_target``). Providers run in sorted entry-point name order; one that
fails to load, raises or returns anything else is left out whole, with one ``CONTEXT_DOCUMENTS_EXTENSION_FAILED``
warning, so a project extension never fails a context load. ``devkit-dist`` reads no ``[tool.*]`` table itself.
"""

from __future__ import annotations

import codecs
import os
import stat
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import FrontmatterError
from devkit_core.core import frontmatter

from devkit_dist.features.distribution.models.errors import BundleError, ContextDocumentsExtensionFailedNotice
from devkit_dist.features.distribution.models.results import ContextDocument
from devkit_dist.features.distribution.services.bundles.manifest import seed_target

HEADER_LIMIT = 4096
FIELD = "context_documents"
PROVIDER_GROUP = "devkit.context_documents"
_EXCLUDED = "README.md"

type ProviderResult = tuple[Sequence[str], Sequence[str]]
"""What a provider returns: the workspace-relative directories to list, then those to mention."""
type Provider = Callable[[Path, Path, str], ProviderResult]
"""A ``devkit.context_documents`` provider: called with the root, the working directory and the declared directory."""


@dataclass(frozen=True)
class ProvidedDirectories:
    """The directories every usable provider returned, each sequence in provider order with duplicates kept."""

    listed: tuple[str, ...] = ()
    mentioned: tuple[str, ...] = ()


def declared_directory(manifest: bytes, context: str) -> str | None:
    """The ``context_documents`` directory a managed ``bundle.toml`` declares, ``None`` without one."""
    try:
        data = tomllib.loads(manifest.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BundleError(f"cannot read {context}: {exc}", target_files=[context]) from exc
    if FIELD not in data:
        return None
    return seed_target(data[FIELD], f"{context}: {FIELD}")


def _directory(root: Path, rel: str) -> Path | None:
    """``root / rel`` when every component exists and none is a symlink, and the last one is a directory."""
    path = root
    for part in rel.split("/"):
        path /= part
        try:
            mode = path.lstat().st_mode
        except OSError:
            return None
        if stat.S_ISLNK(mode):
            return None
    return path if stat.S_ISDIR(mode) else None


def _prefix(path: Path) -> bytes | None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        return os.read(fd, HEADER_LIMIT)
    except OSError:
        return None
    finally:
        os.close(fd)


def _block(data: bytes) -> bytes | None:
    """The bytes from the start through the frontmatter closer line, ``None`` when no block closes within ``data``.

    Only these bytes are decoded, so an invalid byte in the body never hides a readable header. A closer on the last,
    unterminated line of a full prefix may be cut (``----``), so it does not count.
    """
    lines = data.split(b"\n")
    if lines and lines[0].startswith(codecs.BOM_UTF8):
        lines[0] = lines[0][len(codecs.BOM_UTF8) :]
    if not lines or lines[0].rstrip() != b"---":
        return None
    for number, line in enumerate(lines[1:], 1):
        if line.rstrip() in (b"---", b"..."):
            if number == len(lines) - 1 and len(data) >= HEADER_LIMIT:
                return None
            return b"\n".join(lines[: number + 1]) + b"\n"
    return None


def _header(data: bytes) -> dict[str, Any] | None:
    """The frontmatter mapping of a file's first bytes; ``None`` when the block is not UTF-8, does not close within
    them or is not valid YAML."""
    block = _block(data)
    if block is None:
        return None
    try:
        text = block.decode("utf-8")
    except UnicodeError:
        return None
    try:
        located = frontmatter.locate(text)
        if located is None:
            return None
        return frontmatter.load_header(located.header)
    except FrontmatterError:
        return None


def _string(header: dict[str, Any] | None, key: str) -> str | None:
    value = header.get(key) if header is not None else None
    return value if isinstance(value, str) else None


def _entries(root: Path, directory: str) -> list[os.DirEntry[str]] | None:
    """The entries of ``directory`` that are listed, sorted by name; ``None`` when the directory is absent, reached
    through a symlink or unreadable."""
    base = _directory(root, directory)
    if base is None:
        return None
    try:
        entries = sorted(os.scandir(base), key=lambda entry: entry.name)
    except OSError:
        return None
    listed: list[os.DirEntry[str]] = []
    for entry in entries:
        if not entry.name.endswith(".md") or entry.name == _EXCLUDED:
            continue
        try:
            if not entry.is_file(follow_symlinks=False):
                continue
        except OSError:
            continue
        listed.append(entry)
    return listed


def list_documents(root: Path, directory: str | None) -> list[ContextDocument]:
    """The context documents of ``directory`` (workspace-relative) under ``root``, sorted by path."""
    if directory is None:
        return []
    entries = _entries(root, directory)
    if entries is None:
        return []
    documents: list[ContextDocument] = []
    for entry in entries:
        data = _prefix(Path(entry.path))
        header = _header(data) if data is not None else None
        documents.append(ContextDocument(entry.path, _string(header, "title"), _string(header, "summary")))
    return documents


def count_documents(root: Path, directory: str) -> int | None:
    """The number of files ``list_documents`` would list for ``directory``, without reading any; ``None`` when the
    directory is absent or unsafe (a symlink on its path)."""
    entries = _entries(root, directory)
    return None if entries is None else len(entries)


def _failed(name: str, problem: str) -> ContextDocumentsExtensionFailedNotice:
    return ContextDocumentsExtensionFailedNotice(
        f"context documents extension {name} failed: {problem}",
        what_to_report=f"The failure of the {PROVIDER_GROUP} entry point {name}; its directories are left out",
    )


def _directories(value: object, name: str, part: str) -> tuple[str, ...]:
    """``value`` as a tuple of validated workspace-relative directories; ``TypeError``/``BundleError`` otherwise."""
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{part}: expected a sequence of workspace-relative directories, not {type(value).__name__}")
    return tuple(seed_target(item, f"{name}: {part}") for item in value)


def _provided(entry: metadata.EntryPoint, root: Path, working: Path, directory: str) -> ProvidedDirectories:
    provider: Provider = entry.load()
    result = provider(root, working, directory)
    if isinstance(result, (str, bytes)) or not isinstance(result, Sequence) or len(result) != 2:
        raise TypeError("expected a pair (directories to list, directories to mention)")
    listed, mentioned = result
    return ProvidedDirectories(
        _directories(listed, entry.name, "listed directories"),
        _directories(mentioned, entry.name, "mentioned directories"),
    )


def provided_directories(root: Path, working: Path, directory: str) -> tuple[ProvidedDirectories, list[AdvisoryError]]:
    """The directories the installed providers list and mention for ``directory`` under ``root`` when the agent works
    in ``working``, and a ``CONTEXT_DOCUMENTS_EXTENSION_FAILED`` warning for each provider left out.

    Providers run in sorted entry-point name order. A provider that fails to load, raises or returns anything but
    a pair of sequences of safe workspace-relative directories (``seed_target``) contributes nothing: its whole
    result is dropped with one warning naming the entry point.
    """
    listed: list[str] = []
    mentioned: list[str] = []
    notices: list[AdvisoryError] = []
    for entry in sorted(metadata.entry_points(group=PROVIDER_GROUP), key=lambda item: (item.name, item.value)):
        try:
            provided = _provided(entry, root, working, directory)
        except Exception as exc:
            notices.append(_failed(entry.name, str(exc) or type(exc).__name__))
            continue
        listed.extend(provided.listed)
        mentioned.extend(provided.mentioned)
    return ProvidedDirectories(tuple(listed), tuple(mentioned)), notices
