"""Invocation-local collection contracts; never persisted as registry records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devkit.advisory import AdvisoryError

from devkit_spec.features.scope.models.model import Record, ScopeSet


@dataclass(frozen=True)
class CollectionOptions:
    mode: str = "worktrees"
    base: str | None = None
    fetch: tuple[str, ...] = ()
    timeout: int = 30
    source_timeout: int = 5


@dataclass
class Candidate:
    source_id: str
    ref: str = ""
    sha: str = ""
    worktree: str = ""
    branch: str = ""
    record: Record | None = None
    activity: str = "unknown"
    reason: str = "unresolved"
    task_key: str | None = None

    def public(self) -> dict[str, Any]:
        return dict(
            source_id=self.source_id,
            ref=self.ref,
            sha=self.sha,
            worktree=self.worktree,
            activity=self.activity,
            reason=self.reason,
            task_key=self.task_key,
        )


@dataclass
class Observation:
    observation_id: str
    task_key: str | None
    scope: ScopeSet
    provenance: dict[str, Any]
    observed_layers: list[str] = field(default_factory=list)
    missing_layers: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    def public(self) -> dict[str, Any]:
        return dict(
            observation_id=self.observation_id,
            task_key=self.task_key,
            scope=self.scope.to_dict(),
            provenance=self.provenance,
            observed_layers=self.observed_layers,
            missing_layers=self.missing_layers,
            aliases=self.aliases,
        )


@dataclass
class CollectionReport:
    data: dict[str, Any]
    notices: list[AdvisoryError]
