"""``RULE-document-summary``: documents carry a short English ``summary``, the main signal of document search.

``devkit docs search`` embeds a document's ID and ``summary``; titles and bodies may be in any language and are ranked
lexically only. A summary therefore has to exist where agents search and has to be English for the embedding model.

- Capabilities, use cases, decisions, architecture documents, proposals (``proposal.md``) and specs (``spec.md``) MUST
  have a ``summary``: a non-empty string. A file that still carries the skeleton marker (a spec just created by
  ``devkit spec new`` or a handoff) is exempt until it is written.
- Any ``summary``, required or not, MUST be English: no letter outside the Latin script (digits, punctuation and
  symbols are free), and at most ``max_length`` characters (setting, default 300), one or two sentences.

Current documents only (a completed bundle's files when explicitly targeted); materials are free-form and exempt. Not
fixable: a summary is written, never generated.
"""

from __future__ import annotations

from dataclasses import dataclass

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.base.layout import SKELETON_MARKER
from devkit_docs.features.documents import Document, Summary, definition
from devkit_docs.features.governance import document_index, field_line, is_material, reportable
from devkit_docs.utils.text import foreign_letters as foreign_letters

RULE_ID = "RULE-document-summary"
REMEDIATION = (
    "Write `summary:` in the frontmatter: one or two English sentences saying what the document defines"
    " (the title and body may stay in any language)"
)


@dataclass(frozen=True)
class DocumentSummarySettings:
    max_length: int = 300


def required(document: Document) -> bool:
    """Whether ``document``'s kind needs a summary (its ``summary`` in the kind table; a proposal or spec only for its
    anchor file)."""
    row = definition(document.kind)
    if row.summary is Summary.ANCHOR:
        return document.path.rsplit("/", 1)[-1] == row.anchor
    return row.summary is Summary.ALWAYS


class DocumentSummaryRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="document-summary",
            description="Searchable documents carry a short English summary, the main signal of document search.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=DocumentSummarySettings(),
            guide="guide.md",
            related=("docs:living-spec-writing",),
        )

    def validate_settings(self, settings: DocumentSummarySettings) -> None:
        if settings.max_length <= 0:
            raise ValueError("max_length must be a positive integer")

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        found: list[Violation] = []
        for document in index.documents:
            if is_material(document) or not reportable(ctx, index, document):
                continue
            problem = self._problem(ctx, document)
            if problem is not None:
                text = ctx.cache.read_text(document.path)
                line = field_line(text, "summary") if "summary" in document.frontmatter else 1
                found.append(
                    Violation(
                        rule_id=self.id,
                        file=document.path,
                        line=line,
                        message=problem,
                        remediation=REMEDIATION,
                    )
                )
        return found

    def _problem(self, ctx: RuleContext, document: Document) -> str | None:
        value = document.frontmatter.get("summary")
        if value is None:
            if not required(document) or SKELETON_MARKER in ctx.cache.read_text(document.path):
                return None
            return f"{document.id} has no summary"
        if not isinstance(value, str) or not value.strip():
            return "summary must be a non-empty string"
        letters = foreign_letters(value)
        if letters:
            return f"summary must be English; it contains {''.join(letters[:5])}"
        limit = ctx.settings(self, document.path).max_length
        if len(value.strip()) > limit:
            return f"summary has {len(value.strip())} characters; keep it to one or two sentences ({limit} at most)"
        return None
