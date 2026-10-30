"""``RULE-document-reference``: documents reference each other by exact, resolvable full IDs.

Checks every current document that is not a material (``rules.is_material``):

- a relation field of the wrong shape, or holding something that is not a full ID, or an ID of the wrong kind
  (``usecases`` and ``related_usecases`` take ``UC``, ``capabilities`` and ``related_capabilities`` ``CAP``, ``spec``
  ``SPEC``, ``plan`` ``PLAN``);
- a reference to an ID no document declares, or that several declare;
- a ``[ID]`` prose reference: the canonical form is `` `ID` `` (fixable);
- a ``PROP-<slug>`` reference after the proposal was handed off to the only ``SPEC-<slug>`` (fixable); in work history
  (``DocumentIndex.is_historical``) such a reference was valid when written and is accepted silently;
- a reference written with another document's alias (fixable), decision records (``ADR``, ``PADR``) included; a
  document mentioning its own alias is not reported;
- a relative Markdown link to a document that has an ID;
- an ID declared by several documents, and a ``PROP-<slug>`` beside a ``SPEC-<slug>`` or a ``SPEC-<slug>`` alias
  (handoff removes the proposal, so the pair is an unfinished handoff or a reused slug);
- identity checks over every targeted document, materials and completed specs included: a malformed ``aliases``
  field, and an alias that another document declares as its ID or that several documents declare;
- in the ID-free steering files (the Markdown files directly in ``docs/steering/`` other than ``README.md``), every
  backtick-quoted ID must resolve and must not be an alias, and the Owner cells of the five-column tables of
  ``docs/steering/glossary.md`` likewise; neither is fixed or added to the reference graph.

References resolve through ``DocumentIndex.canonical``: a declared ID always wins, an alias only when exactly one
document declares it. The fix converts ``[ID]`` to `` `ID` ``, rewrites handed-off proposal references to the
canonical spec and alias references to the canonical ID, never the ``proposal`` provenance field, in current
documents only (within the targets, when the run names any).
"""

from __future__ import annotations

import re
from collections.abc import Callable

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.features.documents import Document, DocumentIndex, Reference, is_id, relation_prefixes
from devkit_docs.features.documents.models.ids import ID_SOURCE, Kind
from devkit_docs.features.documents.models.markdown import visible_lines
from devkit_docs.features.documents.models.model import is_unit_anchor
from devkit_docs.features.documents.services.dependencies import cycle_members, target_problem
from devkit_docs.features.documents.services.rewrite import rewrite
from devkit_docs.features.governance import FIX_COMMAND, document_index, is_material, reportable

RULE_ID = "RULE-document-reference"
STEERING = "docs/steering"
GLOSSARY = f"{STEERING}/glossary.md"
_CITED = re.compile(rf"(?<!`)`({ID_SOURCE})`(?!`)")
type Add = Callable[..., None]


def _handed_off(index: DocumentIndex, target: str) -> str | None:
    """The canonical ID of the one ``SPEC-<slug>`` (declared or an alias) for a ``PROP-<slug>`` no document declares,
    so one fix pass converges."""
    slug = target.removeprefix("PROP-")
    if slug == target or index.declares(target):
        return None
    spec = index.canonical(f"SPEC-{slug}")
    return spec[0].id if spec is not None else None


def _resolve_problem(index: DocumentIndex, target: str) -> str | None:
    if index.canonical(target) is not None:
        return None
    declared = index.by_id.get(target, [])
    if declared:
        return f"{target} is declared by {len(declared)} documents: {', '.join(d.path for d in declared)}"
    aliased = index.by_alias.get(target, [])
    if aliased:
        return f"{target} is an alias declared by {len(aliased)} documents: {', '.join(d.path for d in aliased)}"
    return f"no document has the ID {target}"


def _alias_target(index: DocumentIndex, document: Document, target: str) -> str | None:
    """The canonical ID when ``target`` is a resolving alias of another document, else ``None``."""
    found = index.canonical(target)
    if found is None or found[1] is None or found[0] is document:
        return None
    return found[0].id


class DocumentReferenceRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="document-reference-check",
            description="Documents reference each other by exact, resolvable full IDs, written as `ID` in prose.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            related=("docs:living-spec-writing",),
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
            spec = index.declares(f"SPEC-{slug}") if slug != document_id else None
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
        self._identity(ctx, index, add)
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
            d.id: [index.canonical_id(ref.target) for ref in d.references if ref.field == "depends_on"]
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
        owners, examined = self._glossary(ctx, index)
        found.extend(owners)
        found.extend(self._steering(ctx, index, examined))
        return found

    def _identity(self, ctx: RuleContext, index: DocumentIndex, add: Add) -> None:
        """Alias shape issues and alias collisions, on every targeted document (materials and history included)."""
        for document in index.documents:
            if ctx.is_file_targeted(document.path):
                for issue in document.alias_issues:
                    add(
                        document, issue.line, issue.message, "Declare previous IDs of this document with its own prefix"
                    )
        for alias, involved in index.alias_collisions():
            unique = list({d.path: d for d in involved}.values())
            paths = ", ".join(d.path for d in unique)
            for document in unique:
                if ctx.is_file_targeted(document.path):
                    add(
                        document,
                        1,
                        f"alias {alias} collides: it is declared by {paths}",
                        "Keep the ID or alias on one document only; a declared ID always wins over an alias",
                    )

    def _alias(self, index: DocumentIndex, document: Document, ref: Reference, historical: bool, add: Add) -> None:
        canonical = _alias_target(index, document, ref.target)
        if canonical is None or historical:
            return
        add(
            document,
            ref.line,
            f"{ref.target} is an alias of {canonical}; reference `{canonical}`",
            f"Run `{FIX_COMMAND}` to replace it with {canonical}",
            column=ref.column,
            fixable=True,
        )

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
                if replacement and target_problem(index, replacement) is None:
                    if historical:
                        return
                    add(
                        document,
                        ref.line,
                        f"{ref.target} was handed off; reference `{replacement}`",
                        f"Run `{FIX_COMMAND}` to replace it with {replacement}",
                        fixable=True,
                    )
                else:
                    add(document, ref.line, problem, "Use one exact proposal/spec anchor ID")
            else:
                self._alias(index, document, ref, historical, add)
            return
        prefix = relation_prefixes().get(ref.field)
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
            self._alias(index, document, ref, historical, add)
            return
        spec = _handed_off(index, ref.target)
        if spec is not None:
            if historical:
                return
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

    def _glossary(self, ctx: RuleContext, index: DocumentIndex) -> tuple[list[Violation], set[tuple[int, str]]]:
        """Resolve only Owner references in the ID-free root glossary's five-column tables; also return the
        ``(line, ID)`` pairs examined, which the steering pass does not report again."""
        path = GLOSSARY
        if not ctx.is_file_targeted(path):
            return [], set()
        # find_files honors snapshot contents, exclusions and symlink policy; never read the live tree directly.
        if ctx.workspace_root / path not in ctx.cache.find_files(ctx.workspace_root / STEERING, extensions=(".md",)):
            return [], set()
        text = ctx.cache.read_text_strict(path)
        if text is None:
            return [], set()
        found: list[Violation] = []
        examined: set[tuple[int, str]] = set()
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
                examined.add((line.number, target))
                problem = _resolve_problem(index, target)
                if problem is None and (canonical := index.canonical_id(target)) != target:
                    problem = f"Owner {target} is an alias of {canonical}; name `{canonical}`"
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
        return found, examined

    def _steering(self, ctx: RuleContext, index: DocumentIndex, examined: set[tuple[int, str]]) -> list[Violation]:
        """Resolve the backtick-quoted IDs of the ID-free steering files, without fixes or graph edges."""
        found: list[Violation] = []
        for file in ctx.cache.find_files(ctx.workspace_root / STEERING, extensions=(".md",)):
            path = ctx.relative_path(file)
            if path is None or path.rsplit("/", 1)[0] != STEERING or path.endswith("/README.md"):
                continue
            if not ctx.is_file_targeted(path):
                continue
            text = ctx.cache.read_text_strict(path)
            if text is None:
                continue
            for line in visible_lines(text):
                for match in _CITED.finditer(line.text):
                    target = match.group(1)
                    if (line.number, target) in examined:
                        continue
                    problem = _resolve_problem(index, target)
                    if problem is None and (canonical := index.canonical_id(target)) != target:
                        problem = f"{target} is an alias of {canonical}; name `{canonical}`"
                    if problem:
                        found.append(
                            Violation(
                                rule_id=self.id,
                                file=path,
                                line=line.number,
                                column=match.start() + 1,
                                message=problem,
                                remediation="Correct the cited ID or give its intended document a unique ID",
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
                if spec is None:
                    spec = _alias_target(index, document, ref.target)
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
