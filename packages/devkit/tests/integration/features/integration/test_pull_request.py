from __future__ import annotations

import asyncio
from dataclasses import replace

import pytest
from devkit.advisory import AdvisoryError
from devkit_agt.features.integration import IntegrationService, Task
from devkit_agt.features.worktree.repositories.pull_request import CommandResult, GitHub, Repository
from devkit_core.base.mcp import ConfirmationReply
from testsupport.rules import git, write

TASK = Task("session", "fixture-task")


class FakeGitHub(GitHub):
    def __init__(self, root, remote):
        super().__init__(root)
        self.remote = remote
        self.pr = None
        self.pending = False
        self.failed = False
        self.mode = "checked"
        self.merge_calls = 0
        self.block_delete = False
        self.after_merge = None

    def resolve(self, remote):
        return Repository(remote, str(self.remote), str(self.remote), "github.example", "owner/repo", False)

    def rules(self, repository, branch):
        return []

    def find(self, repository, branch):
        return [dict(self.pr)] if self.pr else []

    def view(self, repository, number):
        assert self.pr is not None
        return dict(self.pr)

    def checks(self, repository, number):
        return [{"name": "ci", "bucket": "fail" if self.failed else "pending" if self.pending else "pass"}]

    def create(self, repository, branch, target, task_id):
        self.pr = {
            "number": 12,
            "url": "https://github.example/owner/repo/pull/12",
            "state": "OPEN",
            "isDraft": False,
            "isCrossRepository": False,
            "headRefName": branch,
            "baseRefName": target,
            "headRefOid": self.ref(repository, f"refs/heads/{branch}"),
            "mergeCommit": None,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "",
        }
        return CommandResult(0)

    def merge(self, repository, number, source, branch, target, task_id):
        self.merge_calls += 1
        if self.mode == "queue-added":
            return CommandResult(1, http_status=405)
        if self.mode == "unknown":
            return CommandResult(None)
        parent = self.ref(repository, f"refs/heads/{target}")
        assert parent is not None and self.pr is not None
        tree = git(self.root, "rev-parse", f"{source}^{{tree}}")
        if self.mode == "advanced":
            parent = git(
                self.root,
                "commit-tree",
                git(self.root, "rev-parse", f"{parent}^{{tree}}"),
                "-p",
                parent,
                "-m",
                "foreign advance",
            )
        if self.mode == "rewritten-base":
            parent = git(self.root, "commit-tree", tree, "-m", "unrelated target")
        if self.mode == "tree-mismatch":
            tree = git(self.root, "rev-parse", f"{parent}^{{tree}}")
        parents = ["-p", parent] + ([] if self.mode == "squash" else ["-p", source])
        merge = git(self.root, "commit-tree", tree, *parents, "-m", "platform merge")
        landing = source if self.mode == "merge-not-contained" else parent if self.mode == "source-lost" else merge
        git(self.root, "push", "--force", str(self.remote), f"{landing}:refs/heads/{target}")
        self.pr["state"] = "MERGED"
        self.pr["mergeCommit"] = {"oid": merge}
        if self.after_merge:
            self.after_merge()
        return CommandResult(0)

    def dependents(self, repository, branch):
        return [{"number": 13}] if self.block_delete else []


@pytest.fixture
def remote_service(repo, ready_provider, monkeypatch, tmp_path):
    base, worktree = repo
    original = ready_provider.check
    monkeypatch.setattr(
        ready_provider, "check", lambda context: replace(original(context), landed_check="devkit rules check")
    )
    remote = tmp_path / "remote.git"
    git(base, "init", "--bare", str(remote))
    git(base, "remote", "add", "origin", str(remote))
    git(base, "push", "-u", "origin", "main")
    service = IntegrationService(base)
    fake = FakeGitHub(base, remote)
    service.github = fake
    return service, fake, base, worktree


async def approve(message, schema):
    assert "pull request" in message
    assert "github.example/owner/repo" in message
    assert "after the last check" in message or "not recorded" in message
    return ConfirmationReply("accept", {"approve": True})


def run(service):
    return asyncio.run(service.integrate("dev-demo", TASK, approve, "pull-request"))


def test_checked_merge_and_ordered_cleanup(remote_service):
    service, fake, base, worktree = remote_service
    source = git(worktree, "rev-parse", "HEAD")
    result = run(service)
    assert result.status == "completed", result.to_dict()
    assert result.landing["checked"] and fake.merge_calls == 1
    assert git(base, "rev-parse", "HEAD^2") == source
    assert not worktree.exists()
    assert fake.ref(result.request.repository, "refs/heads/dev-demo") is None
    assert result.steps["post_finish"] == "completed"


def test_decline_writes_no_remote_refs(remote_service):
    service, fake, _base, worktree = remote_service
    before = git(fake.remote, "show-ref")

    async def decline(*args):
        return ConfirmationReply("decline", {})

    result = asyncio.run(service.integrate("dev-demo", TASK, decline, "pull-request"))
    assert result.status == "declined"
    assert git(fake.remote, "show-ref") == before and worktree.exists()


def test_pending_resume_reuses_checked_build(remote_service, ready_provider):
    service, fake, _base, _worktree = remote_service
    fake.pending = True
    result = run(service)
    assert result.status == "pending" and not result.errors
    assert result.steps["push"] == result.steps["pull_request"] == "completed"
    assert result.steps["merge"] == "not_run" and fake.merge_calls == 0
    checks = len(ready_provider.calls)
    fake.pending = False
    assert service.resume(result.request.id).status == "completed"
    assert len(ready_provider.calls) == checks


@pytest.mark.parametrize("mode", ["advanced", "tree-mismatch", "rewritten-base", "merge-not-contained"])
def test_unchecked_landing_continues_cleanup(remote_service, mode):
    service, fake, _base, worktree = remote_service
    fake.mode = mode
    result = run(service)
    assert result.status == "completed", result.to_dict()
    assert result.landing["reason"] == mode and not result.landing["checked"]
    assert [n.code for n in result.notices] == ["INTEGRATION_LANDED_UNCHECKED"]
    assert not worktree.exists()


@pytest.mark.parametrize(
    "mode,code",
    [
        ("squash", "INTEGRATION_MERGE_UNCONFIRMED"),
        ("source-lost", "INTEGRATION_SOURCE_NOT_CONTAINED"),
        ("unknown", "INTEGRATION_STEP_UNKNOWN"),
    ],
)
def test_unconfirmed_or_source_loss_preserves_work(remote_service, mode, code):
    service, fake, _base, worktree = remote_service
    fake.mode = mode
    result = run(service)
    assert result.status == "partial"
    assert result.errors[0].code == code
    assert worktree.exists() and result.steps["worktree_remove"] == "not_run"


def test_unknown_merge_is_not_reissued(remote_service):
    service, fake, _base, worktree = remote_service
    fake.mode = "unknown"
    result = run(service)
    service.resume(result.request.id)
    assert fake.merge_calls == 1 and worktree.exists()


def test_target_advance_while_pending_refuses_resume(remote_service):
    service, fake, base, worktree = remote_service
    fake.pending = True
    result = run(service)
    parent = git(base, "rev-parse", "HEAD")
    advance = git(base, "commit-tree", f"{parent}^{{tree}}", "-p", parent, "-m", "advance")
    git(base, "push", "origin", f"{advance}:refs/heads/main")
    fake.pending = False
    result = service.resume(result.request.id)
    assert result.errors[0].code == "INTEGRATION_TARGET_MOVED" and fake.merge_calls == 0
    assert worktree.exists()


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("state", "CLOSED", "INTEGRATION_PR_CONFLICT"),
        ("isDraft", True, "INTEGRATION_PR_CONFLICT"),
        ("baseRefName", "other", "INTEGRATION_PR_CONFLICT"),
        ("headRefOid", "0" * 40, "INTEGRATION_REMOTE_BRANCH_DIVERGED"),
    ],
)
def test_pending_pr_changes_refuse_resume(remote_service, field, value, code):
    service, fake, _base, worktree = remote_service
    fake.pending = True
    result = run(service)
    fake.pr[field] = value
    result = service.resume(result.request.id)
    assert result.errors[0].code == code and worktree.exists()


def test_failed_required_check_does_not_merge(remote_service):
    service, fake, _base, worktree = remote_service
    fake.failed = True
    result = run(service)
    assert result.errors[0].code == "INTEGRATION_MERGE_REFUSED"
    assert fake.merge_calls == 0 and worktree.exists()


def test_dependent_pr_preserves_local_and_remote_cleanup_identity(remote_service):
    service, fake, _base, worktree = remote_service
    fake.block_delete = True
    result = run(service)
    assert result.errors[0].code == "INTEGRATION_REMOTE_DELETE_BLOCKED"
    assert worktree.exists() and fake.ref(result.request.repository, "refs/heads/dev-demo")
    fake.block_delete = False
    result = service.resume(result.request.id)
    assert result.status == "completed", result.to_dict()


def test_fresh_cli_retry_preserves_source_until_remote_cleanup_completes(remote_service):
    service, fake, base, worktree = remote_service
    source = git(worktree, "rev-parse", "HEAD")
    fake.block_delete = True
    digest = service.prepare("dev-demo", TASK, "pull-request").request.digest
    result = service.execute_cli("dev-demo", TASK, "pull-request", expected_digest=digest)
    assert result.status == "partial", result.to_dict()
    assert result.errors[0].code == "INTEGRATION_REMOTE_DELETE_BLOCKED"
    assert result.steps["merge"] == "completed"
    assert worktree.exists() and git(base, "rev-parse", "refs/heads/dev-demo") == source
    assert fake.ref(result.request.repository, "refs/heads/dev-demo") == source
    landed = git(base, "rev-parse", "HEAD")

    fake.block_delete = False
    restarted = IntegrationService(base)
    restarted.github = fake
    digest = restarted.prepare("dev-demo", TASK, "pull-request").request.digest
    recovered = restarted.execute_cli("dev-demo", TASK, "pull-request", expected_digest=digest)
    assert recovered.status == "completed", recovered.to_dict()
    assert fake.merge_calls == 1 and git(base, "rev-parse", "HEAD") == landed
    assert not worktree.exists() and not git(base, "branch", "--list", "dev-demo")
    assert fake.ref(recovered.request.repository, "refs/heads/dev-demo") is None


def test_restart_cleanup_reports_no_recorded_landing(remote_service):
    service, fake, base, _worktree = remote_service
    fake.pending = True
    result = run(service)
    fake.pending = False
    fake.merge(result.request.repository, 12, result.request.context.finish.source_sha, "dev-demo", "main", TASK.id)
    restarted = IntegrationService(base)
    restarted.github = fake
    result = run(restarted)
    assert result.status == "completed", result.to_dict()
    assert result.landing["reason"] == "not-recorded"


def test_queue_added_after_preparation_is_refused_without_enqueue(remote_service):
    service, fake, _base, worktree = remote_service
    fake.mode = "queue-added"
    result = run(service)
    assert result.errors[0].code == "INTEGRATION_MERGE_REFUSED"
    assert fake.pr["state"] == "OPEN" and worktree.exists()


def test_dirty_local_target_blocks_cleanup_and_resume_preserves_then_recovers(remote_service):
    service, fake, base, worktree = remote_service
    fake.after_merge = lambda: write(base, "user-work.txt", "keep me")
    result = run(service)
    assert result.errors[0].code == "INTEGRATION_LOCAL_TARGET_BLOCKED"
    assert worktree.exists() and (base / "user-work.txt").read_text() == "keep me"
    (base / "user-work.txt").unlink()
    assert service.resume(result.request.id).status == "completed"


def test_divergent_local_target_is_never_overwritten(remote_service):
    service, fake, base, worktree = remote_service

    def advance_local():
        git(base, "commit", "--allow-empty", "-qm", "independent local advance")

    fake.after_merge = advance_local
    result = run(service)
    local = git(base, "rev-parse", "HEAD")
    assert result.errors[0].code == "INTEGRATION_LOCAL_TARGET_BLOCKED" and worktree.exists()
    assert git(base, "rev-parse", "HEAD") == local


def test_restart_during_pending_requires_new_confirmation(remote_service):
    service, fake, base, _worktree = remote_service
    fake.pending = True
    pending = run(service)
    restarted = IntegrationService(base)
    restarted.github = fake
    with pytest.raises(Exception, match="not retained"):
        restarted.resume(pending.request.id)
    fake.pending = False
    assert run(restarted).status == "completed"


def test_missing_target_upstream_has_actionable_code(remote_service):
    service, _fake, base, worktree = remote_service
    git(base, "branch", "--unset-upstream", "main")
    with pytest.raises(AdvisoryError) as error:
        service.prepare("dev-demo", TASK, "pull-request")
    assert error.value.code == "INTEGRATION_TARGET_UPSTREAM" and worktree.exists()


def test_remote_source_divergence_refuses_before_approval(remote_service):
    service, fake, base, worktree = remote_service
    parent = git(base, "rev-parse", "HEAD")
    divergent = git(base, "commit-tree", f"{parent}^{{tree}}", "-p", parent, "-m", "remote work")
    git(base, "push", "origin", f"{divergent}:refs/heads/dev-demo")
    with pytest.raises(AdvisoryError) as error:
        service.prepare("dev-demo", TASK, "pull-request")
    assert error.value.code == "INTEGRATION_REMOTE_BRANCH_DIVERGED"
    assert fake.merge_calls == 0 and worktree.exists()


def test_pending_resume_does_not_wait_for_repository_lock(remote_service):
    from devkit_agt.features.worktree import integration_lock

    service, fake, base, worktree = remote_service
    fake.pending = True
    pending = run(service)
    with integration_lock(base / ".git", timeout=0), pytest.raises(AdvisoryError) as error:
        service.resume(pending.request.id)
    assert error.value.code == "LOCK_HELD" and worktree.exists()


def test_source_change_after_remote_merge_blocks_local_fast_forward(remote_service):
    service, fake, base, worktree = remote_service
    before = git(base, "rev-parse", "HEAD")
    fake.after_merge = lambda: git(worktree, "commit", "--allow-empty", "-qm", "new user work")
    result = run(service)
    assert result.status == "partial" and result.errors
    assert result.failing_operation == "local_fast_forward"
    assert git(base, "rev-parse", "HEAD") == before and worktree.exists()


def test_failed_build_then_manual_merge_remains_unchecked(remote_service, ready_provider):
    service, fake, _base, _worktree = remote_service
    original = ready_provider.check
    ready_provider.check = lambda context: replace(
        original(context), reasons=("build failed",) if context.result_sha else ()
    )
    result = run(service)
    assert result.errors and not result.build_checked and result.result_sha
    fake.merge(result.request.repository, 12, result.request.context.finish.source_sha, "dev-demo", "main", TASK.id)
    result = service.resume(result.request.id)
    assert result.status == "completed" and result.landing["reason"] == "not-recorded"
    assert not result.landing["checked"]
    assert any(n.code == "INTEGRATION_LANDED_UNCHECKED" for n in result.notices)


@pytest.mark.parametrize("deletion", [False, True])
def test_git_mutation_timeout_preserves_unknown_recovery(remote_service, monkeypatch, deletion):
    import devkit_agt.features.worktree.repositories.pull_request as adapter
    from devkit_core.base.errors import GitError

    service, fake, base, worktree = remote_service
    original = adapter.run_git

    def fail_mutation(root, *args, **kwargs):
        if args[0] == "push" and ("--delete" in args) == deletion:
            raise GitError("fixture transport timeout", command=("git", *args), returncode=None)
        return original(root, *args, **kwargs)

    monkeypatch.setattr(adapter, "run_git", fail_mutation)
    result = run(service)
    assert result.errors[0].code == "INTEGRATION_STEP_UNKNOWN"
    assert result.steps["remote_delete" if deletion else "push"] == "unknown"
    assert "devkit integration integrate" in result.errors[0].fix
    assert worktree.exists()
    monkeypatch.setattr(adapter, "run_git", original)
    restarted = IntegrationService(base)
    restarted.github = fake
    digest = restarted.prepare("dev-demo", TASK, "pull-request").request.digest
    recovered = restarted.execute_cli("dev-demo", TASK, "pull-request", expected_digest=digest)
    assert recovered.status == "completed", recovered.to_dict()
    assert fake.merge_calls == 1 and not worktree.exists()
    assert fake.ref(recovered.request.repository, "refs/heads/dev-demo") is None


def test_cleanup_only_confirmation_describes_only_remaining_operations(remote_service):
    service, fake, base, _worktree = remote_service
    fake.pending = True
    pending = run(service)
    fake.merge(pending.request.repository, 12, pending.request.context.finish.source_sha, "dev-demo", "main", TASK.id)
    restarted = IntegrationService(base)
    restarted.github = fake
    request = restarted.prepare("dev-demo", TASK, "pull-request").request
    message = request.confirmation_message()
    assert request.context.finish.already_merged
    assert "Approve pull request cleanup" in message and "PR 12 is already merged" in message
    assert "Fetch target; fast-forward local target" in message and "not-recorded" in message
    assert "Push source" not in message and "Merge runs now" not in message
    assert "devkit rules check" in message
