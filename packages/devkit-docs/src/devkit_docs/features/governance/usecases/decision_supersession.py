"""Report inconsistent whole and partial ADR supersession without rewriting decision records."""

from __future__ import annotations

import re
from collections.abc import Callable

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.features.documents import Document, DocumentIndex, is_id
from devkit_docs.features.documents.models.ids import ID_SOURCE
from devkit_docs.features.documents.models.supersession import replacement_texts, same_text, supersedes_ids
from devkit_docs.features.governance import document_index, field_line, is_material

RULE_ID = "RULE-decision-supersession"
_PARTIAL = re.compile(rf"Superseded in part by `({ID_SOURCE})`")
type Add = Callable[[str, int], None]


def _adr(index: DocumentIndex, target: str) -> Document | None:
    found = index.canonical(target)
    return found[0] if found is not None and found[0].id.startswith("ADR-") else None


def _supersedes(document: Document) -> list[str]:
    return supersedes_ids(document.frontmatter.get("supersedes"))


def _partials(text: str) -> list[tuple[str, int]]:
    return [(item.id, item.line) for item in replacement_texts(text) if item.pointer]


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
            if (
                is_material(document)
                or not document.id.startswith(("ADR-", "PADR-"))
                or not ctx.is_file_targeted(document.path)
            ):
                continue
            text = ctx.cache.read_text(document.path)

            def add(message: str, line: int = 1, *, document: Document = document) -> None:
                found.append(
                    Violation(
                        rule_id=self.id,
                        file=document.path,
                        line=line,
                        message=message,
                        remediation="Write one Supersedes in part `ADR-<old>`: <replaced clauses> statement per partial target and copy its text into one reciprocal pointer; align status and metadata",
                    )
                )

            self._statements(ctx, index, document, text, add)
            if document.id.startswith("ADR-"):
                self._whole(index, document, text, add)
                self._replacements(ctx, index, document, text, add)
        self._pointer_text(ctx, index, found)
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
            if document.status not in {"accepted", "superseded"}:
                add("an ADR with a partial replacement pointer must be accepted or wholly superseded", number)
            successor = _adr(index, written)
            if successor is None:
                add(f"partial superseder {written} must resolve to one ADR", number)
            elif document.id not in {index.canonical_id(item) for item in _supersedes(successor)}:
                add(f"partial superseder {written} does not list {document.id} in supersedes", number)

    def _statements(self, ctx: RuleContext, index: DocumentIndex, document: Document, text: str, add: Add) -> None:
        entries = [item for item in replacement_texts(text) if not item.pointer]
        targets = {index.canonical_id(item) for item in _supersedes(document)}
        seen: set[str] = set()
        for item in entries:
            canonical = index.canonical_id(item.id)
            if canonical not in targets:
                add(f"stray partial statement {item.id} is absent from supersedes", item.line)
            elif canonical in seen:
                add(f"duplicated partial statement for {item.id}", item.line)
            elif not item.text:
                add(f"empty partial statement for {item.id}", item.line)
            seen.add(canonical)
        for written in _supersedes(document):
            target = _adr(index, written)
            if target is not None and target.status != "superseded" and target.id not in seen:
                add(f"supersedes target {written} needs a partial statement", field_line(text, "supersedes"))

    def _pointer_text(self, ctx: RuleContext, index: DocumentIndex, found: list[Violation]) -> None:
        for successor in index.documents:
            if is_material(successor) or not successor.id.startswith("ADR-"):
                continue
            for statement in replacement_texts(ctx.cache.read_text(successor.path)):
                if statement.pointer or not statement.text:
                    continue
                earlier = _adr(index, statement.id)
                if earlier is None or earlier.status == "superseded":
                    continue
                if earlier.id not in {index.canonical_id(item) for item in _supersedes(successor)}:
                    continue
                old_targeted = ctx.is_file_targeted(earlier.path)
                if not old_targeted and not ctx.is_file_targeted(successor.path):
                    continue
                pointers = [
                    item
                    for item in replacement_texts(ctx.cache.read_text(earlier.path))
                    if item.pointer and index.canonical_id(item.id) == successor.id
                ]
                if not pointers or any(same_text(item.text, statement.text) for item in pointers):
                    continue
                # One mismatch per pair, even with duplicate statements.
                location = earlier.path if old_targeted else successor.path
                number = pointers[0].line if old_targeted else statement.line
                message = f"partial pointer for {earlier.id} and {successor.id} must repeat the statement text"
                if any(v.message == message for v in found):
                    continue
                found.append(
                    Violation(
                        rule_id=self.id,
                        file=location,
                        line=number,
                        message=message,
                        remediation="Copy the superseder's partial statement text verbatim into one earlier ADR pointer",
                    )
                )
