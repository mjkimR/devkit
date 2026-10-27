"""Read saved files below one registered repository's current working directory."""

from __future__ import annotations

import re
from dataclasses import dataclass
from os import scandir
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.frontmatter import BOM, CLOSERS, OPENER, locate
from devkit_core.core.git import run_git

from devkit_viewer.features.browse.models.errors import ReadError, path_invalid, path_not_found

_BOM = BOM.encode()
_OPENER = OPENER.encode()
_CLOSERS = frozenset(closer.encode() for closer in CLOSERS)
# Bytes of the first line read to recognise an opener (a byte order mark, ``---`` and trailing whitespace).
_OPENER_READ = 64


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

    def tree(self, path: str, *, recursive: bool = False) -> list[TreeItem]:
        """List regular entries, optionally including descendants, without following symlinks."""
        directory = self._resolve(path)
        if not directory.is_dir():
            raise path_not_found(path, "directory")
        items: list[TreeItem] = []
        pending = [directory]
        try:
            while pending:
                with scandir(pending.pop()) as children:
                    for child in children:
                        if child.name.casefold() == ".git" or child.is_symlink():
                            continue
                        child_path = Path(child.path)
                        relative = child_path.relative_to(self.root).as_posix()
                        if child.is_dir(follow_symlinks=False):
                            items.append(TreeItem(child.name, relative, "tree"))
                            if recursive:
                                pending.append(child_path)
                        elif child.is_file(follow_symlinks=False):
                            items.append(
                                TreeItem(child.name, relative, "blob", child.stat(follow_symlinks=False).st_size)
                            )
        except OSError as exc:
            raise path_not_found(path, "directory") from exc
        return sorted(items, key=lambda item: (item.type != "tree", item.path))

    def blob(self, path: str) -> bytes:
        """Read one regular file from the current working tree."""
        target = self._resolve(path)
        if not target.is_file():
            raise path_not_found(path, "file")
        try:
            return target.read_bytes()
        except OSError as exc:
            raise path_not_found(path, "file") from exc

    def frontmatter(self, path: str) -> str:
        """Read the YAML envelope only; leave document bodies unread.

        The block follows ``devkit_core.core.frontmatter``'s grammar (a byte order mark, ``--- `` with trailing
        whitespace and a ``...`` closer are accepted) and is returned normalized as ``---`` + header + ``---``, so
        the frontend reads every file core reads. ``""`` when the file has no frontmatter.
        """
        target = self._resolve(path)
        if not target.is_file():
            raise path_not_found(path, "file")
        try:
            with target.open("rb") as stream:
                first = stream.readline(_OPENER_READ)
                if first.removeprefix(_BOM).rstrip() != _OPENER:
                    return ""
                lines = [first]
                for line in stream:
                    lines.append(line)
                    if line.rstrip() in _CLOSERS:
                        block = locate(b"".join(lines).decode("utf-8"))
                        if block is None:
                            return ""
                        newline = block.newline or "\n"
                        return f"{OPENER}{newline}{block.header}{OPENER}{newline}"
            raise ValueError("unterminated YAML frontmatter")
        except OSError as exc:
            raise path_not_found(path, "file") from exc

    def dashboard_headers(self, section: str) -> dict[str, object]:
        """Discover dashboard candidates and return only their frontmatter."""
        if section not in ("milestones", "proposals", "feedback"):
            raise path_invalid(section)
        roots = (
            ["docs/roadmap"]
            if section == "milestones"
            else ["docs/proposals"]
            if section == "proposals"
            else ["docs", "specs"]
        )
        paths: list[str] = []
        errors: list[str] = []
        for root in roots:
            if not (self.root / root).exists():
                continue
            try:
                entries = self.tree(root, recursive=section == "feedback")
                if section == "proposals":
                    paths.extend(
                        f"{item.path}/proposal.md"
                        for item in entries
                        if item.type == "tree"
                        and re.fullmatch(r"docs/proposals/PROP-[^/]+", item.path)
                        and not (self.root / item.path / "proposal.md").is_symlink()
                        and (self.root / item.path / "proposal.md").is_file()
                    )
                else:
                    paths.extend(
                        item.path
                        for item in entries
                        if item.type == "blob"
                        and (
                            re.fullmatch(r"docs/roadmap/MS-[^/]+\.md", item.path)
                            if section == "milestones"
                            else "/feedback/" in item.path and item.name.endswith(".md") and item.name != "README.md"
                        )
                    )
            except ReadError as exc:
                errors.append(f"{root}: {exc}")
        items: list[dict[str, str]] = []
        for path in sorted(set(paths)):
            try:
                items.append({"path": path, "content": self.frontmatter(path), "encoding": "utf-8"})
            except (ReadError, OSError, ValueError) as exc:
                errors.append(f"{path}: {exc}")
        return {"items": items, "errors": errors}
