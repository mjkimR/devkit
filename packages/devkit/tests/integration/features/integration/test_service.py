from __future__ import annotations

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
    IntegrationConfigError,
    IntegrationService,
)
from devkit_agt.features.worktree import PullRequestPolicyError, RemoveFailedError, finish, locate
from devkit_core.base.errors import GitError
from testsupport.rules import git, write

from .conftest import Entry


def integrate(service: IntegrationService):
    """One Host-approved CLI invocation: the digest pins the scope presented by prepare."""
    digest = service.prepare("dev-demo").request.digest
    return service.execute_cli("dev-demo", expected_digest=digest)


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
    assert result.compact_dict()["landed_sha"] == git(base, "rev-parse", "HEAD")


def test_ask_cli_without_the_presented_digest_has_no_authority(repo):
    base, worktree = repo
    before = git(base, "show-ref")
    with pytest.raises(AuthorityError):
        IntegrationService(base).execute_cli("dev-demo")
    assert git(base, "show-ref") == before and worktree.exists()
    assert not (base / ".git/devkit-integration.lock").exists()


@pytest.mark.parametrize("moved", ["source", "target", "policy", "cleanup"])
def test_changed_scope_invalidates_the_presented_digest(repo, moved):
    base, worktree = repo
    service = IntegrationService(base)
    digest = service.prepare("dev-demo").request.digest
    before = git(base, "rev-parse", "HEAD")
    if moved == "source":
        write(worktree, "changed.txt", "changed\n")
        git(worktree, "add", ".")
        git(worktree, "commit", "-qm", "change scope")
    elif moved == "target":  # rewritten: no longer a descendant of the presented target
        git(base, "commit", "--amend", "-qm", "rewritten target")
        before = git(base, "rev-parse", "HEAD")
    elif moved == "policy":
        write(base, ".devkit/config.toml", "[worktree]\ndelete_branch = false\n")
    else:
        git(base, "worktree", "move", str(worktree), str(worktree.with_name("moved")))
    with pytest.raises(AdvisoryError):
        service.execute_cli("dev-demo", expected_digest=digest)
    assert git(base, "rev-parse", "HEAD") == before


def test_merge_does_not_discover_or_call_readiness(repo, ready_provider, monkeypatch):
    base, worktree = repo
    ready_provider.allowed = False
    original = providers.metadata.entry_points

    def entries(**kw):
        assert kw.get("group") not in {"devkit.integration.readiness", "devkit.finish_guard"}
        return original(**kw)

    monkeypatch.setattr(providers.metadata, "entry_points", entries)
    result = integrate(IntegrationService(base))
    assert result.status == "completed" and result.verification == "pending"
    assert ready_provider.calls == [] and not worktree.exists()


@pytest.mark.parametrize("dirty", ["base", "source", "locked"])
def test_preflight_preserves_dirty_or_locked_worktrees(repo, dirty):
    base, worktree = repo
    if dirty == "locked":
        git(base, "worktree", "lock", str(worktree))
    else:
        write(base if dirty == "base" else worktree, "untracked.txt", "preserve\n")
    with pytest.raises(AdvisoryError):
        IntegrationService(base).prepare("dev-demo")
    assert worktree.exists()


def test_required_pr_blocks_local_execution(repo):
    base, _ = repo
    write(base, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n[worktree]\npull_request = "required"\n')
    git(base, "add", ".")
    git(base, "commit", "-qm", "require PR")
    with pytest.raises(PullRequestPolicyError):
        IntegrationService(base).prepare("dev-demo")


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
        IntegrationService(base).prepare("dev-demo")


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


def test_missing_provider_configuration_is_supported(repo):
    base, worktree = repo
    for root in (base, worktree):
        write(root, ".devkit/config.toml", "")
        git(root, "add", ".")
        git(root, "commit", "-qm", "remove legacy provider")
    assert integrate(IntegrationService(base)).verification == "pending"


@pytest.mark.parametrize("config", ['[integration]\nunknown = "x"\n', 'integration = "x"\n'])
def test_unknown_integration_configuration_is_actionable(repo, config):
    base, _ = repo
    write(base, ".devkit/config.toml", config)
    with pytest.raises(IntegrationConfigError) as raised:
        IntegrationService(base).prepare("dev-demo")
    assert "Remove unknown keys" in (raised.value.fix or "")


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
    assert result.verification == "not_started" and result.landed_sha is None
    monkeypatch.setattr(merging, "run_git", original)
    retried = integrate(service)
    assert retried.status == "completed" and retried.steps["merge"] == "skipped" and len(calls) == 1


def test_server_runtime_inside_worktree_is_refused_even_with_symlinked_python(repo, monkeypatch):
    import sys

    from devkit_agt.features.integration import RuntimeLocationError

    base, worktree = repo
    monkeypatch.setattr(sys, "executable", str(worktree / ".venv/bin/python"))
    with pytest.raises(RuntimeLocationError):
        IntegrationService(base).prepare("dev-demo")


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
    result = IntegrationService(base).prepare("dev-demo")
    assert worktree.exists()
    compact = result.compact_dict()
    assert compact["request"]["repository"] == str(base) and compact["request"]["worktree"]["path"] == str(worktree)
    assert compact["request"]["delete_branch"] is True and compact["request"]["network_operations"] == "excluded"
    assert compact["request"]["cleanup"] == [
        {"extension": "scoped", "targets": [{"kind": "record", "identity": "task-1"}]}
    ]
    detailed = result.to_dict()
    assert detailed["request"]["cleanup"][0]["targets"][0]["revision"] == "internal-revision-1"
    assert compact["request"]["digest"] == detailed["request"]["digest"]


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
        service.execute_cli("dev-demo", expected_digest="0" * 64)
    assert git(base, "show-ref") == before and worktree.exists()


def test_unknown_merge_outcome_is_a_partial_effect(repo, monkeypatch):
    """CAP-INT: a possibly-applied mutation is a partial effect, never "nothing happened"."""
    base, _ = repo
    original = merging.run_git

    def ambiguous(root, *args, **kw):
        value = original(root, *args, **kw)
        if args[0] == "merge":
            raise GitError("merge timed out after ref update")
        return value

    monkeypatch.setattr(merging, "run_git", ambiguous)
    result = integrate(IntegrationService(base))
    assert result.steps["merge"] == "unknown" and result.status == "partial"


def test_landed_commit_mismatch_after_fast_forward_is_partial(repo, monkeypatch):
    import devkit_agt.features.integration.usecases.service as service_module

    base, _ = repo
    original = service_module.fast_forward

    def amended(root, sha):
        original(root, sha)
        write(base, "hook.txt", "changed by a post-merge hook\n")
        git(base, "add", "hook.txt")
        git(base, "commit", "--amend", "-qm", "amended")

    monkeypatch.setattr(service_module, "fast_forward", amended)
    result = integrate(IntegrationService(base))
    assert result.errors and result.failing_operation == "merge"
    assert result.steps["merge"] == "unknown" and result.status == "partial"


def test_refused_fast_forward_discloses_no_seeded_artifacts(repo, monkeypatch):
    """A refused integrate reports no seeded artifacts: nothing landed on the target."""
    import hashlib
    import json

    import devkit_agt.features.integration.usecases.service as service_module

    base, worktree = repo

    def receipt(root, side):
        record = {".agents/skill.md": {"sha256": hashlib.sha256(side.encode()).hexdigest(), "mode": 420}}
        data = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": record}
        (root / ".devkit").mkdir(exist_ok=True)
        (root / ".devkit/installation.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        git(root, "add", ".devkit/installation.json")
        git(root, "commit", "-qm", f"receipt {side}")

    receipt(base, "base")
    git(worktree, "merge", "-q", "main")
    receipt(worktree, "source")
    receipt(base, "target")
    service = IntegrationService(base)
    assert service.prepare("dev-demo").seeded

    def refuse(_root, _sha):
        raise GitError("not a fast-forward", returncode=1)

    monkeypatch.setattr(service_module, "fast_forward", refuse)
    result = integrate(service)
    assert result.status == "blocked" and result.errors[0].code == "WORKTREE_MERGE_FAILED"
    assert result.seeded == ()
    assert "INTEGRATION_GENERATED_SEEDED" not in [notice.code for notice in result.notices]


def test_rerun_after_unknown_fast_forward_keeps_the_seeded_disclosure(repo, monkeypatch):
    """A fast-forward that may have landed keeps its seeded disclosure when a rerun of the request is refused."""
    import hashlib
    import json

    import devkit_agt.features.integration.usecases.service as service_module

    base, worktree = repo

    def receipt(root, side):
        record = {".agents/skill.md": {"sha256": hashlib.sha256(side.encode()).hexdigest(), "mode": 420}}
        data = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": record}
        (root / ".devkit").mkdir(exist_ok=True)
        (root / ".devkit/installation.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        git(root, "add", ".devkit/installation.json")
        git(root, "commit", "-qm", f"receipt {side}")

    receipt(base, "base")
    git(worktree, "merge", "-q", "main")
    receipt(worktree, "source")
    receipt(base, "target")
    service = IntegrationService(base)
    original = service_module.fast_forward

    def timed_out(root, sha):
        original(root, sha)
        raise GitError("fast-forward timed out after ref update")

    monkeypatch.setattr(service_module, "fast_forward", timed_out)
    first = integrate(service)
    seeded = first.seeded
    assert first.steps["merge"] == "unknown" and seeded
    monkeypatch.setattr(service_module, "fast_forward", original)
    rerun = service._run(first.request.id, 0)
    assert rerun.steps["merge"] == "completed" and rerun.seeded == seeded
    assert [notice.code for notice in rerun.notices].count("INTEGRATION_GENERATED_SEEDED") == 1
