"""Expand explicit rule targets within the project workspace."""

from __future__ import annotations

import os
import unicodedata
from collections.abc import Sequence
from pathlib import Path

from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, OVERRIDES_PATH

from devkit_agt.features.rules.models.errors import TargetError
from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache


def expand_targets(workspace_root: Path, cache: WorkspaceCache, targets: Sequence[str | Path]) -> list[str]:
    """Explicit targets as workspace-relative files; a directory expands to the files under it.

    Expansion lists what ``WorkspaceCache.find_files`` lists (regular files,
    skipping ignored directories); a file named directly is checked as is,
    even inside an ignored directory. Relative targets are taken from
    ``workspace_root``. Anything that is not an existing file or directory
    inside the workspace, including a symlink that resolves outside it, and
    anything inside ``.devkit/managed/`` or ``.devkit/overrides/`` (receipt-pinned
    copies that rules never read) raises ``TargetError``.
    """
    files: list[str] = []
    seen: set[str] = set()
    pinned = [workspace_root / directory for directory in (MANAGED_PATH, OVERRIDES_PATH)]
    for target in targets:
        path = Path(target)
        absolute = _on_disk(
            workspace_root, Path(os.path.normpath(path if path.is_absolute() else workspace_root / path))
        )
        if not absolute.is_relative_to(workspace_root):
            absolute = absolute.resolve()
        if not absolute.is_relative_to(workspace_root):
            raise TargetError(
                f"{target} is outside the workspace {workspace_root}",
                target_files=[str(target)],
                fix=f"Drop the argument {target}: rules check only files inside {workspace_root}",
            )
        if any(
            absolute.is_relative_to(directory) or absolute.resolve().is_relative_to(directory) for directory in pinned
        ):
            raise TargetError(
                f"{target} is a receipt-pinned copy under {MANAGED_PATH}/ or {OVERRIDES_PATH}/, which rules never read",
                target_files=[str(target)],
                fix=f"Name the project's own files; check a bundle's rules and documents in its source, not in {MANAGED_PATH}/ or {OVERRIDES_PATH}/",
            )
        if (absolute.is_dir() or absolute.is_file()) and not absolute.resolve().is_relative_to(workspace_root):
            raise TargetError(
                f"{target} is a symlink that resolves outside the workspace {workspace_root}",
                target_files=[str(target)],
                fix=f"Drop the argument {target}: rules check only files inside {workspace_root}",
            )
        if absolute.is_dir():
            for found in cache.find_files(absolute, extensions=None):
                rel = found.relative_to(workspace_root).as_posix()
                if rel not in seen:
                    seen.add(rel)
                    files.append(rel)
        elif absolute.is_file():
            relative = absolute.relative_to(workspace_root).as_posix()
            if relative not in seen:
                seen.add(relative)
                files.append(relative)
        else:
            raise TargetError(
                f"{target} is not an existing file or directory inside the workspace",
                target_files=[str(target)],
                fix=f"Correct the path {target}, or drop it",
            )
    return files


def _on_disk(workspace_root: Path, path: Path) -> Path:
    """``path`` with each name below ``workspace_root`` spelled as on disk; the root and anything outside stay as given.

    A name the file system finds under another case or Unicode normalization (macOS) takes the listed spelling, so a
    directory target expands to the names the workspace walk and Git use. A name the file system keeps as written
    (Linux) is found in the other normalization form when only that one exists. Spelling stops at the first name
    that is not found.
    """
    if not path.is_relative_to(workspace_root):
        return path
    current = workspace_root
    parts = path.relative_to(workspace_root).parts
    for index, part in enumerate(parts):
        try:
            names = os.listdir(current)
        except OSError:
            return current.joinpath(*parts[index:])
        if part not in names:
            if os.path.lexists(current / part):
                key = _spelling_key(part)
                part = next((name for name in names if _spelling_key(name) == key), part)
            else:
                spelled = (unicodedata.normalize(form, part) for form in ("NFC", "NFD"))
                found = next((name for name in spelled if name in names), None)
                if found is None:
                    return current.joinpath(*parts[index:])
                part = found
        current = current / part
    return current


def _spelling_key(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()
