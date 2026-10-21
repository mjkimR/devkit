"""The ``devkit_agt.features.integration.readiness`` provider (``spec``) and end-to-end ``IntegrationService`` tests."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.integration import IntegrationContext, IntegrationService, ReadinessError, Task
from devkit_agt.features.integration.services import providers
from devkit_agt.features.worktree import PullRequestPolicyError, locate, plan_finish
from devkit_core.base.mcp import ConfirmationReply
from devkit_core.core import git as core_git
from devkit_dist.cli import cli as devkit_cli
from spec_support.delivery import _cli, _make_synced_repo, _start_worktree
from spec_support.scope import git, write

from devkit_spec.features.delivery.usecases.integration import check


def _complete_feature_spec(wt: Path, slug: str = "feat", *, date: str = "2026-10-17") -> str:
    month = date[:7]
    compact = date.replace("-", "")
    unit = f"specs/{month}/{compact}-{slug}"
    _cli(wt, "workflow", "new", slug, "--workflow", "sdd-spec-feature", "--date", date)
    _cli(
        wt, "workflow", "answer", "--unit", unit, "--request", "gate:plan-intent", "--action", "accept", "--by", "user"
    )
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
    _cli(
        wt, "workflow", "answer", "--unit", unit, "--request", "gate:plan-intent", "--action", "accept", "--by", "user"
    )
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


def _complete_proposal(wt: Path, slug: str = "idea") -> str:
    unit = f"docs/proposals/PROP-{slug}"
    _cli(wt, "spec", "proposal", "new", slug, "--title", "Idea", "--summary", "Proposal summary.")
    _cli(
        wt, "workflow", "answer", "--unit", unit, "--request", "gate:plan-intent", "--action", "accept", "--by", "user"
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
    prop_file = wt / unit / "proposal.md"
    prop_file.write_text(
        prop_file.read_text(encoding="utf-8").replace("status: draft", "status: accepted"),
        encoding="utf-8",
    )
    _cli(
        wt, "workflow", "answer", "--unit", unit, "--request", "gate:plan-accept", "--action", "accept", "--by", "user"
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "docs(proposal): accept proposal")
    return unit


def test_unit_readiness_passes_for_completed_feature_bugfix_and_proposal(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path / "f", synced_template)
    wt_feat = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit_feat = _complete_feature_spec(wt_feat, "feat")
    plan_feat = plan_finish(locate(repo), "dev-feat")
    ctx_feat = IntegrationContext(plan_feat, Task(kind="unit", id="SPEC-feat", unit=unit_feat))

    r1 = check(ctx_feat)
    r2 = check(ctx_feat)
    assert r1 == r2
    assert r1.reasons == ()
    codes = {item.code: item.value for item in r1.evidence}
    assert codes["TASK_KIND"] == "unit"
    assert codes["WORKFLOW"] == "sdd-spec-feature"
    assert codes["UNIT"] == unit_feat
    assert codes["TASK_TITLE"] == "Feature feat"
    assert codes["TASK_SUMMARY"] == "Add feature feat."
    assert codes["RESULT_SUMMARY"] == "All checks pass."
    assert codes["HOLD_STATUS"] == "clear"
    assert codes["CI_RULES"] == "pass"

    wt_fix = _start_worktree(repo, "dev-fix", tmp_path / "wt-fix")
    unit_fix = _complete_bugfix_spec(wt_fix, "fix")
    plan_fix = plan_finish(locate(repo), "dev-fix")
    ctx_fix = IntegrationContext(plan_fix, Task(kind="unit", id="SPEC-fix", unit=unit_fix))
    r_fix = check(ctx_fix)
    assert r_fix.reasons == ()
    assert dict((e.code, e.value) for e in r_fix.evidence)["WORKFLOW"] == "sdd-spec-bugfix"

    wt_prop = _start_worktree(repo, "plan-idea", tmp_path / "wt-idea")
    unit_prop = _complete_proposal(wt_prop, "idea")
    plan_prop = plan_finish(locate(repo), "plan-idea")
    ctx_prop = IntegrationContext(plan_prop, Task(kind="unit", id="PROP-idea", unit=unit_prop))
    r_prop = check(ctx_prop)
    assert r_prop.reasons == ()
    assert dict((e.code, e.value) for e in r_prop.evidence)["WORKFLOW"] == "sdd-proposal"


def test_unit_readiness_refuses_incomplete_held_mismatched_or_ci_violating_units(
    tmp_path: Path, synced_template: Path
) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")

    # 1. Wrong task.id is refused with non-empty coded evidence.
    plan = plan_finish(locate(repo), "dev-feat")
    bad_id = check(IntegrationContext(plan, Task(kind="unit", id="SPEC-other", unit=unit)))
    assert bad_id.evidence and any("task.id" in reason for reason in bad_id.reasons)

    # 2. Unchecked task in tasks.md is refused.
    tasks_file = wt / unit / "tasks.md"
    tasks_file.write_text(tasks_file.read_text(encoding="utf-8").replace("- [x]", "- [ ]"), encoding="utf-8")
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "uncheck task")
    plan_unchecked = plan_finish(locate(repo), "dev-feat")
    r_unchecked = check(IntegrationContext(plan_unchecked, Task(kind="unit", id="SPEC-feat", unit=unit)))
    assert r_unchecked.evidence and any("tasks-all-checked" in reason for reason in r_unchecked.reasons)

    # Restore tasks.md, add a failed worker envelope with an unresolved problem (hold).
    tasks_file.write_text(tasks_file.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")
    _cli(
        wt,
        "workflow",
        "envelope",
        "worker",
        "--unit",
        unit,
        "--stage",
        "build-verify",
        "--status",
        "failed",
        "--summary",
        "Blocked on contract.",
        "--problem",
        "Contract contradiction.",
        "--recovery",
        "Return to specify.",
        "--effort",
        "medium",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "record blocked worker")
    plan_held = plan_finish(locate(repo), "dev-feat")
    r_held = check(IntegrationContext(plan_held, Task(kind="unit", id="SPEC-feat", unit=unit)))
    assert any("held" in reason for reason in r_held.reasons)

    # 3. Phase.CI rule violation (dangling SPEC-nonexistent reference) is refused.
    write(
        wt,
        "docs/capabilities/delivery/CAP-DLV-sample.md",
        "---\nid: CAP-DLV-sample\ntitle: Sample\nsummary: Sample capability.\nstatus: active\ncreated: 2026-10-01\nupdated: 2026-10-17\n---\n\n# [CAP-DLV-sample] Sample\n\n## 1. Overview\nReferences `SPEC-does-not-exist`.\n",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "introduce broken doc reference")
    plan_ci = plan_finish(locate(repo), "dev-feat")
    r_ci = check(IntegrationContext(plan_ci, Task(kind="unit", id="SPEC-feat", unit=unit)))
    assert any("CI rule violation" in reason for reason in r_ci.reasons)

    with pytest.raises(ReadinessError):
        IntegrationService(repo).prepare("dev-feat", Task(kind="unit", id="SPEC-feat", unit=unit))


def test_session_readiness_verifies_claims_and_refuses_invalid_claims_or_plan_branch(
    tmp_path: Path, synced_template: Path
) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    wt = _start_worktree(repo, "dev-quick", tmp_path / "wt-quick")
    write(wt, "src/app.py", "VALUE = 10\n")
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "fix: quick session fix")
    plan = plan_finish(locate(repo), "dev-quick")

    valid_bugfix = Task(
        kind="session",
        id="quick",
        claims_json=json.dumps(
            {
                "task_kind": "bugfix",
                "effort": "low",
                "review": "passed",
                "tests": "PASS pytest",
                "lint": True,
                "reproduced": True,
                "resolved": True,
            }
        ),
    )
    r_ok = check(IntegrationContext(plan, valid_bugfix))
    assert r_ok.reasons == ()
    assert dict((e.code, e.value) for e in r_ok.evidence)["WORKFLOW"] == "sdd-session-bugfix"

    missing_repro = Task(
        kind="session",
        id="quick",
        claims_json=json.dumps(
            {
                "task_kind": "bugfix",
                "effort": "low",
                "review": True,
                "tests": True,
                "lint": True,
            }
        ),
    )
    r_bad = check(IntegrationContext(plan, missing_repro))
    assert any("reproduced" in reason for reason in r_bad.reasons)

    # A plan-<slug> branch cannot be integrated as a session task.
    wt_plan = _start_worktree(repo, "plan-quick", tmp_path / "wt-plan-quick")
    write(wt_plan, "src/app.py", "VALUE = 11\n")
    git(wt_plan, "add", "-A")
    git(wt_plan, "commit", "-q", "-m", "plan edit")
    plan_branch = plan_finish(locate(repo), "plan-quick")
    r_plan = check(IntegrationContext(plan_branch, valid_bugfix))
    assert any("dev-<slug>" in reason for reason in r_plan.reasons)

    # Touching an unaccepted proposal unit on a session branch is also refused.
    write(
        wt,
        "docs/proposals/PROP-other/proposal.md",
        "---\nid: PROP-other\ntitle: Other\nsummary: Draft.\nstatus: draft\ncreated: 2026-10-17\nupdated: 2026-10-17\n---\n\n# [PROP-other] Other\n\n## 1. Summary\nDraft.\n",
    )
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "touch draft proposal")
    plan_touched_prop = plan_finish(locate(repo), "dev-quick")
    r_prop = check(IntegrationContext(plan_touched_prop, valid_bugfix))
    assert any("touched proposal unit docs/proposals/PROP-other is not accepted" in reason for reason in r_prop.reasons)


@pytest.mark.parametrize("auto", [False, True])
def test_integration_service_end_to_end_approval_cleanup_non_approval_and_no_network(
    tmp_path: Path, synced_template: Path, monkeypatch: pytest.MonkeyPatch, auto: bool
) -> None:
    repo = _make_synced_repo(
        tmp_path, synced_template, extra_config='[workflow.approvals]\ndev-integration="auto"' if auto else ""
    )
    (repo / "docs/proposals/PROP-feat/decisions").mkdir(parents=True)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    assert "[SCOPE: SPEC-feat " in _cli(wt, "spec", "scope", "register", "--spec", unit)

    # Forbid any git network subcommand (fetch, push, ls-remote) during prepare and integrate.
    real_run_git = core_git.run_git

    def _no_network_git(root: Path, *args: str, **kwargs: object) -> bytes:
        assert not ({"fetch", "push", "ls-remote"} & set(args)), f"unexpected network git call: {args}"
        return real_run_git(root, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(core_git, "run_git", _no_network_git)

    service = IntegrationService(repo)
    task = Task(kind="unit", id="SPEC-feat", unit=unit)

    # 1. Declined / unapproved confirmation leaves worktree, branch, base, and scope record untouched.
    async def _decline(_msg: str, _schema: dict) -> ConfirmationReply:
        return ConfirmationReply(action="decline", content={"approve": False})

    if not auto:
        declined = asyncio.run(service.integrate("dev-feat", task, _decline))
        assert declined.status == "declined"
        assert wt.is_dir()
        assert "SPEC-feat" in _cli(repo, "spec", "scope", "query")

    # 2. Affirmative confirmation fast-forwards base, removes worktree & branch, prunes proposal dir, sweeps scope record.
    async def _accept(_msg: str, _schema: dict) -> ConfirmationReply:
        assert not auto, "auto must not request native confirmation"
        return ConfirmationReply(action="accept", content={"approve": True})

    completed = asyncio.run(service.integrate("dev-feat", task, _accept))
    assert completed.status == "completed", completed.to_dict()
    assert completed.authority == ("policy" if auto else "mcp-elicitation")
    assert completed.steps["merge"] == "completed"
    assert completed.steps["worktree_remove"] == "completed"
    assert completed.steps["branch_delete"] == "completed"
    assert completed.steps["post_finish"] == "completed"
    assert completed.cleanup_steps == {"spec": "completed"}
    assert not wt.exists()
    assert not (repo / "docs/proposals/PROP-feat").exists()
    assert "SPEC-feat" not in _cli(repo, "spec", "scope", "query")


def test_integration_service_respects_delete_branch_false_and_pull_request_required(
    tmp_path: Path, synced_template: Path
) -> None:
    repo = _make_synced_repo(
        tmp_path / "keep",
        synced_template,
        extra_config="[worktree]\ndelete_branch = false\n",
    )
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-keep")
    unit = _complete_feature_spec(wt, "feat")
    service = IntegrationService(repo)
    task = Task(kind="unit", id="SPEC-feat", unit=unit)

    async def _accept(_msg: str, _schema: dict) -> ConfirmationReply:
        return ConfirmationReply(action="accept", content={"approve": True})

    res = asyncio.run(service.integrate("dev-feat", task, _accept))
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
    unit_pr = _complete_feature_spec(wt_pr, "feat")
    with pytest.raises(PullRequestPolicyError):
        IntegrationService(pr_repo).prepare("dev-feat", Task(kind="unit", id="SPEC-feat", unit=unit_pr))


def test_integration_service_partial_post_finish_and_resume(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    locked = repo / "docs/proposals/PROP-feat/decisions/locked"
    locked.mkdir(parents=True)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    assert "[SCOPE: SPEC-feat " in _cli(wt, "spec", "scope", "register", "--spec", unit)

    service = IntegrationService(repo)
    task = Task(kind="unit", id="SPEC-feat", unit=unit)

    async def _accept(_msg: str, _schema: dict) -> ConfirmationReply:
        return ConfirmationReply(action="accept", content={"approve": True})

    locked.chmod(0)
    try:
        partial = asyncio.run(service.integrate("dev-feat", task, _accept))
    finally:
        locked.chmod(0o755)

    assert partial.status == "partial"
    assert partial.failing_operation == "post_finish"
    assert partial.steps["merge"] == "completed"
    assert partial.cleanup_steps == {"spec": "failed"}
    # Scope record was still swept even though proposal prune failed.
    assert "SPEC-feat" not in _cli(repo, "spec", "scope", "query")

    resumed = service.resume(partial.request.id)
    assert resumed.status == "completed"
    assert resumed.steps["post_finish"] == "completed"
    assert resumed.cleanup_steps == {"spec": "completed"}
    assert not (repo / "docs/proposals/PROP-feat").exists()
    assert providers.provider("spec")[1] is not None


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


def _handoff_report(repo: Path) -> str:
    """Publish a real source-bound report, including the fixture's Planning evidence."""
    import re

    from devkit_spec.features.proposals.usecases.report import publish, template

    sha = git(repo, "rev-parse", "HEAD")
    body = template(repo, "idea", sha)
    body = re.sub(r"(?m)^(#{2,4} [^\n]+)\n", r"\1\n\nFixture proposal evidence.\n", body)
    return publish(repo, "idea", sha, body).metadata.artifact_uri


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


@pytest.mark.parametrize(
    "action,content,status",
    [
        ("accept", {"approve": False, "activity_effort": "high"}, "not_approved"),
        ("decline", {}, "declined"),
        ("cancel", {}, "cancelled"),
    ],
)
def test_handoff_nonapproval_makes_no_git_changes(accepted_handoff_base, action, content, status):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

    repo = accepted_handoff_base
    before = git(repo, "show-ref")

    async def confirm(message, schema):
        assert 'Goal: "Proposal summary."' in message and "Review report:" in message
        assert schema["properties"]["activity_effort"]["default"] == "high"
        assert schema["properties"]["approve"]["default"] is False
        assert git(repo, "show-ref") == before
        return ConfirmationReply(action, content)

    result = asyncio.run(HandoffService(repo).handoff("idea", _handoff_report(repo), confirm))
    assert result["status"] == status
    assert git(repo, "show-ref") == before
    assert not (repo.parent / "repo-wt-dev-idea").exists()


def test_handoff_approval_creates_development_and_returns_selected_effort(accepted_handoff_base):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

    repo = accepted_handoff_base

    async def confirm(message, schema):
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "low"})

    result = asyncio.run(HandoffService(repo).handoff("idea", _handoff_report(repo), confirm))
    assert result["status"] == "handed_off", json.dumps(result, indent=2)
    assert result["activity_effort"] == "low"
    worktree = Path(result["worktree"]["path"])
    assert git(worktree, "branch", "--show-current") == "dev-idea"
    assert (worktree / result["handoff"]["dir"] / "spec.md").is_file()
    assert (repo / "docs/proposals/PROP-idea/proposal.md").is_file()
    assert not (worktree / "docs/proposals/PROP-idea").exists()


def test_handoff_changed_base_requires_fresh_review_before_creating_worktree(accepted_handoff_base):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService
    from devkit_spec.features.proposals.usecases.report import ReviewRefreshRequiredError

    repo = accepted_handoff_base

    async def confirm(message, schema):
        git(repo, "commit", "--allow-empty", "-q", "-m", "base advanced")
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "medium"})

    with pytest.raises(ReviewRefreshRequiredError):
        asyncio.run(HandoffService(repo).handoff("idea", _handoff_report(repo), confirm))
    assert not (repo.parent / "repo-wt-dev-idea").exists()


@pytest.mark.parametrize("approved", [True, False])
@pytest.mark.parametrize("language", ["en", "ko"])
def test_handoff_native_sdk_roundtrip(accepted_handoff_base, approved, language):
    from datetime import timedelta

    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client

    repo = accepted_handoff_base
    (repo / ".devkit/config.local.toml").write_text(f'[presentation]\nlanguage="{language}"\n')
    report_uri = _handoff_report(repo)
    before = git(repo, "show-ref")
    calls = []

    async def confirm(context, params):
        assert git(repo, "show-ref") == before
        assert params.requestedSchema["properties"]["activity_effort"]["default"] == "high"
        calls.append(params.message)
        assert ("별도 승인" in params.message) == (language == "ko")
        return types.ElicitResult(action="accept", content={"approve": approved, "activity_effort": "medium"})

    async def run():
        params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-c",
                "from pathlib import Path; import sys; from devkit_mcp.features.runtime.mcp.server import serve; serve(Path(sys.argv[1]), Path(sys.argv[1]))",
                str(repo),
            ],
        )
        async with (
            stdio_client(params) as (read, stream),
            ClientSession(
                read, stream, read_timeout_seconds=timedelta(seconds=30), elicitation_callback=confirm
            ) as session,
        ):
            await session.initialize()
            tools = await session.list_tools()
            tool = next(tool for tool in tools.tools if tool.name == "spec_handoff")
            assert tool.annotations is not None and tool.annotations.openWorldHint is True
            response = await session.call_tool("spec_handoff", {"slug": "idea", "report_uri": report_uri})
            assert response.structuredContent is not None
            return response.structuredContent

    result = asyncio.run(run())
    assert len(calls) == 1
    assert result["status"] == ("handed_off" if approved else "not_approved"), result
    if approved:
        assert result["activity_effort"] == "medium"
    else:
        assert git(repo, "show-ref") == before


def test_handoff_pins_reviewed_commit_before_setup_when_base_moves(accepted_handoff_base, monkeypatch):
    from devkit_agt.features.worktree.usecases import lifecycle

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

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

    async def confirm(message, schema):
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "medium"})

    result = asyncio.run(HandoffService(repo).handoff("idea", _handoff_report(repo), confirm))
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


def test_readiness_on_the_result_declares_target_bound_codes_and_reads_the_merged_tree(
    tmp_path: Path, synced_template: Path
) -> None:
    from dataclasses import replace

    from devkit_agt.features.worktree import build_result

    from devkit_spec.features.delivery.usecases.integration import DISCLOSURE, TARGET_BOUND, _build_snapshot

    repo = _make_synced_repo(tmp_path, synced_template)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    plan = plan_finish(locate(repo), "dev-feat")
    context = IntegrationContext(plan, Task(kind="unit", id="SPEC-feat", unit=unit))
    approved = check(context)
    codes = {item.code: item.value for item in approved.evidence}
    assert approved.reasons == () and approved.target_bound == TARGET_BOUND == ("TARGET_SHA", "RESULT_SHA")
    assert approved.disclosure == DISCLOSURE and approved.result_sha is None
    assert "RESULT_SHA" not in codes and len(codes["SPEC_POLICY"]) == 64

    def build(target_change: tuple[str, str]) -> IntegrationContext:
        write(repo, *target_change)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", f"target: {target_change[0]}")
        moved = git(repo, "rev-parse", "HEAD")
        result = build_result(
            repo,
            branch="dev-feat",
            target_branch="main",
            target=moved,
            source=plan.source_sha,
            method="no-ff",
            advance=True,
        )
        return replace(context, finish=replace(plan, target_sha=moved), result_sha=result)

    clean = build(("docs/other.md", "unrelated\n"))
    built = check(clean)
    assert built.reasons == () and built.result_sha == clean.result_sha
    assert {item.code: item.value for item in built.evidence}["RESULT_SHA"] == clean.result_sha
    assert built.comparable() == approved.comparable()  # only target-bound evidence changed
    assert clean.result_sha is not None
    snapshot = _build_snapshot(repo, plan.source_sha, clean.finish.target_sha, clean.result_sha)
    assert snapshot.base == clean.finish.target_sha
    assert snapshot.tree == git(repo, "rev-parse", f"{clean.result_sha}^{{tree}}")
    assert "docs/other.md" not in snapshot.changed and "src/app.py" in snapshot.changed

    in_unit = check(build((f"{unit}/note.md", "target note\n")))
    assert any(f"the target changed {unit}" in reason for reason in in_unit.reasons)


def test_spec_policy_evidence_changes_with_the_target_tool_spec(tmp_path: Path, synced_template: Path) -> None:
    from dataclasses import replace

    from devkit_agt.features.worktree import build_result

    repo = _make_synced_repo(tmp_path, synced_template)
    wt = _start_worktree(repo, "dev-feat", tmp_path / "wt-feat")
    unit = _complete_feature_spec(wt, "feat")
    plan = plan_finish(locate(repo), "dev-feat")
    context = IntegrationContext(plan, Task(kind="unit", id="SPEC-feat", unit=unit))
    before = {item.code: item.value for item in check(context).evidence}["SPEC_POLICY"]
    config = repo / ".devkit/config.toml"
    text = config.read_text(encoding="utf-8")
    text = (
        text.replace("[tool.spec]\n", '[tool.spec]\nworktree = "auto"\n', 1)
        if "[tool.spec]\n" in text
        else (text + '\n[tool.spec]\nworktree = "auto"\n')
    )
    config.write_text(text, encoding="utf-8")
    git(repo, "commit", "-q", "-am", "change tool.spec")
    moved = git(repo, "rev-parse", "HEAD")
    result = build_result(
        repo,
        branch="dev-feat",
        target_branch="main",
        target=moved,
        source=plan.source_sha,
        method="no-ff",
        advance=True,
    )
    after = check(replace(context, finish=replace(plan, target_sha=moved), result_sha=result))
    assert {item.code: item.value for item in after.evidence}["SPEC_POLICY"] != before


def test_native_handoff_initializes_fresh_registration(accepted_handoff_base, monkeypatch):
    from devkit_agt.features.worktree.usecases import lifecycle
    from devkit_dist.features.host.usecases import registrations

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

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

    async def confirm(message, schema):
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "medium"})

    result = asyncio.run(HandoffService(repo).handoff("idea", _handoff_report(repo), confirm))
    assert result["status"] == "handed_off", result
    assert modes == ["--locked", "--registrations-only"]
    worktree = Path(result["worktree"]["path"])
    assert registrations._ledger(worktree)["entries"]
    assert str(worktree) in (worktree / ".mcp.json").read_text()


def test_handoff_reuses_only_clean_pinned_devkit_worktree(accepted_handoff_base):
    from devkit_agt.features.worktree import locate, start

    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

    repo = accepted_handoff_base
    report_uri = _handoff_report(repo)
    started = start(locate(repo), "dev-idea", project=Path("."), revision=git(repo, "rev-parse", "HEAD"))

    async def confirm(message, schema):
        assert "Completed: worktree creation. Reuse worktree:" in message
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "medium"})

    result = asyncio.run(HandoffService(repo).handoff("idea", report_uri, confirm))
    assert result["status"] == "handed_off", result
    assert result["worktree"]["created"] is False
    assert Path(result["worktree"]["path"]) == started.path


@pytest.mark.parametrize("mutation", ["dirty", "head", "marker"])
def test_handoff_recovery_refuses_changed_provenance_before_form(accepted_handoff_base, mutation):
    from devkit_agt.features.worktree import locate, start

    from devkit_spec.base.errors import HandoffNotReadyError
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService

    repo = accepted_handoff_base
    report_uri = _handoff_report(repo)
    started = start(locate(repo), "dev-idea", revision=git(repo, "rev-parse", "HEAD"))
    if mutation == "dirty":
        (started.path / "untracked.txt").write_text("preserve")
    elif mutation == "head":
        git(started.path, "commit", "--allow-empty", "-q", "-m", "unrelated")
    else:
        git(repo, "config", "branch.dev-idea.devkitWorktree", "/wrong")

    async def confirm(message, schema):
        pytest.fail("mismatched recovery cannot reach approval")

    with pytest.raises(HandoffNotReadyError):
        asyncio.run(HandoffService(repo).handoff("idea", report_uri, confirm))
    assert started.path.exists()


def test_handoff_report_language_change_requires_fresh_form(accepted_handoff_base):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService
    from devkit_spec.features.proposals.usecases.report import ReviewRefreshRequiredError

    repo = accepted_handoff_base
    (repo / ".devkit/config.local.toml").write_text('[presentation]\nlanguage="en"\n')
    report_uri = _handoff_report(repo)

    async def confirm(message, schema):
        (repo / ".devkit/config.local.toml").write_text('[presentation]\nlanguage="ko"\n')
        return ConfirmationReply("accept", {"approve": True, "activity_effort": "medium"})

    with pytest.raises(ReviewRefreshRequiredError):
        asyncio.run(HandoffService(repo).handoff("idea", report_uri, confirm))
    assert not (repo.parent / "repo-wt-dev-idea").exists()


def test_handoff_missing_report_never_displays_form(accepted_handoff_base):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService
    from devkit_spec.features.proposals.usecases.report import ReviewRefreshRequiredError

    async def confirm(message, schema):
        pytest.fail("missing report must refuse before approval")

    with pytest.raises(ReviewRefreshRequiredError):
        asyncio.run(HandoffService(accepted_handoff_base).handoff("idea", "shared://missing", confirm))
