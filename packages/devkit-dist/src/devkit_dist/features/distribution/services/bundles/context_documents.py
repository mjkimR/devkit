"""A bundle's context documents: the Markdown files of the workspace directory its manifest declares.

``devkit get-context`` lists each file's ``title`` and ``summary`` so every agent context sees what the directory
covers; bodies are read on demand (``ADR-bundle-context-lists-project-documents``). The files are project-owned, so
they are read from the workspace at run time without a receipt hash, and a file that cannot be read never fails the
context load: each value it cannot provide is ``None``.

Read rules: only regular, non-symlink ``*.md`` files other than ``README.md`` directly inside the directory, which
must itself be reached without a symlink; at most ``HEADER_LIMIT`` bytes of each file are read, so frontmatter that
does not close within them is unreadable. The list is sorted by path.
"""

from __future__ import annotations

import codecs
import os
import stat
import tomllib
from pathlib import Path
from typing import Any

from devkit_core.base.errors import FrontmatterError
from devkit_core.core import frontmatter

from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.models.results import ContextDocument
from devkit_dist.features.distribution.services.bundles.manifest import seed_target

HEADER_LIMIT = 4096
FIELD = "context_documents"
_EXCLUDED = "README.md"


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


def list_documents(root: Path, directory: str | None) -> list[ContextDocument]:
    """The context documents of ``directory`` (workspace-relative) under ``root``, sorted by path."""
    if directory is None:
        return []
    base = _directory(root, directory)
    if base is None:
        return []
    try:
        entries = sorted(os.scandir(base), key=lambda entry: entry.name)
    except OSError:
        return []
    documents: list[ContextDocument] = []
    for entry in entries:
        if not entry.name.endswith(".md") or entry.name == _EXCLUDED:
            continue
        try:
            if not entry.is_file(follow_symlinks=False):
                continue
        except OSError:
            continue
        data = _prefix(Path(entry.path))
        header = _header(data) if data is not None else None
        documents.append(ContextDocument(entry.path, _string(header, "title"), _string(header, "summary")))
    return documents
