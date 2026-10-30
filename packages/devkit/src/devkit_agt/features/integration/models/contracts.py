"""Immutable approval scope, provider evidence and structured partial results."""

from __future__ import annotations

import hashlib
import json
import shlex
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from devkit.advisory import AdvisoryError
from devkit_dist.features.project.models.invocation import devkit_command

from devkit_agt.features.worktree.models.lifecycle import FinishResult
from devkit_agt.features.worktree.models.planning import FinishPlan
from devkit_agt.features.worktree.models.pull_request import Repository


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


def _task_arguments(branch: str, task: Task, route: str) -> str:
    """The arguments that name ``branch``, ``task`` and ``route`` to ``devkit integration prepare|integrate``."""
    parts = [branch, "--task-kind", task.kind, "--task-id", task.id]
    if task.unit is not None:
        parts += ["--unit", task.unit]
    if route != "local":
        parts += ["--route", route]
    if task.claims_json != "{}":
        parts += ["--claims", task.claims_json]
    return " ".join(shlex.quote(part) for part in parts)


def prepare_command(branch: str, task: Task, route: str, *, workspace: str | None = None) -> str:
    """The exact ``prepare`` command that shows the scope of ``branch`` for ``task`` on ``route``."""
    where = f" -w {shlex.quote(workspace)}" if workspace is not None else ""
    return devkit_command(f"integration prepare {_task_arguments(branch, task, route)}{where}")


def integrate_command(branch: str, task: Task, route: str, digest: str | None, *, workspace: str | None = None) -> str:
    """The exact ``integrate`` command for the prepared scope whose digest is ``digest`` (none under ``auto``)."""
    pinned = f" --expected-digest {digest}" if digest else ""
    where = f" -w {shlex.quote(workspace)}" if workspace is not None else ""
    return devkit_command(f"integration integrate {_task_arguments(branch, task, route)}{pinned}{where}")


@dataclass(frozen=True)
class IntegrationContext:
    """What a provider, guard or cleanup extension checks.

    At ``prepare`` this is the approved context: ``finish.target_sha`` is the confirmation target and ``result_sha``
    is ``None`` (nothing is built). When the source does not contain the confirmation target, a provider receives at
    ``prepare`` a prospective context instead: ``result_sha`` is an unsigned prospective merge commit that never lands
    (``ADR-moved-target-merge``). At each build the service passes an execution context: ``finish.target_sha`` is
    the build target (the confirmation target or a descendant) and ``result_sha`` the commit that would land.
    """

    finish: FinishPlan
    task: Task
    network: str = "forbid"
    result_sha: str | None = None


@dataclass(frozen=True)
class Evidence:
    code: str
    value: str


@dataclass(frozen=True)
class Readiness:
    """A provider's verdict bound to the context's source, target and result commits.

    ``target_bound`` names the evidence codes whose values may change when the target advances (all other evidence
    must equal the approved evidence at each build); ``disclosure`` is the one-line, at most 200-character statement
    of what the provider checks on the merged result, included in the report the Host presents before approval. Both
    are part of the request digest.
    """

    source_sha: str
    target_sha: str
    evidence: tuple[Evidence, ...]
    reasons: tuple[str, ...] = ()
    result_sha: str | None = None
    target_bound: tuple[str, ...] = ()
    disclosure: str = ""
    landed_check: str = ""

    def comparable(self) -> tuple[object, ...]:
        """The part a build's readiness must repeat: everything except target-bound evidence and the commits."""
        bound = set(self.target_bound)
        return (
            self.source_sha,
            tuple(item for item in self.evidence if item.code not in bound),
            self.target_bound,
            self.disclosure,
            self.landed_check,
        )


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
    route: str = "local"
    repository: Repository | None = None
    pr_number: int | None = None
    local_target: str | None = None
    unverified_rules: tuple[str, ...] = ()
    approval_policy: str = "ask"
    approval_gate: str = "dev-integration"

    @property
    def digest(self) -> str:
        value = asdict(self)
        value.pop("id")
        return digest(value)

    def approval_scope(self) -> dict[str, Any]:
        """User-visible effects; internal validation remains bound by the full request digest."""
        plan = self.context.finish
        return {
            "id": self.id,
            "digest": self.digest,
            "approval": {"gate": self.approval_gate, "policy": self.approval_policy},
            "repository": plan.base,
            "task": {"kind": self.context.task.kind, "id": self.context.task.id},
            "source": {"branch": plan.branch, "sha": plan.source_sha},
            "target": {"branch": plan.target_branch, "sha": plan.target_sha},
            "worktree": {"path": plan.path, "remove": plan.worktree_identity is not None},
            "delete_branch": plan.delete_branch,
            "cleanup": [
                {
                    "extension": scope.extension,
                    "targets": [{"kind": target.kind, "identity": target.identity} for target in scope.targets],
                }
                for scope in self.cleanup
            ],
            "merge_method": plan.merge_method,
            "already_merged": plan.already_merged,
            "network_operations": "excluded" if self.route == "local" else "approved-pull-request",
            "route": self.route,
            "remote": self.repository.public_scope() if self.repository else None,
            "pull_request": self._pull_request(),
            "readiness": {"disclosure": self.readiness.disclosure},
        }

    def _pull_request(self) -> int | str | None:
        """The pull request the route lands through: its number, ``create`` before it exists, ``None`` on ``local``."""
        if self.pr_number:
            return self.pr_number
        return "create" if self.route == "pull-request" else None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "repository": self.repository.public_scope() if self.repository else None,
            "digest": self.digest,
            "approval": {"gate": self.approval_gate, "policy": self.approval_policy},
            "merge_method": self.context.finish.merge_method,
            "network_operations": "excluded" if self.route == "local" else "approved-pull-request",
            "route": self.route,
            "remote": self.repository.public_scope() if self.repository else None,
            "pull_request": self._pull_request(),
        }


STEPS = ("merge", "worktree_remove", "branch_delete", "marker_clear", "post_finish")


@dataclass(frozen=True)
class SeededArtifact:
    """A generated artifact whose conflicted ``paths`` a build kept from its ``seed`` side without regenerating them
    (``ADR-generated-conflicts-in-prepared-merge``): ``"ours"`` keeps the target's files, ``"theirs"`` the source's."""

    id: str
    paths: tuple[str, ...]
    seed: str

    @property
    def kept(self) -> str:
        return "target" if self.seed == "ours" else "source"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "paths": list(self.paths), "seed": self.seed, "kept": self.kept}


def regenerate_command(seeded: tuple[SeededArtifact, ...]) -> str:
    """The exact command that regenerates ``seeded`` (and the artifacts after them) in the target's checkout."""
    return devkit_command(f"generated regen {' '.join(shlex.quote(item.id) for item in seeded)}")


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
    # The latest build of this process, outside the request digest: the target it read and the commit it built.
    build_target: str | None = None
    result_sha: str | None = None
    build_checked: bool = False
    pull_request: dict[str, Any] = field(default_factory=dict)
    landing: dict[str, Any] = field(default_factory=dict)
    # The generated artifacts the latest build (prospective at prepare, real at integrate) kept from one side.
    seeded: tuple[SeededArtifact, ...] = ()

    def build(self) -> dict[str, Any] | None:
        if self.build_target is None:
            return None
        return {
            "confirmation_target": self.request.context.finish.target_sha,
            "build_target": self.build_target,
            "result": self.result_sha,
        }

    def generated(self) -> dict[str, Any] | None:
        """The seeded generated artifacts and the command that regenerates them; ``None`` when nothing was seeded."""
        if not self.seeded:
            return None
        return {"seeded": [item.to_dict() for item in self.seeded], "regenerate": regenerate_command(self.seeded)}

    def compact_dict(self) -> dict[str, Any]:
        """Bounded default MCP result; detailed inspection uses the full serializer."""
        result: dict[str, Any] = {
            "request": self.request.approval_scope(),
            "status": self.status,
            "authority": self.authority,
            "steps": dict(self.steps),
            "pull_request": dict(self.pull_request),
            "landing": dict(self.landing),
            "errors": [error.to_dict() for error in self.errors],
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.ui_action is not None:
            result["ui_action"] = self.ui_action
        if self.cleanup_steps:
            result["cleanup_steps"] = dict(self.cleanup_steps)
        if self.failing_operation is not None:
            result["failing_operation"] = self.failing_operation
        if self.observed:
            result["observed"] = dict(self.observed)
        if self.build_target is not None:
            result["build"] = self.build()
        if self.seeded:
            result["generated"] = self.generated()
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "status": self.status,
            "authority": self.authority,
            "ui_action": self.ui_action,
            "steps": dict(self.steps),
            "pull_request": dict(self.pull_request),
            "landing": dict(self.landing),
            "cleanup_steps": dict(self.cleanup_steps),
            "finish": self.finish.to_dict() if self.finish else None,
            "observed": self.observed,
            "failing_operation": self.failing_operation,
            "build": self.build(),
            "generated": self.generated(),
            "network_operations": "excluded" if self.request.route == "local" else "approved-pull-request",
            "errors": [error.to_dict() for error in self.errors],
            "notices": [notice.to_dict() for notice in self.notices],
        }
