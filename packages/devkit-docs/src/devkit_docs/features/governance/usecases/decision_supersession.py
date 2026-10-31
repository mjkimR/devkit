"""Report inconsistent whole and partial ADR supersession without rewriting decision records."""

from __future__ import annotations

import re
from collections.abc import Callable

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.features.documents import Document, DocumentIndex, is_id
from devkit_docs.features.documents.models.ids import ID_SOURCE
from devkit_docs.features.documents.models.markdown import visible_lines
from devkit_docs.features.governance import document_index, field_line

RULE_ID = "RULE-decision-supersession"
_PARTIAL = re.compile(rf"Superseded in part by `({ID_SOURCE})`")
type Add = Callable[[str, int], None]


def _adr(index: DocumentIndex, target: str) -> Document | None:
    found = index.canonical(target)
    return found[0] if found is not None and found[0].id.startswith("ADR-") else None


def _supersedes(document: Document) -> list[str]:
    value = document.frontmatter.get("supersedes", [])
    if isinstance(value, str):
        return [value]
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _partials(text: str) -> list[tuple[str, int]]:
    return [(match.group(1), line.number) for line in visible_lines(text) for match in _PARTIAL.finditer(line.text)]


class DecisionSupersessionRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="decision-supersession",
            description="ADR replacement metadata agrees with whole and partial supersession pointers.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            related=("docs:decision-writing",),
            inputs=("docs/**/*.md", "specs/**/*.md"),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        found: list[Violation] = []
        for document in index.documents:
            if not document.id.startswith("ADR-") or not ctx.is_file_targeted(document.path):
                continue
            text = ctx.cache.read_text(document.path)

            def add(message: str, line: int = 1, *, document: Document = document) -> None:
                found.append(
                    Violation(
                        rule_id=self.id,
                        file=document.path,
                        line=line,
                        message=message,
                        remediation="Align ADR status, superseded_by, supersedes and partial replacement pointers; retain accepted status for partial replacements",
                    )
                )

            self._whole(index, document, text, add)
            self._replacements(ctx, index, document, text, add)
        return found

    def _whole(self, index: DocumentIndex, document: Document, text: str, add: Add) -> None:
        value = document.frontmatter.get("superseded_by")
        line = field_line(text, "superseded_by")
        if "superseded_by" in document.frontmatter and document.status != "superseded":
            add("superseded_by is valid only with status superseded", line)
        if value is None and document.status != "superseded" and "superseded_by" not in document.frontmatter:
            return
        if not isinstance(value, str) or not is_id(value) or not value.startswith("ADR-"):
            add("superseded_by must name one ADR when status is superseded", line)
            return
        successor = _adr(index, value)
        if successor is None:
            add(f"superseded_by target {value} must resolve to one ADR", line)
        elif document.id not in {index.canonical_id(item) for item in _supersedes(successor)}:
            add(f"superseded_by target {value} does not list {document.id} in supersedes", line)

    def _replacements(self, ctx: RuleContext, index: DocumentIndex, document: Document, text: str, add: Add) -> None:
        value = document.frontmatter.get("supersedes", [])
        line = field_line(text, "supersedes")
        if not isinstance(value, (str, list)) or (
            isinstance(value, list) and any(not isinstance(v, str) for v in value)
        ):
            add("supersedes must be one ADR ID or a list of ADR IDs", line)
        for written in _supersedes(document):
            target = _adr(index, written) if is_id(written) and written.startswith("ADR-") else None
            if target is None:
                add(f"supersedes target {written!r} must resolve to one ADR", line)
                continue
            pointers = _partials(ctx.cache.read_text(target.path))
            if target.status != "superseded" and document.id not in {index.canonical_id(p) for p, _ in pointers}:
                add(
                    f"supersedes target {written} needs superseded status or a partial pointer naming {document.id}",
                    line,
                )
        for written, number in _partials(text):
            if document.status != "accepted":
                add("an ADR with a partial replacement pointer must stay accepted", number)
            successor = _adr(index, written)
            if successor is None:
                add(f"partial superseder {written} must resolve to one ADR", number)
            elif document.id not in {index.canonical_id(item) for item in _supersedes(successor)}:
                add(f"partial superseder {written} does not list {document.id} in supersedes", number)
