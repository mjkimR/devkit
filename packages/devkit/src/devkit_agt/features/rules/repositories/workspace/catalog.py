from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from devkit_core.core import FrontmatterError

if TYPE_CHECKING:
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache


@dataclass(slots=True)
class Document:
    id: str
    path: str  # workspace-relative path
    title: str = ""
    status: str = ""


class DocumentCatalog:
    """Index of the Markdown files in a workspace: paths, basenames and frontmatter identity.

    The catalog knows nothing about a document model. A frontmatter ``id`` is recorded
    verbatim when present; identifier grammars, reference extraction and relationship
    checks belong to the rules of the bundle that defines the documents.

    The basename index never reads frontmatter. The identity index
    (``documents_by_id``, ``documents_by_path``, ``duplicate_ids``) parses each
    file's frontmatter on first use; a file whose frontmatter cannot be parsed
    is left out and its problem is recorded in ``frontmatter_errors`` instead of
    failing the run, so one malformed document never stops rules that only need
    paths.
    """

    def __init__(self) -> None:
        self.files_by_basename: dict[str, list[str]] = {}
        self._root: Path | None = None
        self._cache: WorkspaceCache | None = None
        self._files: list[Path] = []
        self._identity_built = False
        self._documents_by_id: dict[str, Document] = {}
        self._documents_by_path: dict[str, Document] = {}
        self._duplicate_ids: dict[str, list[str]] = {}
        self._frontmatter_errors: dict[str, str] = {}

    def build(self, workspace_root: Path, cache: WorkspaceCache) -> None:
        self._root = workspace_root.resolve()
        self._cache = cache
        self._files = cache.find_files(self._root, extensions=(".md",))
        self._identity_built = False
        self.files_by_basename = {}
        for file_path in self._files:
            rel_path = file_path.relative_to(self._root).as_posix()
            self.files_by_basename.setdefault(file_path.name, []).append(rel_path)

    def _build_identity(self) -> None:
        if self._identity_built:
            return
        self._identity_built = True
        self._documents_by_id = {}
        self._documents_by_path = {}
        self._duplicate_ids = {}
        self._frontmatter_errors = {}
        if self._root is None or self._cache is None:
            return
        for file_path in self._files:
            rel_path = file_path.relative_to(self._root).as_posix()
            try:
                fm = self._cache.get_frontmatter(file_path)
            except FrontmatterError as exc:
                self._frontmatter_errors[rel_path] = str(exc)
                continue
            if not fm:
                continue
            doc_id = str(fm.get("id") or "").strip()
            if not doc_id:
                continue
            doc = Document(
                id=doc_id,
                path=rel_path,
                title=str(fm.get("title") or "").strip(),
                status=str(fm.get("status") or "").strip(),
            )
            self._documents_by_path[rel_path] = doc
            if doc_id in self._documents_by_id:
                existing = self._documents_by_id[doc_id]
                self._duplicate_ids.setdefault(doc_id, [existing.path]).append(rel_path)
            else:
                self._documents_by_id[doc_id] = doc

    @property
    def documents_by_id(self) -> dict[str, Document]:
        self._build_identity()
        return self._documents_by_id

    @property
    def documents_by_path(self) -> dict[str, Document]:
        self._build_identity()
        return self._documents_by_path

    @property
    def duplicate_ids(self) -> dict[str, list[str]]:
        """IDs declared by more than one file, with every declaring path in path order."""
        self._build_identity()
        return self._duplicate_ids

    @property
    def frontmatter_errors(self) -> dict[str, str]:
        """Workspace-relative path to the reason its frontmatter could not be parsed."""
        self._build_identity()
        return self._frontmatter_errors

    def find_paths_by_basename(self, basename: str) -> list[str]:
        return self.files_by_basename.get(basename, [])
