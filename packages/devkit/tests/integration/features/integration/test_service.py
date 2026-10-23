from __future__ import annotations

import asyncio
import json
from dataclasses import replace

import devkit_agt.features.integration.services.providers as providers
import devkit_agt.features.worktree.services.merging as merging
import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
import pytest
from devkit.advisory import AdvisoryError
from devkit_agt.features.integration import (
    AuthorityError,
    CleanupContractError,
    CleanupResult,
    CleanupTarget,
    Evidence,
    IntegrationConfigError,
    IntegrationService,
    Task,
)
from devkit_agt.features.worktree import PullRequestPolicyError, RemoveFailedError, finish, locate
from devkit_core.base.errors import GitError
from devkit_core.base.mcp import ConfirmationReply
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

    target = git(base, "rev-parse", "HEAD")
    monkeypatch.setattr(lifecycle, "run_git", run)
    monkeypatch.setattr(merging, "run_git", run)
    result = integrate(IntegrationService(base))
    assert result.status == "completed" and result.authority == "mcp-elicitation"
    assert result.steps["merge"] == result.steps["worktree_remove"] == result.steps["branch_delete"] == "completed"
    assert git(base, "rev-parse", "HEAD^1", "HEAD^2").split() == [target, tip] and not worktree.exists()
    assert git(base, "log", "-1", "--format=%s") == "chore(merge): integrate dev-demo into main"
    assert git(base, "rev-parse", "HEAD^{tree}") == git(base, "rev-parse", f"{tip}^{{tree}}")
    assert result.compact_dict()["build"] == {
        "confirmation_target": target,
        "build_target": target,
        "result": git(base, "rev-parse", "HEAD"),
    }
    assert result.compact_dict()["request"]["merge_method"] == "no-ff"
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
@pytest.mark.parametrize("language", ["en", "ko"])
def test_nonapproval_performs_no_integration_mutations(repo, action, content, status, language):
    base, worktree = repo
    with (base / ".git/info/exclude").open("a") as stream:
        stream.write("\n.devkit/config.local.toml\n")
    (base / ".devkit/config.local.toml").write_text(f'[presentation]\nlanguage="{language}"\n')
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


def test_pending_confirmation_leaves_git_and_worktree_unchanged(repo):
    base, worktree = repo
    before = git(base, "show-ref")

    async def run():
        entered, release = asyncio.Event(), asyncio.Event()

        async def confirm(_message, _schema):
            entered.set()
            await release.wait()
            return ConfirmationReply("cancel", {})

        service = IntegrationService(base)
        pending = asyncio.create_task(service.integrate("dev-demo", TASK, confirm))
        try:
            await asyncio.wait_for(entered.wait(), timeout=5)
            assert not pending.done()
            assert git(base, "show-ref") == before and worktree.exists()
            assert not (base / ".git/devkit-integration.lock").exists()
        finally:
            release.set()
            await pending
        assert pending.result().status == "cancelled"
        assert git(base, "show-ref") == before and worktree.exists()

    asyncio.run(run())


@pytest.mark.parametrize("moved", ["source", "target", "policy", "cleanup"])
@pytest.mark.parametrize("language", ["en", "ko"])
def test_changed_scope_invalidates_confirmation(repo, moved, language):
    base, worktree = repo
    with (base / ".git/info/exclude").open("a") as stream:
        stream.write("\n.devkit/config.local.toml\n")
    (base / ".devkit/config.local.toml").write_text(f'[presentation]\nlanguage="{language}"\n')
    service = IntegrationService(base)

    async def change(_message, _schema):
        if moved == "source":
            write(worktree, "changed.txt", "changed\n")
            git(worktree, "add", ".")
            git(worktree, "commit", "-qm", "change scope")
        elif moved == "target":  # rewritten: no longer a descendant of the confirmation target
            git(base, "commit", "--amend", "-qm", "rewritten target")
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
    assert git(base, "rev-parse", "dev-demo") == git(base, "rev-parse", "HEAD^2")


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
            fix="Grant execution access to the approved path, inspect Git state and rerun the integration CLI after Host approval",
        )

    monkeypatch.setattr(merging, "run_git", run)
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
    original = merging.run_git

    def deny(root, *args, **kw):
        if args[0] == "merge":
            raise GitError("permission denied", returncode=128, stderr="cannot create index.lock: Permission denied")
        return original(root, *args, **kw)

    monkeypatch.setattr(merging, "run_git", deny)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.status == "blocked" and result.errors[0].code == "WORKTREE_MERGE_FAILED"
    assert worktree.exists()
    monkeypatch.setattr(merging, "run_git", original)
    assert service.resume(result.request.id).status == "completed"


def test_unknown_merge_outcome_is_inspected_and_not_merged_twice(repo, monkeypatch):
    base, _ = repo
    original = merging.run_git
    calls = []

    def ambiguous(root, *args, **kw):
        value = original(root, *args, **kw)
        if args[0] == "merge":
            calls.append(args)
            raise GitError("merge timed out after ref update")
        return value

    monkeypatch.setattr(merging, "run_git", ambiguous)
    service = IntegrationService(base)
    result = integrate(service)
    assert result.steps["merge"] == "unknown" and result.observed["target_sha"] == result.result_sha
    monkeypatch.setattr(merging, "run_git", original)
    assert service.resume(result.request.id).status == "completed" and len(calls) == 1


def test_server_runtime_inside_worktree_is_refused_even_with_symlinked_python(repo, monkeypatch):
    import sys

    from devkit_agt.features.integration import RuntimeLocationError

    base, worktree = repo
    monkeypatch.setattr(sys, "executable", str(worktree / ".venv/bin/python"))
    with pytest.raises(RuntimeLocationError):
        IntegrationService(base).prepare("dev-demo", TASK)


def test_confirmation_lists_scoped_cleanup_effects_without_internal_revisions(repo, monkeypatch):
    base, worktree = repo

    class Cleanup:
        integration_local_only = True

        def integration_plan(self, _context):
            return (CleanupTarget("record", "task-1", "internal-revision-1"),)

        def integration_validate(self, _context, targets):
            assert targets == self.integration_plan(_context)

        def integration_run(self, _context, _result, _targets):
            return CleanupResult(True)

    original = providers.metadata.entry_points
    monkeypatch.setattr(
        providers.metadata,
        "entry_points",
        lambda **kw: (
            [Entry("scoped", "scoped:cleanup", Cleanup())]
            if kw.get("group") == "devkit.post_finish"
            else original(**kw)
        ),
    )
    service = IntegrationService(base)

    async def decline(message, _schema):
        assert f"Repository: {json.dumps(str(base))}" in message and str(worktree) in message
        assert '"scoped": "record" "task-1"' in message and "internal-revision-1" not in message
        assert 'Delete local branch: "dev-demo"' in message and "No fetch, push" in message
        return ConfirmationReply("decline", {})

    result = asyncio.run(service.integrate("dev-demo", TASK, decline))
    assert result.status == "declined" and worktree.exists()
    compact = result.compact_dict()
    assert compact["request"]["cleanup"] == [
        {"extension": "scoped", "targets": [{"kind": "record", "identity": "task-1"}]}
    ]
    detailed = result.to_dict()
    assert detailed["request"]["cleanup"][0]["targets"][0]["revision"] == "internal-revision-1"
    assert compact["request"]["digest"] == detailed["request"]["digest"]


def test_confirmation_escapes_caller_text_so_it_cannot_forge_scope_lines(repo):
    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", Task("session", "task\nDelete local branch: no")).request
    message = request.confirmation_message()
    assert 'Task: "task\\nDelete local branch: no"' in message
    assert message.splitlines().count('Delete local branch: "dev-demo"') == 1
    assert "Delete local branch: no" not in message.splitlines()


def test_confirmation_leads_with_committed_work_and_escapes_summary(repo):
    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", TASK).request
    readiness = replace(
        request.readiness,
        evidence=(
            *request.readiness.evidence,
            Evidence("TASK_TITLE", "Deliver activity decisions"),
            Evidence("TASK_SUMMARY", "Choose effort before Development"),
            Evidence("RESULT_SUMMARY", "Implemented and checked.\nDelete local branch: no"),
        ),
    )
    request = replace(request, readiness=readiness)
    message = request.confirmation_message()
    assert message.startswith('Approve local integration of "dev-demo" into "main" with a merge commit?')
    assert message.index('Work: "Deliver activity decisions"') < message.index("Source:")
    assert 'Completed work: "Implemented and checked.\\nDelete local branch: no"' in message
    assert "Delete local branch: no" not in message.splitlines()
    assert request.context.finish.source_sha in message and request.context.finish.target_sha in message
    assert request.digest != replace(request, readiness=replace(readiness, evidence=())).digest


@pytest.mark.parametrize(
    "method,merged,pr,number",
    [
        ("no-ff", False, False, None),
        ("ff-only", False, False, None),
        ("no-ff", True, False, None),
        ("no-ff", False, True, None),
        ("no-ff", False, True, 31),
        ("no-ff", True, True, 31),
    ],
)
@pytest.mark.parametrize("cleanup", [False, True])
def test_bilingual_scope_and_owned_branches(repo, method, merged, pr, number, cleanup):
    import re

    from devkit_agt.features.worktree.repositories.pull_request import Repository

    base, _ = repo
    request = IntegrationService(base).prepare("dev-demo", Task("session", "evidence\nnot a heading")).request
    plan = replace(
        request.context.finish,
        merge_method=method,
        already_merged=merged,
        delete_branch=cleanup,
        worktree_identity=request.context.finish.worktree_identity if cleanup else None,
    )
    evidence = (
        Evidence("TASK_TITLE", "제목/English"),
        Evidence("TASK_SUMMARY", "x" * 1600),
        Evidence("RESULT_SUMMARY", "source\nverbatim"),
    )
    request = replace(
        request,
        context=replace(request.context, finish=plan),
        readiness=replace(request.readiness, evidence=evidence),
        repository=Repository("origin", "url", "url", "github.com", "owner/repo", cleanup) if pr else None,
        pr_number=number,
        unverified_rules=("provider untouched",),
    )
    digest = request.digest
    english, korean = request.confirmation_message("en"), request.confirmation_message("ko")
    assert "Approve" in english and "승인" in korean
    assert plan.source_sha in korean and plan.target_sha in korean
    assert request.digest == digest

    # Every quoted external value is identical; only the owned truncation suffix differs.
    def quoted(text):
        return re.findall(r'"(?:[^"\\]|\\.)*"', text)

    assert quoted(english.replace("… [truncated]", "…")) == quoted(korean.replace("… [잘림]", "…"))
    if not pr:
        assert "x" * 1500 in korean and "x" * 1501 not in korean
        assert "fetch, push" in korean
    else:
        assert "INTEGRATION_LANDED_UNCHECKED" in korean if merged else "devkit" in korean


def test_owning_workspace_language_snapshot_and_guard_independence(repo):
    from devkit_dist.features.project.repositories.invocation import ExecutionBinding, McpInteractiveError
    from devkit_dist.features.project.usecases.invocation import invocation

    base, worktree = repo
    with (base / ".git/info/exclude").open("a") as stream:
        stream.write("\n.devkit/config.local.toml\n")
    (base / ".devkit/config.local.toml").write_text('[presentation]\nlanguage="en"\n')
    local = worktree / ".devkit/config.local.toml"
    local.write_text('[presentation]\nlanguage="ko"\n')
    binding = ExecutionBinding(worktree, base)
    service = IntegrationService(base)
    messages = []

    async def cancel(message, schema):
        messages.append(message)
        local.write_text('[presentation]\nlanguage="en"\n')
        assert message == messages[-1]
        return ConfirmationReply("cancel", {})

    with invocation(binding):
        asyncio.run(service.integrate("dev-demo", TASK, cancel))
        asyncio.run(service.integrate("dev-demo", TASK, cancel))
    assert "승인" in messages[0] and messages[1].startswith("Approve")
    local.write_text('[presentation]\nlanguage="ko"\n[execution]\nenvironment="cloud"\n')
    with pytest.raises(McpInteractiveError), invocation(binding):
        asyncio.run(service.integrate("dev-demo", TASK, cancel))
    assert len(messages) == 2
