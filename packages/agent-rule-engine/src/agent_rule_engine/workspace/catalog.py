from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_rule_engine.workspace.cache import WorkspaceCache


@dataclass(slots=True)
class Document:
    id: str
    path: str  # workspace-relative path
    title: str = ""
    status: str = ""
    line: int = 1


class DocumentCatalog:
    """Index of the Markdown files in a workspace: paths, basenames and frontmatter identity.

    The catalog knows nothing about a document model. A frontmatter ``id`` is recorded
    verbatim when present; identifier grammars, reference extraction and relationship
    checks belong to the rules of the bundle that defines the documents.
    """

    def __init__(self) -> None:
        self.documents_by_id: dict[str, Document] = {}
        self.documents_by_path: dict[str, Document] = {}
        self.files_by_basename: dict[str, list[str]] = {}
        self.duplicate_ids: dict[str, list[str]] = {}

    def build(self, workspace_root: Path, cache: WorkspaceCache) -> None:
        self.documents_by_id.clear()
        self.documents_by_path.clear()
        self.files_by_basename.clear()
        self.duplicate_ids.clear()

        for file_path in cache.find_files(workspace_root, extensions=(".md",)):
            rel_path = file_path.relative_to(workspace_root).as_posix()
            self.files_by_basename.setdefault(file_path.name, []).append(rel_path)

            fm, _, _ = cache.get_frontmatter(file_path)
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
            self.documents_by_path[rel_path] = doc
            if doc_id in self.documents_by_id:
                existing = self.documents_by_id[doc_id]
                self.duplicate_ids.setdefault(doc_id, [existing.path]).append(rel_path)
            else:
                self.documents_by_id[doc_id] = doc

    def has_id(self, doc_id: str) -> bool:
        return doc_id in self.documents_by_id

    def get_doc(self, doc_id: str) -> Document | None:
        return self.documents_by_id.get(doc_id)

    def find_paths_by_basename(self, basename: str) -> list[str]:
        return self.files_by_basename.get(basename, [])
