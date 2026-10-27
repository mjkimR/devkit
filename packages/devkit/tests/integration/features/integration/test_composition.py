"""The composed acceptance-and-integration engine that ``spec proposal accept`` drives (``_compose_execute``)."""

from __future__ import annotations

from pathlib import Path

import devkit_agt.features.integration.services.providers as providers
import pytest
from devkit.advisory import AdvisoryError
from devkit_agt.features.integration import AuthorityError, CleanupResult, CleanupTarget, IntegrationService, Task
from devkit_agt.features.worktree import integration_lock
from devkit_core.core import LockHeldError
from testsupport.rules import git, write


class Lifecycle:
    approval_gate = "dev-integration"

    def automatic(self, request):
        return None

    def __init__(self, worktree, provider, *, existing=False):
        self.worktree = worktree
        self.provider = provider
        self.existing = existing
        self.accepted = False
        self.selected = False

    def preview(self, context):
        return self.provider.check(context)

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


def compose(service, lifecycle, between=None):
    """Prepare with the lifecycle and execute the composition as the Host-authorized CLI does.

    ``between`` runs after preparation, before the composition takes the operation lock. A refusal before execution
    raises its advisory, which the CLI reports as blocked.
    """
    request = service._prepare("dev-demo", Task("session", "fixture"), lifecycle=lifecycle).request
    lifecycle.validate(request)
    lifecycle.select({})
    if between is not None:
        between()
    return service._compose_execute(request, lifecycle, "host-conversation")


def retained_authority(service, result):
    return service._records[result.request.id].approved


@pytest.mark.parametrize("existing", [False, True])
def test_composition_integrates_exact_acceptance_and_revokes_authority(repo, ready_provider, existing):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider, existing=existing)
    result = compose(service, lifecycle)
    assert result.status == "completed" and result.authority == "host-conversation"
    assert lifecycle.accepted and lifecycle.selected
    assert not worktree.exists()
    assert retained_authority(service, result) is False


def test_composition_target_change_after_preparation_blocks_acceptance(repo, ready_provider):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)

    def advance():
        write(base, "moved.txt", "moved\n")
        git(base, "add", ".")
        git(base, "commit", "-qm", "advance base")

    with pytest.raises(AdvisoryError):
        compose(service, lifecycle, advance)
    assert not lifecycle.accepted and worktree.exists()


def test_composition_partial_result_retains_no_authority(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)

    def partial(record, approving):
        assert approving is False
        result = record.result
        result.status = "partial"
        return result

    monkeypatch.setattr(service, "_execute", partial)
    result = compose(service, lifecycle)
    assert result.status == "partial"
    assert retained_authority(service, result) is False


def test_composition_rechecks_real_provider_after_acceptance(repo, ready_provider):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    before = git(base, "rev-parse", "HEAD")

    def refuse():
        ready_provider.allowed = False

    with pytest.raises(AdvisoryError):
        compose(service, lifecycle, refuse)
    assert lifecycle.accepted
    assert git(base, "rev-parse", "HEAD") == before and worktree.exists()


def test_composition_refuses_target_move_after_reprepare(repo, ready_provider, monkeypatch):
    base, worktree = repo
    service = IntegrationService(base)
    lifecycle = Lifecycle(worktree, ready_provider)
    original = service._prepare

    def moved(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs.get("lifecycle") is not None:
            return result
        write(base, "moved.txt", "moved\n")
        git(base, "add", ".")
        git(base, "commit", "-qm", "advance base after preparation")
        return result

    monkeypatch.setattr(service, "_prepare", moved)
    result = compose(service, lifecycle)
    assert result.status == "blocked" and lifecycle.accepted
    assert result.steps["merge"] == "not_run" and worktree.exists()
    assert git(base, "log", "-1", "--format=%s") == "advance base after preparation"
    assert retained_authority(service, result) is False


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
    result = compose(service, lifecycle)
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
    if change == "source":
        assert compose(service, lifecycle).status == "completed" and not worktree.exists()
    else:
        with pytest.raises(AdvisoryError) as refused:
            compose(service, lifecycle)
        assert refused.value.code == "INTEGRATION_REQUEST_STALE" and worktree.exists()


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
    with pytest.raises(AuthorityError):
        compose(service, lifecycle)
    assert worktree.exists()
    assert git(base, "rev-parse", "HEAD") == before
    assert git(worktree, "rev-parse", "HEAD^") == source
