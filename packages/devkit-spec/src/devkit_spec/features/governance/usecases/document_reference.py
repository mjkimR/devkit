"""``RULE-document-reference``: documents reference each other by exact, resolvable full IDs.

Checks every current document that is not a material (``rules.is_material``):

- a relation field of the wrong shape, or holding something that is not a full ID, or an ID of the wrong kind
  (``stories`` and ``related_stories`` take ``US``, ``capabilities`` and ``related_capabilities`` ``CAP``, ``spec``
  ``SPEC``, ``plan`` ``PLAN``);
- a reference to an ID no document declares, or that several declare;
- a ``[ID]`` prose reference: the canonical form is `` `ID` `` (fixable);
- a ``PROP-<slug>`` reference after the proposal was handed off to the only ``SPEC-<slug>`` (fixable);
- a relative Markdown link to a document that has an ID;
- an ID declared by several documents, and a ``PROP-<slug>`` beside a ``SPEC-<slug>`` (handoff removes the
  proposal, so the pair is an unfinished handoff or a reused slug).

The fix converts ``[ID]`` to `` `ID` `` and rewrites handed-off proposal references, never the ``proposal``
provenance field, in current documents only (within the targets, when the run names any).
"""

from __future__ import annotations

import re
from collections.abc import Callable

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_spec.features.documents import Document, DocumentIndex, Reference, is_id
from devkit_spec.features.documents.models.ids import ID_SOURCE, Kind
from devkit_spec.features.documents.models.markdown import visible_lines
from devkit_spec.features.documents.models.model import is_unit_anchor
from devkit_spec.features.documents.services.dependencies import cycle_members, target_problem
from devkit_spec.features.documents.services.rewrite import rewrite
from devkit_spec.features.governance import FIX_COMMAND, document_index, is_material, reportable

RULE_ID = "RULE-document-reference"
type Add = Callable[..., None]
EXPECTED_PREFIX = {
    "stories": "US-",
    "related_stories": "US-",
    "capabilities": "CAP-",
    "related_capabilities": "CAP-",
    "spec": "SPEC-",
    "plan": "PLAN-",
    "milestone": "MS-",
    "depends_on": "MS-",
}


def _handed_off(index: DocumentIndex, target: str) -> str | None:
    """``SPEC-<slug>`` for an undeclared ``PROP-<slug>`` when exactly one such spec exists."""
    slug = target.removeprefix("PROP-")
    if slug == target or index.by_id.get(target) or len(index.by_id.get(f"SPEC-{slug}", [])) != 1:
        return None
    return f"SPEC-{slug}"


def _resolve_problem(index: DocumentIndex, target: str) -> str | None:
    declared = index.by_id.get(target, [])
    if len(declared) == 1:
        return None
    if not declared:
        return f"no document has the ID {target}"
    return f"{target} is declared by {len(declared)} documents: {', '.join(d.path for d in declared)}"


class DocumentReferenceRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="document-reference-check",
            description="Documents reference each other by exact, resolvable full IDs, written as `ID` in prose.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            related=("spec:living-spec-writing",),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        found: list[Violation] = []

        def add(
            document: Document, line: int, message: str, remediation: str, *, column: int = 0, fixable: bool = False
        ) -> None:
            found.append(
                Violation(
                    rule_id=self.id,
                    file=document.path,
                    line=line,
                    column=column,
                    message=message,
                    remediation=remediation,
                    fixable=fixable,
                )
            )

        for document_id, declared in sorted(index.by_id.items()):
            if len(declared) > 1:
                paths = ", ".join(d.path for d in declared)
                for document in declared:
                    if ctx.is_file_targeted(document.path):
                        add(
                            document,
                            1,
                            f"{document_id} is declared by {len(declared)} documents: {paths}",
                            "Give each document its own full ID, then update the references to it",
                        )
            slug = document_id.removeprefix("PROP-")
            spec = index.by_id.get(f"SPEC-{slug}") if slug != document_id else None
            if spec:
                for document in declared:
                    if ctx.is_file_targeted(document.path):
                        add(
                            document,
                            1,
                            f"{document_id} shares its slug with SPEC-{slug} ({spec[0].path});"
                            " a proposal and a spec cannot share a slug",
                            "Remove the proposal if it was already handed off, or rename it to an unused slug",
                        )
        for document in index.documents:
            if is_material(document) or not reportable(ctx, index, document):
                continue
            historical = index.is_historical(document)
            for issue in document.issues:
                add(document, issue.line, issue.message, "Use the documented relation field type")
            for ref in document.references:
                self._reference(index, document, ref, historical, add)
            for ref in document.provenance:
                if ref.field in {"decomposed_from", "supersedes"} and (
                    not is_id(ref.target) or not ref.target.startswith("PROP-")
                ):
                    add(
                        document,
                        ref.line,
                        f"{ref.field} takes PROP- IDs, got {ref.target!r}",
                        "Use the source proposal ID as provenance",
                    )
            self._links(ctx, index, document, add)
        graph = {
            d.id: [ref.target for ref in d.references if ref.field == "depends_on"]
            for d in index.documents
            if d.kind is Kind.MILESTONE
        }
        for document in index.documents:
            if document.id not in graph or not reportable(ctx, index, document):
                continue
            pending = list(graph[document.id])
            seen: set[str] = set()
            while pending:
                current = pending.pop()
                if current == document.id:
                    add(
                        document,
                        1,
                        f"milestone dependency cycle includes {document.id}",
                        "Remove a depends_on edge to break the cycle",
                    )
                    break
                if current not in seen:
                    seen.add(current)
                    pending.extend(graph.get(current, []))
        cyclic = cycle_members(index)
        for document in index.documents:
            if document.id in cyclic and reportable(ctx, index, document):
                add(
                    document,
                    1,
                    f"unit dependency cycle includes {document.id}",
                    "Remove a depends_on edge to break the cycle",
                )
        found.extend(self._glossary(ctx, index))
        return found

    def _reference(self, index: DocumentIndex, document: Document, ref: Reference, historical: bool, add: Add) -> None:
        if not is_id(ref.target):
            add(
                document,
                ref.line,
                f"{ref.field} must contain a full document ID, got {ref.target!r}",
                "Replace the value with the target document's ID",
                column=ref.column,
            )
            return
        if ref.field == "depends_on" and is_unit_anchor(document):
            problem = target_problem(index, ref.target)
            if problem is not None:
                replacement = _handed_off(index, ref.target)
                if replacement and not historical and target_problem(index, replacement) is None:
                    add(
                        document,
                        ref.line,
                        f"{ref.target} was handed off; reference `{replacement}`",
                        f"Run `{FIX_COMMAND}` to replace it with {replacement}",
                        fixable=True,
                    )
                else:
                    add(document, ref.line, problem, "Use one exact proposal/spec anchor ID")
            return
        prefix = EXPECTED_PREFIX.get(ref.field)
        if prefix and not ref.target.startswith(prefix):
            add(
                document,
                ref.line,
                f"{ref.field} takes {prefix} IDs, got {ref.target}",
                "Use an ID of the document kind the field takes",
                column=ref.column,
            )
            return
        if ref.bracket and not historical:
            add(
                document,
                ref.line,
                f"prose reference {ref.target} must be written `{ref.target}`, not [{ref.target}]",
                f"Run `{FIX_COMMAND}` to convert it to backticks",
                column=ref.column,
                fixable=True,
            )
        problem = _resolve_problem(index, ref.target)
        if problem is None:
            return
        spec = _handed_off(index, ref.target)
        if spec is not None and not historical:
            add(
                document,
                ref.line,
                f"{ref.target} was handed off; reference `{spec}`",
                f"Run `{FIX_COMMAND}` to replace it with {spec}",
                column=ref.column,
                fixable=True,
            )
            return
        add(document, ref.line, problem, "Create the intended document or correct the exact ID", column=ref.column)

    def _links(self, ctx: RuleContext, index: DocumentIndex, document: Document, add: Add) -> None:
        by_path = {d.path: d for d in index.documents}
        lines = ctx.cache.read_text(document.path).split("\n")
        base = document.path.rsplit("/", 1)[0]
        for link in ctx.cache.get_links(document.path):
            line_text = lines[link.line - 1] if 0 < link.line <= len(lines) else ""
            target = link.target
            if link.start > 0 and line_text[link.start - 1 : link.start] == "!":
                continue
            if any(char in target for char in "#?:") or target.startswith("/"):
                continue
            resolved = _normalize(f"{base}/{target}")
            destination = by_path.get(resolved) if resolved else None
            if destination is not None:
                add(
                    document,
                    link.line,
                    f"internal document link {target} must be the ID `{destination.id}`",
                    f"Replace the Markdown link with `{destination.id}`",
                    column=link.start + 1,
                )

    def _glossary(self, ctx: RuleContext, index: DocumentIndex) -> list[Violation]:
        """Resolve only Owner references in the ID-free root glossary's five-column tables."""
        path = "docs/glossary.md"
        if not ctx.is_file_targeted(path):
            return []
        # find_files honors snapshot contents, exclusions and symlink policy; never read the live tree directly.
        if ctx.workspace_root / path not in ctx.cache.find_files(ctx.workspace_root / "docs", extensions=(".md",)):
            return []
        text = ctx.cache.read_text_strict(path)
        if text is None:
            return []
        found: list[Violation] = []
        state, previous = "", 0
        for line in visible_lines(text):
            if line.number != previous + 1:
                state = ""
            previous = line.number
            cells = line.text.strip().removeprefix("|").removesuffix("|").split("|")
            cells = [cell.strip() for cell in cells]
            if cells == ["Term", "Definition", "Owner", "Avoid", "Code identifiers"]:
                state = "header"
                continue
            if state == "header":
                state = "rows" if len(cells) == 5 and all(re.fullmatch(r":?-{3,}:?", c) for c in cells) else ""
                continue
            if state != "rows" or "|" not in line.text:
                state = ""
                continue
            # Markdown rows may omit trailing cells or include surplus ones; the header fixes Owner at column 3.
            owner = cells[2] if len(cells) > 2 else ""
            for match in re.finditer(rf"`({ID_SOURCE})`|\[({ID_SOURCE})\]", owner):
                target = match.group(1) or match.group(2)
                problem = _resolve_problem(index, target)
                if problem:
                    found.append(
                        Violation(
                            rule_id=self.id,
                            file=path,
                            line=line.number,
                            message=problem,
                            remediation="Correct the glossary Owner ID or give its intended document a unique ID",
                        )
                    )
        return found

    def fix(self, ctx: RuleContext) -> list[str]:
        index = document_index(ctx)
        changed: list[str] = []
        for document in index.documents:
            if is_material(document) or index.is_historical(document) or not ctx.is_file_targeted(document.path):
                continue
            mapping: dict[str, str] = {}
            for ref in document.references:
                spec = _handed_off(index, ref.target)
                if spec is not None:
                    if ref.field == "depends_on" and is_unit_anchor(document) and target_problem(index, spec):
                        continue
                    mapping[ref.target] = spec
                elif ref.bracket:
                    mapping.setdefault(ref.target, ref.target)
            if not mapping:
                continue
            text = ctx.cache.read_text_strict(document.path)
            if text is None:
                continue
            updated = rewrite(text, document.references, mapping)
            if updated != text:
                ctx.cache.write_text(document.path, updated, dry_run=ctx.dry_run)
                changed.append(document.path)
        return changed


def _normalize(path: str) -> str | None:
    """``path`` with ``.`` and ``..`` segments resolved; ``None`` when it leaves the workspace."""
    parts: list[str] = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)
