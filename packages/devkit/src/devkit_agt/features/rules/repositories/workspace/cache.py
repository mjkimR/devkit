"""Session cache of workspace files, frontmatter, links, parsed Python and the document catalog.

File discovery skips dependency and cache directories and the hash-pinned
copies ``devkit sync`` owns (``.devkit/managed/`` and ``.devkit/overrides/``),
which are never rule input and never written. Inside a Git work tree it is
further restricted to the files Git does not ignore
(``git ls-files --cached --others --exclude-standard``), so a virtual
environment or build output that ``.gitignore`` covers is never scanned. Files
named as explicit targets on the command line (``add_explicit``; ``RuleContext``
adds them for a working-tree run, never for a snapshot's changed files) are
listed even when Git ignores them or they sit in a dependency or cache
directory: an explicit target is checked as is. Pinned copies are never listed, not even as targets. A
materialized snapshot passes ``git_filter=False``: its tree already holds
tracked files only. Git and the file system may spell a non-ASCII name in
different Unicode normalization forms (macOS Git reports NFC with
``core.precomposeunicode`` while the disk may hold NFD), so names are
compared in NFC, and a file reached under both spellings is listed once.
"""

from __future__ import annotations

import ast
import os
import unicodedata
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

from devkit_core.core import GitError, UnsafePathError, atomic_write_bytes, run_git
from devkit_core.core.frontmatter import parse as parse_frontmatter
from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, OVERRIDES_PATH

from devkit_agt.features.rules.models.errors import PinnedWriteError
from devkit_agt.features.rules.models.file_facts import FileFactsDescriptor, JsonValue
from devkit_agt.features.rules.repositories.workspace.file_facts import FileFactsCache
from devkit_agt.features.rules.repositories.workspace.markdown import MarkdownLink, extract_links

if TYPE_CHECKING:
    from devkit_agt.features.rules.repositories.workspace.catalog import DocumentCatalog

__all__ = ["WorkspaceCache"]

T = TypeVar("T")

# Workspace-relative directories holding copies whose hashes the installation receipt pins.
_PINNED_DIRS = (MANAGED_PATH, OVERRIDES_PATH)
_IGNORED_DIRS = {".git", ".venv", ".pytest_cache", ".ruff_cache", "node_modules", "__pycache__"}
_T = TypeVar("_T", bound=ast.AST)


def _nfc(name: str) -> str:
    """``name`` in Unicode normalization form C, the form file names are compared in."""
    return unicodedata.normalize("NFC", name)


class WorkspaceCache:
    """In-memory workspace cache for file listings, bytes, text, frontmatter, links, parsed Python and the catalog.

    Reads go through the cache and writes through ``write_text``; ``invalidate``
    drops one file (and every derived index), ``invalidate_all`` everything.
    Each path argument is resolved (symlinks followed) once between
    invalidations: the cache assumes the workspace does not change outside it
    during a run, so a symlink retargeted without an invalidation keeps the
    target it first resolved to. ``write_text`` always resolves afresh.
    """

    def __init__(
        self,
        workspace_root: Path | None = None,
        *,
        git_filter: bool = True,
        facts_enabled: bool = True,
        facts_root: Path | None = None,
        facts_writer: bool = False,
        facts_prune: bool = False,
    ) -> None:
        self.workspace_root = workspace_root.resolve() if workspace_root else Path.cwd().resolve()
        self._git_filter = git_filter
        self._git_files: set[str] | None = None
        self._git_files_loaded = False
        self._explicit: set[str] = set()
        self._bytes_cache: dict[str, bytes] = {}
        self._text_cache: dict[str, str] = {}
        self._frontmatter_cache: dict[str, dict[str, Any] | None] = {}
        self._links_cache: dict[str, list[MarkdownLink]] = {}
        # A parsed module, or the type and arguments of the error its parse raised.
        self._ast_cache: dict[str, ast.Module | tuple[type[Exception], tuple[Any, ...]]] = {}
        # Per-file node index: by-type sequence and query cache.
        self._nodes_cache: dict[
            str,
            tuple[
                dict[type[ast.AST], tuple[tuple[int, ast.AST], ...]],
                dict[tuple[type[ast.AST], ...], tuple[ast.AST, ...]],
            ],
        ] = {}
        # The resolved path of each path argument as given, until the next invalidation.
        self._resolved: dict[str | Path, Path] = {}
        self._catalog: DocumentCatalog | None = None
        self._files_cache: dict[tuple[Path, tuple[str, ...] | None], list[Path]] = {}
        self._computed_cache: dict[str, Any] = {}
        self._file_facts = FileFactsCache(
            self,
            root=facts_root or self.workspace_root,
            enabled=facts_enabled,
            writer=facts_writer,
            prune=facts_prune,
        )

    def get_file_facts(
        self,
        path: str | Path,
        descriptor: FileFactsDescriptor[T],
        *,
        context_key: JsonValue = None,
    ) -> T:
        """Pull immutable rule-owned extraction; persistent reuse still verifies exact cached source bytes."""
        return self._file_facts.get(path, descriptor, context_key)

    def complete_file_facts(self, descriptor: FileFactsDescriptor[Any], paths: list[str]) -> None:
        """Mark a complete successful enumeration; caught source failures must skip this call."""
        self._file_facts.complete(descriptor, paths)

    def flush_file_facts(self) -> None:
        """Flush only with an explicit writer after successful evaluation and final rechecks."""
        self._file_facts.flush()

    def _resolve_fresh(self, path: str | Path) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def _resolve_path(self, path: str | Path) -> Path:
        """``path`` resolved against the workspace root, once per path argument until an invalidation."""
        resolved = self._resolved.get(path)
        if resolved is None:
            resolved = self._resolved[path] = self._resolve_fresh(path)
        return resolved

    def _key(self, path: str | Path) -> str:
        return self._resolve_path(path).as_posix()

    def read_bytes(self, path: str | Path) -> bytes:
        resolved = self._resolve_path(path)
        key = resolved.as_posix()
        if key not in self._bytes_cache:
            if not resolved.is_file():
                raise FileNotFoundError(f"File not found: {resolved}")
            self._bytes_cache[key] = resolved.read_bytes()
        return self._bytes_cache[key]

    def read_text(self, path: str | Path) -> str:
        """The file decoded as UTF-8; undecodable bytes become U+FFFD (use ``read_text_strict`` before rewriting)."""
        key = self._key(path)
        if key not in self._text_cache:
            self._text_cache[key] = self.read_bytes(path).decode("utf-8", errors="replace")
        return self._text_cache[key]

    def read_text_strict(self, path: str | Path) -> str | None:
        """The file decoded as UTF-8, or ``None`` when it is not valid UTF-8 and must not be rewritten."""
        try:
            return self.read_bytes(path).decode("utf-8")
        except UnicodeDecodeError:
            return None

    def write_text(self, path: str | Path, content: str, dry_run: bool = False) -> None:
        """Write ``content`` as UTF-8 bytes, exactly (no newline translation), and refresh the cache.

        The path is resolved (symlinks followed) and the file replaced
        atomically, keeping its permission bits (``devkit_core.core.atomic_write_bytes``).
        A path that resolves outside the workspace root raises
        ``devkit_core.core.UnsafePathError`` (``PATH_UNSAFE``). Files under
        ``.devkit/managed/`` and ``.devkit/overrides/`` are never written: the
        installation receipt pins their hashes, so writing one raises
        ``PinnedWriteError`` (``RULES_PINNED_WRITE_REFUSED``, ``BLOCKED``).
        """
        resolved = self._resolve_fresh(path)
        if not resolved.is_relative_to(self.workspace_root):
            raise UnsafePathError(
                f"refusing to write outside the workspace root {self.workspace_root}: {path} resolves to {resolved}",
                target_files=[str(path)],
            )
        if self._pinned(resolved):
            raise PinnedWriteError(
                f"refusing to write a receipt-pinned copy under {' or '.join(_PINNED_DIRS)}: {resolved}",
                target_files=[str(resolved)],
            )
        key = resolved.as_posix()
        data = content.encode("utf-8")
        if dry_run:
            self._file_facts.writer = False
        if not dry_run:
            atomic_write_bytes(resolved, data)
        self.invalidate(path)
        self._text_cache[key] = content
        self._bytes_cache[key] = data

    def get_python_ast(self, path: str | Path) -> ast.Module:
        """The parsed module of a Python file, shared by every caller for the run: never modify it.

        The file's bytes are parsed once as CPython reads source (a BOM and a
        PEP 263 coding cookie are honoured), under its workspace-relative POSIX
        name (the resolved absolute path for a file outside the workspace). A
        ``SyntaxError`` or ``ValueError`` from the parse is remembered and
        raised again, as a fresh exception of the same type and arguments, on
        every later call. A missing file raises ``FileNotFoundError`` like
        ``read_bytes`` and is not remembered. ``invalidate`` and
        ``invalidate_all`` drop the tree or the error.
        """
        resolved = self._resolve_path(path)
        key = resolved.as_posix()
        outcome = self._ast_cache.get(key)
        if outcome is None:
            data = self.read_bytes(path)
            try:
                name = resolved.relative_to(self.workspace_root).as_posix()
            except ValueError:
                name = key
            try:
                outcome = ast.parse(data, filename=name)
            except (SyntaxError, ValueError) as exc:
                outcome = (type(exc), exc.args)
            self._ast_cache[key] = outcome
        if isinstance(outcome, ast.Module):
            return outcome
        error_type, args = outcome
        raise error_type(*args)

    @overload
    def get_python_nodes(self, path: str | Path, __t1: type[_T], /) -> tuple[_T, ...]: ...

    @overload
    def get_python_nodes(self, path: str | Path, *types: type[ast.AST]) -> tuple[ast.AST, ...]: ...

    def get_python_nodes(self, path: str | Path, *types: type[ast.AST]) -> tuple[ast.AST, ...]:
        """Nodes of the requested AST types from a parsed Python module, in document traversal order.

        Builds the file's type-indexed node table on the first call from ``get_python_ast(path)``.
        Returns an immutable tuple of nodes whose type matches any of ``types`` in document
        traversal order (as yielded by ``ast.walk``).
        Raises ``ValueError`` if no types are passed, and re-raises any ``SyntaxError`` or
        ``ValueError`` from ``get_python_ast``.
        """
        if not types:
            raise ValueError("at least one node type must be specified")
        for t in types:
            if not isinstance(t, type) or not issubclass(t, ast.AST):
                raise TypeError(f"expected ast.AST subclass, got {t!r}")

        tree = self.get_python_ast(path)
        resolved = self._resolve_path(path)
        key = resolved.as_posix()

        file_index = self._nodes_cache.get(key)
        if file_index is None:
            by_type: dict[type[ast.AST], list[tuple[int, ast.AST]]] = {}
            for i, node in enumerate(ast.walk(tree)):
                nt = type(node)
                if nt not in by_type:
                    by_type[nt] = []
                by_type[nt].append((i, node))
            file_index = (
                {t: tuple(items) for t, items in by_type.items()},
                {},
            )
            self._nodes_cache[key] = file_index

        by_type_map, query_cache = file_index
        cached_result = query_cache.get(types)
        if cached_result is not None:
            return cached_result

        matched: list[tuple[int, ast.AST]] = []
        for nt, items in by_type_map.items():
            if issubclass(nt, types):
                matched.extend(items)

        if len(matched) > 1:
            matched.sort(key=lambda x: x[0])

        result: tuple[ast.AST, ...] = tuple(node for _, node in matched)
        query_cache[types] = result
        return result

    def get_frontmatter(self, path: str | Path) -> dict[str, Any] | None:
        """The YAML frontmatter mapping of a file (``devkit_core.core.frontmatter`` grammar), or ``None``.

        A missing file and a file without frontmatter are ``None``. Raises
        ``devkit_core.core.FrontmatterError`` (``FRONTMATTER_INVALID``) for a block that
        is unclosed, invalid YAML or not a mapping with string keys.
        """
        key = self._key(path)
        if key not in self._frontmatter_cache:
            try:
                text = self.read_text(path)
            except FileNotFoundError:
                return None
            self._frontmatter_cache[key] = parse_frontmatter(text).data
        return self._frontmatter_cache[key]

    def get_links(self, path: str | Path) -> list[MarkdownLink]:
        """Inline Markdown links of a file in document order (see ``workspace.markdown.extract_links``)."""
        key = self._key(path)
        if key not in self._links_cache:
            try:
                text = self.read_text(path)
            except FileNotFoundError:
                return []
            self._links_cache[key] = extract_links(text)
        return self._links_cache[key]

    def get_catalog(self, workspace_root: Path | None = None) -> DocumentCatalog:
        from devkit_agt.features.rules.repositories.workspace.catalog import DocumentCatalog

        if self._catalog is None:
            root = (workspace_root or self.workspace_root).resolve()
            catalog = DocumentCatalog()
            catalog.build(root, self)
            self._catalog = catalog
        return self._catalog

    def get_or_compute(self, key: str, factory: Callable[[], T]) -> T:
        """A run-scoped object computed once by ``factory`` and retained until an invalidation."""
        if key not in self._computed_cache:
            self._computed_cache[key] = factory()
        return cast(T, self._computed_cache[key])

    def _visible_files(self) -> set[str] | None:
        """Workspace-relative files Git does not ignore, or ``None`` outside a Git work tree."""
        if not self._git_filter:
            return None
        if not self._git_files_loaded:
            self._git_files_loaded = True
            try:
                output = run_git(
                    self.workspace_root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "."
                )
            except GitError:
                self._git_files = None
            else:
                self._git_files = {
                    _nfc(part.decode("utf-8", errors="surrogateescape")) for part in output.split(b"\0") if part
                }
        return self._git_files

    def add_explicit(self, paths: Iterable[str]) -> None:
        """Workspace-relative files a run names explicitly; Git ignore rules never hide them from scans."""
        added = {_nfc(path) for path in paths} - self._explicit
        if added:
            self._explicit |= added
            self._files_cache.clear()

    def _pinned(self, path: Path) -> bool:
        return any(path.is_relative_to(self.workspace_root / pinned) for pinned in _PINNED_DIRS)

    def find_files(self, root: Path, extensions: tuple[str, ...] | None = (".md",)) -> list[Path]:
        """Regular files under ``root`` (inside the workspace) with one of ``extensions``, sorted.

        ``extensions=None`` lists every regular file. Dependency and cache
        directories, ``.devkit/managed/`` and ``.devkit/overrides/``, symlinks
        that resolve outside the workspace and, inside a Git work tree,
        Git-ignored files are skipped; an explicit target (``add_explicit``)
        under ``root`` is listed even in a dependency or cache directory or
        when Git ignores it, but never under the pinned directories. A
        ``root`` that resolves outside the workspace lists nothing.
        """
        root = root.resolve()
        key = (root, extensions)
        if key not in self._files_cache:
            visible = self._visible_files()
            results: list[Path] = []
            if root.is_dir() and root.is_relative_to(self.workspace_root) and not self._pinned(root):
                for directory, dirs, files in os.walk(root):
                    here = Path(directory)
                    dirs[:] = sorted(d for d in dirs if d not in _IGNORED_DIRS and not self._pinned(here / d))
                    for name in files:
                        path = here / name
                        if extensions is not None and path.suffix not in extensions:
                            continue
                        if visible is not None and not self._visible(path, visible):
                            continue
                        if path.is_file() and self._stays_inside(path):
                            results.append(path)
                listed = {self._name(path) for path in results}
                for relative in self._explicit:
                    path = self.workspace_root / relative
                    if (
                        relative not in listed
                        and path.is_relative_to(root)
                        and (extensions is None or path.suffix in extensions)
                        and not self._pinned(path)
                        and path.is_file()
                        and path.resolve().is_relative_to(self.workspace_root)
                    ):
                        results.append(path)
            self._files_cache[key] = sorted(results)
        return list(self._files_cache[key])

    def _name(self, path: Path) -> str:
        """``path`` relative to the workspace, POSIX and NFC: the form explicit targets are kept in."""
        return _nfc(path.relative_to(self.workspace_root).as_posix())

    def _visible(self, path: Path, visible: set[str]) -> bool:
        try:
            relative = path.relative_to(self.workspace_root).as_posix()
        except ValueError:
            return False
        relative = _nfc(relative)
        return relative in visible or relative in self._explicit

    def _stays_inside(self, path: Path) -> bool:
        """A symlink is listed only when it resolves inside the workspace, as a snapshot materializes it."""
        return not path.is_symlink() or path.resolve().is_relative_to(self.workspace_root)

    def invalidate(self, path: str | Path) -> None:
        self._file_facts.invalidate(self._key(path))
        self._resolved.clear()
        key = self._key(path)
        self._file_facts.invalidate(key)
        self._bytes_cache.pop(key, None)
        self._text_cache.pop(key, None)
        self._frontmatter_cache.pop(key, None)
        self._links_cache.pop(key, None)
        self._ast_cache.pop(key, None)
        self._nodes_cache.pop(key, None)
        self._catalog = None
        self._computed_cache.clear()
        self._files_cache.clear()
        self._git_files_loaded = False

    def invalidate_many(self, paths: Iterable[str | Path]) -> None:
        for p in paths:
            self.invalidate(p)

    def invalidate_all(self) -> None:
        self._file_facts.invalidate()
        self._resolved.clear()
        self._ast_cache.clear()
        self._nodes_cache.clear()
        self._bytes_cache.clear()
        self._text_cache.clear()
        self._frontmatter_cache.clear()
        self._links_cache.clear()
        self._catalog = None
        self._computed_cache.clear()
        self._files_cache.clear()
        self._git_files_loaded = False
