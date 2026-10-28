"""``RULE-ux-coverage``: the steps of a use case a UX document serves, and the UX document's interactions, are
linked (``ADR-ux-step-links-and-coverage``).

For every use case some current UX document lists in ``usecases`` (parsing in ``governance.services.ux``), it
reports each main-scenario step and extension that cites no UX ID, once: on the first UX document listing the use
case that the run reports (path order, at its ``usecases`` entry), else on the use case at the step's line. It also
reports, on its UX document, each Interactions row whose Step cell is empty. A step may legitimately happen off
screen (a mail sent, a background job), so the rule is a ``warning``, as ``RULE-spec-progress`` is; contradictions
are ``RULE-ux-links``'s. A use case no UX document lists is never reported. Nothing is fixable.
"""

from __future__ import annotations

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.features.documents import Document
from devkit_docs.features.governance import document_index, reportable
from devkit_docs.features.governance.services.ux import model

RULE_ID = "RULE-ux-coverage"


class UxCoverageRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="ux-coverage-check",
            description=(
                "Every step of a use case a UX document serves cites a UX document, and every interaction names the"
                " step it serves (warning)."
            ),
            phase=Phase.LINTER,
            severity=Severity.WARNING,
            guide="guide.md",
            related=("docs:ux-writing", "docs:usecase-writing"),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        index = document_index(ctx)
        flows = model(index, ctx.cache.read_text_strict)
        found: list[Violation] = []

        def add(path: str, line: int, message: str, remediation: str) -> None:
            found.append(Violation(rule_id=self.id, file=path, line=line, message=message, remediation=remediation))

        listing: dict[str, list[tuple[str, int, Document]]] = {}
        for screen in flows.screens.values():
            for listed, line in screen.usecases:
                listing.setdefault(listed, []).append((screen.document.path, line, screen.document))
            if reportable(ctx, index, screen.document):
                for row in screen.rows:
                    if row.step_empty:
                        add(
                            screen.document.path,
                            row.line,
                            "interaction has no Step",
                            "Name the use case step it serves as `UC-<slug>` <key>; a global control may stay empty",
                        )
        for usecase_id, places in sorted(listing.items()):
            usecase = flows.usecases.get(usecase_id)
            if usecase is None:
                continue
            reported = [
                (path, line)
                for path, line, document in sorted(places, key=lambda place: (place[0], place[1]))
                if reportable(ctx, index, document)
            ]
            for step in usecase.steps:
                if step.screens:
                    continue
                message = f"{usecase_id} step {step.key} cites no UX document"
                remediation = (
                    f"Cite the UX ID of the screen step {step.key} happens on, or of the screen its response appears on;"
                    " leave it uncited only when it happens off screen"
                )
                if reported:
                    add(reported[0][0], reported[0][1], f"{message} ({usecase.document.path})", remediation)
                elif reportable(ctx, index, usecase.document):
                    add(usecase.document.path, step.line, message, remediation)
        return sorted(found, key=lambda v: (v.file, v.line, v.message))
