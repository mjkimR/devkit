"""Bounded pages of the diagnostic scope journal."""

from __future__ import annotations

from dataclasses import dataclass

from devkit.advisory import AdvisoryError

from devkit_spec.features.scope.models.model import Event


@dataclass(frozen=True)
class HistoryPage:
    events: list[Event]
    summary: dict[str, object]
    pagination: dict[str, object]
    notices: list[AdvisoryError]

    def to_dict(self) -> dict[str, object]:
        return {
            "events": [event.to_dict() for event in self.events],
            "summary": self.summary,
            "pagination": self.pagination,
            "notices": [notice.to_dict() for notice in self.notices],
        }
