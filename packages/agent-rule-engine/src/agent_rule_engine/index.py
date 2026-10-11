from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_rule_engine.cache import WorkspaceCache

ID_PATTERN = re.compile(r"^(CAP|US|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT)-[A-Za-z0-9][A-Za-z0-9_-]*$")
DOC_ID_EXTRACTOR = re.compile(
    r"\b((?:CAP|US|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT)-[A-Za-z0-9][A-Za-z0-9_-]*)\b"
)


def is_valid_doc_id(val: str) -> bool:
    return bool(ID_PATTERN.match(val))


@dataclass(slots=True)
class Document:
    id: str
    path: str  # workspace-relative path
    title: str = ""
    status: str = ""
    line: int = 1
    references: list[str] = field(default_factory=list)


class DocumentCatalog:
    """Catalog of all indexed specification and governance documents in the workspace."""

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

        # Target documentation directories
        target_subdirs = ("docs", "specs")
        files = cache.find_files(workspace_root, extensions=(".md",), subdirs=target_subdirs)

        for file_path in files:
            rel_path = file_path.relative_to(workspace_root).as_posix()
            basename = file_path.name
            self.files_by_basename.setdefault(basename, []).append(rel_path)

            fm, body, _ = cache.get_frontmatter(file_path)
            doc_id = ""
            title = ""
            status = ""

            if fm:
                doc_id = str(fm.get("id") or "").strip()
                title = str(fm.get("title") or "").strip()
                status = str(fm.get("status") or "").strip()

            # Find references mentioned in body or frontmatter
            refs = list(set(DOC_ID_EXTRACTOR.findall(body)))

            if doc_id:
                doc = Document(
                    id=doc_id,
                    path=rel_path,
                    title=title,
                    status=status,
                    references=refs,
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
