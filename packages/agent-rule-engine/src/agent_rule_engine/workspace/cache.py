from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from agent_rule_engine.workspace.catalog import DocumentCatalog


@dataclass(slots=True)
class MarkdownLink:
    text: str
    target: str
    line: int
    start: int
    end: int


_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_IGNORED_DIRS = {".git", ".venv", ".pytest_cache", ".ruff_cache", "node_modules", "__pycache__"}


class WorkspaceCache:
    """In-memory unified workspace cache for files, frontmatter, links, and catalogs."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        self.workspace_root = workspace_root.resolve() if workspace_root else Path.cwd().resolve()
        self._bytes_cache: dict[str, bytes] = {}
        self._text_cache: dict[str, str] = {}
        self._frontmatter_cache: dict[str, tuple[dict[str, Any] | None, str, int]] = {}
        self._links_cache: dict[str, list[MarkdownLink]] = {}
        self._catalog: DocumentCatalog | None = None
        self._files_cache: dict[tuple[Path, tuple[str, ...] | None, tuple[str, ...] | None], list[Path]] = {}

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = (self.workspace_root / p).resolve()
        return p.resolve()

    def _key(self, path: str | Path) -> str:
        return self._resolve_path(path).as_posix()

    def read_bytes(self, path: str | Path) -> bytes:
        key = self._key(path)
        if key not in self._bytes_cache:
            resolved = self._resolve_path(path)
            if not resolved.is_file():
                raise FileNotFoundError(f"File not found: {resolved}")
            self._bytes_cache[key] = resolved.read_bytes()
        return self._bytes_cache[key]

    def read_text(self, path: str | Path) -> str:
        key = self._key(path)
        if key not in self._text_cache:
            raw = self.read_bytes(path)
            self._text_cache[key] = raw.decode("utf-8", errors="replace")
        return self._text_cache[key]

    def write_text(self, path: str | Path, content: str, dry_run: bool = False) -> None:
        resolved = self._resolve_path(path)
        key = self._key(path)
        if not dry_run:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
        self.invalidate(path)
        self._text_cache[key] = content
        self._bytes_cache[key] = content.encode("utf-8")

    def get_frontmatter(self, path: str | Path) -> tuple[dict[str, Any] | None, str, int]:
        """Parse and cache YAML frontmatter.

        Returns (frontmatter_dict or None, body_text, line_offset).
        """
        key = self._key(path)
        if key not in self._frontmatter_cache:
            try:
                text = self.read_text(path)
            except FileNotFoundError:
                return None, "", 0

            lines = text.splitlines(keepends=True)
            if lines and lines[0].strip() == "---":
                closing = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
                if closing is None:
                    raise ValueError(f"Unclosed YAML frontmatter in {path}")
                fm_raw = "".join(lines[1:closing])
                body = "".join(lines[closing + 1 :])
                try:
                    parsed = yaml.safe_load(fm_raw)
                except yaml.YAMLError as exc:
                    raise ValueError(f"Invalid YAML frontmatter in {path}: {exc}") from exc
                if parsed is None:
                    parsed = {}
                if not isinstance(parsed, dict):
                    raise ValueError(f"YAML frontmatter must be a mapping in {path}")
                self._frontmatter_cache[key] = (parsed, body, closing + 1)
                return self._frontmatter_cache[key]
            self._frontmatter_cache[key] = (None, text, 0)
        return self._frontmatter_cache[key]

    def get_links(self, path: str | Path) -> list[MarkdownLink]:
        """Extract and cache markdown links from file."""
        key = self._key(path)
        if key not in self._links_cache:
            try:
                text = self.read_text(path)
            except FileNotFoundError:
                return []

            links: list[MarkdownLink] = []
            in_code_block = False
            for line_idx, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("```") or stripped.startswith("~~~"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue

                backtick_spans = [(bt.start(), bt.end()) for bt in re.finditer(r"`[^`]+`", line)]
                for match in _LINK_PATTERN.finditer(line):
                    start, end = match.start(), match.end()
                    if any(b_start <= start and end <= b_end for b_start, b_end in backtick_spans):
                        continue
                    text_match, target_match = match.group(1), match.group(2)
                    links.append(
                        MarkdownLink(
                            text=text_match,
                            target=target_match,
                            line=line_idx,
                            start=start,
                            end=end,
                        )
                    )
            self._links_cache[key] = links
        return self._links_cache[key]

    def get_catalog(self, workspace_root: Path | None = None) -> DocumentCatalog:
        from agent_rule_engine.workspace.catalog import DocumentCatalog

        if self._catalog is None:
            root = (workspace_root or self.workspace_root).resolve()
            catalog = DocumentCatalog()
            catalog.build(root, self)
            self._catalog = catalog
        return self._catalog

    def find_files(
        self,
        root: Path,
        extensions: tuple[str, ...] | None = (".md",),
        subdirs: tuple[str, ...] | None = None,
    ) -> list[Path]:
        """Recursively scan files matching extensions under subdirs, skipping ignored directories.

        ``extensions=None`` lists every regular file.
        """
        root = root.resolve()
        key = (root, extensions, subdirs)
        if key not in self._files_cache:
            results: set[Path] = set()
            target_dirs = [root / d for d in subdirs] if subdirs else [root]
            for target_dir in target_dirs:
                if not target_dir.is_dir():
                    continue
                for directory, dirs, files in os.walk(target_dir):
                    dirs[:] = sorted(d for d in dirs if d not in _IGNORED_DIRS)
                    for name in files:
                        path = Path(directory) / name
                        if (extensions is None or path.suffix in extensions) and path.is_file():
                            results.add(path)
            self._files_cache[key] = sorted(results)
        return list(self._files_cache[key])

    def invalidate(self, path: str | Path) -> None:
        key = self._key(path)
        self._bytes_cache.pop(key, None)
        self._text_cache.pop(key, None)
        self._frontmatter_cache.pop(key, None)
        self._links_cache.pop(key, None)
        self._catalog = None
        self._files_cache.clear()

    def invalidate_many(self, paths: Iterable[str | Path]) -> None:
        for p in paths:
            self.invalidate(p)

    def invalidate_all(self) -> None:
        self._bytes_cache.clear()
        self._text_cache.clear()
        self._frontmatter_cache.clear()
        self._links_cache.clear()
        self._catalog = None
        self._files_cache.clear()
