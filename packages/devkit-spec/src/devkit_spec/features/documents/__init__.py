"""devkit_spec.features.documents: the document model of spec-driven development.

IDs (``ids``), documents and references (``model``), the parser
(``parse_document``), the Markdown body scanner (``markdown``) and the
workspace index (``DocumentIndex``). Contract: ``CAP-DOCS-document-model`` (``docs/capabilities/documents/``).
"""

from devkit_spec.features.documents.models.ids import ID_PATTERN, PREFIXES, Kind, is_id, kind_of
from devkit_spec.features.documents.models.markdown import VisibleLine, visible_lines
from devkit_spec.features.documents.models.model import Document, Issue, Reference
from devkit_spec.features.documents.models.parse import parse_document
from devkit_spec.features.documents.repositories.index import (
    SOURCE_DIRECTORIES,
    DocumentIndex,
    in_feedback,
    in_source_directory,
    is_document_file,
)
from devkit_spec.features.documents.services.rewrite import rewrite

__all__ = [
    "ID_PATTERN",
    "PREFIXES",
    "SOURCE_DIRECTORIES",
    "Document",
    "DocumentIndex",
    "Issue",
    "Kind",
    "Reference",
    "VisibleLine",
    "in_feedback",
    "in_source_directory",
    "is_document_file",
    "is_id",
    "kind_of",
    "parse_document",
    "rewrite",
    "visible_lines",
]
