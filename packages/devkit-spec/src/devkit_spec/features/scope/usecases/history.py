"""Read recent journal pages and continue backwards without shifts from new appends."""

from __future__ import annotations

import hashlib
import json

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.base.errors import ScopeJournalLineWarning
from devkit_spec.features.scope.models.history import HistoryPage
from devkit_spec.features.scope.models.model import JOURNAL_FILE, Event
from devkit_spec.features.scope.usecases.flow import Session


def _cursor(namespace: str, task: str | None, events: list[Event], before: int) -> str:
    # Bind the boundary to the journal prefix and filter, not a moving offset from its end.
    payload = [namespace, task, [event.to_dict() for event in events[:before]]]
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{before}.{digest}"


class QueryScopeHistoryUseCase(BaseUseCase):
    def execute(
        self, session: Session, *, task: str | None = None, limit: int = 50, cursor: str | None = None
    ) -> HistoryPage:
        """Return the most recent page in journal order; a cursor selects the preceding page."""
        if not 1 <= limit <= 100:
            raise ArgumentError("history limit must be between 1 and 100", target_files=["--limit"])
        location = session.location
        events, problems = session.registry.history(location.namespace, session.deadline)
        if task:
            events = [event for event in events if event.matches(task)]
        before = len(events)
        if cursor is not None:
            try:
                before = int(cursor.split(".", 1)[0])
                valid = 0 < before <= len(events) and cursor == _cursor(location.namespace, task, events, before)
            except ValueError:
                valid = False
            if not valid:
                raise ArgumentError(
                    "history cursor is invalid for this namespace, task filter or journal",
                    target_files=["--cursor"],
                    fix="Restart query --history with the intended --task filter and use its next_cursor",
                )
        start = max(0, before - limit)
        page = events[start:before]
        notices: list[AdvisoryError] = []
        if problems:
            notices.append(
                ScopeJournalLineWarning(
                    f"{len(problems)} journal line(s) are not JSON events and were skipped",
                    *(f"line {problem.line}: {problem.reason}" for problem in problems),
                    target_files=[str(location.shared_path / location.namespace / JOURNAL_FILE)],
                )
            )
        return HistoryPage(
            events=page,
            summary={"namespace": location.namespace, "events": len(page), "problems": len(problems)},
            pagination={
                "limit": limit,
                "total": len(events),
                "next_cursor": _cursor(location.namespace, task, events, start) if start else None,
            },
            notices=notices,
        )
