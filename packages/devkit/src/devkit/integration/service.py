"""Prepare, confirm and execute an exact local request; retain partial progress only in this process.

The request is immutable and binds the confirmation target. The approving call absorbs target commits that landed
since the confirmation in one build: the target must descend from the confirmation target, the result commit is built
outside the base checkout (``devkit.worktree.merging``), the guards and the readiness provider run again with the
execution context (source, build target, result), the result's effective policy must equal the prospected one and
the merge must leave no receipt record inconsistent; the base then fast-forwards onto the result only while it still
points at the build target. ``integration_resume`` continues only onto the last build target (or, without a build,
the confirmation target). See ``ADR-target-advance-readiness``.
"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from devkit.advisory import AdvisoryError, Level
from devkit.core import LockHeldError
from devkit.core.errors import GitError
from devkit.core.git import run_git
from devkit.core.mcp import Confirmation
from devkit.core.mcp_context import capture_terminal_removal, guard_execution
from devkit.core.paths import normalize_relpath
from devkit.core.presentation import approval_language
from devkit.core.project import read_project_config
from devkit.integration import providers, receipts
from devkit.integration.errors import (
    AuthorityError,
    CleanupContractError,
    CleanupIncompleteWarning,
    IntegrationConfigError,
    ProviderError,
    RuntimeLocationError,
    StaleRequestError,
    TargetMovedError,
)
from devkit.integration.models import (
    CleanupResult,
    IntegrationContext,
    IntegrationRequest,
    IntegrationResult,
    Task,
)
from devkit.worktree import (
    FinishResult,
    MergeFailedError,
    PullRequestPolicyError,
    build_result,
    fast_forward,
    finish,
    integration_lock,
    is_ancestor,
    locate,
    merge_method,
    plan_finish,
    read_worktree_config,
    run_finish_guards,
    validate_finish,
)

LOCK_WAIT = 20.0  # seconds the approving call waits for another devkit integration; integration_resume never waits


def _git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode("utf-8", errors="surrogateescape").strip()


def _prospective(root: Path, commit: str, other: str) -> tuple[str, dict[str, Any]]:
    """The effective policy digest and parsed configuration ``commit`` brings to the base.

    When neither ``commit`` nor ``other`` tracks the configuration, the base checkout's untracked file stays in force.
    """
    config = providers.commit_config(root, commit)
    if config is None:
        config = read_project_config(root) if providers.commit_config(root, other) is None else {}
    return providers.policy_digest(config), config


@dataclass
class _Record:
    result: IntegrationResult
    approved: bool = False
    finalized: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)


class IntegrationService:
    """Trusted application service. No method accepts a caller-supplied approval boolean or serialized authority."""

    def __init__(self, root: Path) -> None:
        from devkit.worktree.pull_request import GitHub

        self.root = root.resolve()
        self.github = GitHub(self.root)
        self._records: dict[str, _Record] = {}

    def prepare(self, branch: str, task: Task, route: str = "local") -> IntegrationResult:
        guard_execution()
        if (
            task.kind not in {"unit", "session"}
            or not isinstance(task.id, str)
            or not task.id.strip()
            or len(task.id) > 256
        ):
            raise IntegrationConfigError("task requires kind unit|session and a nonempty id of at most 256 characters")
        if (task.kind == "unit") != (task.unit is not None):
            raise IntegrationConfigError("unit tasks require a unit path; session tasks must not invent one")
        if task.unit is not None:
            normalize_relpath(task.unit, canonical=True)
        try:
            claims = json.loads(task.claims_json)
            if not isinstance(claims, dict) or len(task.claims_json.encode()) > 16384:
                raise ValueError("invalid claims")
        except (ValueError, UnicodeError) as exc:
            raise IntegrationConfigError("task claims must be a JSON object of at most 16 KiB") from exc
        if len(self._records) >= 128:
            retired = next(
                (
                    key
                    for key, record in self._records.items()
                    if record.result.status in {"completed", "cancelled", "declined", "not_approved"}
                ),
                None,
            )
            if retired is None:
                raise AuthorityError(
                    "the process already retains 128 pending requests; inspect and finish them before preparing more"
                )
            self._records.pop(retired)
        approval_policy = providers.effective(read_project_config(self.root))["dev-integration"]
        if route == "pull-request" and approval_policy == "auto":
            raise AuthorityError(
                "automatic integration authorizes local execution only",
                fix="Use the verified local route; obtain separate publication authority for a pull request",
            )
        if route == "pull-request":
            from devkit.integration.pull_request import prepare

            result = prepare(self, branch, task)
            self._records[result.request.id] = _Record(result)
            return result
        if route != "local":
            raise IntegrationConfigError("route must be local or pull-request")
        name, policy_digest = providers.policy(self.root)
        config = read_worktree_config(self.root)
        position = locate(self.root)
        method = merge_method(self.root, config.merge, f"refs/heads/{branch}")
        plan = plan_finish(position, branch, pull_request=config.pull_request, delete_branch=False, merge_method=method)
        if plan.worktree_identity is not None and (
            Path(sys.executable).absolute().is_relative_to(Path(plan.path))
            or Path(sys.prefix).resolve().is_relative_to(Path(plan.path))
        ):
            raise RuntimeLocationError("the active interpreter would be removed by approved worktree cleanup")
        if plan.already_merged:
            # A cleanup-only request builds nothing: the target's policy at prepare is what the cleanup runs under.
            post_digest, prospective = policy_digest, read_project_config(self.root)
        else:
            post_digest, prospective = _prospective(self.root, plan.source_sha, plan.target_sha)
        if approval_policy == "auto" and providers.effective(prospective)["dev-integration"] != "auto":
            raise AuthorityError(
                "the prospective result revokes automatic integration authority",
                fix="Resolve prospective policy revocation before automatic integration; do not bypass it with another authority route",
            )
        worktree_policy = prospective.get("worktree", {})
        if not isinstance(worktree_policy, dict) or type(worktree_policy.get("delete_branch", True)) is not bool:
            raise IntegrationConfigError("source worktree policy is invalid")
        if worktree_policy.get("pull_request", "auto") == "required":
            raise PullRequestPolicyError("the source policy requires PR integration; the local path is unavailable")
        plan = replace(plan, delete_branch=config.delete_branch and worktree_policy.get("delete_branch", True))
        context = IntegrationContext(plan, task)
        ident, provider = providers.provider(name)
        ready = providers.check(provider, context)
        guard_identities = providers.guards()
        # The guard base is the merge base: the target, or the source itself for a cleanup-only request.
        run_finish_guards(
            self.root, branch, plan.source_sha if plan.already_merged else plan.target_sha, plan.source_sha
        )
        cleanup = providers.cleanup_scopes(context, providers.cleanup_extensions())
        validate_finish(plan)
        request = IntegrationRequest(
            uuid4().hex,
            context,
            name,
            ident,
            policy_digest,
            post_digest,
            guard_identities,
            ready,
            cleanup,
            approval_policy=approval_policy,
        )
        result = IntegrationResult(request)
        result.steps["branch_delete" if not plan.delete_branch else "marker_clear"] = "skipped"
        if plan.worktree_identity is None:
            result.steps["worktree_remove"] = "skipped"
        if plan.already_merged:
            result.steps["merge"] = "skipped"
        result.cleanup_steps = {scope.extension: "not_run" for scope in cleanup}
        self._records[request.id] = _Record(result)
        return result

    def inspect(self, request_id: str) -> IntegrationResult:
        record = self._record(request_id)
        record.result.observed = self._observe(record.result.request)
        return record.result

    def _record(self, request_id: str) -> _Record:
        record = self._records.get(request_id)
        if record is None:
            raise AuthorityError("request is not retained in this process; inspect Git before preparing new scope")
        return record

    async def integrate(
        self, branch: str, task: Task, confirm: Confirmation, route: str = "local"
    ) -> IntegrationResult:
        guard_execution()
        language = approval_language(self.root)
        result = await asyncio.to_thread(self.prepare, branch, task, route)
        request = result.request
        if request.approval_policy == "auto":
            guard_execution()
            self._records[request.id].approved = True
            result.authority = "policy"
            return await asyncio.to_thread(self._run, request.id, LOCK_WAIT, True)
        message = request.confirmation_message(language)
        try:
            reply = await confirm(
                message,
                {
                    "type": "object",
                    "properties": {
                        "approve": {
                            "type": "boolean",
                            "title": "이 정확한 통합 작업 승인"
                            if language == "ko"
                            else "Approve this exact integration",
                            "default": False,
                        }
                    },
                    "required": ["approve"],
                },
            )
        except AdvisoryError as exc:
            result.status = "blocked"
            result.errors.append(exc)
            return result
        result.ui_action = reply.action
        if reply.action != "accept" or reply.content.get("approve") is not True:
            result.status = (
                reply.action
                if reply.action in {"declined", "cancelled"}
                else {"decline": "declined", "cancel": "cancelled"}.get(reply.action, "not_approved")
            )
            return result
        guard_execution()
        self._records[request.id].approved = True
        result.authority = "mcp-elicitation"
        return await asyncio.to_thread(self._run, request.id, LOCK_WAIT, True)

    def _observe(self, request: IntegrationRequest) -> dict:
        if request.route == "pull-request":
            from devkit.integration.pull_request import observe

            return observe(self, request)
        plan = request.context.finish
        observed: dict = {"worktree_exists": Path(plan.path).exists() if plan.worktree_identity else None}
        for key, ref in (
            ("target_sha", f"refs/heads/{plan.target_branch}"),
            ("source_sha", f"refs/heads/{plan.branch}"),
        ):
            try:
                observed[key] = _git(self.root, "rev-parse", "--verify", ref)
            except GitError as exc:
                observed[key] = None
                if exc.returncode is None:
                    observed["inspection_incomplete"] = True
        try:
            entries = _git(self.root, "worktree", "list", "--porcelain", "-z").split("\0")
            observed["worktree_registered"] = f"worktree {plan.path}" in entries if plan.worktree_identity else None
        except GitError:
            observed["inspection_incomplete"] = True
        return observed

    @staticmethod
    def _context(result: IntegrationResult) -> IntegrationContext:
        """The execution context: the approved context, plus the build target and result once a build exists."""
        context = result.request.context
        plan = context.finish
        if plan.already_merged:
            return replace(context, result_sha=plan.source_sha)
        if result.build_target is None or result.result_sha is None:
            return context
        return replace(context, finish=replace(plan, target_sha=result.build_target), result_sha=result.result_sha)

    def _validate(
        self,
        request: IntegrationRequest,
        *,
        merged: bool,
        removed: bool,
        finalized: bool,
        cleanup_done: set[str] | None = None,
        context: IntegrationContext | None = None,
        target: str | None = None,
    ) -> None:
        guard_execution(terminal=removed)
        plan = request.context.finish
        # The digest comparison comes first: a changed policy is a stale request whatever its new value is.
        expected = request.post_policy_digest if merged else request.policy_digest
        if providers.current_policy(self.root) != expected:
            raise StaleRequestError("the effective integration policy changed outside the approved merge")
        if (
            request.approval_policy == "auto"
            and providers.effective(read_project_config(self.root))["dev-integration"] != "auto"
        ):
            raise AuthorityError(
                "automatic integration authority was revoked",
                fix="Stop remaining effects and inspect current policy and completed progress; obtain fresh authority before recovery",
            )
        if not merged:
            providers.policy(self.root)
        if providers.guards() != request.guards:
            raise StaleRequestError("finish guard registrations changed")
        context = context or request.context
        try:
            validate_finish(
                plan, merged=merged, removed=removed, finalized=finalized, result=context.result_sha, target=target
            )
        except (GitError, AdvisoryError) as exc:
            if getattr(exc, "code", "") == "WORKTREE_CONFLICT":
                raise StaleRequestError(exc.message) from exc
            raise
        ident, _ = providers.provider(request.provider)
        if ident != request.provider_identity:
            raise StaleRequestError("readiness provider installation changed")
        extensions = providers.cleanup_extensions()
        if {name: ident for name, (ident, _) in extensions.items()} != {
            scope.extension: scope.identity for scope in request.cleanup
        }:
            raise StaleRequestError("post-finish extension installation changed")
        for scope in request.cleanup:
            if scope.extension not in (cleanup_done or set()):
                extensions[scope.extension][1].integration_validate(context, scope.targets)

    def resume(self, request_id: str) -> IntegrationResult:
        return self._run(request_id, 0, False)

    def _run(self, request_id: str, wait: float, approving: bool) -> IntegrationResult:
        guard_execution()
        record = self._record(request_id)
        if not record.approved:
            raise AuthorityError("this request has no execution authority")
        if not record.lock.acquire(blocking=False):
            raise AuthorityError("this request is already executing; inspect it after the current call finishes")
        try:
            if record.result.request.route == "pull-request":
                from devkit.integration.pull_request import execute

                return execute(self, record, wait, approving)
            plan = record.result.request.context.finish
            try:
                with integration_lock(Path(plan.common_dir), timeout=wait):
                    return self._execute(record, approving)
            except LockHeldError as exc:
                if not approving:
                    raise
                result = record.result
                result.observed = self._observe(result.request)
                exc.fix = (
                    "Call integration_resume with the same request id once the other devkit integration finishes"
                    if result.observed.get("target_sha") == plan.target_sha
                    else "Call integration_integrate for a new confirmation: the target moved past the confirmation"
                    " target and integration_resume does not absorb it"
                )
                result.errors[:] = [exc]
                result.failing_operation = "lock"
                result.status = "blocked"
                return result
        finally:
            record.lock.release()

    def _execute(self, record: _Record, approving: bool) -> IntegrationResult:
        result, request = record.result, record.result.request
        if result.status == "completed":
            return result
        plan = request.context.finish
        result.errors.clear()
        result.notices[:] = [notice for notice in result.notices if notice.code != "INTEGRATION_CLEANUP_INCOMPLETE"]
        result.failing_operation = None
        operation = "preflight"
        merged = result.steps["merge"] in {"completed", "skipped"}
        removed = result.steps["worktree_remove"] in {"completed", "skipped"}
        try:
            observed = self._observe(request)
            if observed.get("inspection_incomplete"):
                raise StaleRequestError("Git inspection is incomplete; inspect state before further mutations")
            head = observed.get("target_sha")
            if result.steps["merge"] in {"unknown", "failed"} and result.build_target is not None:
                if (
                    result.result_sha is not None
                    and head is not None
                    and is_ancestor(self.root, result.result_sha, head)
                ):
                    merged = True
                elif head != result.build_target:
                    raise StaleRequestError("merge outcome is ambiguous; inspect Git before taking further action")
            if result.steps["worktree_remove"] == "unknown" and not Path(plan.path).exists():
                removed = True
            if (
                merged
                and not observed.get("worktree_registered")
                and not observed.get("worktree_exists")
                and plan.delete_branch
                and observed.get("source_sha") is None
                and result.steps["branch_delete"] in {"failed", "unknown"}
            ):
                record.finalized = True
                removed = True
                result.steps["branch_delete"] = "completed"
                if plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
            cleanup_done = {name for name, state in result.cleanup_steps.items() if state == "completed"}
            if not merged:
                operation = "merge"
                self._land(result, head, approving, removed=removed, cleanup_done=cleanup_done)
                merged = True
            else:
                self._validate(
                    request,
                    merged=True,
                    removed=removed,
                    finalized=record.finalized,
                    cleanup_done=cleanup_done,
                    context=self._context(result),
                )
                if result.steps["merge"] != "skipped":
                    result.steps["merge"] = "completed"
            context = self._context(result)

            def before_step(step: str, progress: FinishResult) -> None:
                nonlocal operation
                operation = step
                self._validate(
                    request,
                    merged=True,
                    removed=removed or progress.removed is True,
                    finalized=False,
                    context=context,
                )
                if step == "worktree_remove" and approving:
                    capture_terminal_removal(Path(plan.path))
                result.finish = progress
                if progress.removed is True and plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
                result.steps[step] = "running"

            if not record.finalized:
                operation = "cleanup"
                result.finish = finish(
                    locate(self.root),
                    plan.branch,
                    merge=False,
                    network="forbid",
                    delete_branch=plan.delete_branch,
                    before_step=before_step,
                )
                result.finish.merged = result.steps["merge"] == "completed"
                record.finalized = True
                if plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
                result.steps["branch_delete" if plan.delete_branch else "marker_clear"] = "completed"
            operation = "post_finish"
            self._validate(
                request, merged=True, removed=True, finalized=True, cleanup_done=cleanup_done, context=context
            )
            extensions = providers.cleanup_extensions()
            assert result.finish is not None
            for scope in request.cleanup:
                if result.cleanup_steps[scope.extension] == "completed":
                    continue
                guard_execution(terminal=True)
                result.cleanup_steps[scope.extension] = "running"
                outcome = extensions[scope.extension][1].integration_run(context, result.finish, scope.targets)
                if (
                    not isinstance(outcome, CleanupResult)
                    or type(outcome.done) is not bool
                    or not all(isinstance(notice, AdvisoryError) for notice in outcome.notices)
                ):
                    raise CleanupContractError("scoped cleanup must return CleanupResult")
                result.notices.extend(
                    notice.with_level(Level.WARNING) if notice.level is Level.ERROR else notice
                    for notice in outcome.notices
                )
                result.cleanup_steps[scope.extension] = "completed" if outcome.done else "failed"
            result.steps["post_finish"] = (
                "completed" if all(value == "completed" for value in result.cleanup_steps.values()) else "failed"
            )
            result.status = "completed" if result.steps["post_finish"] == "completed" else "partial"
            if result.status == "partial":
                result.failing_operation = "post_finish"
                result.notices.append(
                    CleanupIncompleteWarning(
                        "Git integration completed; scoped post-finish cleanup remains",
                        *[name for name, state in result.cleanup_steps.items() if state != "completed"],
                    )
                )
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, AdvisoryError)
                else ProviderError(f"integration operation {operation} failed ({type(exc).__name__})")
            )
            result.errors.append(error)
            result.failing_operation = operation
            if isinstance(exc, TargetMovedError):
                result.steps["merge"] = "not_run"
            elif result.steps.get(operation) == "running":
                result.steps[operation] = (
                    "unknown" if isinstance(exc, GitError) and exc.returncode is None else "failed"
                )
            if result.finish and result.finish.removed is True and plan.worktree_identity:
                result.steps["worktree_remove"] = "completed"
            result.status = "partial" if any(value == "completed" for value in result.steps.values()) else "blocked"
        result.observed = self._observe(request)
        return result

    def _land(
        self, result: IntegrationResult, head: str | None, approving: bool, *, removed: bool, cleanup_done: set[str]
    ) -> None:
        """Build the result commit on the current target, check it and fast-forward the base onto it."""
        request = result.request
        plan = request.context.finish
        if result.build_target is not None:
            if head != result.build_target:
                raise StaleRequestError(
                    "the target moved after this approval's build; a later target needs a new confirmation"
                )
        elif not approving:
            if head != plan.target_sha:
                raise StaleRequestError(
                    "the target moved since the confirmation; integration_resume does not absorb it, so a later target"
                    " needs a new confirmation"
                )
        elif head is None or not is_ancestor(self.root, plan.target_sha, head):
            raise StaleRequestError("the target no longer descends from the confirmation target (reset or rewritten)")
        assert head is not None
        self._validate(request, merged=False, removed=removed, finalized=False, cleanup_done=cleanup_done, target=head)
        result.steps["merge"] = "running"
        result.build_target, result.result_sha = head, None
        result.result_sha = build_result(
            self.root,
            branch=plan.branch,
            target_branch=plan.target_branch,
            target=head,
            source=plan.source_sha,
            method=plan.merge_method,
            advance=True,
        )
        context = self._context(result)
        merge_base = _git(self.root, "merge-base", head, plan.source_sha)
        run_finish_guards(self.root, plan.branch, merge_base, plan.source_sha)
        _, provider = providers.provider(request.provider)
        ready = providers.check(provider, context)
        if ready.comparable() != request.readiness.comparable():
            raise StaleRequestError("completion evidence changed; prepare a new request")
        if result.result_sha != plan.source_sha:
            if _prospective(self.root, result.result_sha, head)[0] != request.post_policy_digest:
                raise StaleRequestError("the merged result changes the effective integration policy")
            receipts.check_merge(self.root, result.result_sha, (head, plan.source_sha))
        if _git(self.root, "rev-parse", "--verify", f"refs/heads/{plan.target_branch}") != head:
            raise TargetMovedError("the base branch moved after the build; nothing changed on the target")
        self._validate(request, merged=False, removed=removed, finalized=False, cleanup_done=cleanup_done, target=head)
        try:
            fast_forward(self.root, result.result_sha)
        except GitError as exc:
            if exc.returncode is None:
                raise
            raise MergeFailedError(f"local merge of {plan.branch} failed: {exc.stderr or exc.message}") from exc
        # Git runs post-merge hooks before returning. A hook may amend commit metadata,
        # so bind cleanup to the observed commit only after proving checked content and
        # ordered provenance unchanged. Never substitute for the approved ff-only source.
        landed = _git(self.root, "rev-parse", "--verify", f"refs/heads/{plan.target_branch}^{{commit}}")
        if landed != result.result_sha:
            if plan.merge_method != "no-ff" or _git(self.root, "show", "-s", "--format=%T %P", landed) != _git(
                self.root, "show", "-s", "--format=%T %P", result.result_sha
            ):
                raise StaleRequestError("the landed commit differs from the checked result tree or ordered parents")
            result.result_sha = landed
        result.steps["merge"] = "completed"
