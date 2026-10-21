from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from devkit.core import LockHeldError
from devkit.core.mcp import ConfirmationReply
from devkit.integration import AuthorityError, CleanupResult, CleanupTarget, IntegrationService, Task, providers
from devkit.worktree import integration_lock
from testsupport.rules import git, write


class Lifecycle:
    def __init__(self, worktree, provider, *, existing=False):
        self.worktree = worktree
        self.provider = provider
        self.existing = existing
        self.accepted = False
        self.selected = False

    def preview(self, context):
        return self.provider.check(context)

    def confirmation(self, request, language):
        return request.confirmation_message(language), {
            "type": "object",
            "properties": {"approve": {"type": "boolean", "default": False}},
            "required": ["approve"],
        }

    def select(self, content):
        self.selected = True

    def validate(self, request):
        pass

    def before_merge(self, request):
        assert self.accepted
        assert request.context.finish.source_sha == git(self.worktree, "rev-parse", "HEAD")

    def accept(self, request):
        self.accepted = True
        if not self.existing:
            write(self.worktree, "accepted.txt", "accepted\n")
            git(self.worktree, "add", ".")
            git(self.worktree, "commit", "-qm", "accept fixture")
        return git(self.worktree, "rev-parse", "HEAD")


async def approve(message, schema):
    return ConfirmationReply("accept", {"approve": True})


@pytest.mark.parametrize("existing", [False, True])
def test_composition_integrates_exact_acceptance_and_revokes_authority(repo, ready_provider, existing):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider, existing=existing)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == "completed"
    assert lifecycle.accepted and lifecycle.selected
    assert not worktree.exists()
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


@pytest.mark.parametrize("action,value", [("accept", False), ("accept", "true"), ("cancel", True)])
def test_composition_nonapproval_cannot_accept_or_integrate(repo, ready_provider, action, value):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    before = git(base, "show-ref")

    async def reply(message, schema):
        return ConfirmationReply(action, {"approve": value})

    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, reply))
    assert not lifecycle.accepted and not lifecycle.selected
    assert git(base, "show-ref") == before
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_target_change_during_form_blocks_acceptance(repo, ready_provider):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)

    async def reply(message, schema):
        write(base, "moved.txt", "moved\n")
        git(base, "add", ".")
        git(base, "commit", "-qm", "advance base")
        return ConfirmationReply("accept", {"approve": True})

    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, reply))
    assert result.status == "blocked"
    assert not lifecycle.accepted and worktree.exists()
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_partial_result_has_no_resume_authority(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)

    def partial(record, approving):
        assert approving is False
        result = record.result
        result.status = "partial"
        return result

    monkeypatch.setattr(service, "_execute", partial)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == "partial"
    monkeypatch.undo()
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_rechecks_real_provider_after_acceptance(repo, ready_provider):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    before = git(base, "rev-parse", "HEAD")

    async def reply(message, schema):
        ready_provider.allowed = False
        return ConfirmationReply("accept", {"approve": True})

    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, reply))
    assert result.status == "blocked" and lifecycle.accepted
    assert git(base, "rev-parse", "HEAD") == before and worktree.exists()
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_refuses_target_move_after_reprepare(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    original = service.prepare

    def moved(*args, **kwargs):
        result = original(*args, **kwargs)
        write(base, "moved.txt", "moved\n")
        git(base, "add", ".")
        git(base, "commit", "-qm", "advance base after preparation")
        return result

    monkeypatch.setattr(service, "prepare", moved)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == "blocked" and lifecycle.accepted
    assert result.steps["merge"] == "not_run" and worktree.exists()
    assert git(base, "log", "-1", "--format=%s") == "advance base after preparation"
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_holds_operation_lock_before_acceptance(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    accept = lifecycle.accept

    def locked_accept(request):
        with pytest.raises(LockHeldError), integration_lock(Path(request.context.finish.common_dir), timeout=0):
            pytest.fail("acceptance ran without the operation lock")
        return accept(request)

    monkeypatch.setattr(lifecycle, "accept", locked_accept)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == "completed"


@pytest.mark.parametrize("change", ["source", "identity", "revision"])
def test_composition_cleanup_only_transforms_exact_source_bound_revision(repo, ready_provider, monkeypatch, change):
    base, worktree = repo
    original_source = git(worktree, "rev-parse", "HEAD")

    class Cleanup:
        integration_local_only = True

        def integration_plan(self, context):
            source = context.finish.source_sha
            identity = "different" if change == "identity" and source != original_source else "task"
            revision = "other" if change == "revision" and source != original_source else source
            return (CleanupTarget("record", identity, revision),)

        def integration_validate(self, context, targets):
            assert targets == self.integration_plan(context)

        def integration_run(self, context, result, targets):
            assert targets == self.integration_plan(context)
            return CleanupResult(True)

    monkeypatch.setattr(providers, "cleanup_extensions", lambda: {"fixture": ("fixture:cleanup", Cleanup())})
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == ("completed" if change == "source" else "blocked")
    assert worktree.exists() is (change != "source")
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)


def test_composition_package_guard_after_acceptance_blocks_merge(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    before = git(base, "rev-parse", "HEAD")
    source = git(worktree, "rev-parse", "HEAD")

    def expired(request):
        assert lifecycle.accepted and request.context.finish.source_sha != source
        raise AuthorityError("package evidence expired after acceptance")

    monkeypatch.setattr(lifecycle, "before_merge", expired)
    result = asyncio.run(service._compose("dev-demo", Task("session", "fixture"), lifecycle, approve))
    assert result.status == "blocked" and worktree.exists()
    assert git(base, "rev-parse", "HEAD") == before
    assert git(worktree, "rev-parse", "HEAD^") == source
    with pytest.raises(AuthorityError):
        service.resume(result.request.id)
