"""One native decision for proposal acceptance, checked integration and optional handoff."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path

from devkit.advisory import AdvisoryError
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
from devkit_core.core import GitError, run_git
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.usecases.configuration import (
    approval_language,
    read_effective_config,
    resolve_execution_environment,
)
from devkit_dist.features.project.usecases.invocation import guard_execution

from devkit_spec.base.errors import SpecError
from devkit_spec.features.proposals import accept_proposal
from devkit_spec.features.proposals.models.axes import EFFORTS
from devkit_spec.features.proposals.usecases.accept import _STATUS, _frontmatter_end
from devkit_spec.features.proposals.usecases.scaffold import require_slug


class ProposalApprovalStaleError(SpecError):
    code = "PROPOSAL_APPROVAL_STALE"
    fix = "Inspect completed effects, refresh the report and request a fresh native approval for remaining effects"


class ProposalApprovalNotReadyError(SpecError):
    code = "PROPOSAL_APPROVAL_NOT_READY"
    fix = "Resolve the reported Planning prerequisite and publish a fresh report before requesting approval"


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


def _schema(effort: str, language: str) -> dict:
    return {
        "type": "object",
        "properties": {
            "approve": {
                "type": "boolean",
                "default": False,
                "title": "명시적으로 승인" if language == "ko" else "Explicitly approve",
            },
            "mode": {"type": "string", "enum": ["accept_and_handoff", "accept_only"], "default": "accept_and_handoff"},
            "activity_effort": {"type": "string", "enum": ["low", "medium", "high"], "default": effort},
        },
        "required": ["approve", "mode", "activity_effort"],
        "additionalProperties": False,
    }


class _Acceptance:
    def __init__(self, root: Path, slug: str, report_uri: str):
        self.root, self.slug, self.report_uri = root, slug, report_uri
        self.unit = f"docs/proposals/PROP-{slug}"
        self.mode, self.effort = "accept_and_handoff", "medium"
        self.completed: list[str] = []
        self.acceptance_sha: str | None = None
        self.source: Path | None = None
        self.snapshot: tuple | None = None

    def preview(self, context: IntegrationContext) -> Readiness:
        from devkit_spec.features.proposals.usecases.report import validate

        plan = context.finish
        relative = self.root.relative_to(locate(self.root).base)
        self.source = Path(plan.path) / relative
        report = validate(self.source, self.slug, plan.source_sha, self.report_uri)
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
        elif (
            meta.get("status") != "reviewing" or evaluation.stage is None or evaluation.stage.id != "direction-handoff"
        ):
            raise ProposalApprovalNotReadyError("proposal is not ready for plan-accept")
        self.effort = str(meta.get("dev_effort", "medium"))
        if self.effort not in EFFORTS:
            raise ProposalApprovalNotReadyError("dev_effort must be low, medium or high")
        if report.metadata.language != approval_language(self.root):
            raise ProposalApprovalNotReadyError("report language differs from the owning workspace")
        self.meta, self.report = meta, report
        self.snapshot = self._snapshot()
        return Readiness(
            plan.source_sha,
            plan.target_sha,
            (Evidence("PROPOSAL_REVIEW", report.metadata.content_sha256),),
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
        from devkit_spec.features.proposals.usecases.report import validate_artifact

        if self.snapshot != self._snapshot():
            raise ProposalApprovalStaleError("source, base, configuration or execution environment changed")
        assert self.source is not None
        current = validate_artifact(self.source, self.slug, request.context.finish.source_sha, self.report_uri)
        if current != self.report:
            raise ProposalApprovalStaleError("the exact report changed after review")

    def before_merge(self, request: IntegrationRequest) -> None:
        from devkit_spec.features.proposals.usecases.report import validate_artifact

        assert self.source is not None and self.snapshot is not None
        current = self._snapshot()
        expected = (self.snapshot[0], self.acceptance_sha, *self.snapshot[2:])
        if current != expected:
            raise ProposalApprovalStaleError("environment, base or acceptance changed before merge")
        validate_artifact(self.source, self.slug, self.report.metadata.source_sha, self.report_uri)

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
            f"Report: {self.report_uri}\nPADRs: {re.findall(r'PADR-[A-Za-z0-9-]+', self.report.content)}\n"
            f"Planning support: {self._support()}\n{effects}\n"
            f"dev_effort={self.effort}; completed={self.completed}\n"
            f"Development worktree: {path_for(position, 'dev-' + self.slug)}\nSetup: {setup!r}\n"
            f"{request.confirmation_message(language)}"
        )
        return message, _schema(self.effort, language)

    def _support(self) -> str:
        from devkit_spec.features.proposals.usecases.report import SECTIONS, _sections

        return _sections(self.report.content, 2)[SECTIONS[self.report.metadata.language][3]]

    def select(self, content: dict) -> None:
        mode, effort = content.get("mode"), content.get("activity_effort")
        if mode not in {"accept_only", "accept_and_handoff"} or (
            mode == "accept_and_handoff" and effort not in EFFORTS
        ):
            raise ProposalApprovalNotReadyError("choose accept_only or accept_and_handoff and low|medium|high effort")
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
        end = _frontmatter_end(original)
        prefix, count = _STATUS.subn("status: accepted", original[:end], count=1)
        if count != 1:
            raise ProposalApprovalNotReadyError("proposal status cannot be changed exactly")
        expected_anchor = (prefix + original[end:]).encode()
        accepted = accept_proposal(self.source, self.slug, by="user")
        self.completed.append("acceptance_record")
        if accepted.decision is None:
            raise ProposalApprovalStaleError("acceptance did not produce a user gate record")
        paths = [accepted.path, accepted.decision]
        expected = {accepted.path: expected_anchor, accepted.decision: (self.source / accepted.decision).read_bytes()}
        if anchor.read_bytes() != expected_anchor:
            raise ProposalApprovalStaleError("acceptance changed unrelated proposal text")
        # A pre-existing clean index was bound by the preview; only these exact two writes may enter this commit.
        _git(self.source, "add", "--", *paths)
        changed = set(_git(self.source, "diff", "--cached", "--name-only").splitlines())
        if changed != set(paths):
            raise ProposalApprovalStaleError("index contains changes outside the exact acceptance delta")
        guard_execution()
        _git(self.source, "commit", "-m", f"spec: accept proposal {self.slug}")
        head = _git(self.source, "rev-parse", "HEAD")
        self.acceptance_sha = head
        self.completed.append("acceptance_commit")
        previous = request.context.finish.source_sha
        if (
            _git(self.source, "rev-list", "--parents", "-n", "1", head).split() != [head, previous]
            or set(_git(self.source, "diff", "--name-only", previous, head).splitlines()) != set(paths)
            or any(run_git(self.source, "show", f"{head}:{path}") != data for path, data in expected.items())
            or _git(self.source, "status", "--porcelain", "--untracked-files=normal")
        ):
            raise ProposalApprovalStaleError("committed acceptance differs from the exact service-created delta")
        return head


class PlanAcceptService:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._lock = asyncio.Lock()

    async def _remaining(self, slug: str, report_uri: str, confirm: Confirmation) -> dict:
        from devkit_spec.features.proposals.usecases.native_handoff import HandoffService, prepare
        from devkit_spec.features.proposals.usecases.report import validate

        preview = await asyncio.to_thread(prepare, self.root, slug, report_uri)
        validate(self.root, slug, preview.head, report_uri)
        language = approval_language(self.root)
        snapshot = _configuration(self.root)
        message = (
            "수락 및 병합 완료. 남은 효과만 승인합니다. accept_only는 추가 작업 없이 종료합니다. "
            "accept_and_handoff는 아래 Development 효과를 수행합니다.\n"
            if language == "ko"
            else "Acceptance and merge already completed. Approve remaining effects only. accept_only performs "
            "no further effects; accept_and_handoff performs the Development effects below.\n"
        )
        reply = await confirm(message + preview.message(language), _schema(preview.effort, language))
        result = {
            "status": "held",
            "completed_steps": ["acceptance_commit", "merge"],
            "landed_sha": preview.head,
            "next_action": "Request fresh approval for remaining effects",
        }
        if reply.action != "accept" or reply.content.get("approve") is not True:
            return result
        guard_execution()
        mode, effort = reply.content.get("mode"), reply.content.get("activity_effort")
        if mode not in {"accept_only", "accept_and_handoff"} or (
            mode == "accept_and_handoff" and effort not in EFFORTS
        ):
            raise ProposalApprovalNotReadyError("choose a valid mode and Development effort")
        validate(self.root, slug, preview.head, report_uri)
        if _configuration(self.root) != snapshot or prepare(self.root, slug, report_uri) != preview:
            raise ProposalApprovalStaleError("accepted base, report, policy or environment changed")
        if mode == "accept_only":
            return {**result, "status": "accepted", "next_action": "Acceptance already complete"}
        handed = await asyncio.to_thread(HandoffService(self.root)._execute, preview, str(effort))
        return {
            **result,
            "status": handed["status"],
            "handoff": handed,
            "activity_effort": effort,
            "next_action": handed.get("next_command", result["next_action"]),
        }

    async def accept(self, slug: str, report_uri: str, confirm: Confirmation) -> dict:
        slug = require_slug(slug)
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
                return await self._remaining(slug, report_uri, confirm)
            lifecycle = _Acceptance(self.root, slug, report_uri)
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
                "source_sha": lifecycle.report.metadata.source_sha,
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
                    "next_action": "Base moved after integration; refresh report and request remaining-effects approval",
                }
            payload.update(status="accepted", landed_sha=landed, next_action="Acceptance complete")
            if lifecycle.mode == "accept_only":
                return payload
            from devkit_spec.features.proposals.usecases.native_handoff import HandoffService, prepare

            try:
                guard_execution()
                from devkit_spec.features.proposals.usecases.report import validate_artifact

                validate_artifact(self.root, slug, lifecycle.report.metadata.source_sha, report_uri)
                preview = prepare(self.root, slug)
                if preview.setup != lifecycle.setup:
                    raise ProposalApprovalStaleError("setup differs from the disclosed prospective source setup")
                if preview.head != landed:
                    raise ProposalApprovalStaleError("base changed between integration and handoff")
                handed = await asyncio.to_thread(HandoffService(self.root)._execute, preview, lifecycle.effort)
                payload.update(
                    status=handed["status"],
                    handoff=handed,
                    next_action=handed.get("next_command")
                    or (
                        "Inspect the preserved accepted base and Development worktree; resolve reported setup/handoff "
                        "failure, publish a fresh accepted-base report and request fresh approval for remaining effects"
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
                    "prerequisite, publish a fresh accepted-base report and request fresh approval for remaining effects",
                )
            return payload
