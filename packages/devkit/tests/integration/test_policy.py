from __future__ import annotations

import asyncio

import pytest
from devkit.integration import AuthorityError, IntegrationService, Task
from devkit.worktree import RemoveFailedError, lifecycle, locate, start
from testsupport.rules import git, init_repo, write

TASK = Task("session", "fixture-task")


async def no_confirmation(_message, _schema):
    pytest.fail("policy authority must not invoke elicitation")


@pytest.fixture
def auto_repo(tmp_path, ready_provider):
    def create(method="no-ff", delete=True):
        base = init_repo(tmp_path / "auto")
        config = (
            '[integration]\nprovider="fixture"\n[workflow.approvals]\ndev-integration="auto"\n'
            f'[worktree]\nmerge="{method}"\ndelete_branch={str(delete).lower()}\n'
        )
        write(base, ".devkit/config.toml", config)
        write(base, ".gitignore", ".devkit/transient/\n")
        git(base, "add", ".")
        git(base, "commit", "-qm", "authorize local integration")
        worktree = start(locate(base), "dev-demo").path
        write(worktree, "ready.txt", "ready\n")
        git(worktree, "add", ".")
        git(worktree, "commit", "-qm", "implement fixture")
        return base, worktree

    return create


@pytest.mark.parametrize("method", ["no-ff", "ff-only"])
@pytest.mark.parametrize("delete", [True, False])
def test_auto_local_exact_effects_without_confirmation(auto_repo, method, delete):
    base, worktree = auto_repo(method, delete)
    git(base, "remote", "add", "origin", "unreachable://fixture")
    tip = git(worktree, "rev-parse", "HEAD")
    service = IntegrationService(base)
    result = asyncio.run(service.integrate("dev-demo", TASK, no_confirmation))
    assert result.status == "completed", result.errors
    assert result.authority == "policy" and result.ui_action is None
    assert result.request.approval_policy == "auto"
    assert not worktree.exists()
    assert ("refs/heads/dev-demo" in git(base, "show-ref")) is not delete
    assert git(base, "rev-parse", "HEAD^{tree}") == git(base, "rev-parse", f"{tip}^{{tree}}")
    assert result.to_dict()["network_operations"] == "excluded"
    assert service.resume(result.request.id).status == "completed"


def test_auto_prepare_is_not_authority(auto_repo):
    base, _ = auto_repo()
    service = IntegrationService(base)
    request = service.prepare("dev-demo", TASK)
    with pytest.raises(AuthorityError):
        service.resume(request.request.id)
    with pytest.raises(AuthorityError):
        IntegrationService(base).resume(request.request.id)


def test_auto_pr_refused_before_port_access(auto_repo, monkeypatch):
    base, _ = auto_repo()
    service = IntegrationService(base)
    monkeypatch.setattr(service.github, "begin_call", lambda: pytest.fail("remote port used"))
    with pytest.raises(AuthorityError) as error:
        asyncio.run(service.integrate("dev-demo", TASK, no_confirmation, "pull-request"))
    assert error.value.fix is not None
    assert "separate publication authority" in error.value.fix


def test_prospective_revocation_refuses_before_mutation(auto_repo):
    base, worktree = auto_repo()
    config = worktree / ".devkit/config.toml"
    config.write_text(config.read_text().replace('dev-integration="auto"', 'dev-integration="ask"'))
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "revoke policy")
    before = git(base, "show-ref")
    with pytest.raises(AuthorityError) as error:
        asyncio.run(IntegrationService(base).integrate("dev-demo", TASK, no_confirmation))
    assert error.value.fix is not None
    assert "do not bypass" in error.value.fix
    assert git(base, "show-ref") == before and worktree.exists()


@pytest.mark.parametrize("revoke", [False, True])
def test_partial_auto_resume_preserves_authority_and_revocation(auto_repo, monkeypatch, revoke):
    base, worktree = auto_repo()
    original = lifecycle._remove

    def deny(*args, **kwargs):
        raise RemoveFailedError("fixture permission denial")

    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    result = asyncio.run(service.integrate("dev-demo", TASK, no_confirmation))
    assert result.status == "partial" and result.steps["merge"] == "completed"
    merged = git(base, "rev-parse", "HEAD")
    monkeypatch.setattr(lifecycle, "_remove", original)
    if revoke:
        config = base / ".devkit/config.toml"
        config.write_text(config.read_text().replace('dev-integration="auto"', 'dev-integration="ask"'))
    result = service.resume(result.request.id)
    assert result.authority == "policy" and git(base, "rev-parse", "HEAD") == merged
    assert result.status == ("partial" if revoke else "completed")
    assert worktree.exists() is revoke


def test_source_only_auto_still_requires_ask(repo):
    from devkit_core.base.mcp import ConfirmationReply

    base, worktree = repo
    config = worktree / ".devkit/config.toml"
    config.write_text(config.read_text() + '[workflow.approvals]\ndev-integration="auto"\n')
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "source-only auto")
    calls = []

    async def decline(message, schema):
        calls.append(message)
        return ConfirmationReply("decline", {})

    result = asyncio.run(
        IntegrationService(base).integrate(
            "dev-demo", Task("session", "fixture", claims_json='{"approved": true}'), decline
        )
    )
    assert result.status == "declined" and result.authority == "none"
    assert len(calls) == 1 and worktree.exists()


def test_cloud_transition_blocks_auto_resume(auto_repo, monkeypatch):
    from devkit.core.mcp_context import ExecutionBinding, McpInteractiveError, invocation

    base, worktree = auto_repo()
    binding = ExecutionBinding(base, base)
    original = lifecycle._remove

    def deny(*args, **kwargs):
        raise RemoveFailedError("fixture denial")

    monkeypatch.setattr(lifecycle, "_remove", deny)
    service = IntegrationService(base)
    with invocation(binding):
        result = asyncio.run(service.integrate("dev-demo", TASK, no_confirmation))
    assert result.status == "partial"
    monkeypatch.setattr(lifecycle, "_remove", original)
    (base / ".devkit/config.local.toml").write_text('[execution]\nenvironment="cloud"\n')
    with pytest.raises(McpInteractiveError), invocation(binding):
        service.resume(result.request.id)
    assert worktree.exists()
