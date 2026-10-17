"""Immutable approval scope, provider evidence and structured partial results."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from devkit.advisory import AdvisoryError
from devkit.worktree import FinishPlan, FinishResult


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Task:
    kind: str
    id: str
    unit: str | None = None
    # Caller declarations are distinct from provider-verified evidence and are never approval authority.
    claims_json: str = "{}"


@dataclass(frozen=True)
class IntegrationContext:
    finish: FinishPlan
    task: Task
    network: str = "forbid"


@dataclass(frozen=True)
class Evidence:
    code: str
    value: str


@dataclass(frozen=True)
class Readiness:
    source_sha: str
    target_sha: str
    evidence: tuple[Evidence, ...]
    reasons: tuple[str, ...] = ()


class ReadinessProvider(Protocol):
    def check(self, context: IntegrationContext) -> Readiness: ...


@dataclass(frozen=True)
class CleanupTarget:
    """Opaque package-owned identity and revision; only its extension interprets it."""

    kind: str
    identity: str
    revision: str


@dataclass(frozen=True)
class CleanupResult:
    done: bool
    notices: tuple[AdvisoryError, ...] = ()


class ScopedCleanup(Protocol):
    integration_local_only: bool

    def integration_plan(self, context: IntegrationContext) -> tuple[CleanupTarget, ...]: ...
    def integration_validate(self, context: IntegrationContext, targets: tuple[CleanupTarget, ...]) -> None: ...
    def integration_run(
        self, context: IntegrationContext, result: FinishResult, targets: tuple[CleanupTarget, ...]
    ) -> CleanupResult: ...


@dataclass(frozen=True)
class CleanupScope:
    extension: str
    identity: str
    targets: tuple[CleanupTarget, ...]


@dataclass(frozen=True)
class IntegrationRequest:
    id: str
    context: IntegrationContext
    provider: str
    provider_identity: str
    policy_digest: str
    post_policy_digest: str
    guards: tuple[str, ...]
    readiness: Readiness
    cleanup: tuple[CleanupScope, ...]

    @property
    def digest(self) -> str:
        value = asdict(self)
        value.pop("id")
        return digest(value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"digest": self.digest, "merge_method": "ff-only", "network_operations": "excluded"}


STEPS = ("merge", "worktree_remove", "branch_delete", "marker_clear", "post_finish")


@dataclass
class IntegrationResult:
    request: IntegrationRequest
    status: str = "prepared"
    authority: str = "none"
    ui_action: str | None = None
    steps: dict[str, str] = field(default_factory=lambda: dict.fromkeys(STEPS, "not_run"))
    cleanup_steps: dict[str, str] = field(default_factory=dict)
    finish: FinishResult | None = None
    observed: dict[str, Any] = field(default_factory=dict)
    failing_operation: str | None = None
    errors: list[AdvisoryError] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "status": self.status,
            "authority": self.authority,
            "ui_action": self.ui_action,
            "steps": dict(self.steps),
            "cleanup_steps": dict(self.cleanup_steps),
            "finish": self.finish.to_dict() if self.finish else None,
            "observed": self.observed,
            "failing_operation": self.failing_operation,
            "network_operations": "excluded",
            "errors": [error.to_dict() for error in self.errors],
            "notices": [notice.to_dict() for notice in self.notices],
        }
