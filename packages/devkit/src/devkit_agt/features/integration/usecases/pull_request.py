"""Process-local approved PR execution; only this executor performs remote mutations."""

from __future__ import annotations

import re
import sys
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from devkit.advisory import AdvisoryError, Level
from devkit_core.core.git import run_git
from devkit_dist.features.project.repositories.invocation import capture_terminal_removal, guard_execution
from devkit_dist.features.project.repositories.project import read_project_config

import devkit_agt.features.integration.repositories.receipts as receipts
import devkit_agt.features.integration.services.providers as providers
from devkit_agt.features.integration.models.contracts import (
    IntegrationContext,
    IntegrationRequest,
    IntegrationResult,
    Task,
)
from devkit_agt.features.integration.models.errors import IntegrationConfigError, StaleRequestError
from devkit_agt.features.worktree import (
    FinishResult,
    build_result,
    fast_forward,
    finish,
    integration_lock,
    is_ancestor,
    locate,
    plan_finish,
    run_finish_guards,
    validate_finish,
)
from devkit_agt.features.worktree.repositories.pull_request import GitHub, PullRequestError

if TYPE_CHECKING:
    from devkit_agt.features.integration.usecases.service import IntegrationService, _Record


def _git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode("utf-8", errors="surrogateescape").strip()


def _error(
    code: str,
    message: str,
    fix: str = "Inspect Git and PR state, preserve completed steps, then rerun `devkit integration integrate --route pull-request` after Host approval",
) -> PullRequestError:
    return PullRequestError(code, message, fix)


def _port(service: IntegrationService) -> GitHub:
    return service.github


def _policy(root: Path, sha: str) -> dict[str, Any]:
    config = providers.commit_config(root, sha)
    return read_project_config(root) if config is None else config


def _pr_identity(pr: dict[str, Any], branch: str, target: str) -> None:
    if pr.get("isCrossRepository"):
        raise _error("INTEGRATION_REMOTE_UNSUPPORTED", "Fork PRs are unsupported")
    if (
        pr.get("isDraft")
        or pr.get("baseRefName") != target
        or pr.get("headRefName") != branch
        or pr.get("state") == "CLOSED"
    ):
        raise _error("INTEGRATION_PR_CONFLICT", "PR draft, base, head or closed state conflicts with approved scope")


def prepare(service: IntegrationService, branch: str, task: Task) -> IntegrationResult:
    guard_execution()
    root, port = service.root, _port(service)
    port.begin_call()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}", task.id):
        raise IntegrationConfigError("PR task id must be an identifier, not free-form published text")
    position = locate(root)
    if position.branch is None:
        raise _error("INTEGRATION_TARGET_UPSTREAM", "Target checkout is detached")
    target = position.branch
    try:
        remote = _git(root, "config", "--get", f"branch.{target}.remote")
        remote_ref = _git(root, "config", "--get", f"branch.{target}.merge")
    except AdvisoryError as exc:
        raise _error(
            "INTEGRATION_TARGET_UPSTREAM",
            "Target has no remote upstream",
            "Set a same-named target upstream and prepare again",
        ) from exc
    if not remote or remote == "." or remote.startswith("-") or remote_ref != f"refs/heads/{target}":
        raise _error(
            "INTEGRATION_TARGET_UPSTREAM",
            "Target requires a same-named remote upstream",
            "Configure the target upstream with the same branch name and prepare again",
        )
    repository = port.resolve(remote)
    guard_execution()
    target_sha = port.fetch(repository, target)
    local_target = _git(root, "rev-parse", "HEAD")
    if not is_ancestor(root, local_target, target_sha):
        raise _error(
            "INTEGRATION_TARGET_UPSTREAM",
            "Local target has unpublished or divergent commits",
            "Publish or reconcile local target commits before preparing again",
        )
    target_config = _policy(root, target_sha)
    target_policy = providers.effective(target_config)
    source = _git(root, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    source_config = _policy(root, source)
    source_policy = providers.effective(source_config)
    if any(
        type(policy["delete_branch"]) is not bool
        or policy["merge"] not in {"no-ff", "ff-only"}
        or policy["pull_request"] not in {"auto", "required"}
        for policy in (target_policy, source_policy)
    ):
        raise IntegrationConfigError("Invalid source or target worktree policy")
    if target_policy["merge"] == "ff-only" or source_policy["merge"] == "ff-only":
        raise _error("INTEGRATION_MERGE_COMMIT_FORBIDDEN", "Effective policy forbids a merge commit")
    remote_rules = port.rules(repository, target)
    candidates = port.find(repository, branch)
    opened = [pr for pr in candidates if pr["state"] == "OPEN"]
    matched = opened or [
        pr
        for pr in candidates
        if pr["state"] == "MERGED" and pr["baseRefName"] == target and pr["headRefOid"] == source
    ]
    if len(opened) > 1:
        raise _error("INTEGRATION_PR_CONFLICT", "Multiple open PRs use this head")
    pr = matched[0] if matched else None
    if pr:
        _pr_identity(pr, branch, target)
    plan = plan_finish(position, branch, delete_branch=False, target_sha=target_sha)
    if plan.worktree_identity and (
        Path(sys.executable).absolute().is_relative_to(plan.path)
        or Path(sys.prefix).resolve().is_relative_to(plan.path)
    ):
        raise _error("INTEGRATION_RUNTIME_IN_WORKTREE", "Runtime is inside the cleanup target")
    already = bool(pr and pr["state"] == "MERGED")
    if already:
        assert pr is not None
        merge_oid = (pr.get("mergeCommit") or {}).get("oid")
        if merge_oid:
            guard_execution()
            port.fetch_commit(repository, merge_oid)
        _confirmed(root, pr, source)
        if not is_ancestor(root, source, target_sha):
            raise _error("INTEGRATION_SOURCE_NOT_CONTAINED", "Fetched target lacks approved source")
    elif not is_ancestor(root, target_sha, source):
        raise _error(
            "WORKTREE_MERGE_NOT_FF",
            "Source must contain the fetched confirmation target",
            "Merge the target into the source, re-verify and prepare again; do not rebase",
        )
    remote_source = port.ref(repository, f"refs/heads/{branch}")
    if remote_source and remote_source != source:
        guard_execution()
        fetched_source = port.fetch(repository, branch)
        if fetched_source != remote_source or not is_ancestor(root, remote_source, source):
            raise _error(
                "INTEGRATION_REMOTE_BRANCH_DIVERGED", "Remote source is not an ancestor of the approved source"
            )
    plan = replace(
        plan,
        already_merged=already,
        delete_branch=bool(target_policy["delete_branch"] and (already or source_policy["delete_branch"])),
    )
    name = target_policy["provider"]
    if not isinstance(name, str) or not providers.NAME.fullmatch(name) or target_policy["dev-integration"] != "ask":
        raise IntegrationConfigError("Remote target requires a configured provider and dev-integration=ask")
    context = IntegrationContext(plan, task)
    ident, provider = providers.provider(name)
    ready = providers.check(provider, context)
    if not isinstance(ready.landed_check, str) or not ready.landed_check.strip():
        raise IntegrationConfigError("PR integration requires the provider to declare a landed-target check")
    run_finish_guards(root, branch, source if already else target_sha, source)
    cleanup = providers.cleanup_scopes(context, providers.cleanup_extensions())
    validate_finish(plan, target=local_target, check_upstream=False)
    request = IntegrationRequest(
        uuid4().hex,
        context,
        name,
        ident,
        providers.policy_digest(target_config),
        providers.policy_digest(target_config if already else source_config),
        providers.guards(),
        ready,
        cleanup,
        "pull-request",
        repository,
        pr["number"] if pr else None,
        local_target,
        tuple(r["type"] for r in remote_rules if r["type"].startswith("unverified")),
    )
    result = IntegrationResult(request)
    result.observed["unverified_rules"] = [r["type"] for r in remote_rules if r["type"].startswith("unverified")]
    result.steps = dict.fromkeys(
        (
            "push",
            "pull_request",
            "merge",
            "fetch",
            "local_fast_forward",
            "worktree_remove",
            "branch_delete",
            "marker_clear",
            "remote_delete",
            "post_finish",
        ),
        "not_run",
    )
    if already:
        result.steps.update(push="completed", pull_request="completed", merge="completed")
    result.pull_request = dict(pr or {})
    result.cleanup_steps = {scope.extension: "not_run" for scope in cleanup}
    return result


def observe(service: IntegrationService, request: IntegrationRequest) -> dict[str, Any]:
    repository = request.repository
    assert repository is not None
    port = _port(service)
    port.begin_call()
    plan = request.context.finish
    return {
        "remote_target": port.ref(repository, f"refs/heads/{plan.target_branch}"),
        "remote_source": port.ref(repository, f"refs/heads/{plan.branch}"),
        "pull_requests": port.find(repository, plan.branch),
    }


def _confirmed(root: Path, pr: dict[str, Any], source: str) -> tuple[str, str, str]:
    merge = (pr.get("mergeCommit") or {}).get("oid")
    if pr.get("state") != "MERGED" or not merge:
        raise _error("INTEGRATION_MERGE_UNCONFIRMED", "PR has no confirmed merge commit")
    parents = _git(root, "rev-list", "--parents", "-n", "1", merge).split()
    if len(parents) != 3 or parents[2] != source:
        raise _error(
            "INTEGRATION_MERGE_UNCONFIRMED",
            "PR merge second parent differs from approved source",
            "Report the unconfirmed merge to the user and retain the branches; clean up outside this route",
        )
    return merge, parents[1], _git(root, "rev-parse", f"{merge}^{{tree}}")


def _checks(port: GitHub, request: IntegrationRequest, pr: dict[str, Any]) -> list[str]:
    repository = request.repository
    assert repository is not None
    checks = port.checks(repository, pr["number"])
    if (
        pr.get("mergeable") == "CONFLICTING"
        or pr.get("reviewDecision") == "CHANGES_REQUESTED"
        or any(c["bucket"] in {"fail", "cancel"} for c in checks)
    ):
        raise _error(
            "INTEGRATION_MERGE_REFUSED",
            "Required check, review or merge conflict refuses the merge",
            "Inspect the PR failure, fix the source, re-verify and prepare a new request",
        )
    pending = [c["name"] for c in checks if c["bucket"] not in {"pass", "skipping"}]
    if pr.get("reviewDecision") == "REVIEW_REQUIRED":
        pending.append("required review")
    if pr.get("mergeable") != "MERGEABLE" or pr.get("mergeStateStatus") not in {"CLEAN", "HAS_HOOKS", "UNSTABLE"}:
        pending.append("platform mergeability or protection")
    return pending


def _validate(service: IntegrationService, result: IntegrationResult, *, merged: bool, finalized: bool = False) -> None:
    request = result.request
    plan = request.context.finish
    assert request.repository is not None
    _port(service).validate(request.repository)
    validate_finish(
        plan,
        merged=merged,
        removed=result.steps["worktree_remove"] == "completed",
        finalized=finalized,
        target=request.local_target,
        check_upstream=False,
    )
    if providers.guards() != request.guards or providers.provider(request.provider)[0] != request.provider_identity:
        raise StaleRequestError("Installed guard or readiness provider changed")
    extensions = providers.cleanup_extensions()
    if {n: i for n, (i, _) in extensions.items()} != {s.extension: s.identity for s in request.cleanup}:
        raise StaleRequestError("Cleanup extension installation changed")
    for scope in request.cleanup:
        if result.cleanup_steps[scope.extension] != "completed":
            extensions[scope.extension][1].integration_validate(service._context(result), scope.targets)


def execute(service: IntegrationService, record: _Record, wait: float, approving: bool) -> IntegrationResult:
    result, request, root = record.result, record.result.request, service.root
    if result.status == "completed":
        return result
    guard_execution()
    plan, repository, port = request.context.finish, request.repository, _port(service)
    assert repository is not None
    port.begin_call()
    result.errors.clear()
    result.notices.clear()
    operation = "preflight"
    try:
        # Publication is outside the repository lock. Re-read the exact bound PR before any write.
        if result.steps["push"] != "completed":
            _validate(service, result, merged=False)
            found = [pr for pr in port.find(repository, plan.branch) if pr["state"] == "OPEN"]
            if (request.pr_number is None and found) or (
                request.pr_number is not None and (len(found) != 1 or found[0]["number"] != request.pr_number)
            ):
                raise _error("INTEGRATION_PR_CONFLICT", "PR identity changed after preparation")
            if found:
                _pr_identity(found[0], plan.branch, plan.target_branch)
            operation = "push"
            prior_unknown = result.steps[operation] == "unknown"
            if prior_unknown and port.ref(repository, f"refs/heads/{plan.branch}") != plan.source_sha:
                raise _error(
                    "INTEGRATION_STEP_UNKNOWN",
                    "Prior push remains unconfirmed; inspect remote state before new authority",
                )
            result.steps[operation] = "unknown"
            if port.ref(repository, f"refs/heads/{plan.branch}") != plan.source_sha:
                guard_execution()
                port.push(repository, plan.source_sha, plan.branch)
            if port.ref(repository, f"refs/heads/{plan.branch}") != plan.source_sha:
                raise _error("INTEGRATION_STEP_UNKNOWN", "Push outcome is not confirmed")
            result.steps[operation] = "completed"
        if result.steps["pull_request"] != "completed":
            operation = "pull_request"
            if request.pr_number:
                pr = port.view(repository, request.pr_number)
            else:
                if result.steps[operation] == "unknown":
                    candidates = [p for p in port.find(repository, plan.branch) if p["state"] == "OPEN"]
                    if len(candidates) != 1:
                        raise _error("INTEGRATION_STEP_UNKNOWN", "PR creation outcome remains unknown")
                    pr = candidates[0]
                else:
                    result.steps[operation] = "unknown"
                    guard_execution()
                    port.create(repository, plan.branch, plan.target_branch, request.context.task.id)
                    candidates = [p for p in port.find(repository, plan.branch) if p["state"] == "OPEN"]
                    if len(candidates) != 1:
                        raise _error("INTEGRATION_STEP_UNKNOWN", "PR creation outcome is not confirmed")
                    pr = candidates[0]
            _pr_identity(pr, plan.branch, plan.target_branch)
            result.pull_request = pr
            result.steps[operation] = "completed"
        operation = "lock"
        with integration_lock(Path(plan.common_dir), timeout=wait):
            guard_execution()
            if result.steps["worktree_remove"] == "unknown" and not Path(plan.path).exists():
                entries = _git(root, "worktree", "list", "--porcelain", "-z").split("\0")
                if f"worktree {plan.path}" not in entries:
                    result.steps["worktree_remove"] = "completed"
            if result.steps["branch_delete"] == "unknown" and result.steps["worktree_remove"] == "completed":
                refs = _git(root, "for-each-ref", "--format=%(refname)", f"refs/heads/{plan.branch}")
                if not refs:
                    record.finalized = True
                    result.steps["branch_delete"] = "completed"
                    result.finish = FinishResult(
                        plan.branch, Path(plan.path), merged=True, removed=True, branch_deleted=True
                    )
            operation = "merge"
            pr = port.view(repository, result.pull_request["number"])
            _pr_identity(pr, plan.branch, plan.target_branch)
            if pr["headRefOid"] != plan.source_sha:
                raise _error("INTEGRATION_REMOTE_BRANCH_DIVERGED", "PR head changed after approval")
            guard_execution()
            target = port.fetch(repository, plan.target_branch)
            if pr["state"] != "MERGED":
                if result.steps["merge"] == "unknown":
                    raise _error("INTEGRATION_STEP_UNKNOWN", "Prior merge remains unconfirmed; no destructive retry")
                _validate(service, result, merged=False)
                if not is_ancestor(root, plan.target_sha, target):
                    raise _error("INTEGRATION_TARGET_MOVED", "Target rewrote the confirmation history")
                if (result.build_target is not None and target != result.build_target) or (
                    not approving and result.build_target is None and target != plan.target_sha
                ):
                    raise _error(
                        "INTEGRATION_TARGET_MOVED",
                        "Target moved while waiting",
                        "Merge the target into the source, re-verify and prepare again; report repeated target movement to the user",
                    )
                if providers.policy_digest(_policy(root, target)) != request.policy_digest:
                    raise StaleRequestError("Remote target effective policy changed")
                if result.result_sha is None or not result.build_checked:
                    result.build_checked = False
                    result.build_target = target
                    guard_execution()
                    result.result_sha = build_result(
                        root,
                        branch=plan.branch,
                        target_branch=plan.target_branch,
                        target=target,
                        source=plan.source_sha,
                        method="no-ff",
                        advance=True,
                    )
                    context = service._context(result)
                    run_finish_guards(
                        root, plan.branch, _git(root, "merge-base", target, plan.source_sha), plan.source_sha
                    )
                    ready = providers.check(providers.provider(request.provider)[1], context)
                    if (
                        ready.comparable() != request.readiness.comparable()
                        or providers.policy_digest(_policy(root, result.result_sha)) != request.post_policy_digest
                    ):
                        raise StaleRequestError("Prospective merge changes approved policy or completion evidence")
                    receipts.check_merge(root, result.result_sha, (target, plan.source_sha))
                    result.build_checked = True
                pending = _checks(port, request, pr)
                if pending:
                    notice = _error(
                        "INTEGRATION_CHECKS_PENDING",
                        "Pending: " + ", ".join(pending),
                        f"Wait with `gh pr checks {pr['number']} -R {repository.selector} --watch` using an agent bound, then inspect the PR and rerun `devkit integration integrate {plan.branch} --task-kind <kind> --task-id <id> --route pull-request` after Host approval; report checks that do not start",
                    )
                    notice.level = Level.NOTICE
                    result.notices.append(notice)
                    result.pull_request = pr
                    result.status = "pending"
                    result.steps["merge"] = "not_run"
                    return result
                if port.ref(repository, f"refs/heads/{plan.target_branch}") != target:
                    raise _error("INTEGRATION_TARGET_MOVED", "Target moved after the checked build")
                result.steps["merge"] = "unknown"
                guard_execution()
                response = port.merge(
                    repository, pr["number"], plan.source_sha, plan.branch, plan.target_branch, request.context.task.id
                )
                pr = port.view(repository, pr["number"])
                if pr["state"] != "MERGED" and response.http_status in {403, 405, 409, 422}:
                    result.steps["merge"] = "failed"
                    raise _error(
                        "INTEGRATION_MERGE_REFUSED",
                        f"Platform rejected merge with HTTP {response.http_status}",
                        "Inspect platform policy and head state, resolve the refusal and prepare again",
                    )
                if pr["state"] != "MERGED":
                    raise _error("INTEGRATION_STEP_UNKNOWN", "Platform merge outcome is not confirmed")
                guard_execution()
                target = port.fetch(repository, plan.target_branch)
            result.pull_request = pr
            merge_oid = (pr.get("mergeCommit") or {}).get("oid")
            if merge_oid:
                try:
                    _git(root, "cat-file", "-t", merge_oid)
                except AdvisoryError:
                    guard_execution()
                    port.fetch_commit(repository, merge_oid)
            merge, parent, tree = _confirmed(root, pr, plan.source_sha)
            result.steps["merge"] = "completed"
            operation = "fetch"
            result.steps["fetch"] = "completed"
            if not is_ancestor(root, plan.source_sha, target):
                raise _error(
                    "INTEGRATION_SOURCE_NOT_CONTAINED",
                    "Fetched target does not contain approved source",
                    "Keep the branches and report to the user; resume once the fetched target contains the source",
                )
            reason = None
            if not result.build_checked or result.build_target is None or result.result_sha is None:
                reason = "not-recorded"
            elif not is_ancestor(root, merge, target):
                reason = "merge-not-contained"
            elif not is_ancestor(root, plan.target_sha, parent):
                reason = "rewritten-base"
            elif parent != result.build_target:
                reason = "advanced"
            elif tree != _git(root, "rev-parse", f"{result.result_sha}^{{tree}}"):
                reason = "tree-mismatch"
            result.landing = {
                "checked": reason is None,
                "reason": reason,
                "merge": merge,
                "first_parent": parent,
                "fetched_target": target,
            }
            if reason:
                notice = _error(
                    "INTEGRATION_LANDED_UNCHECKED",
                    f"Landing was not checked: {reason}",
                    f"After cleanup run {request.readiness.landed_check} in {plan.base}; do not report integration as checked; fix failures in a new unit",
                )
                notice.level = Level.WARNING
                result.notices.append(notice)
            operation = "local_fast_forward"
            if (
                _git(root, "status", "--porcelain")
                or _git(root, "symbolic-ref", "HEAD") != f"refs/heads/{plan.target_branch}"
            ):
                raise _error(
                    "INTEGRATION_LOCAL_TARGET_BLOCKED",
                    "Base checkout is dirty or on another branch",
                    "Make the base checkout clean on the target branch, inspect the merged PR and rerun `devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` after Host approval",
                )
            if not is_ancestor(root, _git(root, "rev-parse", "HEAD"), target):
                raise _error(
                    "INTEGRATION_LOCAL_TARGET_BLOCKED",
                    "Local target cannot fast-forward",
                    "Make the base checkout clean and fast-forwardable, inspect the merged PR and rerun `devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` after Host approval",
                )
            validate_finish(
                plan,
                target=_git(root, "rev-parse", "HEAD"),
                removed=result.steps["worktree_remove"] == "completed",
                finalized=record.finalized,
                check_upstream=False,
            )
            guard_execution()
            fast_forward(root, target)
            result.steps[operation] = "completed"
            _validate(service, result, merged=True, finalized=record.finalized)
            operation = "remote_delete"
            if plan.delete_branch and result.steps[operation] != "completed":
                remote_source = port.ref(repository, f"refs/heads/{plan.branch}")
                if remote_source:
                    if remote_source != plan.source_sha or port.dependents(repository, plan.branch):
                        raise _error(
                            "INTEGRATION_REMOTE_DELETE_BLOCKED",
                            "Remote source moved or is the base of an open PR",
                            "Inspect the lease and dependent PRs; preserve the local and remote branches, resolve the blocker, then prepare and approve a fresh CLI cleanup request",
                        )
                    result.steps[operation] = "unknown"
                    guard_execution(terminal=record.finalized)
                    port.delete(repository, plan.source_sha, plan.branch)
                    if port.ref(repository, f"refs/heads/{plan.branch}") is not None:
                        raise _error("INTEGRATION_STEP_UNKNOWN", "Remote deletion is unconfirmed")
                result.steps[operation] = "completed"
            if not record.finalized:
                _validate(service, result, merged=True)

                def before_step(step: str, progress: FinishResult) -> None:
                    nonlocal operation
                    operation = step
                    guard_execution(terminal=bool(progress.removed))
                    if step == "worktree_remove" and approving:
                        capture_terminal_removal(Path(plan.path))
                    if progress.removed:
                        result.steps["worktree_remove"] = "completed"
                    _validate(service, result, merged=True)
                    result.steps[step] = "unknown"

                result.finish = finish(
                    locate(root),
                    plan.branch,
                    network="forbid",
                    delete_branch=plan.delete_branch,
                    before_step=before_step,
                )
                record.finalized = True
                result.steps["worktree_remove"] = "completed"
                result.steps["branch_delete" if plan.delete_branch else "marker_clear"] = "completed"
            _validate(service, result, merged=True, finalized=True)
            operation = "post_finish"
            assert result.finish is not None
            for scope in request.cleanup:
                if result.cleanup_steps[scope.extension] != "completed":
                    guard_execution(terminal=True)
                    done = providers.cleanup_extensions()[scope.extension][1].integration_run(
                        service._context(result), result.finish, scope.targets
                    )
                    result.notices.extend(done.notices)
                    if not done.done:
                        raise _error(
                            "INTEGRATION_CLEANUP_INCOMPLETE",
                            "Scoped cleanup is incomplete",
                            "Inspect Git, PR and cleanup state, then rerun `devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` after Host approval",
                        )
                    result.cleanup_steps[scope.extension] = "completed"
            result.steps[operation] = "completed"
            result.status = "completed"
    except (AdvisoryError, OSError, ValueError, KeyError) as exc:
        if getattr(exc, "code", "") == "LOCK_HELD" and not approving:
            raise
        error = exc if isinstance(exc, AdvisoryError) else _error("INTEGRATION_STEP_UNKNOWN", str(exc))
        result.errors.append(error)
        result.failing_operation = operation
        result.status = "partial" if any(s == "completed" for s in result.steps.values()) else "blocked"
        if result.steps.get(operation) != "unknown":
            result.steps[operation] = "failed"
    return result
