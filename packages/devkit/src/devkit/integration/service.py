"""Prepare, confirm and execute an exact local request; retain partial progress only in this process."""

from __future__ import annotations

import asyncio
import json
import sys
import threading
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from uuid import uuid4

from devkit.advisory import AdvisoryError, Level
from devkit.core.errors import GitError
from devkit.core.git import run_git
from devkit.core.locks import file_lock
from devkit.core.paths import normalize_relpath
from devkit.host.mcp import Confirmation
from devkit.integration import providers
from devkit.integration.errors import (
    AuthorityError,
    CleanupContractError,
    CleanupIncompleteWarning,
    IntegrationConfigError,
    ProviderError,
    RuntimeLocationError,
    StaleRequestError,
)
from devkit.integration.models import (
    CleanupResult,
    IntegrationContext,
    IntegrationRequest,
    IntegrationResult,
    Task,
    digest,
)
from devkit.worktree import (
    FinishResult,
    PullRequestPolicyError,
    finish,
    locate,
    plan_finish,
    read_worktree_config,
    run_finish_guards,
    validate_finish,
)


def _git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode("utf-8", errors="surrogateescape").strip()


def _file_at(root: Path, sha: str, relative: str) -> bytes | None:
    if not run_git(root, "ls-tree", "--name-only", sha, "--", relative).strip():
        return None
    return run_git(root, "show", f"{sha}:{relative}")


def _post_policy(root: Path, source: str, target: str) -> tuple[str, dict]:
    files = []
    for relative in (".devkit/config.toml", ".devkit/installation.json"):
        raw = _file_at(root, source, relative)
        if raw is None and _file_at(root, target, relative) is None:
            path = root / relative
            raw = path.read_bytes() if path.exists() else None
        files.append((relative, raw.hex() if raw is not None else None))
    config = bytes.fromhex(files[0][1]) if files[0][1] is not None else b""
    try:
        parsed = tomllib.loads(config.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise IntegrationConfigError("source commit contains invalid integration policy") from exc
    return digest(files), parsed


@dataclass
class _Record:
    result: IntegrationResult
    approved: bool = False
    finalized: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)


class IntegrationService:
    """Trusted application service. No method accepts a caller-supplied approval boolean or serialized authority."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._records: dict[str, _Record] = {}

    def prepare(self, branch: str, task: Task) -> IntegrationResult:
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
        name, policy_digest = providers.policy(self.root)
        config = read_worktree_config(self.root)
        plan = plan_finish(locate(self.root), branch, pull_request=config.pull_request, delete_branch=False)
        if plan.worktree_identity is not None and (
            Path(sys.executable).absolute().is_relative_to(Path(plan.path))
            or Path(sys.prefix).resolve().is_relative_to(Path(plan.path))
        ):
            raise RuntimeLocationError("the active interpreter would be removed by approved worktree cleanup")
        post_digest, prospective = _post_policy(self.root, plan.source_sha, plan.target_sha)
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
        run_finish_guards(self.root, branch, plan.target_sha, plan.source_sha)
        cleanup = providers.cleanup_scopes(context, providers.cleanup_extensions())
        validate_finish(plan)
        request = IntegrationRequest(
            uuid4().hex, context, name, ident, policy_digest, post_digest, guard_identities, ready, cleanup
        )
        result = IntegrationResult(request)
        result.steps["branch_delete" if not plan.delete_branch else "marker_clear"] = "skipped"
        if plan.worktree_identity is None:
            result.steps["worktree_remove"] = "skipped"
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

    async def integrate(self, branch: str, task: Task, confirm: Confirmation) -> IntegrationResult:
        result = await asyncio.to_thread(self.prepare, branch, task)
        request = result.request
        message = request.confirmation_message()
        try:
            reply = await confirm(
                message,
                {
                    "type": "object",
                    "properties": {
                        "approve": {
                            "type": "boolean",
                            "title": "Approve this exact local integration",
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
        self._records[request.id].approved = True
        result.authority = "mcp-elicitation"
        return await asyncio.to_thread(self.resume, request.id)

    def _observe(self, request: IntegrationRequest) -> dict:
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

    def _validate(
        self,
        request: IntegrationRequest,
        *,
        merged: bool,
        removed: bool,
        finalized: bool,
        cleanup_done: set[str] | None = None,
    ) -> None:
        plan = request.context.finish
        _, current_digest = providers.policy(self.root) if not merged else (None, self._current_policy_digest())
        if current_digest != (request.post_policy_digest if merged else request.policy_digest):
            raise StaleRequestError("effective policy or installed receipt changed outside the approved merge")
        if providers.guards() != request.guards:
            raise StaleRequestError("finish guard registrations changed")
        try:
            validate_finish(plan, merged=merged, removed=removed, finalized=finalized)
        except (GitError, AdvisoryError) as exc:
            if getattr(exc, "code", "") == "WORKTREE_CONFLICT":
                raise StaleRequestError(exc.message) from exc
            raise
        ident, provider = providers.provider(request.provider)
        if ident != request.provider_identity:
            raise StaleRequestError("readiness provider installation changed")
        if not merged and providers.check(provider, request.context) != request.readiness:
            raise StaleRequestError("completion evidence changed; prepare a new request")
        extensions = providers.cleanup_extensions()
        if {name: ident for name, (ident, _) in extensions.items()} != {
            scope.extension: scope.identity for scope in request.cleanup
        }:
            raise StaleRequestError("post-finish extension installation changed")
        for scope in request.cleanup:
            if scope.extension not in (cleanup_done or set()):
                extensions[scope.extension][1].integration_validate(request.context, scope.targets)

    def _current_policy_digest(self) -> str:
        files = []
        for relative in (".devkit/config.toml", ".devkit/installation.json"):
            path = self.root / relative
            if path.is_symlink():
                raise StaleRequestError("an integration policy path became a symlink")
            files.append((relative, path.read_bytes().hex() if path.exists() else None))
        return digest(files)

    def resume(self, request_id: str) -> IntegrationResult:
        record = self._record(request_id)
        if not record.approved:
            raise AuthorityError("this request received no affirmative confirmation")
        if not record.lock.acquire(blocking=False):
            raise AuthorityError("this request is already executing; inspect it after the current call finishes")
        try:
            with file_lock(
                Path(record.result.request.context.finish.common_dir) / "devkit-integration.lock", timeout=0
            ):
                return self._execute(record)
        finally:
            record.lock.release()

    def _execute(self, record: _Record) -> IntegrationResult:
        result, request = record.result, record.result.request
        if result.status == "completed":
            return result
        plan = request.context.finish
        result.errors.clear()
        result.notices[:] = [notice for notice in result.notices if notice.code != "INTEGRATION_CLEANUP_INCOMPLETE"]
        result.failing_operation = None
        operation = "preflight"
        merged = result.steps["merge"] == "completed"
        removed = result.steps["worktree_remove"] in {"completed", "skipped"}
        try:
            observed = self._observe(request)
            if observed.get("inspection_incomplete"):
                raise StaleRequestError("Git inspection is incomplete; inspect state before further mutations")
            if result.steps["merge"] in {"unknown", "failed"}:
                if observed.get("target_sha") == plan.source_sha:
                    merged = True
                elif observed.get("target_sha") != plan.target_sha:
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
            self._validate(
                request, merged=merged, removed=removed, finalized=record.finalized, cleanup_done=cleanup_done
            )
            if merged:
                result.steps["merge"] = "completed"

            def before_step(step: str, progress: FinishResult) -> None:
                nonlocal operation
                operation = step
                self._validate(
                    request,
                    merged=merged or progress.merged,
                    removed=removed or progress.removed is True,
                    finalized=False,
                )
                result.finish = progress
                if progress.merged or merged:
                    result.steps["merge"] = "completed"
                if progress.removed is True and plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
                result.steps[step] = "running"

            if not record.finalized:
                result.finish = finish(
                    locate(self.root),
                    plan.branch,
                    merge=not merged,
                    network="forbid",
                    delete_branch=plan.delete_branch,
                    guard=lambda base, tip: run_finish_guards(self.root, plan.branch, base, tip),
                    before_step=before_step,
                )
                record.finalized = True
                result.steps["merge"] = "completed"
                if plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
                result.steps["branch_delete" if plan.delete_branch else "marker_clear"] = "completed"
            operation = "post_finish"
            self._validate(request, merged=True, removed=True, finalized=True, cleanup_done=cleanup_done)
            extensions = providers.cleanup_extensions()
            assert result.finish is not None
            for scope in request.cleanup:
                if result.cleanup_steps[scope.extension] == "completed":
                    continue
                result.cleanup_steps[scope.extension] = "running"
                outcome = extensions[scope.extension][1].integration_run(request.context, result.finish, scope.targets)
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
            if result.steps.get(operation) == "running":
                result.steps[operation] = (
                    "unknown" if isinstance(exc, GitError) and exc.returncode is None else "failed"
                )
            if result.finish:
                if result.finish.merged:
                    result.steps["merge"] = "completed"
                if result.finish.removed is True and plan.worktree_identity:
                    result.steps["worktree_remove"] = "completed"
            result.status = "partial" if any(value == "completed" for value in result.steps.values()) else "blocked"
        result.observed = self._observe(request)
        return result
