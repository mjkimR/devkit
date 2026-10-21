"""Inspect and remove stale scope records while protecting revisions and journaling outcomes."""

from dataclasses import dataclass

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.base.errors import ScopeStaleRevisionError
from devkit_spec.features.scope.models.model import SweepResult, Verdict
from devkit_spec.features.scope.usecases.flow import Session, journal, sweep_events


@dataclass(frozen=True)
class SweptScopes:
    results: list[SweepResult]
    summary: dict[str, str | int]
    notices: list[AdvisoryError]
    error: AdvisoryError | None


class SweepScopesUseCase(BaseUseCase):
    def execute(self, session: Session, *, apply: bool = False, expected: dict[str, int] | None = None) -> SweptScopes:
        location = session.location
        if apply and not expected:
            records, _ = session.registry.query(location.namespace, session.deadline)
            expected = {record.task_id: record.revision for record in records}
        results = session.registry.sweep(location.namespace, apply, expected or {}, session.deadline)
        notices = journal(session.registry, location.namespace, sweep_events(results))
        counts = {str(verdict): sum(result.verdict is verdict for result in results) for verdict in Verdict}
        summary: dict[str, str | int] = {"namespace": location.namespace, **counts}
        moved = [result.task_id for result in results if result.reason == "stale-revision"]
        error = None
        if moved:
            error = ScopeStaleRevisionError(
                f"{len(moved)} stale record(s) changed since they were read and were kept: {', '.join(moved)}",
                fix="Run devkit spec scope sweep again and pass the revisions it reports to --apply --expect",
            )
        return SweptScopes(results, summary, notices, error)
