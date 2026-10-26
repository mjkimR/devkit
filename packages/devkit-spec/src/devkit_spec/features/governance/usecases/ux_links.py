"""``RULE-ux-links``: a UX document and the use cases it serves do not contradict each other
(``ADR-ux-step-links-and-coverage``).

Over every current UX document (kind ``ux``; parsing in ``governance.services.ux``) it reports:

- a missing ``element``, or one other than ``screen``, ``modal`` or ``panel``;
- a missing ``Interactions`` H2, or one without a table whose header is
  ``Trigger | Step | From | To | Target | Capability | Feedback``;
- a Step cell that is neither empty nor `` `UC-<slug>` <key> `` pairs; a pair naming a use case ``usecases`` does
  not list, a key the use case has no step for, or a step that does not cite the document;
- a ``usecases`` entry no Step cell names;
- a Target cell that is neither empty, a UX document's ID, ``close``, ``back`` nor ``end``;
- a ``modal`` without a ``close`` or ``back`` row;
- per listed use case whose steps cite it: a ``screen`` without an exit that no terminal step cites, and a ``screen``
  or ``modal`` not reachable from the use case's entries (panels are exempt from both);
- a use case step citing the document while its ``usecases`` does not list the use case.

A finding that concerns a use case too is reported on the UX document, or on the use case (at the step's line) when
only the use case is in the run, as ``RULE-traceability-link`` does for its targeted side. A use case or ID that does
not resolve is ``RULE-document-reference``'s and is skipped here. Nothing is fixable.
"""

from __future__ import annotations

from collections.abc import Callable

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_spec.features.documents import Document
from devkit_spec.features.governance import document_index, reportable
from devkit_spec.features.governance.services.ux import ELEMENTS, Model, UseCase, UxDocument, model

RULE_ID = "RULE-ux-links"
COLUMNS = "Trigger | Step | From | To | Target | Capability | Feedback"
type Add = Callable[..., None]


class UxLinksRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="ux-link-check",
            description=(
                "UX documents declare a valid element and Interactions table, and their Step cells, usecases lists,"
                " targets, exits and reachability agree with the use case steps that cite them."
            ),
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            related=("spec:ux-writing", "spec:usecase-writing"),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        found: list[Violation] = []

        def violation(document: Document, line: int, message: str, remediation: str) -> None:
            found.append(
                Violation(rule_id=self.id, file=document.path, line=line, message=message, remediation=remediation)
            )

        def add(
            screen: UxDocument,
            line: int,
            message: str,
            remediation: str,
            *,
            usecase: Document | None = None,
            usecase_line: int = 1,
        ) -> None:
            if reportable(ctx, index, screen.document):
                violation(screen.document, line, message, remediation)
            elif usecase is not None and reportable(ctx, index, usecase):
                violation(usecase, usecase_line, f"{message} ({screen.document.path})", remediation)

        flows = model(index, ctx.cache.read_text_strict)
        for screen in flows.screens.values():
            _own(screen, add)
            _links(flows, screen, add)
            _flow(flows, screen, add)
        return sorted(found, key=lambda v: (v.file, v.line, v.message))


def _own(screen: UxDocument, add: Add) -> None:
    """What the UX document alone decides: its element, its table, its cells and a modal's close."""
    element = screen.element
    if element is None:
        add(screen, 1, "element is missing; set screen, modal or panel", "Add element: screen, modal or panel")
    elif element not in ELEMENTS:
        add(screen, 1, f'element "{element}" is not screen, modal or panel', "Set element to screen, modal or panel")
    if not screen.section:
        add(screen, 1, "no Interactions section", f"Add an ## Interactions section with the table {COLUMNS}")
    elif not screen.table:
        add(
            screen,
            screen.section,
            f"Interactions has no table with the columns {COLUMNS}",
            f"Write the Interactions table with exactly the header {COLUMNS}",
        )
    for row in screen.rows:
        if not row.step_valid:
            add(
                screen,
                row.line,
                f'Step cell "{row.step_cell}" is not `UC-<slug>` <key>',
                "Write the served step as `UC-<slug>` <key> (for example `UC-sign-in` 2a), or leave the cell empty",
            )
        if not row.target_valid:
            add(
                screen,
                row.line,
                f'Target "{row.target_cell}" is not a UX document, close, back or end',
                "Name the UX ID of the element the interaction opens, close, back or end; leave it empty to stay",
            )
    if element == "modal" and not screen.closes():
        add(
            screen,
            screen.table or 1,
            "modal has no close or back interaction",
            "Add an interaction whose Target is close or back",
        )


def _links(flows: Model, screen: UxDocument, add: Add) -> None:
    """Step cells and ``usecases`` against the use case steps, both directions."""
    named: set[str] = set()
    for row in screen.rows:
        for ref in row.steps:
            named.add(ref.usecase)
            usecase = flows.usecases.get(ref.usecase)
            if usecase is None:
                continue  # an unresolved use case is RULE-document-reference's
            if not screen.lists(ref.usecase):
                add(
                    screen,
                    row.line,
                    f"Step names {ref.usecase}, which usecases does not list",
                    f"Add {ref.usecase} to usecases, or name a listed use case",
                    usecase=usecase.document,
                )
                continue
            step = usecase.step(ref.key)
            if step is None:
                add(
                    screen,
                    row.line,
                    f"Step names {ref.usecase} {ref.key}, which is not a step of {ref.usecase}",
                    f"Name a step or extension key of {ref.usecase} (renumbered steps change their keys)",
                    usecase=usecase.document,
                )
            elif screen.id not in step.screens:
                add(
                    screen,
                    row.line,
                    f"Step names {ref.usecase} {ref.key}, which does not cite {screen.id}",
                    f"Cite `{screen.id}` in step {ref.key} of {ref.usecase}, or name the step that happens here",
                    usecase=usecase.document,
                    usecase_line=step.line,
                )
    for listed, line in screen.usecases:
        usecase = flows.usecases.get(listed)
        if usecase is not None and listed not in named:
            add(
                screen,
                line,
                f"usecases lists {listed}, but no Step cell names it",
                f"Name the {listed} step each interaction serves in its Step cell, or remove {listed} from usecases",
                usecase=usecase.document,
            )
    for usecase in flows.usecases.values():
        if screen.lists(usecase.document.id):
            continue
        for step in usecase.citing(screen.id):
            add(
                screen,
                1,
                f"{usecase.document.id} step {step.key} cites {screen.id}, whose usecases does not list"
                f" {usecase.document.id}",
                f"Add {usecase.document.id} to the usecases of {screen.document.path}",
                usecase=usecase.document,
                usecase_line=step.line,
            )


def _served(flows: Model, screen: UxDocument) -> list[UseCase]:
    """The listed use cases whose steps cite ``screen``."""
    found: list[UseCase] = []
    for listed, _ in screen.usecases:
        usecase = flows.usecases.get(listed)
        if usecase is not None and usecase.citing(screen.id) and usecase not in found:
            found.append(usecase)
    return found


def _flow(flows: Model, screen: UxDocument, add: Add) -> None:
    """Exits and reachability per listed use case; panels are exempt."""
    if screen.element not in ("screen", "modal"):
        return
    for usecase in _served(flows, screen):
        steps = usecase.citing(screen.id)
        line = steps[0].line
        if screen.element == "screen" and not screen.has_exit() and not any(usecase.terminal(s) for s in steps):
            add(
                screen,
                screen.table or 1,
                f"screen has no exit in {usecase.document.id}",
                "Add an interaction whose Target is another UX document, close, back or end",
                usecase=usecase.document,
                usecase_line=line,
            )
        if screen.id not in flows.reachable(usecase):
            add(
                screen,
                1,
                f"{screen.id} is not reachable from an entry of {usecase.document.id}",
                f"Add an interaction that targets {screen.id} to the screen of the step before, or cite the screens"
                f" of {usecase.document.id} in step order",
                usecase=usecase.document,
                usecase_line=line,
            )
