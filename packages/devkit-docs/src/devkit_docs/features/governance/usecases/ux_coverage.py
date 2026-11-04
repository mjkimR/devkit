"""``RULE-ux-coverage``: the steps of a use case a UX document serves, and the UX document's interactions, are
linked (``ADR-ux-screens``), unless an explicit, reasoned classification says why not
(``ADR-explicit-ux-coverage-exception-notation``).

For every use case some current UX document lists in ``usecases`` (parsing in ``governance.services.ux``), it
reports each main-scenario step and extension that cites no UX ID, once: on the use case at the step's line when the
run reports it, else on the first UX document listing the use case that the run reports (path order, at its
``usecases`` entry) (``ADR-ux-coverage-step-targeting``). It also reports, on its UX document, each Interactions row
whose Step cell is empty. A step classified ``off screen: <reason>`` and a row classified ``global: <reason>`` are not
reported; a classification without a reason, and an off-screen classification on a step that cites a UX ID, are
reported with their own messages. The rule is a ``warning``, as ``RULE-spec-progress`` is; contradictions are
``RULE-ux-links``'s. A use case no UX document lists is never reported. Nothing is fixable.
"""

from __future__ import annotations

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from devkit_docs.features.documents import Document
from devkit_docs.features.governance import document_index, reportable
from devkit_docs.features.governance.services.ux import Step, model

RULE_ID = "RULE-ux-coverage"

_STEP_REMEDIATION = (
    "Cite the UX ID of the screen step {key} happens on, or of the screen its response appears on; when it truly"
    " happens off screen, say why with `off screen: <reason>` on the step"
)


class UxCoverageRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="ux-coverage-check",
            description=(
                "Every step of a use case a UX document serves cites a UX document, and every interaction names the"
                " step it serves, unless classified off screen or global with a reason (warning)."
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
                            "Name the use case step it serves as `UC-<slug>` <key>; a global control says why with"
                            " `global: <reason>`",
                        )
                    elif row.global_reason == "":
                        add(
                            screen.document.path,
                            row.line,
                            "interaction is classified global without a reason",
                            "Write the reason after `global:`, or name the use case step the interaction serves",
                        )
        for usecase_id, places in sorted(listing.items()):
            usecase = flows.usecases.get(usecase_id)
            if usecase is None:
                continue
            on_usecase = reportable(ctx, index, usecase.document)
            reported = [
                (path, line)
                for path, line, document in sorted(places, key=lambda place: (place[0], place[1]))
                if reportable(ctx, index, document)
            ]
            for step in usecase.steps:
                report = _step_report(usecase_id, step)
                if report is None:
                    continue
                message, remediation = report
                if on_usecase:
                    add(usecase.document.path, step.line, message, remediation)
                elif reported:
                    add(reported[0][0], reported[0][1], f"{message} ({usecase.document.path})", remediation)
        return sorted(found, key=lambda v: (v.file, v.line, v.message))


def _step_report(usecase_id: str, step: Step) -> tuple[str, str] | None:
    """The message and remediation for ``step``, or ``None`` when it is covered or classified with a reason."""
    if step.screens:
        if step.off_screen is None:
            return None
        return (
            f"{usecase_id} step {step.key} is classified off screen but cites {step.screens[0]}",
            f"Remove the `off screen:` phrase from step {step.key}, or its screen citation when nothing of it appears"
            " on a screen",
        )
    if step.off_screen is None:
        return f"{usecase_id} step {step.key} cites no UX document", _STEP_REMEDIATION.format(key=step.key)
    if step.off_screen == "":
        return (
            f"{usecase_id} step {step.key} is classified off screen without a reason",
            f"Write the reason after `off screen:` on step {step.key}, or cite the screen it happens on",
        )
    return None
