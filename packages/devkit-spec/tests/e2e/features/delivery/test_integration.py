"""The ``devkit_agt.features.integration.readiness`` provider (``spec``) and end-to-end ``IntegrationService`` tests."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.integration import IntegrationService
from devkit_agt.features.worktree import PullRequestPolicyError, locate
from devkit_core.core import git as core_git
from devkit_dist.cli import cli as devkit_cli
from spec_support.delivery import _cli, _complete_proposal, _make_synced_repo, _start_worktree
from spec_support.scope import git, write

from devkit_spec.features.scope import Deadline, RegisterScopeUseCase, open_session


def _scope_tasks(root: Path) -> list[str]:
    session = open_session(root)
    return [record.task_id for record in session.registry.query(session.location.namespace, Deadline(5))[0]]


def _complete_feature_spec(
    wt: Path, slug: str = "feat", *, date: str = "2026-10-17", extra: dict[str, str] | None = None
) -> str:
    """A completed feature unit; ``extra`` files are written into its implementation commit."""
    month = date[:7]
    compact = date.replace("-", "")
    unit = f"specs/{month}/{compact}-{slug}"
    _cli(wt, "workflow", "new", slug, "--workflow", "sdd-spec-feature", "--date", date)
    write(
        wt,
        f"{unit}/spec.md",
        f"---\nid: SPEC-{slug}\ntitle: Feature {slug}\nsummary: Add feature {slug}.\nstatus: completed\ncreated: {date}\nworkflow: sdd-spec-feature\n---\n\n# [SPEC-{slug}] Feature {slug}\n\n## 1. Problem Statement & Motivation\nNeed feature {slug}.\n\n## 2. Acceptance Criteria\n\n### Scenario 1: [AC-01] Feature works\n- **Given** x\n- **When** y\n- **Then** z\n",
    )
    _cli(wt, "workflow", "bind", "--unit", unit, "--workflow", "sdd-spec-feature")
    write(
        wt,
        f"{unit}/plan.md",
        f"---\nid: PLAN-{slug}\nspec: SPEC-{slug}\n---\n\n# Technical Plan\n\n## 1. Design\nUpdate src/app.py.\n",
    )
    write(
        wt,
        f"{unit}/tasks.md",
        f"---\nid: TASKS-{slug}\nplan: PLAN-{slug}\n---\n\n# Tasks\n\n- [x] **Task 1: Update app**\n  - _Boundary: `src/app.py`\n  - _Requirements: AC-01_\n",
    )
    write(wt, "src/app.py", "VALUE = 2\n")
    write(
        wt,
        "docs/capabilities/delivery/CAP-DLV-sample.md",
        "---\nid: CAP-DLV-sample\ntitle: Sample\nsummary: Sample capability.\nstatus: active\narea: delivery\ncreated: 2026-10-01\nupdated: 2026-10-17\n---\n\n# [CAP-DLV-sample] Sample\n\n## 1. Overview\nSample capability updated.\n",
    )
    for rel, text in (extra or {}).items():
        write(wt, rel, text)
    write(
        wt,
        f"{unit}/reconcile.md",
        f"---\nreconcile_id: REC-{slug}\nspec: SPEC-{slug}\nstatus: resolved\ntargets:\n  - file: docs/capabilities/delivery/CAP-DLV-sample.md\n    resolution: modified\n---\n\n# Reconcile\n\nUpdated sample capability.\n",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "feat: implement feature")
    head = git(wt, "rev-parse", "HEAD")
    _cli(
        wt,
        "workflow",
        "envelope",
        "review",
        "--unit",
        unit,
        "--stage",
        "review-refine",
        "--summary",
        "Review passed.",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "reconcile-check",
        "--stage",
        "living-spec-draft",
        "--summary",
        "Reconcile verified.",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "feedback",
        "--stage",
        "collect-feedback",
        "--summary",
        "Sweep complete.",
        "--check",
        "swept=PASS 0 items",
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "final-report",
        "--stage",
        "final-change-report",
        "--summary",
        "All checks pass.",
        "--check",
        "tests=PASS pytest",
        "--check",
        "build=PASS build",
        "--check",
        "lint=PASS lint",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "chore: record envelopes")
    return unit


def _complete_bugfix_spec(wt: Path, slug: str = "fix", *, date: str = "2026-10-17") -> str:
    month = date[:7]
    compact = date.replace("-", "")
    unit = f"specs/{month}/{compact}-{slug}"
    _cli(wt, "workflow", "new", slug, "--workflow", "sdd-spec-bugfix", "--date", date)
    write(
        wt,
        f"{unit}/spec.md",
        f"---\nid: SPEC-{slug}\ntitle: Bugfix {slug}\nsummary: Fix bug {slug}.\nstatus: completed\ncreated: {date}\nworkflow: sdd-spec-bugfix\n---\n\n# [SPEC-{slug}] Bugfix {slug}\n\n## 1. Defect Characterization\nBug details.\n\n## 2. Acceptance Criteria\n\n### Scenario 1: [AC-01] Bug fixed\n- **Given** x\n- **When** y\n- **Then** z\n",
    )
    _cli(wt, "workflow", "bind", "--unit", unit, "--workflow", "sdd-spec-bugfix")
    write(
        wt,
        f"{unit}/plan.md",
        f"---\nid: PLAN-{slug}\nspec: SPEC-{slug}\n---\n\n# Fix Plan\n\n## 1. Design\nFix src/app.py.\n",
    )
    write(
        wt,
        f"{unit}/tasks.md",
        f"---\nid: TASKS-{slug}\nplan: PLAN-{slug}\n---\n\n# Tasks\n\n- [x] **Task 1: Fix bug**\n  - _Boundary: `src/app.py`\n  - _Requirements: AC-01_\n",
    )
    write(wt, "src/app.py", "VALUE = 3\n")
    write(
        wt,
        f"{unit}/reconcile.md",
        f"---\nreconcile_id: REC-{slug}\nspec: SPEC-{slug}\nstatus: resolved\ntargets:\n  - file: docs/capabilities/delivery/CAP-DLV-sample.md\n    resolution: waived\n    rationale: Behavior already matches documented contract.\n---\n\n# Reconcile\n\nNo doc change needed.\n",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "fix: resolve defect")
    head = git(wt, "rev-parse", "HEAD")
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "red",
        "--stage",
        "reproduce",
        "--summary",
        "Reproduced failure.",
        "--check",
        "reproduced=PASS pytest failed before fix",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "green",
        "--stage",
        "fix-verify",
        "--summary",
        "Verified fix.",
        "--check",
        "resolved=PASS pytest passed",
        "--check",
        "preserved=PASS regression suite passed",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "review",
        "--unit",
        unit,
        "--stage",
        "review-refine",
        "--summary",
        "Review passed.",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "reconcile-check",
        "--stage",
        "living-spec-draft",
        "--summary",
        "Reconcile verified.",
        "--head",
        head,
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "feedback",
        "--stage",
        "collect-feedback",
        "--summary",
        "Sweep complete.",
        "--check",
        "swept=PASS 0 items",
    )
    _cli(
        wt,
        "workflow",
        "envelope",
        "new",
        "--unit",
        unit,
        "--kind",
        "final-report",
        "--stage",
        "final-change-report",
        "--summary",
        "All checks pass.",
        "--check",
        "tests=PASS pytest",
        "--check",
        "build=PASS build",
        "--check",
        "lint=PASS lint",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "chore: record bugfix envelopes")
    return unit


@pytest.mark.parametrize("auto", [False, True])
def test_integration_service_end_to_end_approval_cleanup_and_no_network(
    tmp_path: Path, synced_template: Path, monkeypatch: pytest.MonkeyPatch, auto: bool
) -> None:
    repo = _make_synced_repo(
        tmp_path, synced_template, extra_config='[workflow.approvals]\ndev-integration="auto"' if auto else ""
    )
    (repo / "docs/proposals/PROP-feat/decisions").mkdir(parents=True)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    assert RegisterScopeUseCase().execute(open_session(wt), unit).record.task_id == "SPEC-feat"

    # Forbid any git network subcommand (fetch, push, ls-remote) during prepare and integrate.
    real_run_git = core_git.run_git

    def _no_network_git(root: Path, *args: str, **kwargs: object) -> bytes:
        assert not ({"fetch", "push", "ls-remote"} & set(args)), f"unexpected network git call: {args}"
        return real_run_git(root, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(core_git, "run_git", _no_network_git)

    service = IntegrationService(repo)

    # 1. Preparing (the scope the Host presents) leaves worktree, branch, base, and scope record untouched.
    digest = service.prepare("dev-feat").request.digest
    assert wt.is_dir()
    assert "SPEC-feat" in _scope_tasks(repo)

    # 2. The approved invocation merges into base, removes worktree & branch, prunes proposal dir, sweeps scope record.
    completed = service.execute_cli("dev-feat", expected_digest=None if auto else digest)
    assert completed.status == "completed", completed.compact_dict()
    assert completed.authority == ("policy" if auto else "host-conversation")
    assert completed.steps["merge"] == "completed"
    assert completed.steps["worktree_remove"] == "completed"
    assert completed.steps["branch_delete"] == "completed"
    assert completed.steps["post_finish"] == "completed"
    assert completed.cleanup_steps == {"spec": "completed"}
    assert not wt.exists()
    assert not (repo / "docs/proposals/PROP-feat").exists()
    assert "SPEC-feat" not in _scope_tasks(repo)


def test_integration_service_respects_delete_branch_false_and_pull_request_required(
    tmp_path: Path, synced_template: Path
) -> None:
    repo = _make_synced_repo(
        tmp_path / "keep",
        synced_template,
        extra_config="[worktree]\ndelete_branch = false\n",
    )
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-keep")
    _complete_feature_spec(wt, "feat")
    service = IntegrationService(repo)

    res = service.execute_cli("dev-feat", expected_digest=service.prepare("dev-feat").request.digest)
    assert res.status == "completed"
    assert res.steps["branch_delete"] == "skipped"
    assert res.steps["marker_clear"] == "completed"
    assert git(repo, "rev-parse", "--verify", "refs/heads/dev-feat") == res.request.context.finish.source_sha

    # pull_request = "required" fails closed during prepare.
    pr_repo = _make_synced_repo(
        tmp_path / "pr",
        synced_template,
        extra_config='[worktree]\npull_request = "required"\n',
    )
    wt_pr = _start_worktree(pr_repo, "dev-feat", tmp_path / "wt-pr")
    _complete_feature_spec(wt_pr, "feat")
    with pytest.raises(PullRequestPolicyError):
        IntegrationService(pr_repo).prepare("dev-feat")


def test_integration_service_reports_partial_post_finish(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    locked = repo / "docs/proposals/PROP-feat/decisions/locked"
    locked.mkdir(parents=True)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    assert RegisterScopeUseCase().execute(open_session(wt), unit).record.task_id == "SPEC-feat"

    service = IntegrationService(repo)

    locked.chmod(0)
    try:
        partial = service.execute_cli("dev-feat", expected_digest=service.prepare("dev-feat").request.digest)
    finally:
        locked.chmod(0o755)

    assert partial.status == "partial"
    assert partial.failing_operation == "post_finish"
    assert partial.steps["merge"] == "completed"
    assert partial.cleanup_steps == {"spec": "failed"}
    # Scope record was still swept even though proposal prune failed.
    assert "SPEC-feat" not in _scope_tasks(repo)

    assert (repo / "docs/proposals/PROP-feat").exists()
    assert partial.verification == "pending"


@pytest.fixture(scope="module")
def handoff_repository_template(tmp_path_factory: pytest.TempPathFactory, synced_template: Path) -> Path:
    """Worker-local standalone seed; every case creates its own real Planning worktree."""
    repo = _make_synced_repo(tmp_path_factory.mktemp("handoff-template"), synced_template)
    _cli(repo, "sync")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "track complete synchronized projections")
    return repo


@pytest.fixture
def accepted_handoff_base(tmp_path: Path, handoff_repository_template: Path) -> Path:
    repo = tmp_path / "repo"
    # The seed has no linked worktrees, so its Git metadata needs no path repair.
    shutil.copytree(handoff_repository_template, repo, symlinks=True)
    wt = _start_worktree(repo, "plan-idea", tmp_path / "wt-idea")
    unit = _complete_proposal(wt)
    file = wt / unit / "proposal.md"
    file.write_text(file.read_text().replace("dev_effort: medium", "dev_effort: high"))
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "refine effort")
    git(repo, "merge", "--ff-only", "plan-idea")
    return repo


def test_handoff_cli_creates_or_preserves_the_development_worktree(accepted_handoff_base):
    from click.testing import CliRunner

    from devkit_spec.features.delivery.cli.proposals import proposal_group

    repo = accepted_handoff_base
    result = CliRunner().invoke(
        proposal_group,
        [
            "handoff",
            "idea",
            "--effort",
            "medium",
            "-w",
            str(repo),
            "--format",
            "json",
        ],
    )
    assert result.exit_code in {0, 1}, result.output
    payload = json.loads(result.output)
    assert payload["authority"] == "host-conversation"
    assert payload["status"] in {"handed_off", "needs_recovery"}
    assert result.exit_code == (0 if payload["status"] == "handed_off" else 1)
    worktree = Path(payload["worktree"]["path"])
    assert worktree.exists()
    if payload["status"] == "handed_off":
        assert payload["handoff"]["proposal"] == "PROP-idea"
    else:
        assert payload["worktree"]["created"] is True


# SPEC-handoff-modes-and-template-report AC-04
def test_handoff_cli_refuses_an_unmet_prerequisite_as_blocked(accepted_handoff_base):
    from devkit_spec.features.delivery.cli.proposals import proposal_group

    repo = accepted_handoff_base
    (repo / "untracked.txt").write_text("not committed\n")
    result = CliRunner().invoke(proposal_group, ["handoff", "idea", "--effort", "medium", "-w", str(repo)])
    assert result.exit_code == 2, result.output
    assert "SPEC_HANDOFF_BASE_DIRTY" in result.stderr
    assert "[ACTION] INTERACTION" in result.stderr
    assert "[TARGET] untracked.txt" in result.stderr
    assert result.stdout == ""  # a refusal prints no success sentinel
    assert not git(repo, "branch", "--list", "dev-idea")


def test_handoff_initialization_keeps_template_isolated(
    accepted_handoff_base: Path, handoff_repository_template: Path
) -> None:
    repo, template = accepted_handoff_base, handoff_repository_template
    relative_asset = Path(".devkit/managed/spec/workflows/sdd-proposal.md")
    refs = git(template, "show-ref")
    config = (template / ".git/config").read_bytes()
    source = (template / "src/app.py").read_bytes()
    asset = (template / relative_asset).read_bytes()
    assert not (repo / ".git/index").samefile(template / ".git/index")
    assert git(repo, "rev-parse", "--absolute-git-dir") == str(repo / ".git")
    assert git(template, "rev-parse", "--absolute-git-dir") == str(template / ".git")
    assert git(template, "worktree", "list", "--porcelain").count("worktree ") == 1
    worktrees = git(repo, "worktree", "list", "--porcelain")
    assert worktrees.count("worktree ") == 2
    assert str(template) not in worktrees
    assert f"worktree {repo.parent / 'wt-idea'}" in worktrees

    git(repo, "config", "fixture.isolation", "case")
    git(repo, "checkout", "-q", "-b", "isolated-case")
    write(repo, "src/app.py", "VALUE = 3\n")
    git(repo, "add", "src/app.py")
    git(repo, "commit", "-q", "-m", "test: mutate isolated case")
    (repo / relative_asset).write_text("case-only managed asset\n")

    assert git(template, "show-ref") == refs
    assert (template / ".git/config").read_bytes() == config
    assert (template / "src/app.py").read_bytes() == source
    assert (template / relative_asset).read_bytes() == asset
    assert git(template, "status", "--porcelain") == ""


def test_handoff_approval_creates_development_and_returns_selected_effort(accepted_handoff_base):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    repo = accepted_handoff_base
    result = HandoffUseCase(repo).execute("idea", "low")
    assert result["status"] == "handed_off", json.dumps(result, indent=2)
    assert result["activity_effort"] == "low" and result["authority"] == "host-conversation"
    worktree = Path(result["worktree"]["path"])
    assert git(worktree, "branch", "--show-current") == "dev-idea"
    assert (worktree / result["handoff"]["dir"] / "spec.md").is_file()
    assert (repo / "docs/proposals/PROP-idea/proposal.md").is_file()
    assert not (worktree / "docs/proposals/PROP-idea").exists()


def test_handoff_changed_base_requires_fresh_review_before_creating_worktree(accepted_handoff_base, monkeypatch):
    import devkit_spec.features.delivery.usecases.native_handoff as module
    from devkit_spec.base.errors import HandoffStaleError

    repo = accepted_handoff_base
    original = module.prepare
    calls = []

    def prepare(*args, **kwargs):
        preview = original(*args, **kwargs)
        if not calls:
            git(repo, "commit", "--allow-empty", "-q", "-m", "base advanced")
        calls.append(preview)
        return preview

    monkeypatch.setattr(module, "prepare", prepare)
    with pytest.raises(HandoffStaleError):
        module.HandoffUseCase(repo).execute("idea", "medium")
    assert not (repo.parent / "repo-wt-dev-idea").exists()


def test_handoff_pins_reviewed_commit_before_setup_when_base_moves(accepted_handoff_base, monkeypatch):
    from devkit_agt.features.worktree.usecases import lifecycle

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    repo = accepted_handoff_base
    reviewed = git(repo, "rev-parse", "HEAD")
    original_refuse = lifecycle._refuse_existing
    setup_heads = []

    def move_during_remote_check(base, branch):
        notices = original_refuse(base, branch)
        git(base, "commit", "--allow-empty", "-q", "-m", "advance while checking remote branches")
        return notices

    def capture_setup(path, setup, project, notices, *, before_step=None):
        if before_step is not None:
            before_step("sync")
        setup_heads.append(git(path, "rev-parse", "HEAD"))
        # The fixture has no setup command; copy its locked managed assets without invoking unrelated CLI work.
        shutil.copytree(repo / ".devkit/managed", path / ".devkit/managed")
        return None, True

    monkeypatch.setattr(lifecycle, "_refuse_existing", move_during_remote_check)
    monkeypatch.setattr(lifecycle, "_prepare", capture_setup)
    result = HandoffUseCase(repo).execute("idea", "medium")
    assert result["status"] == "handed_off", result
    assert setup_heads == [reviewed]
    assert git(repo, "rev-parse", "HEAD") != reviewed


def test_handoff_stage_off_cannot_replace_required_plan_approvals(accepted_handoff_base):
    from devkit_spec.base.errors import HandoffNotReadyError
    from devkit_spec.features.delivery.usecases.native_handoff import prepare

    repo = accepted_handoff_base
    for record in (repo / "docs/proposals/PROP-idea/decisions").glob("*-gate-plan-*.yaml"):
        record.unlink()
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.stages]\nintent-proposal = "off"\ndirection-handoff = "off"\n')
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "disable proposal gate stages")
    with pytest.raises(HandoffNotReadyError):
        prepare(repo, "idea")


def test_handoff_initializes_fresh_registration(accepted_handoff_base, monkeypatch):
    from devkit_agt.features.worktree.usecases import lifecycle
    from devkit_dist.features.host.usecases import registrations

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    repo = accepted_handoff_base
    original = lifecycle._execute
    modes = []

    def execute(argv, cwd, label, timeout):
        if argv[1:4] == ["-m", "devkit_dist", "sync"]:
            modes.append(argv[4])
            result = CliRunner().invoke(devkit_cli, argv[3:])
            return subprocess.CompletedProcess(argv, result.exit_code, result.stdout.encode(), result.stderr.encode())
        return original(argv, cwd, label, timeout)

    monkeypatch.setattr(lifecycle, "_execute", execute)
    monkeypatch.setattr(registrations, "collisions", lambda *args: [])
    monkeypatch.setattr(
        registrations,
        "provider",
        lambda root, *args: registrations.LaunchDescriptor(
            sys.executable,
            ("-m", "devkit_dist", "mcp", "serve", "--configuration-workspace", str(root)),
            str(repo),
            str(root),
            "local",
        ),
    )
    result = HandoffUseCase(repo).execute("idea", "medium")
    assert result["status"] == "handed_off", result
    assert modes == ["--locked", "--registrations-only"]
    worktree = Path(result["worktree"]["path"])
    assert registrations._ledger(worktree)["entries"]
    assert str(worktree) in (worktree / ".mcp.json").read_text()


def test_handoff_reuses_only_clean_pinned_devkit_worktree(accepted_handoff_base):
    from devkit_agt.features.worktree import start

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase, prepare

    repo = accepted_handoff_base
    started = start(locate(repo), "dev-idea", sync=True, revision=git(repo, "rev-parse", "HEAD"))
    assert prepare(repo, "idea").existing
    result = HandoffUseCase(repo).execute("idea", "medium")
    assert result["status"] == "handed_off", result
    assert result["worktree"]["created"] is False
    assert Path(result["worktree"]["path"]) == started.path


@pytest.mark.parametrize("mutation", ["dirty", "head", "marker"])
def test_handoff_recovery_refuses_changed_provenance_before_effects(accepted_handoff_base, mutation):
    from devkit_agt.features.worktree import start

    from devkit_spec.base.errors import HandoffWorktreeConflictError
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    repo = accepted_handoff_base
    started = start(locate(repo), "dev-idea", revision=git(repo, "rev-parse", "HEAD"))
    if mutation == "dirty":
        (started.path / "untracked.txt").write_text("preserve")
    elif mutation == "head":
        git(started.path, "commit", "--allow-empty", "-q", "-m", "unrelated")
    else:
        git(repo, "config", "branch.dev-idea.devkitWorktree", "/wrong")

    with pytest.raises(HandoffWorktreeConflictError) as caught:
        HandoffUseCase(repo).execute("idea", "medium")
    assert caught.value.target_files == ("dev-idea",)
    assert started.path.exists()


@pytest.mark.parametrize("policy", ["ask", "auto"])
def test_handoff_boundary_follows_owning_policy(accepted_handoff_base, policy):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    repo = accepted_handoff_base
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + f'\n[workflow.approvals]\nproposal-handoff = "{policy}"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Configure proposal handoff boundary")
    # Automatic handoff must use the proposal's declared dev_effort (high); an asked handoff takes the user's choice.
    result = HandoffUseCase(repo).execute("idea", "low" if policy == "ask" else "high")
    assert result["status"] == "handed_off", result
    assert result["authority"] == ("host-conversation" if policy == "ask" else "policy")
    assert result["activity_effort"] == ("low" if policy == "ask" else "high")


def test_handoff_automatic_policy_revocation_preserves_git_state(accepted_handoff_base, monkeypatch):
    import devkit_spec.features.delivery.usecases.native_handoff as module

    repo = accepted_handoff_base
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nproposal-handoff = "auto"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate handoff")
    before = git(repo, "show-ref")
    original = module.approval_policy

    def revoke(root, gate):
        result = original(root, gate)
        config.write_text(config.read_text().replace('proposal-handoff = "auto"', 'proposal-handoff = "ask"'))
        return result

    monkeypatch.setattr(module, "approval_policy", revoke)

    with pytest.raises(module.HandoffBaseDirtyError) as caught:
        module.HandoffUseCase(repo).execute("idea", "high")
    assert caught.value.code == "SPEC_HANDOFF_BASE_DIRTY"
    assert git(repo, "show-ref") == before
    assert not git(repo, "branch", "--list", "dev-idea")


def _commit_base(repo: Path, rel: str, text: str | None) -> str:
    """Commit a change to ``rel`` on the base (``None`` deletes it) and return the moved target."""
    if text is None:
        git(repo, "rm", "-q", rel)
    else:
        write(repo, rel, text)
        git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", f"docs: change {rel} on the base")
    return git(repo, "rev-parse", "HEAD")


def test_moved_target_that_changed_tool_spec_integrates_through_the_spec_provider(
    tmp_path: Path, synced_template: Path
) -> None:
    """``SPEC-integration-merge-moved-target``: ``SPEC_POLICY`` binds the prospective result at prepare."""
    repo = _make_synced_repo(tmp_path, synced_template)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    _complete_feature_spec(wt, "feat")
    tip = git(wt, "rev-parse", "HEAD")
    text = (repo / ".devkit/config.toml").read_text(encoding="utf-8")
    text = (
        text.replace("[tool.spec]\n", '[tool.spec]\nworktree = "auto"\n', 1)
        if "[tool.spec]\n" in text
        else (text + '\n[tool.spec]\nworktree = "auto"\n')
    )
    moved = _commit_base(repo, ".devkit/config.toml", text)
    service = IntegrationService(repo)
    request = service.prepare("dev-feat").request
    assert request.acceptance is None and request.context.result_sha is None
    completed = service.execute_cli("dev-feat", expected_digest=request.digest)
    assert completed.status == "completed", completed.compact_dict()
    assert git(repo, "rev-parse", "HEAD^1", "HEAD^2").split() == [moved, tip]


def test_reference_drift_is_left_to_final_landed_rules(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    cited = "docs/capabilities/delivery/CAP-DLV-cited.md"
    _commit_base(
        repo,
        cited,
        "---\nid: CAP-DLV-cited\ntitle: Cited\nsummary: Cited capability.\nstatus: active\narea: delivery\n"
        "created: 2026-10-01\nupdated: 2026-10-01\n---\n\n# [CAP-DLV-cited] Cited\n\n## 1. Overview\nCited.\n",
    )
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    sample = (
        "---\nid: CAP-DLV-sample\ntitle: Sample\nsummary: Sample capability.\nstatus: active\narea: delivery\n"
        "created: 2026-10-01\nupdated: 2026-10-17\n---\n\n# [CAP-DLV-sample] Sample\n\n## 1. Overview\n"
        "Builds on `CAP-DLV-cited`.\n"
    )
    _complete_feature_spec(wt, "feat", extra={"docs/capabilities/delivery/CAP-DLV-sample.md": sample})
    IntegrationService(repo).prepare("dev-feat")  # ready while the target still has the cited document
    moved = _commit_base(repo, cited, None)
    service = IntegrationService(repo)
    prepared = service.prepare("dev-feat")
    assert prepared.verification == "not_started"
    assert git(repo, "rev-parse", "HEAD") == moved and wt.is_dir()
    result = service.execute_cli("dev-feat", expected_digest=prepared.request.digest)
    assert result.verification == "pending" and result.status == "completed"
