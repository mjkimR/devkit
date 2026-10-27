from __future__ import annotations

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
from testsupport.rules import git, write

from .conftest import Entry

TASK = Task("session", "fixture-task")


def integrate(service: IntegrationService):
    """One Host-approved CLI invocation: the digest pins the scope presented by prepare."""
    digest = service.prepare("dev-demo", TASK).request.digest
    return service.execute_cli("dev-demo", TASK, expected_digest=digest)


def test_host_approved_cli_integrates_and_cleans_without_network(repo, monkeypatch):
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
    assert result.status == "completed" and result.authority == "host-conversation"
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


def test_ask_cli_without_the_presented_digest_has_no_authority(repo):
    base, worktree = repo
    before = git(base, "show-ref")
    with pytest.raises(AuthorityError):
        IntegrationService(base).execute_cli("dev-demo", TASK)
    assert git(base, "show-ref") == before and worktree.exists()
    assert not (base / ".git/devkit-integration.lock").exists()


@pytest.mark.parametrize("moved", ["source", "target", "policy", "cleanup"])
def test_changed_scope_invalidates_the_presented_digest(repo, moved):
    base, worktree = repo
    service = IntegrationService(base)
    digest = service.prepare("dev-demo", TASK).request.digest
    before = git(base, "rev-parse", "HEAD")
    if moved == "source":
        write(worktree, "changed.txt", "changed\n")
        git(worktree, "add", ".")
        git(worktree, "commit", "-qm", "change scope")
    elif moved == "target":  # rewritten: no longer a descendant of the presented target
        git(base, "commit", "--amend", "-qm", "rewritten target")
        before = git(base, "rev-parse", "HEAD")
    elif moved == "policy":
        write(base, ".devkit/config.toml", '[integration]\nprovider = "other"\n')
    else:
        git(base, "worktree", "move", str(worktree), str(worktree.with_name("moved")))
    with pytest.raises(AdvisoryError):
        service.execute_cli("dev-demo", TASK, expected_digest=digest)
    assert git(base, "rev-parse", "HEAD") == before


def test_review_readiness_is_rechecked_by_the_approving_call(repo, ready_provider):
    base, worktree = repo
    service = IntegrationService(base)
    digest = service.prepare("dev-demo", TASK).request.digest
    ready_provider.allowed = False
    with pytest.raises(AdvisoryError) as error:
        service.execute_cli("dev-demo", TASK, expected_digest=digest)
    assert error.value.code == "INTEGRATION_NOT_READY"
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


def test_merge_then_permission_failure_retries_cleanup_without_second_merge(repo, monkeypatch):
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
    result = integrate(service)
    assert result.status == "completed" and result.steps["merge"] == "skipped"
    assert not worktree.exists() and len(merged) == 1


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


def test_scoped_cleanup_receives_exact_targets_and_reports_partial_after_git_is_finished(repo, monkeypatch):
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
    assert result.cleanup_steps == {"scoped": "failed"} and cleanup.attempts == 1


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


def test_merge_permission_failure_has_correct_remedy_and_a_fresh_call_completes(repo, monkeypatch):
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
    assert integrate(service).status == "completed"


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
    retried = integrate(service)
    assert retried.status == "completed" and retried.steps["merge"] == "skipped" and len(calls) == 1


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
    result = IntegrationService(base).prepare("dev-demo", TASK)
    message = result.request.confirmation_message()
    assert f"Repository: {json.dumps(str(base))}" in message and str(worktree) in message
    assert '"scoped": "record" "task-1"' in message and "internal-revision-1" not in message
    assert 'Delete local branch: "dev-demo"' in message and "No fetch, push" in message
    assert worktree.exists()
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


def test_cloud_execution_environment_blocks_the_cli_before_effects(repo):
    from devkit_dist.features.project.repositories.invocation import ExecutionBinding, McpInteractiveError
    from devkit_dist.features.project.usecases.invocation import invocation

    base, worktree = repo
    with (base / ".git/info/exclude").open("a") as stream:
        stream.write("\n.devkit/config.local.toml\n")
    local = worktree / ".devkit/config.local.toml"
    local.write_text('[execution]\nenvironment="cloud"\n')
    before = git(base, "show-ref")
    service = IntegrationService(base)
    with pytest.raises(McpInteractiveError), invocation(ExecutionBinding(worktree, base)):
        service.execute_cli("dev-demo", TASK, expected_digest="0" * 64)
    assert git(base, "show-ref") == before and worktree.exists()
