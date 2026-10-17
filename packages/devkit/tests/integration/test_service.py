from __future__ import annotations

import asyncio

import pytest
from devkit.advisory import AdvisoryError
from devkit.core.errors import GitError
from devkit.host.mcp import ConfirmationReply
from devkit.integration import (
    AuthorityError,
    CleanupContractError,
    CleanupResult,
    CleanupTarget,
    IntegrationConfigError,
    IntegrationService,
    Task,
    providers,
)
from devkit.worktree import (
    PullRequestPolicyError,
    RemoveFailedError,
    finish,
    lifecycle,
    locate,
)
from testsupport.rules import git, write

from .conftest import Entry

TASK = Task("session", "fixture-task")


async def approve(_message: str, _schema: dict) -> ConfirmationReply:
    return ConfirmationReply("accept", {"approve": True})


def integrate(service: IntegrationService):
    return asyncio.run(service.integrate("dev-demo", TASK, approve))


def test_native_approval_integrates_and_cleans_without_network(repo, monkeypatch):
    base, worktree = repo
    git(base, "remote", "add", "origin", "unreachable://fixture")
    git(base, "config", "branch.main.remote", "origin")
    git(base, "config", "branch.main.merge", "refs/heads/main")
    tip = git(worktree, "rev-parse", "HEAD")
    called = []
    original = lifecycle.run_git

    def run(root, *args, **kw):
        called.append(args[0])
        return original(root, *args, **kw)

    monkeypatch.setattr(lifecycle, "run_git", run)
    result = integrate(IntegrationService(base))
    assert result.status == "completed" and result.authority == "mcp-elicitation"
    assert result.steps["merge"] == result.steps["worktree_remove"] == result.steps["branch_delete"] == "completed"
    assert git(base, "rev-parse", "HEAD") == tip and not worktree.exists()
    assert "refs/heads/dev-demo" not in git(base, "show-ref")
    assert "merge" in called and not set(called) & {"fetch", "push", "ls-remote"}
    assert result.to_dict()["network_operations"] == "excluded"


@pytest.mark.parametrize(
    "action,content,status",
    [
        ("accept", {"approve": False}, "not_approved"),
        ("accept", {}, "not_approved"),
        ("accept", {"approve": "true"}, "not_approved"),
        ("decline", {}, "declined"),
        ("cancel", {}, "cancelled"),
    ],
)
def test_nonapproval_performs_no_integration_mutations(repo, action, content, status):
    base, worktree = repo
    before = git(base, "show-ref")

    async def reply(_message, schema):
        assert schema["properties"]["approve"]["default"] is False
        return ConfirmationReply(action, content)

    service = IntegrationService(base)
    result = asyncio.run(service.integrate("dev-demo", TASK, reply))
    assert result.status == status and result.authority == "none"
    assert git(base, "show-ref") == before and worktree.exists()
    assert not (base / ".git/devkit-integration.lock").exists()
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_prepared_request_is_not_authority_and_cannot_cross_process(repo):
    base, _ = repo
    service = IntegrationService(base)
    result = service.prepare("dev-demo", TASK)
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)
    with pytest.raises(AuthorityError):
        IntegrationService(base).inspect(result.request.id)


@pytest.mark.parametrize("moved", ["source", "target", "policy", "cleanup"])
def test_changed_scope_invalidates_confirmation(repo, moved):
    base, worktree = repo
    service = IntegrationService(base)

    async def change(_message, _schema):
        if moved in {"source", "target"}:
            root = worktree if moved == "source" else base
            write(root, "changed.txt", "changed\n")
            git(root, "add", ".")
            git(root, "commit", "-qm", "change scope")
        elif moved == "policy":
            write(base, ".devkit/config.toml", '[integration]\nprovider = "other"\n')
        else:
            git(base, "worktree", "move", str(worktree), str(worktree.with_name("moved")))
        return await approve(_message, _schema)

    result = asyncio.run(service.integrate("dev-demo", TASK, change))
    assert result.status == "blocked" and result.errors
    assert result.steps["merge"] == "not_run"


def test_review_readiness_is_rechecked_after_confirmation(repo, ready_provider):
    base, worktree = repo

    async def change(message, schema):
        ready_provider.allowed = False
        return await approve(message, schema)

    result = asyncio.run(IntegrationService(base).integrate("dev-demo", TASK, change))
    assert result.status == "blocked" and result.errors[0].code == "INTEGRATION_NOT_READY"
    assert worktree.exists()


@pytest.mark.parametrize("dirty", ["base", "source", "locked"])
def test_preflight_preserves_dirty_or_locked_worktrees(repo, dirty):
    base, worktree = repo
    if dirty == "locked":
        git(base, "worktree", "lock", str(worktree))
    else:
        write(base if dirty == "base" else worktree, "untracked.txt", "preserve\n")
    with pytest.raises(AdvisoryError):
        IntegrationService(base).prepare("dev-demo", TASK)
    assert worktree.exists()


def test_required_pr_blocks_local_execution(repo):
    base, _ = repo
    write(base, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n[worktree]\npull_request = "required"\n')
    git(base, "add", ".")
    git(base, "commit", "-qm", "require PR")
    with pytest.raises(PullRequestPolicyError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_delete_branch_false_is_preserved(repo):
    base, worktree = repo
    for root in (base, worktree):
        write(root, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n[worktree]\ndelete_branch = false\n')
        git(root, "add", ".")
        git(root, "commit", "-qm", "keep branch")
    git(worktree, "merge", "--no-edit", "main")
    result = integrate(IntegrationService(base))
    assert result.status == "completed" and result.steps["branch_delete"] == "skipped"
    assert result.steps["marker_clear"] == "completed" and not worktree.exists()
    assert git(base, "rev-parse", "dev-demo") == git(base, "rev-parse", "HEAD")


def test_merge_then_permission_failure_resumes_cleanup_without_second_merge_or_approval(repo, monkeypatch):
    base, worktree = repo
    original_remove, original_git = lifecycle._remove, lifecycle.run_git
    merged = []

    def run(root, *args, **kw):
        if args[0] == "merge":
            merged.append(args)
        return original_git(root, *args, **kw)

    def deny(_base, _path):
        raise RemoveFailedError(
            "permission denied",
            fix="Grant execution access to the approved path, then call integration_resume with the same request id",
        )

    monkeypatch.setattr(lifecycle, "run_git", run)
    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "partial" and result.steps["merge"] == "completed" and worktree.exists()
    assert result.failing_operation == "worktree_remove" and result.errors[0].code == "WORKTREE_REMOVE_FAILED"
    monkeypatch.setattr(lifecycle, "_remove", original_remove)
    result = service.resume(result.request.id)
    assert result.status == "completed" and not worktree.exists() and len(merged) == 1


def test_unscoped_post_finish_extension_blocks_before_approval(repo, monkeypatch):
    base, _ = repo
    original = providers.metadata.entry_points
    monkeypatch.setattr(
        providers.metadata,
        "entry_points",
        lambda **kw: (
            [Entry("legacy", "legacy:cleanup", lambda *args: None)]
            if kw.get("group") == "devkit.post_finish"
            else original(**kw)
        ),
    )
    with pytest.raises(CleanupContractError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_scoped_cleanup_receives_exact_targets_and_can_resume_after_git_is_finished(repo, monkeypatch):
    base, _ = repo

    class Cleanup:
        integration_local_only = True
        attempts = 0

        def integration_plan(self, _context):
            return (CleanupTarget("record", "task-1", "revision-1"),)

        def integration_validate(self, _context, targets):
            assert targets == self.integration_plan(_context)

        def integration_run(self, _context, result, targets):
            assert result.branch == "dev-demo" and targets[0].identity == "task-1"
            self.attempts += 1
            return CleanupResult(self.attempts > 1)

    cleanup = Cleanup()
    original = providers.metadata.entry_points
    monkeypatch.setattr(
        providers.metadata,
        "entry_points",
        lambda **kw: (
            [Entry("scoped", "scoped:cleanup", cleanup)] if kw.get("group") == "devkit.post_finish" else original(**kw)
        ),
    )
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "partial" and result.steps["merge"] == "completed"
    result = service.resume(result.request.id)
    assert result.status == "completed" and cleanup.attempts == 2


def test_missing_provider_configuration_fails_closed(repo):
    base, _ = repo
    write(base, ".devkit/config.toml", "")
    with pytest.raises(IntegrationConfigError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_public_local_only_finish_excludes_fetch_and_push(repo):
    base, worktree = repo
    git(base, "remote", "add", "origin", "unreachable://fixture")
    git(base, "config", "branch.main.remote", "origin")
    git(base, "config", "branch.main.merge", "refs/heads/main")
    result = finish(locate(base), "dev-demo", merge=True, network="forbid")
    assert result.merged and result.push == "excluded" and not worktree.exists()


def test_merge_permission_failure_has_correct_remedy_and_retains_authority(repo, monkeypatch):
    base, worktree = repo
    original = lifecycle.run_git

    def deny(root, *args, **kw):
        if args[0] == "merge":
            raise GitError("permission denied", returncode=128, stderr="cannot create index.lock: Permission denied")
        return original(root, *args, **kw)

    monkeypatch.setattr(lifecycle, "run_git", deny)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "blocked" and result.errors[0].code == "WORKTREE_MERGE_FAILED"
    assert worktree.exists()
    monkeypatch.setattr(lifecycle, "run_git", original)
    assert service.resume(result.request.id).status == "completed"


def test_unknown_merge_outcome_is_inspected_and_not_merged_twice(repo, monkeypatch):
    base, _ = repo
    original = lifecycle.run_git
    calls = []

    def ambiguous(root, *args, **kw):
        value = original(root, *args, **kw)
        if args[0] == "merge":
            calls.append(args)
            raise GitError("merge timed out after ref update")
        return value

    monkeypatch.setattr(lifecycle, "run_git", ambiguous)
    service = IntegrationService(base)
    result = integrate(service)
    assert (
        result.steps["merge"] == "unknown" and result.observed["target_sha"] == result.request.context.finish.source_sha
    )
    monkeypatch.setattr(lifecycle, "run_git", original)
    assert service.resume(result.request.id).status == "completed" and len(calls) == 1


def test_server_runtime_inside_worktree_is_refused_even_with_symlinked_python(repo, monkeypatch):
    import sys

    from devkit.integration import RuntimeLocationError

    base, worktree = repo
    monkeypatch.setattr(sys, "executable", str(worktree / ".venv/bin/python"))
    with pytest.raises(RuntimeLocationError):
        IntegrationService(base).prepare("dev-demo", TASK)
