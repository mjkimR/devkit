"""Compose source-bound proposal acceptance and optional handoff for the Host-authorized CLI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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
from devkit_agt.features.worktree import locate, read_worktree_config
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import GitError, run_git, run_git_text
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.usecases.configuration import (
    approval_language,
    read_effective_config,
    resolve_execution_environment,
)
from devkit_dist.features.project.usecases.invocation import guard_execution

from devkit_spec.base.axes import DEFAULT_EFFORT, DEV_EFFORT, EFFORTS, PROPOSAL_WORKFLOW
from devkit_spec.base.errors import (
    ProposalAcceptanceUnrecordedError,
    ProposalAcceptCommitRefusedError,
    ProposalApprovalNotReadyError,
    ProposalApprovalReplyError,
    ProposalApprovalStaleError,
    ProposalInvalidError,
    ProposalPolicyNotAutoError,
    ProposalWrongWorktreeError,
    SpecConfigError,
    acceptance_unrecorded_fix,
)
from devkit_spec.base.units import proposal_unit
from devkit_spec.features.policy import require_sdd
from devkit_spec.features.policy.usecases.approvals import approval_policy
from devkit_spec.features.proposals import accept_proposal
from devkit_spec.features.proposals.services.status import accepted_text
from devkit_spec.features.proposals.usecases.scaffold import require_slug


def _proposal_error(error: AdvisoryError) -> AdvisoryError:
    if error.code in {"INTEGRATION_REQUEST_STALE", "INTEGRATION_TARGET_MOVED", "SPEC_HANDOFF_STALE"}:
        return ProposalApprovalStaleError(error.message, f"Underlying guard: {error.code}: {error.message}")
    return error


def _accept_command(slug: str, mode: str, effort: str | None, by: str) -> str:
    """The caller's own composed command: its ``--by`` is kept, never replaced by ``user``."""
    tail = f" --effort {effort}" if mode == "accept_and_handoff" and effort else ""
    return devkit_command(f"spec proposal accept {slug} --by {by} --mode {mode}{tail}")


def _base_checkout(root: Path, slug: str, command: str) -> None:
    """Refuse a composed acceptance off the retained base checkout (``ProposalWrongWorktreeError``); ``command`` is the
    caller's own CLI command."""
    position = locate(root)
    if position.linked or not position.branch or position.branch.startswith(("dev-", "plan-")):
        raise ProposalWrongWorktreeError(
            f"the composed acceptance of PROP-{slug} runs in the retained base checkout, not on "
            f"{position.branch or '- (detached HEAD)'}",
            fix=f"Run `{command}` in the main worktree on its base branch; the Planning branch plan-{slug} is integrated "
            "from there",
        )


def _require_policy_authority(root: Path, slug: str, by: str) -> None:
    """``--by policy`` needs the owning ``plan-accept=auto``; checked before anything else so the refusal is the policy
    one (``SPEC_PROPOSAL_POLICY_NOT_AUTO``), never a fix that switches the authority to the user."""
    if by == "policy" and approval_policy(root, "plan-accept") != "auto":
        raise ProposalPolicyNotAutoError(
            f"--by policy cannot accept PROP-{slug}: the retained base's plan-accept policy is not auto"
        )


def _spec_refusal(error: AdvisoryError, slug: str, by: str) -> AdvisoryError:
    """A base-level refusal of the integration preparation as the spec-level condition it means; any command it
    names keeps the caller's ``--by``."""
    if error.code == "WORKTREE_NOT_FOUND":
        direct = devkit_command(f"spec proposal accept {slug} --by {by} --direct")
        when = " after the user's explicit acceptance" if by == "user" else ""
        return ProposalApprovalNotReadyError(
            f"PROP-{slug} has no Planning branch plan-{slug} to accept and integrate",
            f"{error.code}: {error.message}",
            target_files=[f"plan-{slug}"],
            fix=f"Run Planning on plan-{slug} first (`{devkit_command(f'worktree start plan-{slug}')}` in the base "
            f"checkout); a draft that skips Planning is accepted with `{direct}`{when}, adding --note with the "
            "reason the draft is eligible",
        )
    if error.code == "INTEGRATION_CONFIG_INVALID":
        return SpecConfigError(
            f"the integration policy of the retained base cannot run the composed acceptance: {error.message}",
            f"{error.code}: {error.message}",
            fix="Correct [workflow.approvals] plan-accept and [worktree] in .devkit/config.toml of the base checkout "
            "(ask or auto), then rerun the same command",
        )
    return error


def _configuration(root: Path) -> str:
    value = {
        "config": read_effective_config(root).values,
        "environment": resolve_execution_environment(root).environment,
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


class _Acceptance:
    approval_gate = "plan-accept"

    def __init__(self, root: Path, slug: str, mode: str = "accept_and_handoff"):
        self.root, self.slug = root, slug
        self.unit = proposal_unit(slug)
        self.requested_mode = mode
        self.mode, self.effort = mode, DEFAULT_EFFORT
        self.actor = "user"
        self.completed: list[str] = []
        self.acceptance_sha: str | None = None
        self.source: Path | None = None
        self.snapshot: tuple | None = None

    def preview(self, context: IntegrationContext) -> Readiness:
        plan = context.finish
        self.source = Path(plan.path)
        meta = parse((self.source / self.unit / "proposal.md").read_text()).data or {}
        workspace = Workspace(self.source)
        ref = workspace.resolve_unit(self.unit)
        evaluation = workspace.evaluate_unit(ref, lint=False)
        anchor = f"{self.unit}/proposal.md"
        next_step = devkit_command(f"workflow next --unit {self.unit}")
        conditions = (
            [f"workflow: {ref.doc.id} (expected {PROPOSAL_WORKFLOW})"] if ref.doc.id != PROPOSAL_WORKFLOW else []
        )
        conditions += [f"problem ({error.code}): {error.message}" for error in evaluation.errors]
        conditions += [f"hold: {line}" for line in evaluation.hold.reasons()]
        conditions += [f"unmet: {item.name}" for item in evaluation.unmet if item.name != "gate:plan-accept"]
        if meta.get("needs_decompose") is True:
            conditions.append("needs_decompose: true (Backlog splits it first)")
        if conditions:
            raise ProposalApprovalNotReadyError(
                f"Planning of PROP-{self.slug} is not ready for plan-accept",
                *conditions,
                target_files=[anchor],
                fix=f"Once the user agrees, resolve the conditions on plan-{self.slug} (`{next_step}` there names the "
                "next step), commit them, then rerun the same command",
            )
        if meta.get("status") == "accepted":
            if not evaluation.complete:
                raise ProposalAcceptanceUnrecordedError(
                    f"PROP-{self.slug} says status: accepted on plan-{self.slug} without its completed plan-accept",
                    target_files=[anchor],
                    fix=acceptance_unrecorded_fix(self.slug),
                )
            self.completed = ["acceptance_commit"]
        elif meta.get("status") != "reviewing" or (
            not evaluation.complete and (evaluation.stage is None or evaluation.stage.id != "direction-handoff")
        ):
            stage = evaluation.stage.id if evaluation.stage is not None else "complete"
            raise ProposalApprovalNotReadyError(
                f"PROP-{self.slug} is not ready for plan-accept",
                f"status: {meta.get('status') or '-'} (expected reviewing)",
                f"stage: {stage} (expected direction-handoff)",
                target_files=[anchor],
                fix=f"Once the user agrees, finish Planning on plan-{self.slug} (`{next_step}` there names the next "
                "step), commit it, then rerun the same command",
            )
        self.effort = str(meta.get(DEV_EFFORT, DEFAULT_EFFORT))
        if self.effort not in EFFORTS:
            raise ProposalInvalidError(
                f"PROP-{self.slug} has dev_effort {self.effort!r}, not low, medium or high",
                target_files=[anchor],
                fix=f"Set dev_effort to low, medium or high in {anchor} on plan-{self.slug}, commit it, then rerun",
            )
        self._check_result(context, anchor)
        self.meta = meta
        self.snapshot = self._snapshot()
        return Readiness(
            plan.source_sha,
            plan.target_sha,
            (Evidence("PROPOSAL", plan.source_sha),),
            disclosure="Validate completed acceptance and all integration readiness before merge",
        )

    def _check_result(self, context: IntegrationContext, anchor: str) -> None:
        """Refuse before the acceptance commit when the prospective merge with a moved target fails the delivery
        provider's result-dependent checks (``ADR-moved-target-merge``); nothing to check without one."""
        from devkit_spec.features.delivery.usecases.integration import result_reasons

        reasons = result_reasons(context)
        if reasons:
            raise ProposalApprovalNotReadyError(
                f"the merge of plan-{self.slug} with the moved target {context.finish.target_sha[:12]} fails its checks",
                *reasons,
                target_files=[anchor],
                fix=f"Merge the target into plan-{self.slug} in its worktree, run "
                f"`{devkit_command(f'rules fix {self.unit}')}` and commit its repairs, re-verify what the merge changed, "
                "then rerun the same command",
            )

    def _snapshot(self) -> tuple:
        assert self.source is not None
        guard_execution()
        return (
            run_git_text(self.root, "rev-parse", "HEAD"),
            run_git_text(self.source, "rev-parse", "HEAD"),
            run_git_text(self.root, "status", "--porcelain", "--untracked-files=normal"),
            run_git_text(self.source, "status", "--porcelain", "--untracked-files=normal"),
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
        if policies["plan-accept"] != "auto" or request.approval_policy != "auto":
            return None
        self.actor = "policy"
        self.setup = read_worktree_config(self.source).setup
        return {
            "mode": self.requested_mode if policies.get("proposal-handoff") == "auto" else "accept_only",
            "activity_effort": self.effort,
        }

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
            raise ProposalInvalidError(
                f"{self.unit}/proposal.md has no status line to change", target_files=[f"{self.unit}/proposal.md"]
            ) from exc
        accepted = accept_proposal(self.source, self.slug, by=self.actor)
        self.completed.append("acceptance_record")
        if accepted.decision is None:
            raise ProposalApprovalStaleError("acceptance did not produce an authority gate record")
        paths = [accepted.path, accepted.decision]
        expected = {accepted.path: expected_anchor, accepted.decision: (self.source / accepted.decision).read_bytes()}
        if anchor.read_bytes() != expected_anchor:
            raise ProposalApprovalStaleError("acceptance changed unrelated proposal text")
        # A pre-existing clean index was bound by the preview; only these exact two writes may enter this commit.
        run_git_text(self.source, "add", "--", *paths)
        changed = set(run_git_text(self.source, "diff", "--cached", "--name-only").splitlines())
        if changed != set(expected):
            raise ProposalApprovalStaleError("index contains changes outside the exact acceptance delta")
        guard_execution()
        try:
            run_git_text(self.source, "commit", "-m", f"spec: accept proposal {self.slug}")
        except GitError as exc:
            # Nothing landed: withdraw this service's own two writes so the worktree is clean for the rerun.
            run_git_text(self.source, "reset", "-q", "--", *paths)
            anchor.write_text(original)
            (self.source / accepted.decision).unlink()
            self.completed.remove("acceptance_record")
            raise ProposalAcceptCommitRefusedError(
                f"the commit gate refused the acceptance commit of PROP-{self.slug} on plan-{self.slug}; the "
                "acceptance writes were withdrawn",
                *[line for line in exc.stderr.splitlines() if line.strip()][-20:],
                target_files=[f"plan-{self.slug}"],
                fix=f"In the plan-{self.slug} worktree run `{devkit_command('rules check')}`, fix what it reports, "
                "commit the fixes, then rerun the same command",
            ) from exc
        head = run_git_text(self.source, "rev-parse", "HEAD")
        self.acceptance_sha = head
        self.completed.append("acceptance_commit")
        previous = request.context.finish.source_sha
        if (
            run_git_text(self.source, "rev-list", "--parents", "-n", "1", head).split() != [head, previous]
            or set(run_git_text(self.source, "diff", "--name-only", previous, head).splitlines()) != set(expected)
            or any(run_git(self.source, "show", f"{head}:{path}") != data for path, data in expected.items())
            or run_git_text(self.source, "status", "--porcelain", "--untracked-files=normal")
        ):
            raise ProposalApprovalStaleError("committed acceptance differs from the exact service-created delta")
        return head


class PlanAcceptUseCase(BaseUseCase):
    def __init__(self, root: Path) -> None:
        self.root = root

    def execute(
        self, slug: str, *, mode: str = "accept_and_handoff", effort: str | None = None, by: str = "user"
    ) -> dict[str, Any]:
        """Accept and integrate a reviewed proposal after Host-carried approval."""
        from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase, prepare

        require_sdd(self.root)
        self.root = self.root.resolve()
        slug = require_slug(slug)
        if mode not in {"accept_only", "accept_and_handoff"}:
            raise ProposalApprovalReplyError("choose accept_only or accept_and_handoff")
        if mode == "accept_and_handoff" and effort not in EFFORTS:
            raise ProposalApprovalReplyError("choose low, medium or high Development effort", target_files=["--effort"])
        guard_execution()
        _require_policy_authority(self.root, slug, by)
        _base_checkout(self.root, slug, _accept_command(slug, mode, effort, by))
        lifecycle = _Acceptance(self.root, slug, mode)
        integration = IntegrationService(self.root)
        try:
            request = integration._prepare(
                f"plan-{slug}",
                Task("unit", f"PROP-{slug}", lifecycle.unit),
                lifecycle=lifecycle,
                approval_gate=lifecycle.approval_gate,
            ).request
        except AdvisoryError as exc:
            raise _spec_refusal(exc, slug, by) from exc
        lifecycle.validate(request)
        automatic = lifecycle.automatic(request)
        if automatic is not None:
            lifecycle.select(automatic)
            authority = "policy"
        else:
            if by == "policy":
                raise ProposalPolicyNotAutoError(
                    f"--by policy cannot accept PROP-{slug}: the retained base's plan-accept policy is not auto"
                )
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
            # The merged target and what was checked on the merged result (``ADR-moved-target-merge``).
            "target_sha": result.build_target or result.request.context.finish.target_sha,
            "disclosure": result.request.readiness.disclosure,
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
        if run_git_text(self.root, "rev-parse", "HEAD") != landed:
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
