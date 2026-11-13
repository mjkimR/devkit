"""The ``devkit.post_finish`` extension: proposal pruning and the finished worktree's scope record."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import Level
from devkit_agt.features.integration import (
    CleanupContractError,
    CleanupTarget,
    IntegrationContext,
    StaleRequestError,
)
from devkit_agt.features.worktree import FinishPlan, FinishResult
from devkit_dist.cli import cli as devkit_cli
from spec_support.scope import SPEC, git, make_repo, write

from devkit_spec.base.errors import (
    PostFinishCleanupNotice,
    ProposalCleanupWarning,
    ScopeTimeoutError,
    SpecConfigError,
)
from devkit_spec.features.delivery.usecases.cleanup import (
    KIND_PROPOSAL,
    KIND_SCOPE,
    after_finish,
    integration_local_only,
    integration_plan,
    integration_run,
    integration_validate,
)
from devkit_spec.features.policy.services.config import ScopeConfig
from devkit_spec.features.scope import Deadline, FlockLocker, RegisterScopeUseCase, locate, open_session


def _scope(root: Path, *args: str) -> str:
    return CliRunner().invoke(devkit_cli, ["spec", "scope", *args, "-w", str(root)]).stdout


def _register(root: Path, spec: str) -> str:
    """Register ``spec`` from ``root`` as creation does and return its task ID."""
    return RegisterScopeUseCase().execute(open_session(root), spec).record.task_id


def _tasks(root: Path) -> list[str]:
    session = open_session(root)
    return [record.task_id for record in session.registry.query(session.location.namespace, Deadline(5))[0]]


def _context(repo: Path, worktree: Path, *, branch: str = "dev-s") -> IntegrationContext:
    head = git(repo, "rev-parse", "HEAD")
    plan = FinishPlan(
        base=str(repo),
        common_dir=str(repo / ".git"),
        common_identity=(0, 0),
        branch=branch,
        source_sha=head,
        target_branch="main",
        target_sha=head,
        path=str(worktree),
        worktree_identity=None if worktree == repo else (1, 1),
        source_upstream="",
        markers=("true", "main", ""),
        delete_branch=True,
    )
    return IntegrationContext(finish=plan)


def _commit_handoff(repo: Path) -> None:
    """Retain committed proposal provenance after its tracked files have been handed off."""
    write(repo, "docs/proposals/PROP-s/proposal.md", "proposal\n")
    git(repo, "add", "docs/proposals/PROP-s/proposal.md")
    git(repo, "commit", "-q", "-m", "proposal")
    git(repo, "rm", "-q", "docs/proposals/PROP-s/proposal.md")
    git(repo, "commit", "-q", "-m", "handoff")


def _finish_result(context: IntegrationContext) -> FinishResult:
    plan = context.finish
    return FinishResult(
        branch=plan.branch,
        path=Path(plan.path),
        merged=True,
        removed=plan.worktree_identity is not None,
        branch_deleted=plan.delete_branch,
    )


def test_a_project_without_the_spec_bundle_is_left_alone(tmp_path: Path) -> None:
    write(tmp_path, "docs/proposals/PROP-x/decisions/.keep-dir/x", "")
    assert after_finish(tmp_path, {"slug": "x", "path": str(tmp_path / "wt")}) is None


def test_finish_prunes_the_proposal_and_removes_only_the_finished_worktree_record(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    (repo / "docs/proposals/PROP-s/decisions").mkdir(parents=True)  # what a merged handoff leaves
    (repo / "docs/proposals/PROP-kept/materials").mkdir(parents=True)
    write(repo, "docs/proposals/PROP-kept/materials/note.md", "kept\n")
    finished, other = tmp_path / "wt-s", tmp_path / "wt-b"
    git(repo, "worktree", "add", "-q", "-b", "s", str(finished))
    git(repo, "worktree", "add", "-q", "-b", "b", str(other))
    write(other, "specs/2026-10/20261002-b/spec.md", "---\nid: SPEC-b\n---\n")
    write(other, "specs/2026-10/20261002-b/tasks.md", "- [ ] t\n  - _Boundary: src/a/\n")
    assert _register(finished, SPEC) == "SPEC-s"
    assert _register(other, "specs/2026-10/20261002-b") == "SPEC-b"
    git(repo, "worktree", "remove", "--force", str(finished))
    git(repo, "worktree", "remove", "--force", str(other))

    lines = after_finish(repo, {"branch": "dev-s", "slug": "s", "path": str(finished)})
    assert lines == ["removed empty proposal directory docs/proposals/PROP-s", "removed the scope record of SPEC-s"]
    assert not (repo / "docs/proposals/PROP-s").exists() and (repo / "docs/proposals/PROP-kept").is_dir()
    # The other stale record waits for an explicit sweep.
    assert "[SWEEP: SPEC-b verdict=stale" in _scope(repo, "sweep")
    assert after_finish(repo, {"slug": "s", "path": str(finished)}) is None  # nothing left: idempotent


def test_a_task_of_the_base_checkout_releases_its_record(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    write(repo, "specs/2026-10/20261002-b/spec.md", "---\nid: SPEC-b\n---\n")
    write(repo, "specs/2026-10/20261002-b/tasks.md", "- [ ] t\n  - _Boundary: src/a/\n")
    assert _register(repo, "specs/2026-10/20261002-b") == "SPEC-b"
    # devkit reports a --no-worktree task (finished or discarded) with the base checkout's own path.
    lines = after_finish(repo, {"branch": "dev-b", "slug": "b", "path": str(repo), "discarded": True})
    assert lines == ["released the scope record of SPEC-b"]
    assert "SPEC-b" not in _tasks(repo)
    assert after_finish(repo, {"branch": "dev-b", "slug": "b", "path": str(repo)}) is None  # idempotent


def test_a_failed_record_removal_keeps_the_prune_notices(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    (repo / "docs/proposals/PROP-s/decisions").mkdir(parents=True)
    write(repo, ".devkit/config.toml", "[tool.spec.scope]\ntimeout = 1\n")
    location = locate(repo, ScopeConfig(), Deadline(5))
    lock = location.shared_path / location.namespace / ".lock"
    lock.parent.mkdir(parents=True)
    unlock = FlockLocker().acquire(lock, Deadline(5))  # another registry command holds the namespace
    try:
        lines = after_finish(repo, {"slug": "s", "path": str(tmp_path / "wt-s")})
    finally:
        unlock()
    assert lines is not None and lines[0] == "removed empty proposal directory docs/proposals/PROP-s"
    assert len(lines) == 2 and isinstance(lines[1], ScopeTimeoutError)
    assert str(lines[1].fix).endswith(
        "then run uv run devkit spec scope sweep --apply to remove the finished worktree's scope record"
    )


def test_a_malformed_config_is_reported_with_the_sweep_fix(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    write(repo, ".devkit/config.toml", "[tool.spec.scope]\ntimeout = 0\n")
    lines = after_finish(repo, {"slug": "s", "path": str(tmp_path / "wt-s")})
    assert lines is not None and len(lines) == 1 and isinstance(lines[0], SpecConfigError)
    assert str(lines[0].fix).endswith(
        "then run uv run devkit spec scope sweep --apply to remove the finished worktree's scope record"
    )


def test_a_failed_prune_is_a_warning_and_the_sweep_still_runs(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    locked = repo / "docs/proposals/PROP-s/decisions/locked"
    locked.mkdir(parents=True)
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "s", str(finished))
    assert _register(finished, SPEC) == "SPEC-s"
    git(repo, "worktree", "remove", "--force", str(finished))
    locked.chmod(0)  # a directory that cannot be listed
    try:
        lines = after_finish(repo, {"branch": "dev-s", "slug": "s", "path": str(finished)})
    finally:
        locked.chmod(0o755)
    assert lines is not None and len(lines) == 2
    warning, swept = lines
    assert isinstance(warning, ProposalCleanupWarning) and warning.level is Level.WARNING
    assert warning.target_files == ("docs/proposals/PROP-s",)
    assert str(warning.fix).endswith("then run uv run devkit spec proposal prune s")
    assert swept == "removed the scope record of SPEC-s"
    assert locked.is_dir(), "nothing was removed"


def test_scoped_cleanup_plans_validates_and_runs_exact_targets(tmp_path: Path) -> None:
    assert integration_local_only is True and after_finish.integration_local_only is True
    repo = make_repo(tmp_path / "repo")
    _commit_handoff(repo)
    finished, other = tmp_path / "wt-s", tmp_path / "wt-b"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    git(repo, "worktree", "add", "-q", "-b", "dev-b", str(other))
    context = _context(repo, finished)

    # Without .devkit/managed/spec, scoped cleanup declares no targets and is a no-op.
    assert integration_plan(context) == ()
    integration_validate(context, ())
    assert integration_run(context, _finish_result(context), ()).done is True

    (repo / ".devkit/managed/spec").mkdir(parents=True)
    (repo / "docs/proposals/PROP-s/decisions").mkdir(parents=True)
    write(other, "specs/2026-10/20261002-b/spec.md", "---\nid: SPEC-b\n---\n")
    write(other, "specs/2026-10/20261002-b/tasks.md", "- [ ] t\n  - _Boundary: src/a/\n")
    assert _register(finished, SPEC) == "SPEC-s"
    assert _register(other, "specs/2026-10/20261002-b") == "SPEC-b"

    targets = integration_plan(context)
    assert len(targets) == 2
    assert targets[0] == CleanupTarget(KIND_PROPOSAL, "docs/proposals/PROP-s", context.finish.source_sha)
    assert targets[1].kind == KIND_SCOPE and targets[1].identity == "SPEC-s"
    assert targets[1].revision.startswith("worktree:") and targets[1].revision.endswith(":1")
    integration_validate(context, targets)

    git(repo, "worktree", "remove", "--force", str(finished))
    git(repo, "worktree", "remove", "--force", str(other))
    outcome = integration_run(context, _finish_result(context), targets)
    assert outcome.done is True
    assert [notice.message for notice in outcome.notices] == [
        "removed empty proposal directory docs/proposals/PROP-s",
        "removed the scope record of SPEC-s",
    ]
    assert all(isinstance(notice, PostFinishCleanupNotice) for notice in outcome.notices)
    assert "[SWEEP: SPEC-b verdict=stale" in _scope(repo, "sweep")


def test_scoped_cleanup_refuses_stale_scope_record_revision(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    assert _register(finished, SPEC) == "SPEC-s"
    context = _context(repo, finished)
    targets = integration_plan(context)

    # Namespace drift in [tool.spec.scope] is also rejected as StaleRequestError.
    drifted = (CleanupTarget(KIND_SCOPE, "SPEC-s", "worktree:other-namespace:1"),)
    try:
        integration_validate(context, drifted)
    except StaleRequestError:
        pass
    else:
        raise AssertionError("expected StaleRequestError when scope namespace changed")

    # Another writer moves the scope record's revision after planning.
    session = open_session(finished)
    record = session.location.shared_path / session.location.namespace / "SPEC-s.json"
    data = json.loads(record.read_text())
    record.write_text(json.dumps(data | {"revision": 2}))

    try:
        integration_validate(context, targets)
    except StaleRequestError:
        pass
    else:
        raise AssertionError("expected StaleRequestError when scope revision changed")

    git(repo, "worktree", "remove", "--force", str(finished))
    try:
        integration_run(context, _finish_result(context), targets)
    except StaleRequestError:
        pass
    else:
        raise AssertionError("expected StaleRequestError when running with stale scope revision")
    assert "[SWEEP: SPEC-s verdict=stale" in _scope(repo, "sweep")


def test_scoped_cleanup_partial_failure_and_idempotent_resume(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    _commit_handoff(repo)
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    locked = repo / "docs/proposals/PROP-s/decisions/locked"
    locked.mkdir(parents=True)
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    assert _register(finished, SPEC) == "SPEC-s"
    context = _context(repo, finished)
    targets = integration_plan(context)
    git(repo, "worktree", "remove", "--force", str(finished))

    locked.chmod(0)
    try:
        first = integration_run(context, _finish_result(context), targets)
    finally:
        locked.chmod(0o755)
    assert first.done is False
    assert any(isinstance(n, ProposalCleanupWarning) for n in first.notices)
    assert any(n.message == "removed the scope record of SPEC-s" for n in first.notices)

    # Once the permission issue is fixed, validation and re-execution complete idempotently.
    integration_validate(context, targets)
    second = integration_run(context, _finish_result(context), targets)
    assert second.done is True
    assert [n.message for n in second.notices] == ["removed empty proposal directory docs/proposals/PROP-s"]
    assert not (repo / "docs/proposals/PROP-s").exists()


def test_scoped_cleanup_base_checkout_releases_own_record_and_rejects_bad_targets(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    assert _register(repo, SPEC) == "SPEC-s"
    context = _context(repo, repo)
    targets = integration_plan(context)
    assert len(targets) == 1
    assert targets[0].kind == KIND_SCOPE and targets[0].identity == "SPEC-s"
    assert targets[0].revision.startswith("base:") and targets[0].revision.endswith(":1")
    outcome = integration_run(context, _finish_result(context), targets)
    assert outcome.done is True
    assert [n.message for n in outcome.notices] == ["released the scope record of SPEC-s"]
    assert "SPEC-s" not in _tasks(repo)

    try:
        integration_validate(context, (*targets, CleanupTarget("unknown-kind", "x", "1")))
    except CleanupContractError:
        pass
    else:
        raise AssertionError("expected CleanupContractError for unknown target kind")


def test_post_git_means_the_base_contains_the_result(tmp_path: Path) -> None:
    from dataclasses import replace

    from devkit_spec.features.delivery.usecases.cleanup import _is_post_git

    repo = make_repo(tmp_path / "repo")
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    write(finished, "work.txt", "x\n")
    git(finished, "add", ".")
    git(finished, "commit", "-q", "-m", "work")
    source = git(finished, "rev-parse", "HEAD")
    git(repo, "merge", "-q", "--no-ff", "-m", "chore(merge): integrate dev-s into main", "dev-s")
    result = git(repo, "rev-parse", "HEAD")
    write(repo, "later.txt", "later\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "later commit on the base")
    context = _context(repo, finished)
    context = replace(context, finish=replace(context.finish, source_sha=source), result_sha=result)
    assert not _is_post_git(repo, context)  # the worktree still exists
    git(repo, "worktree", "remove", str(finished))
    assert _is_post_git(repo, context)
    assert _is_post_git(repo, replace(context, result_sha=None))  # the source (ff-only, cleanup-only)
    git(repo, "reset", "-q", "--hard", "HEAD~2")
    assert not _is_post_git(repo, context)


def test_cleanup_reads_legacy_records_and_leaves_the_journal(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    assert _register(finished, SPEC) == "SPEC-s"
    session = open_session(repo)
    directory = session.location.shared_path / session.location.namespace
    record = directory / "SPEC-s.json"
    legacy = json.loads(record.read_text()) | {"last_request_id": "req-2", "last_added": 3, "last_removed": 1}
    record.write_text(json.dumps(legacy | {"revision": 3}))  # written by the retired update
    journal = directory / "journal.jsonl"
    journal.write_bytes(b'{"event": "update", "task": "SPEC-s"}\n')
    context = _context(repo, finished)
    targets = integration_plan(context)
    assert targets[-1] == CleanupTarget(KIND_SCOPE, "SPEC-s", f"worktree:{session.location.namespace}:3")
    git(repo, "worktree", "remove", "--force", str(finished))
    outcome = integration_run(context, _finish_result(context), targets)
    assert outcome.done is True and "removed the scope record of SPEC-s" in [n.message for n in outcome.notices]
    assert journal.read_bytes() == b'{"event": "update", "task": "SPEC-s"}\n'


def test_a_base_checkout_token_without_its_record_plans_no_scope_target(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    assert _register(repo, SPEC) == "SPEC-s"
    session = open_session(repo)
    (session.location.shared_path / session.location.namespace / "SPEC-s.json").unlink()  # released elsewhere
    targets = integration_plan(_context(repo, repo))
    assert targets == ()


@pytest.mark.parametrize("proposal_side", ["source", "target"])
def test_pinned_proposal_history_survives_handoff_prune_and_revalidation(tmp_path: Path, proposal_side: str) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    finished = tmp_path / "wt-s"
    git(repo, "worktree", "add", "-q", "-b", "dev-s", str(finished))
    _commit_handoff(finished if proposal_side == "source" else repo)
    context = _context(repo, finished)
    context = replace(context, finish=replace(context.finish, source_sha=git(finished, "rev-parse", "HEAD")))
    directory = repo / "docs/proposals/PROP-s/decisions"
    directory.mkdir(parents=True)
    expected = (CleanupTarget(KIND_PROPOSAL, "docs/proposals/PROP-s", context.finish.source_sha),)
    assert integration_plan(context) == expected
    integration_validate(context, expected)
    first = integration_run(context, _finish_result(context), expected)
    assert first.done and len(first.notices) == 1
    assert not directory.parent.exists()
    # The pinned history, rather than the mutable checkout, determines identity after cleanup.
    assert integration_plan(context) == expected
    integration_validate(context, expected)
    assert integration_run(context, _finish_result(context), expected).notices == ()
    for invalid in [
        (),
        (*expected, *expected),
        (CleanupTarget(KIND_PROPOSAL, "docs/proposals/PROP-other", context.finish.source_sha),),
        (CleanupTarget(KIND_PROPOSAL, expected[0].identity, "other-source"),),
    ]:
        with pytest.raises(StaleRequestError):
            integration_validate(context, invalid)
        with pytest.raises(StaleRequestError):
            integration_run(context, _finish_result(context), invalid)


def test_spec_only_cleanup_omits_proposal_even_if_an_untracked_directory_appears(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".devkit/managed/spec").mkdir(parents=True)
    assert _register(repo, SPEC) == "SPEC-s"
    context = _context(repo, repo)
    targets = integration_plan(context)
    assert [target.kind for target in targets] == [KIND_SCOPE]
    (repo / "docs/proposals/PROP-s/decisions").mkdir(parents=True)
    assert integration_plan(context) == targets
    integration_validate(context, targets)
    outcome = integration_run(context, _finish_result(context), targets)
    assert outcome.done and [n.message for n in outcome.notices] == ["released the scope record of SPEC-s"]
    assert (repo / "docs/proposals/PROP-s").is_dir()
    extra = (*targets, CleanupTarget(KIND_PROPOSAL, "docs/proposals/PROP-s", context.finish.source_sha))
    with pytest.raises(StaleRequestError):
        integration_validate(context, extra)
    with pytest.raises(StaleRequestError):
        integration_run(context, _finish_result(context), extra)
