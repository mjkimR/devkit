"""The consumer workspace as devkit sees it: well-known paths, file contents and path safety.

Every workspace-relative path devkit reads or writes goes through
``checked_path`` (canonical relative POSIX via ``devkit.core.paths``, no
backslash, no symlinked component, a regular file if it exists).
``project_path`` adds the paths a transaction may never write;
``owned_path`` narrows that to what the receipt's ``files`` map may own.
"""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass
from pathlib import Path

from devkit.core.errors import UnsafePathError
from devkit.core.paths import normalize_relpath
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH

from ..errors import UnsafeWorkspaceError

RECEIPT = RECEIPT_PATH
CONFIG = CONFIG_PATH
TRANSIENT = ".devkit/transient"
JOURNAL = f"{TRANSIENT}/sync-journal.json"
LOCK = f"{TRANSIENT}/lock"
MANAGED = ".devkit/managed"
OVERRIDES = ".devkit/overrides"
# Pristine upstream copies taken when an override is created or accepted, for ``override diff``.
BASELINE = f"{OVERRIDES}/.baseline"
# Root guidance file: only its marker block is managed (see ``guidance_block``).
AGENTS_FILE = "AGENTS.md"

# Destinations the receipt may own: devkit's managed cache and native agent projections.
OWNED_PREFIXES = (
    f"{MANAGED}/",
    ".agents/skills/",
    ".agents/agents/",
    ".claude/skills/",
    ".codex/agents/",
    ".claude/agents/",
)
# Installation metadata the receipt can never own.
METADATA = frozenset({RECEIPT, JOURNAL, LOCK, CONFIG, AGENTS_FILE})


@dataclass(frozen=True)
class Content:
    data: bytes
    mode: int


def normal_mode(mode: int) -> int:
    """The mode devkit records and compares: ``0o755`` when any execute bit is set, else ``0o644``.

    Group-writable checkouts (umask ``002``) and other permission noise are not edits.
    """
    return 0o755 if mode & 0o111 else 0o644


def same_content(left: Content | None, right: Content | None) -> bool:
    """Equal bytes and equal normalized mode (``None`` means absent)."""
    if left is None or right is None:
        return left is right
    return left.data == right.data and normal_mode(left.mode) == normal_mode(right.mode)


def checked_path(root: Path, name: str) -> Path:
    """``root / name`` for a canonical relative path without backslashes or symlinked components."""
    try:
        rel = normalize_relpath(name, canonical=True)
    except UnsafePathError as exc:
        raise UnsafeWorkspaceError(f"unsafe deployment path: {name}", target_files=[name]) from exc
    if "\\" in name:
        raise UnsafeWorkspaceError(f"unsafe deployment path: {name}", target_files=[name])
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise UnsafeWorkspaceError(f"deployment symlink: {name}", target_files=[name])
    if path.exists() and not path.is_file():
        raise UnsafeWorkspaceError(f"nonregular deployment path: {name}", target_files=[name])
    return path


def project_path(root: Path, name: str) -> Path:
    """A workspace-relative path devkit may read or write in a transaction.

    Besides owned destinations this admits seeded targets anywhere in the
    project except Git's own directory and devkit's project-authored files,
    compared case-insensitively so a case-insensitive file system cannot be
    used to reach them. Receipt ownership is narrower; see ``owned_path``.
    """
    folded = name.casefold()
    if (
        folded.split("/", 1)[0] == ".git"
        or folded == CONFIG.casefold()
        or folded.startswith(OVERRIDES.casefold() + "/")
    ):
        raise UnsafeWorkspaceError(f"unsafe deployment path: {name}", target_files=[name])
    return checked_path(root, name)


def owned_path(root: Path, name: str) -> Path:
    """A path the receipt's ``files`` map may own: managed cache or agent projection."""
    if name in METADATA or not name.startswith(OWNED_PREFIXES):
        raise UnsafeWorkspaceError(f"unsafe deployment path: {name}", target_files=[name])
    return project_path(root, name)


def owned_prefix(name: str) -> str | None:
    return next((prefix for prefix in OWNED_PREFIXES if name.startswith(prefix)), None)


def snapshot(root: Path, name: str) -> Content | None:
    path = project_path(root, name)
    if not path.exists():
        return None
    return Content(path.read_bytes(), stat.S_IMODE(path.stat().st_mode))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def signature(content: Content) -> tuple[str, int]:
    """``(sha256, normalized mode)``: what the receipt records for a file."""
    return sha256(content.data), normal_mode(content.mode)
