"""Immutable approval scope, provider evidence and structured partial results."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from devkit.advisory import AdvisoryError
from devkit.worktree import FinishPlan, FinishResult
from devkit.worktree.pull_request import Repository


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
    """What a provider, guard or cleanup extension checks.

    At ``prepare`` this is the approved context: ``finish.target_sha`` is the confirmation target and ``result_sha``
    is ``None`` (nothing is built). At each build the service passes an execution context: ``finish.target_sha`` is
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
    of what the provider checks on the merged result, shown in the confirmation form. Both are part of the approved
    request digest.
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
            "pull_request": self.pr_number if self.pr_number else "create",
        }

    def confirmation_message(self) -> str:
        """Show decisions and exact effect targets without implementation diagnostics."""
        plan = self.context.finish

        def display(value: str) -> str:
            return json.dumps(value, ensure_ascii=False)

        presentation = {item.code: item.value for item in self.readiness.evidence}

        def brief(value: str, limit: int = 1500) -> str:
            return display(value if len(value) <= limit else value[:limit] + "… [truncated]")

        branch, target = display(plan.branch), display(plan.target_branch)
        if self.repository:
            return "\n".join(
                [
                    f"Approve pull request integration of {branch} into {display(self.repository.selector)} {target} with a merge commit?",
                    f"Source: {plan.source_sha}; confirmation target: {plan.target_sha}",
                    f"Push source; {'use PR ' + str(self.pr_number) if self.pr_number else 'create PR'}; merge; fetch; fast-forward local target.",
                    f"Remove worktree: {display(plan.path) if plan.worktree_identity else 'no'}; delete local and remote source branches: {plan.delete_branch} (remote lease {plan.source_sha}).",
                    f"Additional cleanup: {display(json.dumps([asdict(scope) for scope in self.cleanup]))}",
                    f"GitHub automatic branch deletion: {self.repository.delete_on_merge}; when enabled the platform can delete the remote branch regardless of devkit delete_branch policy.",
                    "Merge runs now only when required checks and reviews pass; otherwise resume later on the unchanged checked target. A frequently advancing target may prevent this route from ever merging.",
                    "A target commit landing after the last check can merge without devkit checks; this is reported and does not stop cleanup.",
                    f"Unverified platform rules: {display(str(self.unverified_rules))}",
                    f"Result check: {display(self.readiness.disclosure)}; landed-target check after cleanup: {display(self.readiness.landed_check)}",
                    "A host timeout can leave execution running; inspect integration_status before recovery.",
                ]
            )
        if plan.already_merged:
            lines = [f"Approve cleanup of {branch}, already merged into {target}?"]
        elif plan.merge_method == "no-ff":
            lines = [f"Approve local integration of {branch} into {target} with a merge commit?"]
        else:
            lines = [f"Approve local integration of {branch} into {target} by fast-forward?"]
        for code, label in (("TASK_TITLE", "Work"), ("TASK_SUMMARY", "Goal"), ("RESULT_SUMMARY", "Completed work")):
            if presentation.get(code):
                lines.append(f"{label}: {brief(presentation[code])}")
        if plan.already_merged:
            lines.append(
                "The branch is already merged into the target: nothing is merged; only the cleanup below runs."
            )
        elif plan.merge_method == "no-ff":
            lines += [
                "Later commits on the target are merged in without another confirmation only if the merge is clean,"
                " the integration policy is unchanged and readiness provider"
                f" {display(self.provider)} passes again on the merged result; otherwise nothing changes on the"
                " target.",
                f"Result check: {display(self.readiness.disclosure)}",
            ]
        else:
            lines.append(
                "The target advances to the verified source commit (fast-forward); if the target moved, nothing"
                " changes on the target."
            )
        lines += [
            "",
            f"Repository: {display(plan.base)}",
            f"Task: {display(self.context.task.id)}",
            f"Source: {display(plan.branch)} @ {plan.source_sha}",
            f"Target: {display(plan.target_branch)} @ {plan.target_sha} (at confirmation)",
            f"Remove worktree: {display(plan.path)}" if plan.worktree_identity is not None else "Remove worktree: no",
            f"Delete local branch: {display(plan.branch)}" if plan.delete_branch else "Delete local branch: no",
            "Additional cleanup:",
        ]
        targets = [
            f"- {display(scope.extension)}: {display(target.kind)} {display(target.identity)}"
            for scope in self.cleanup
            for target in scope.targets
        ]
        lines.extend(targets or ["- none"])
        lines += [
            "",
            "Approve only if this work and the cleanup above are ready.",
            "No fetch, push, remote deletion or PR operations.",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {
            "repository": self.repository.public_scope() if self.repository else None,
            "digest": self.digest,
            "merge_method": self.context.finish.merge_method,
            "network_operations": "excluded" if self.route == "local" else "approved-pull-request",
            "route": self.route,
            "remote": self.repository.public_scope() if self.repository else None,
            "pull_request": self.pr_number if self.pr_number else "create",
        }


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
    # The latest build of this process, outside the request digest: the target it read and the commit it built.
    build_target: str | None = None
    result_sha: str | None = None
    build_checked: bool = False
    pull_request: dict[str, Any] = field(default_factory=dict)
    landing: dict[str, Any] = field(default_factory=dict)

    def build(self) -> dict[str, Any] | None:
        if self.build_target is None:
            return None
        return {
            "confirmation_target": self.request.context.finish.target_sha,
            "build_target": self.build_target,
            "result": self.result_sha,
        }

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
            "network_operations": "excluded" if self.request.route == "local" else "approved-pull-request",
            "errors": [error.to_dict() for error in self.errors],
            "notices": [notice.to_dict() for notice in self.notices],
        }
