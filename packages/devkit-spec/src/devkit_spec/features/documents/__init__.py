"""devkit_spec.features.documents: the document model of spec-driven development.

IDs (``ids``), the kind definition table (``kinds``), documents and references (``model``), the parser
(``parse_document``), the Markdown body scanner (``markdown``) and the
workspace index (``DocumentIndex``). Contract: ``CAP-DOCS-document-model`` (``docs/capabilities/documents/``).
"""

from devkit_spec.features.documents.models.ids import PREFIXES, Kind, is_id, kind_of
from devkit_spec.features.documents.models.kinds import (
    FormatScope,
    KindTableError,
    Summary,
    by_prefix,
    definition,
    definitions,
    relation_prefixes,
)
from devkit_spec.features.documents.models.markdown import VisibleLine, visible_lines
from devkit_spec.features.documents.models.model import Document, Issue, Reference
from devkit_spec.features.documents.models.parse import parse_document
from devkit_spec.features.documents.repositories.index import (
    SOURCE_DIRECTORIES,
    TERMINAL_STATUSES,
    DocumentIndex,
    in_feedback,
    in_source_directory,
    is_document_file,
)
from devkit_spec.features.documents.services.rewrite import rewrite

__all__ = [
    "PREFIXES",
    "SOURCE_DIRECTORIES",
    "TERMINAL_STATUSES",
    "Document",
    "DocumentIndex",
    "FormatScope",
    "Issue",
    "Kind",
    "KindTableError",
    "Reference",
    "Summary",
    "VisibleLine",
    "by_prefix",
    "definition",
    "definitions",
    "in_feedback",
    "in_source_directory",
    "is_document_file",
    "is_id",
    "kind_of",
    "parse_document",
    "relation_prefixes",
    "rewrite",
    "visible_lines",
]
