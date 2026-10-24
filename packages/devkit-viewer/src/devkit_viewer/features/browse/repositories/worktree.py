"""Read saved files below one registered repository's current working directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git

from devkit_viewer.features.browse.models.errors import path_invalid, path_not_found


@dataclass(frozen=True)
class TreeItem:
    """One file or directory in the current working tree."""

    name: str
    path: str
    type: str
    size: int | None = None

    def as_json(self) -> dict[str, object]:
        data: dict[str, object] = {"name": self.name, "path": self.path, "type": self.type}
        if self.size is not None:
            data["size"] = self.size
        return data


def check_path(path: str) -> str:
    """Return a repository-relative path or raise ``VIEWER_PATH_INVALID``."""
    if path == "":
        return path
    if path.startswith("/") or "\\" in path or "\0" in path:
        raise path_invalid(path)
    if any(part in ("", ".", "..") or part.casefold() == ".git" for part in path.split("/")):
        raise path_invalid(path)
    return path


class WorkingTreeReader:
    """Read saved repository files while refusing symlinks and paths outside the root."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def branch(self) -> str:
        """The checked-out local branch, or ``HEAD`` when detached."""
        try:
            return run_git(self.root, "symbolic-ref", "--quiet", "--short", "HEAD").decode().strip()
        except GitError:
            return "HEAD"

    def _resolve(self, path: str) -> Path:
        path = check_path(path)
        candidate = self.root
        for part in path.split("/") if path else ():
            candidate = candidate / part
            try:
                if candidate.is_symlink():
                    raise path_not_found(path, "path")
            except OSError as exc:
                raise path_not_found(path, "path") from exc
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(self.root)
        except (OSError, RuntimeError, ValueError) as exc:
            raise path_not_found(path, "path") from exc
        return resolved

    def tree(self, path: str) -> list[TreeItem]:
        """List immediate regular files and directories, omitting symlinks and special files."""
        directory = self._resolve(path)
        if not directory.is_dir():
            raise path_not_found(path, "directory")
        items: list[TreeItem] = []
        try:
            for child in directory.iterdir():
                if child.is_symlink() or child.name.casefold() == ".git":
                    continue
                relative = child.relative_to(self.root).as_posix()
                if child.is_dir():
                    items.append(TreeItem(child.name, relative, "tree"))
                elif child.is_file():
                    items.append(TreeItem(child.name, relative, "blob", child.stat().st_size))
        except OSError as exc:
            raise path_not_found(path, "directory") from exc
        return sorted(items, key=lambda item: (item.type != "tree", item.name))

    def blob(self, path: str) -> bytes:
        """Read one regular file from the current working tree."""
        target = self._resolve(path)
        if not target.is_file():
            raise path_not_found(path, "file")
        try:
            return target.read_bytes()
        except OSError as exc:
            raise path_not_found(path, "file") from exc
