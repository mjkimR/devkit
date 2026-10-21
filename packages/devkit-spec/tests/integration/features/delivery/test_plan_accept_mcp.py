from __future__ import annotations

import asyncio
import json

import pytest
from devkit_core.base.mcp import ConfirmationReply
from spec_support.delivery import _cli, _make_synced_repo, _start_worktree
from spec_support.scope import git

from devkit_spec.features.delivery.usecases.native_plan_accept import PlanAcceptService
from devkit_spec.features.proposals.usecases.report import publish, template


@pytest.fixture
def pending(tmp_path, request):
    synced = request.getfixturevalue("synced_template")
    policies = getattr(request, "param", {})
    extra = (
        "[workflow.approvals]\n" + "".join(f'{gate} = "{policy}"\n' for gate, policy in policies.items())
        if policies
        else ""
    )
    repo = _make_synced_repo(tmp_path, synced, extra_config=extra)
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


@pytest.mark.parametrize("pending", [{}, {"proposal-handoff": "auto", "dev-integration": "ask"}], indirect=True)
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
    if change in {"source", "base", "policy"}:
        assert result["errors"][0]["code"] == "PROPOSAL_APPROVAL_STALE"
    assert "status: reviewing" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not list((wt / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))


def test_plan_accept_commit_failure_preserves_exact_dirty_acceptance(pending, monkeypatch):
    import devkit_spec.features.delivery.usecases.native_plan_accept as module

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
    import devkit_spec.features.delivery.usecases.native_plan_accept as module

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
    import devkit_spec.features.proposals.usecases.report as reports

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
    from devkit_dist.features.host.models.errors import HostConfirmationError

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
    import devkit_spec.features.delivery.usecases.native_plan_accept as module

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


@pytest.mark.parametrize("uri", ["", "shared://wrong/invalid"])
def test_remaining_effects_require_report_before_form(pending, uri):
    from devkit_spec.features.proposals.usecases.report import ReviewRefreshRequiredError

    repo, _wt, report = pending

    async def accept(*_):
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    assert asyncio.run(PlanAcceptService(repo).accept("idea", report, accept))["status"] == "accepted"
    before = git(repo, "show-ref")

    async def forbidden(*_):
        raise AssertionError("invalid report must refuse before confirmation")

    with pytest.raises(ReviewRefreshRequiredError):
        asyncio.run(PlanAcceptService(repo).accept("idea", uri, forbidden))
    assert git(repo, "show-ref") == before
    assert not git(repo, "branch", "--list", "dev-idea")


@pytest.mark.parametrize("failure", ["returned", "raised"])
def test_combined_partial_failure_has_recovery_directive(pending, monkeypatch, failure):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffService
    from devkit_spec.features.delivery.usecases.native_plan_accept import ProposalApprovalStaleError

    repo, _wt, uri = pending

    def failed(*_):
        if failure == "raised":
            raise ProposalApprovalStaleError("injected prerequisite change after integration")
        return {"status": "needs_recovery", "errors": [], "notices": [], "worktree": {"created": True}}

    monkeypatch.setattr(HandoffService, "_execute", failed)

    async def confirm(*_):
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_and_handoff", "activity_effort": "low"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "needs_recovery", result
    assert "merge" in result["completed_steps"]
    assert "fresh accepted-base report" in result["next_action"]
    assert "fresh approval" in result["next_action"]
    assert result["next_action"] != "Acceptance complete"


def test_changed_integration_identity_returns_proposal_stale_code(pending, monkeypatch):
    from devkit_agt.features.integration.services import providers

    repo, wt, uri = pending
    before = git(repo, "show-ref")

    async def confirm(*_):
        monkeypatch.setattr(providers, "guards", lambda: ("replaced-registration",))
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, confirm))
    assert result["status"] == "blocked"
    assert result["errors"][0]["code"] == "PROPOSAL_APPROVAL_STALE"
    assert result["integration"]["errors"][0]["code"] == "INTEGRATION_REQUEST_STALE"
    assert git(repo, "show-ref") == before
    assert git(wt, "status", "--porcelain") == ""


@pytest.mark.parametrize(
    "pending",
    [{"plan-accept": "auto", "proposal-handoff": "auto", "dev-integration": "ask"}],
    indirect=True,
)
def test_automatic_acceptance_integration_and_handoff_need_no_form(pending):
    repo, wt, uri = pending

    async def forbidden(*_):
        raise AssertionError("automatic policies must not open a confirmation form")

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, forbidden))
    assert result["status"] == "handed_off", json.dumps(result, indent=2)
    assert result["acceptance_authority"] == "policy"
    assert {"acceptance_commit", "merge", "handoff"} <= set(result["completed_steps"])
    assert not wt.exists()
    decisions = list((repo / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))
    assert len(decisions) == 1
    assert "policy" in decisions[0].read_text()
    assert git(repo, "branch", "--list", "dev-idea")


@pytest.mark.parametrize(
    "pending", [{"plan-accept": "auto", "proposal-handoff": "ask", "dev-integration": "auto"}], indirect=True
)
def test_automatic_acceptance_preserves_result_at_handoff_ask(pending):
    repo, wt, uri = pending

    async def forbidden(*_):
        raise AssertionError("handoff ask must not force a combined form for automatic acceptance")

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, forbidden))
    assert result["status"] == "accepted", result
    assert result["acceptance_authority"] == "policy"
    assert "handoff approval" in result["next_action"]
    assert "status: accepted" in (repo / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not wt.exists()
    assert not git(repo, "branch", "--list", "dev-idea")


@pytest.mark.parametrize("pending", [{"dev-integration": "auto"}], indirect=True)
@pytest.mark.parametrize("approved", [False, True])
def test_source_auto_cannot_grant_itself_acceptance_authority(pending, approved):
    repo, wt, _uri = pending
    config = wt / ".devkit/config.toml"
    config.write_text(config.read_text() + 'plan-accept = "auto"\nproposal-handoff = "auto"\n')
    git(wt, "add", ".devkit/config.toml")
    git(wt, "commit", "-m", "Request automatic source approval")
    uri = _report(wt)
    before = git(repo, "show-ref")
    calls = []

    async def decline(*_):
        calls.append(1)
        return (
            ConfirmationReply("accept", {"approve": True, "mode": "accept_only"})
            if approved
            else ConfirmationReply("decline", {})
        )

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, decline))
    assert len(calls) == 1
    if approved:
        assert result["status"] == "accepted", result
        assert result["acceptance_authority"] == "user"
        assert "status: accepted" in (repo / "docs/proposals/PROP-idea/proposal.md").read_text()
        assert not wt.exists()
    else:
        assert result["status"] == "held", result
        assert git(repo, "show-ref") == before
        assert "status: reviewing" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()
        assert not list((wt / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))


@pytest.mark.parametrize(
    "pending", [{"plan-accept": "auto", "proposal-handoff": "auto", "dev-integration": "auto"}], indirect=True
)
@pytest.mark.parametrize("gate", ["plan-accept", "proposal-handoff"])
def test_source_revocation_blocks_automatic_effects(pending, gate):
    repo, wt, _uri = pending
    config = wt / ".devkit/config.toml"
    config.write_text(config.read_text().replace(f'{gate} = "auto"', f'{gate} = "ask"'))
    git(wt, "add", ".devkit/config.toml")
    git(wt, "commit", "-m", "Revoke automatic authority")
    uri = _report(wt)
    before = git(repo, "show-ref")

    async def forbidden(*_):
        raise AssertionError("prospective revocation must refuse before a confirmation form")

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, forbidden))
    assert result["status"] == "blocked", result
    assert git(repo, "show-ref") == before
    assert git(wt, "status", "--porcelain") == ""
    assert not list((wt / "docs/proposals/PROP-idea/decisions").glob("*plan-accept*"))


@pytest.mark.parametrize("pending", [{"plan-accept": "auto", "proposal-handoff": "auto"}], indirect=True)
def test_explicit_accept_only_never_handoffs_even_under_auto_and_retry(pending):
    repo, wt, uri = pending

    async def forbidden(*_):
        raise AssertionError("automatic accept-only requires no form and never starts Development")

    service = PlanAcceptService(repo)
    result = asyncio.run(service.accept("idea", uri, forbidden, mode="accept_only"))
    assert result["status"] == "accepted", result
    assert not wt.exists()
    assert not git(repo, "branch", "--list", "dev-idea")
    before = git(repo, "show-ref")
    retried = asyncio.run(service.accept("idea", _report(repo), forbidden, mode="accept_only"))
    assert retried["status"] == "accepted", retried
    assert git(repo, "show-ref") == before
    assert not git(repo, "branch", "--list", "dev-idea")


def test_explicit_accept_only_form_cannot_widen_operation_scope(pending):
    repo, wt, uri = pending
    before = git(repo, "show-ref")

    async def widen(_message, schema):
        assert schema["properties"]["mode"]["enum"] == ["accept_only"]
        assert schema["properties"]["mode"]["default"] == "accept_only"
        return ConfirmationReply("accept", {"approve": True, "mode": "accept_and_handoff", "activity_effort": "low"})

    result = asyncio.run(PlanAcceptService(repo).accept("idea", uri, widen, mode="accept_only"))
    assert result["status"] == "blocked", result
    assert git(repo, "show-ref") == before
    assert git(wt, "status", "--porcelain") == ""
    assert "status: reviewing" in (wt / "docs/proposals/PROP-idea/proposal.md").read_text()


def test_plan_accept_mcp_declares_optional_operation_scope(tmp_path):
    from devkit_spec.features.delivery.mcp.plan_accept import create_tools

    [tool] = create_tools(tmp_path)
    assert tool.input_schema["required"] == ["slug", "report_uri"]
    assert tool.input_schema["properties"]["mode"]["enum"] == ["accept_only", "accept_and_handoff"]
    assert tool.input_schema["properties"]["mode"]["default"] == "accept_and_handoff"
