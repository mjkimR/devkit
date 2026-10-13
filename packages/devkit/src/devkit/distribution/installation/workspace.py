"""The consumer workspace as devkit sees it: well-known paths, file snapshots and path safety.

Every workspace-relative path devkit reads or writes goes through
``checked_path`` (canonical relative POSIX via ``devkit.core.paths``, no
backslash, no symlinked component, a regular file if it exists).
``project_path`` adds the paths a transaction may never write;
``owned_path`` narrows that to what the receipt's ``files`` map may own.
"""

from __future__ import annotations

import stat
from pathlib import Path

from devkit.core.errors import UnsafePathError
from devkit.core.paths import normalize_relpath
from devkit.core.receipt import AGENTS_FILE, CONFIG_PATH, MANAGED_PATH, OVERRIDES_PATH, RECEIPT_PATH
from devkit.distribution.content import Content
from devkit.distribution.errors import UnsafeWorkspaceError

TRANSIENT = ".devkit/transient"
JOURNAL = f"{TRANSIENT}/sync-journal.json"
LOCK = f"{TRANSIENT}/lock"
# The installed bundles this clone has already been told about (``BUNDLE_UNSELECTED`` reports each once).
SEEN_BUNDLES = f"{TRANSIENT}/seen-bundles.json"
# The signature of every file this clone's last sync left in place. The receipt is committed but the files it records
# are Git-ignored, so after a pull that moves the receipt an untouched file differs from it; this local record tells
# such a stale file from a hand edit.
DEPLOYED = f"{TRANSIENT}/deployed.json"
# Ignores the generated parts of ``.devkit/``; written by a sync when absent, then project-owned.
DEVKIT_GITIGNORE = ".devkit/.gitignore"
DEVKIT_GITIGNORE_TEXT = """\
# Written by devkit sync when missing; edit freely, devkit never changes it.
# Generated content: `devkit sync` rebuilds it from the installed packages.
/managed/
/transient/
"""
# Pristine upstream copies taken when an override is created or accepted, for ``override diff``.
BASELINE = f"{OVERRIDES_PATH}/.baseline"

# Destinations the receipt may own: devkit's managed cache and native agent projections.
OWNED_PREFIXES = (
    f"{MANAGED_PATH}/",
    ".agents/skills/",
    ".agents/agents/",
    ".claude/skills/",
    ".codex/agents/",
    ".claude/agents/",
)
# Installation metadata the receipt can never own.
METADATA = frozenset({RECEIPT_PATH, JOURNAL, LOCK, SEEN_BUNDLES, DEPLOYED, CONFIG_PATH, AGENTS_FILE, DEVKIT_GITIGNORE})


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
        or folded == CONFIG_PATH.casefold()
        or folded.startswith(OVERRIDES_PATH.casefold() + "/")
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
