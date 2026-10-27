"""Compose source-bound proposal acceptance and optional handoff for the Host-authorized CLI."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_agt.features.integration import AuthorityError
from devkit_agt.features.integration.models.contracts import (
    Evidence,
    IntegrationContext,
    IntegrationRequest,
    Readiness,
    Task,
)
from devkit_agt.features.integration.usecases.service import IntegrationService
from devkit_agt.features.workflow import Workspace
from devkit_agt.features.worktree import locate, path_for, read_worktree_config
from devkit_core.base.mcp import Confirmation
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import GitError, run_git
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.usecases.configuration import (
    approval_language,
    read_effective_config,
    resolve_execution_environment,
)
from devkit_dist.features.project.usecases.invocation import guard_execution

from devkit_spec.base.errors import SpecError
from devkit_spec.features.policy.usecases.approvals import approval_policy
from devkit_spec.features.proposals import accept_proposal
from devkit_spec.features.proposals.models.axes import EFFORTS
from devkit_spec.features.proposals.services.status import accepted_text
from devkit_spec.features.proposals.usecases.scaffold import require_slug


class ProposalApprovalStaleError(SpecError):
    """The reviewed source, base, environment or exact acceptance delta changed (``MAINTENANCE``): completed effects
    need inspection before any further effect."""

    code = "PROPOSAL_APPROVAL_STALE"
    fix = (
        "Inspect completed effects, refresh the review evidence and obtain Host authority for the remaining CLI effects"
    )


class ProposalApprovalNotReadyError(SpecError):
    """A Planning or worktree prerequisite of the acceptance does not hold (``BLOCKED``): the user or Host resolves
    it, never a tool defect."""

    code = "PROPOSAL_APPROVAL_NOT_READY"
    guardrail = True
    fix = "Resolve the Planning prerequisite the message names, then rerun the CLI operation"


class ProposalApprovalReplyError(SpecError):
    """The requested or confirmed acceptance mode or Development effort is invalid (``INPUT_ERROR``)."""

    code = "PROPOSAL_APPROVAL_REPLY_INVALID"
    input_error = True
    fix = "Choose accept_only, or accept_and_handoff with a low, medium or high Development effort, then rerun"


def _proposal_error(error: AdvisoryError) -> AdvisoryError:
    if error.code in {"INTEGRATION_REQUEST_STALE", "INTEGRATION_TARGET_MOVED", "SPEC_HANDOFF_STALE"}:
        return ProposalApprovalStaleError(error.message, f"Underlying guard: {error.code}: {error.message}")
    return error


def _git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode().strip()


def _configuration(root: Path) -> str:
    value = {
        "config": read_effective_config(root).values,
        "environment": resolve_execution_environment(root).environment,
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def _schema(effort: str, language: str, mode: str = "accept_and_handoff") -> dict:
    return {
        "type": "object",
        "properties": {
            "approve": {
                "type": "boolean",
                "default": False,
                "title": "명시적으로 승인" if language == "ko" else "Explicitly approve",
            },
            "mode": {
                "type": "string",
                "enum": ["accept_only"] if mode == "accept_only" else ["accept_and_handoff", "accept_only"],
                "default": mode,
            },
            "activity_effort": {"type": "string", "enum": ["low", "medium", "high"], "default": effort},
        },
        "required": ["approve", "mode", "activity_effort"],
        "additionalProperties": False,
    }


class _Acceptance:
    approval_gate = "plan-accept"

    def __init__(self, root: Path, slug: str, mode: str = "accept_and_handoff"):
        self.root, self.slug = root, slug
        self.unit = f"docs/proposals/PROP-{slug}"
        self.requested_mode = mode
        self.mode, self.effort = mode, "medium"
        self.actor = "user"
        self.completed: list[str] = []
        self.acceptance_sha: str | None = None
        self.source: Path | None = None
        self.snapshot: tuple | None = None

    def preview(self, context: IntegrationContext) -> Readiness:
        plan = context.finish
        relative = self.root.relative_to(locate(self.root).base)
        self.source = Path(plan.path) / relative
        meta = parse((self.source / self.unit / "proposal.md").read_text()).data or {}
        workspace = Workspace(self.source)
        ref = workspace.resolve_unit(self.unit)
        evaluation = workspace.evaluate_unit(ref, lint=False)
        if (
            ref.doc.id != "sdd-proposal"
            or evaluation.errors
            or evaluation.hold.reasons()
            or any(item.name != "gate:plan-accept" for item in evaluation.unmet)
            or meta.get("needs_decompose") is True
        ):
            raise ProposalApprovalNotReadyError("Planning has unmet checks, problems, questions or decomposition")
        if meta.get("status") == "accepted":
            if not evaluation.complete:
                raise ProposalApprovalNotReadyError("accepted status lacks completed workflow approval")
            self.completed = ["acceptance_commit"]
        elif meta.get("status") != "reviewing" or (
            not evaluation.complete and (evaluation.stage is None or evaluation.stage.id != "direction-handoff")
        ):
            raise ProposalApprovalNotReadyError("proposal is not ready for plan-accept")
        self.effort = str(meta.get("dev_effort", "medium"))
        if self.effort not in EFFORTS:
            raise ProposalApprovalNotReadyError("dev_effort must be low, medium or high")
        self.meta = meta
        self.snapshot = self._snapshot()
        return Readiness(
            plan.source_sha,
            plan.target_sha,
            (Evidence("PROPOSAL", plan.source_sha),),
            disclosure="Validate completed acceptance and all integration readiness before merge",
        )

    def _snapshot(self) -> tuple:
        assert self.source is not None
        guard_execution()
        return (
            _git(self.root, "rev-parse", "HEAD"),
            _git(self.source, "rev-parse", "HEAD"),
            _git(self.root, "status", "--porcelain", "--untracked-files=normal"),
            _git(self.source, "status", "--porcelain", "--untracked-files=normal"),
            _configuration(self.root),
            _configuration(self.source),
            approval_language(self.root),
        )

    def validate(self, request: IntegrationRequest) -> None:
        if self.snapshot != self._snapshot():
            raise ProposalApprovalStaleError("source, base, configuration or execution environment changed")

    def before_merge(self, request: IntegrationRequest) -> None:
        assert self.source is not None and self.snapshot is not None
        current = self._snapshot()
        expected = (self.snapshot[0], self.acceptance_sha, *self.snapshot[2:])
        if current != expected:
            raise ProposalApprovalStaleError("environment, base or acceptance changed before merge")

    def automatic(self, request: IntegrationRequest) -> dict | None:
        assert self.source is not None
        policies = {"plan-accept": approval_policy(self.source, "plan-accept")}
        if self.requested_mode == "accept_and_handoff":
            policies["proposal-handoff"] = approval_policy(self.source, "proposal-handoff")
        # Acceptance may complete while Development waits for a separate ask boundary.
        # An ask at acceptance can include handoff in the same explicit native decision.
        if policies["plan-accept"] != "auto" or request.approval_policy != "auto":
            return None
        self.actor = "policy"
        self.setup = read_worktree_config(self.source).setup
        return {
            "mode": self.requested_mode if policies.get("proposal-handoff") == "auto" else "accept_only",
            "activity_effort": self.effort,
        }

    def confirmation(self, request: IntegrationRequest, language: str) -> tuple[str, dict]:
        position = locate(self.root)
        assert self.source is not None
        setup = read_worktree_config(self.source).setup
        self.setup = setup
        title = "제안 수락 및 Development 승인" if language == "ko" else "Accept proposal and approve Development"
        effects = (
            "approve=true와 accept 응답만 승인합니다. accept_only는 수락 기록·커밋·검증된 병합과 표시된 정리만 수행합니다. "
            "accept_and_handoff는 추가로 표시된 Development 작업 트리 생성·설정·handoff·범위 등록을 수행합니다. "
            "activity_effort는 low|medium|high이며 accept_only에서는 무시합니다. 실패 시 완료된 효과를 보존하고 새 승인이 필요합니다."
            if language == "ko"
            else "Only action=accept and approve=true authorize effects. accept_only records and commits acceptance, "
            "performs checked merge and disclosed cleanup. accept_and_handoff additionally creates the disclosed "
            "Development worktree, runs setup, handoff and scope registration. activity_effort is low|medium|high "
            "and ignored for accept_only. Partial failure preserves effects and requires fresh approval."
        )
        message = (
            f"{title}\n{self.meta.get('title', self.slug)}\n{self.meta.get('summary', '')}\n"
            f"{effects}\n"
            f"dev_effort={self.effort}; completed={self.completed}\n"
            f"Development worktree: {path_for(position, 'dev-' + self.slug)}\nSetup: {setup!r}\n"
            f"{request.confirmation_message(language)}"
        )
        return message, _schema(self.effort, language, self.requested_mode)

    def select(self, content: dict) -> None:
        mode, effort = content.get("mode"), content.get("activity_effort")
        if self.requested_mode == "accept_only" and mode != "accept_only":
            raise ProposalApprovalReplyError("accept_only does not authorize Development handoff")
        if mode not in {"accept_only", "accept_and_handoff"} or (
            mode == "accept_and_handoff" and effort not in EFFORTS
        ):
            raise ProposalApprovalReplyError("choose accept_only or accept_and_handoff and low|medium|high effort")
        self.mode = mode
        if mode == "accept_and_handoff":
            self.effort = str(effort)

    def accept(self, request: IntegrationRequest) -> str:
        self.validate(request)
        assert self.source is not None
        if self.meta.get("status") == "accepted":
            self.acceptance_sha = request.context.finish.source_sha
            return self.acceptance_sha
        anchor = self.source / self.unit / "proposal.md"
        original = anchor.read_text()
        try:
            expected_anchor = accepted_text(original).encode()
        except ValueError as exc:
            raise ProposalApprovalNotReadyError("proposal status cannot be changed exactly") from exc
        accepted = accept_proposal(self.source, self.slug, by=self.actor)
        self.completed.append("acceptance_record")
        if accepted.decision is None:
            raise ProposalApprovalStaleError("acceptance did not produce an authority gate record")
        paths = [accepted.path, accepted.decision]
        expected = {accepted.path: expected_anchor, accepted.decision: (self.source / accepted.decision).read_bytes()}
        if anchor.read_bytes() != expected_anchor:
            raise ProposalApprovalStaleError("acceptance changed unrelated proposal text")
        # A pre-existing clean index was bound by the preview; only these exact two writes may enter this commit.
        _git(self.source, "add", "--", *paths)
        # Git reports and resolves tree paths from the top level; the project may be a subdirectory of it.
        prefix = _git(self.source, "rev-parse", "--show-prefix")
        tree = {f"{prefix}{path}": data for path, data in expected.items()}
        changed = set(_git(self.source, "diff", "--cached", "--name-only").splitlines())
        if changed != set(tree):
            raise ProposalApprovalStaleError("index contains changes outside the exact acceptance delta")
        guard_execution()
        try:
            _git(self.source, "commit", "-m", f"spec: accept proposal {self.slug}")
        except GitError as exc:
            # Nothing landed: withdraw this service's own two writes so the worktree is clean for the rerun.
            _git(self.source, "reset", "-q", "--", *paths)
            anchor.write_text(original)
            (self.source / accepted.decision).unlink()
            self.completed.remove("acceptance_record")
            raise ProposalApprovalNotReadyError(
                "the commit gate refused the acceptance commit; `devkit rules check --staged` in the Planning "
                "worktree reproduces it",
                *[line for line in exc.stderr.splitlines() if line.strip()][-20:],
            ) from exc
        head = _git(self.source, "rev-parse", "HEAD")
        self.acceptance_sha = head
        self.completed.append("acceptance_commit")
        previous = request.context.finish.source_sha
        if (
            _git(self.source, "rev-list", "--parents", "-n", "1", head).split() != [head, previous]
            or set(_git(self.source, "diff", "--name-only", previous, head).splitlines()) != set(tree)
            or any(run_git(self.source, "show", f"{head}:{path}") != data for path, data in tree.items())
            or _git(self.source, "status", "--porcelain", "--untracked-files=normal")
        ):
            raise ProposalApprovalStaleError("committed acceptance differs from the exact service-created delta")
        return head


class PlanAcceptUseCase(BaseUseCase):
    def __init__(self, root: Path) -> None:
        self.root = root
        self._lock = asyncio.Lock()

    def execute(
        self, slug: str, *, mode: str = "accept_and_handoff", effort: str | None = None, by: str = "user"
    ) -> dict[str, Any]:
        """Accept and integrate a reviewed proposal after Host-carried approval."""
        from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase, prepare

        self.root = self.root.resolve()
        slug = require_slug(slug)
        if mode not in {"accept_only", "accept_and_handoff"}:
            raise ProposalApprovalReplyError("choose accept_only or accept_and_handoff")
        if mode == "accept_and_handoff" and effort not in EFFORTS:
            raise ProposalApprovalReplyError("choose low, medium or high Development effort")
        guard_execution()
        position = locate(self.root)
        if position.linked or not position.branch or position.branch.startswith(("dev-", "plan-")):
            raise ProposalApprovalNotReadyError("run the service from the retained base checkout")
        lifecycle = _Acceptance(self.root, slug, mode)
        integration = IntegrationService(self.root)
        request = integration._prepare(
            f"plan-{slug}",
            Task("unit", f"PROP-{slug}", lifecycle.unit),
            lifecycle=lifecycle,
            approval_gate=lifecycle.approval_gate,
        ).request
        lifecycle.validate(request)
        automatic = lifecycle.automatic(request)
        if automatic is not None:
            lifecycle.select(automatic)
            authority = "policy"
        else:
            if by == "policy":
                raise AuthorityError("--by policy requires retained plan-accept=auto authority")
            lifecycle.actor = "user"
            lifecycle.select({"mode": mode, "activity_effort": effort or lifecycle.effort})
            authority = "host-conversation"
        try:
            result = integration._compose_execute(request, lifecycle, authority)
        except AdvisoryError as exc:
            return {
                "status": "needs_recovery" if lifecycle.completed else "blocked",
                "completed_steps": lifecycle.completed,
                "acceptance_sha": lifecycle.acceptance_sha,
                "errors": [_proposal_error(exc).to_dict()],
                "next_action": exc.fix,
            }
        completed = list(lifecycle.completed)
        completed += [name for name, state in result.steps.items() if state == "completed"]
        payload: dict[str, Any] = {
            "status": result.status,
            "completed_steps": completed,
            "source_sha": request.context.finish.source_sha,
            "acceptance_sha": lifecycle.acceptance_sha,
            "integration": result.compact_dict(),
            "errors": [_proposal_error(error).to_dict() for error in result.errors],
            "activity_effort": lifecycle.effort,
            "acceptance_authority": lifecycle.actor,
            "next_action": "Inspect completed effects and resolve the reported integration step",
        }
        if result.status != "completed":
            payload["status"] = "needs_recovery" if completed else "blocked"
            return payload
        landed = result.result_sha or request.context.finish.source_sha
        if _git(self.root, "rev-parse", "HEAD") != landed:
            return {
                **payload,
                "status": "needs_recovery",
                "landed_sha": landed,
                "next_action": "Inspect the base and request fresh approval for remaining effects",
            }
        payload.update(status="accepted", landed_sha=landed, next_action="Acceptance complete")
        if lifecycle.mode == "accept_only":
            return payload
        try:
            preview = prepare(self.root, slug)
            if preview.head != landed:
                raise ProposalApprovalStaleError("base changed between integration and handoff")
            handed = HandoffUseCase(self.root)._execute(preview, lifecycle.effort)
            payload.update(
                status=handed["status"],
                handoff=handed,
                next_action=handed.get("next_command", "Inspect preserved handoff effects"),
            )
            if handed["status"] == "handed_off":
                payload["completed_steps"] += ["worktree_setup", "handoff"]
                if handed.get("scope_token"):
                    payload["completed_steps"].append("scope_registration")
            elif handed.get("worktree", {}).get("created"):
                payload["completed_steps"].append("worktree_setup")
            payload["errors"] = handed.get("errors", [])
            payload["notices"] = handed.get("notices", [])
        except AdvisoryError as exc:
            payload.update(status="needs_recovery", errors=[exc.to_dict()], next_action=exc.fix)
        return payload

    async def _remaining(self, slug: str, confirm: Confirmation, mode: str) -> dict:
        from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase, prepare

        preview = await asyncio.to_thread(prepare, self.root, slug)
        language = approval_language(self.root)
        snapshot = _configuration(self.root)
        message = (
            "수락 및 병합 완료. 남은 효과만 승인합니다. accept_only는 추가 작업 없이 종료합니다. "
            "accept_and_handoff는 아래 Development 효과를 수행합니다.\n"
            if language == "ko"
            else "Acceptance and merge already completed. Approve remaining effects only. accept_only performs "
            "no further effects; accept_and_handoff performs the Development effects below.\n"
        )
        if mode == "accept_only":
            return {
                "status": "accepted",
                "completed_steps": ["acceptance_commit", "merge"],
                "landed_sha": preview.head,
                "next_action": "Acceptance already complete",
            }
        if approval_policy(self.root, "proposal-handoff") == "auto":
            handed = await asyncio.to_thread(HandoffUseCase(self.root)._execute, preview, preview.effort)
            return {
                "status": handed["status"],
                "completed_steps": ["acceptance_commit", "merge"],
                "landed_sha": preview.head,
                "handoff": handed,
                "handoff_authority": "policy",
                "next_action": handed.get("next_command", "Inspect remaining handoff effects"),
            }
        reply = await confirm(message + preview.message(language), _schema(preview.effort, language, mode))
        result = {
            "status": "held",
            "completed_steps": ["acceptance_commit", "merge"],
            "landed_sha": preview.head,
            "next_action": "Request fresh approval for remaining effects",
        }
        if reply.action != "accept" or reply.content.get("approve") is not True:
            return result
        guard_execution()
        selected_mode, effort = reply.content.get("mode"), reply.content.get("activity_effort")
        if selected_mode not in {"accept_only", "accept_and_handoff"} or (
            selected_mode == "accept_and_handoff" and effort not in EFFORTS
        ):
            raise ProposalApprovalReplyError("choose a valid mode and Development effort")
        if _configuration(self.root) != snapshot or prepare(self.root, slug) != preview:
            raise ProposalApprovalStaleError("accepted base, policy or environment changed")
        if selected_mode == "accept_only":
            return {**result, "status": "accepted", "next_action": "Acceptance already complete"}
        handed = await asyncio.to_thread(HandoffUseCase(self.root)._execute, preview, str(effort))
        return {
            **result,
            "status": handed["status"],
            "handoff": handed,
            "activity_effort": effort,
            "next_action": handed.get("next_command", result["next_action"]),
        }

    async def execute_native(
        self, slug: str, confirm: Confirmation, *, mode: str = "accept_and_handoff"
    ) -> dict[str, Any]:
        self.root = self.root.resolve()
        slug = require_slug(slug)
        if mode not in {"accept_only", "accept_and_handoff"}:
            raise ProposalApprovalReplyError("choose accept_only or accept_and_handoff")
        guard_execution()
        async with self._lock:
            position = locate(self.root)
            if position.linked or not position.branch or position.branch.startswith(("dev-", "plan-")):
                raise ProposalApprovalNotReadyError("run the service from the retained base checkout")
            try:
                _git(self.root, "show-ref", "--verify", f"refs/heads/plan-{slug}")
            except GitError as exc:
                if exc.returncode is None:
                    raise
                return await self._remaining(slug, confirm, mode)
            lifecycle = _Acceptance(self.root, slug, mode)
            integration = IntegrationService(self.root)
            try:
                result = await integration._compose(
                    f"plan-{slug}", Task("unit", f"PROP-{slug}", lifecycle.unit), lifecycle, confirm
                )
            except AdvisoryError as exc:
                return {
                    "status": "needs_recovery" if lifecycle.completed else "blocked",
                    "completed_steps": lifecycle.completed,
                    "acceptance_sha": lifecycle.acceptance_sha,
                    "errors": [_proposal_error(exc).to_dict()],
                    "next_action": exc.fix,
                }
            payload = {
                "status": "held",
                "completed_steps": list(lifecycle.completed),
                "source_sha": result.request.context.finish.source_sha,
                "acceptance_sha": lifecycle.acceptance_sha,
                "integration": result.compact_dict(),
                "errors": [_proposal_error(error).to_dict() for error in result.errors],
                "activity_effort": lifecycle.effort,
                "next_action": "Inspect completed effects and request fresh approval for remaining effects",
            }
            payload["completed_steps"] += [name for name, status in result.steps.items() if status == "completed"]
            if result.status != "completed":
                payload["status"] = (
                    "needs_recovery"
                    if payload["completed_steps"]
                    else ("held" if result.status in {"not_approved", "cancelled", "declined"} else "blocked")
                )
                return payload
            landed = result.result_sha or result.request.context.finish.source_sha
            if _git(self.root, "rev-parse", "HEAD") != landed:
                return {
                    **payload,
                    "status": "needs_recovery",
                    "landed_sha": landed,
                    "next_action": "Base moved after integration; request remaining-effects approval",
                }
            payload.update(status="accepted", landed_sha=landed, next_action="Acceptance complete")
            payload["acceptance_authority"] = lifecycle.actor
            if lifecycle.mode == "accept_only":
                if (
                    lifecycle.actor == "policy"
                    and lifecycle.requested_mode != "accept_only"
                    and approval_policy(self.root, "proposal-handoff") == "ask"
                ):
                    payload["next_action"] = "Acceptance complete; request proposal handoff approval separately"
                return payload
            from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase, prepare

            try:
                guard_execution()
                preview = prepare(self.root, slug)
                if preview.setup != lifecycle.setup:
                    raise ProposalApprovalStaleError("setup differs from the disclosed prospective source setup")
                if preview.head != landed:
                    raise ProposalApprovalStaleError("base changed between integration and handoff")
                handed = await asyncio.to_thread(HandoffUseCase(self.root)._execute, preview, lifecycle.effort)
                payload.update(
                    status=handed["status"],
                    handoff=handed,
                    next_action=handed.get("next_command")
                    or (
                        "Inspect the preserved accepted base and Development worktree; resolve reported setup/handoff "
                        "failure, and request fresh approval for remaining effects"
                    ),
                )
                if handed["status"] == "handed_off":
                    payload["completed_steps"] += ["worktree_setup", "handoff"]
                    if handed.get("scope_token"):
                        payload["completed_steps"].append("scope_registration")
            except AdvisoryError as exc:
                payload.update(
                    status="needs_recovery",
                    errors=[exc.to_dict()],
                    next_action="Inspect the preserved accepted base and Development worktree; resolve the reported "
                    "prerequisite, and request fresh approval for remaining effects",
                )
            return payload
