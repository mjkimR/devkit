from __future__ import annotations

import asyncio
import json

import pytest
from devkit.core.mcp import ConfirmationReply
from scope.support import git
from test_integration import _cli, _make_synced_repo, _start_worktree, synced_template  # noqa: F401

from devkit_spec.plan_accept_mcp import PlanAcceptService
from devkit_spec.proposal_report import publish, template


@pytest.fixture
def pending(tmp_path, request):
    synced = request.getfixturevalue("synced_template")
    repo = _make_synced_repo(tmp_path, synced)
    _cli(repo, "sync")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Record complete consumer installation")
    wt = _start_worktree(repo, "plan-idea", tmp_path / "planning")
    unit = "docs/proposals/PROP-idea"
    _cli(wt, "spec", "proposal", "new", "idea", "--title", "Idea", "--summary", "Review this idea.")
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
        "Observed sweep complete.",
        "--check",
        "swept=PASS",
    )
    anchor = wt / unit / "proposal.md"
    anchor.write_text(anchor.read_text().replace("status: draft", "status: reviewing"))
    git(wt, "add", "-A")
    git(wt, "commit", "-m", "Planning complete")
    sha = git(wt, "rev-parse", "HEAD")
    text = template(wt, "idea", sha)
    text = (
        "\n".join(
            line + "\nEvidence reviewed." if line.startswith(("## ", "#### ")) else line for line in text.splitlines()
        )
        + "\n"
    )
    report = publish(wt, "idea", sha, text)
    return repo, wt, report.metadata.artifact_uri


@pytest.mark.parametrize("mode", ["accept_only", "accept_and_handoff"])
def test_plan_accept_real_git(pending, mode):
    repo, wt, uri = pending
    calls = []

    async def confirm(message, schema):
        calls.append(message)
        assert uri in message and "accept_only" in message and "Setup:" in message
        return ConfirmationReply("accept", {"approve": True, "mode": mode, "activity_effort": "low"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == ("accepted" if mode == "accept_only" else "handed_off"), json.dumps(result, indent=2)
    assert len(calls) == 1
    assert "acceptance_commit" in result["completed_steps"]
    assert "status: accepted" in (repo / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not wt.exists()
    assert bool(git(repo, "branch", "--list", "dev-idea")) == (mode == "accept_and_handoff")


@pytest.mark.parametrize("action,approve", [("accept", False), ("decline", True), ("cancel", True)])
def test_plan_accept_false_reply_no_effects(pending, action, approve):
    repo, wt, uri = pending
    before = git(repo, "show-ref")

    async def confirm(*_):
        return ConfirmationReply(action, {"approve": approve, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "held", result
    assert git(repo, "show-ref") == before
    assert git(wt, "status", "--porcelain") == ""


@pytest.mark.parametrize("change", ["source", "base", "policy", "environment", "language"])
def test_plan_accept_stale_before_effects(pending, change):
    repo, wt, uri = pending

    async def confirm(*_):
        if change in {"source", "base"}:
            git(wt if change == "source" else repo, "commit", "--allow-empty", "-m", "moved")
        elif change == "policy":
            with (repo / ".devkit/config.toml").open("a") as handle:
                handle.write("\n[worktree]\ndelete_branch = false\n")
        else:
            section = (
                '[execution]\nenvironment = "cloud"\n'
                if change == "environment"
                else '[presentation]\nlanguage = "ko"\n'
            )
            (repo / ".devkit/config.local.toml").write_text(section)
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "blocked", result
    assert "status: reviewing" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not list((wt / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))


def test_plan_accept_commit_failure_preserves_exact_dirty_acceptance(pending, monkeypatch):
    import devkit_spec.plan_accept_mcp as module

    repo, wt, uri = pending
    original = module._git

    def fail_commit(root, *args):
        if args[0] == "commit":
            raise module.ProposalApprovalNotReadyError("injected commit gate refusal")
        return original(root, *args)

    monkeypatch.setattr(module, "_git", fail_commit)

    async def confirm(*_):
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "needs_recovery", result
    assert result["completed_steps"] == ["acceptance_record"]
    assert git(wt, "status", "--porcelain")
    assert "status: accepted" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not (repo / "docs/proposals/PROP-idea/proposal.md").exists()


def test_plan_accept_rejects_commit_hook_unrelated_delta(pending, monkeypatch):
    import devkit_spec.plan_accept_mcp as module

    repo, wt, uri = pending
    original = module._git

    def hook(root, *args):
        if args[0] == "commit":
            (wt / "src/app.py").write_text("UNRELATED = True\n")
            git(wt, "add", "src/app.py")
        return original(root, *args)

    monkeypatch.setattr(module, "_git", hook)

    async def confirm(*_):
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "needs_recovery", result
    assert "acceptance_commit" in result["completed_steps"]
    assert not (repo / "docs/proposals/PROP-idea/proposal.md").exists()
    assert "exact service-created delta" in json.dumps(result)


def test_plan_accept_expiry_while_form_waits_refuses(pending, monkeypatch):
    import devkit_spec.proposal_report as reports

    repo, wt, uri = pending

    async def confirm(*_):
        def expired(*_):
            raise reports.ReviewRefreshRequiredError("injected report expiry")

        monkeypatch.setattr(reports, "validate_artifact", expired)
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "blocked", result
    assert git(wt, "status", "--porcelain") == ""
    assert "PROPOSAL_REVIEW_REFRESH_REQUIRED" in json.dumps(result)


def test_plan_accept_unavailable_form_performs_no_effect(pending):
    from devkit.host.errors import HostConfirmationError

    repo, wt, uri = pending
    before = git(repo, "show-ref")

    async def confirm(*_):
        raise HostConfirmationError("injected unavailable form")

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "blocked", result
    assert git(repo, "show-ref") == before
    assert git(wt, "status", "--porcelain") == ""


def _report(root):
    sha = git(root, "rev-parse", "HEAD")
    text = template(root, "idea", sha)
    body = (
        "\n".join(
            line + "\nReviewed evidence." if line.startswith(("## ", "#### ")) else line for line in text.splitlines()
        )
        + "\n"
    )
    return publish(root, "idea", sha, body).metadata.artifact_uri


def test_restart_after_acceptance_requires_fresh_report_and_form(pending, monkeypatch):
    import devkit_spec.plan_accept_mcp as module

    repo, wt, uri = pending
    original = module._Acceptance.before_merge

    def failed(*_):
        raise module.ProposalApprovalStaleError("injected post-acceptance failure")

    monkeypatch.setattr(module._Acceptance, "before_merge", failed)
    calls = []

    async def confirm(*_):
        calls.append(1)
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    first = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert first["status"] == "needs_recovery", first
    acceptance = git(wt, "rev-parse", "HEAD")
    monkeypatch.setattr(module._Acceptance, "before_merge", original)
    refreshed = _report(wt)
    second = asyncio.run(PlanAcceptService(repo).accept("idea", refreshed, confirm))
    assert second["status"] == "accepted", second
    assert second["acceptance_sha"] == acceptance
    assert len(calls) == 2
    assert len(list((repo / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))) == 1


def test_accepted_base_remaining_handoff_uses_fresh_form(pending):
    repo, _wt, uri = pending

    async def accept(*_):
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    first = asyncio.run(PlanAcceptService(repo).accept("idea", uri, accept))
    assert first["status"] == "accepted", first
    report = _report(repo)
    calls = []

    async def remaining(message, schema):
        calls.append(message)
        assert "already completed" in message
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_and_handoff", "activity_effort": "high"})

    second = asyncio.run(PlanAcceptService(repo).accept("idea", report, remaining))
    assert second["status"] == "handed_off", second
    assert second["activity_effort"] == "high"
    assert len(calls) == 1


def test_required_pr_policy_refuses_before_native_form(pending):
    repo, wt, uri = pending
    with (repo / ".devkit/config.toml").open("a") as file:
        file.write('\n[worktree]\npull_request = "required"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Require pull request")

    async def forbidden(*_):
        raise AssertionError("required PR cannot show local combination form")

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, forbidden))
    assert result["status"] == "blocked", result
    assert "status: reviewing" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()
