from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from spec_support.delivery import _cli, _make_synced_repo, _start_worktree
from spec_support.scope import git

from devkit_spec.features.delivery.cli.proposals import proposal_group


@pytest.fixture(scope="module")
def proposal_seed_template(synced_template: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    seed_root = tmp_path_factory.mktemp("proposal-seed-template")
    repo = _make_synced_repo(seed_root, synced_template)
    _cli(repo, "sync")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Record complete consumer installation")
    wt = _start_worktree(repo, "plan-idea", seed_root / "seed-planning")
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
    git(repo, "worktree", "remove", "--force", str(wt))
    return repo


@pytest.fixture
def pending(tmp_path: Path, proposal_seed_template: Path):
    repo = tmp_path / "repo"
    shutil.copytree(proposal_seed_template, repo, symlinks=True)
    wt = tmp_path / "planning"
    git(repo, "worktree", "add", "-q", str(wt), "plan-idea")
    git(repo, "config", "branch.plan-idea.devkitWorktree", "true")
    git(repo, "config", "branch.plan-idea.devkitBase", "main")
    shutil.copytree(repo / ".devkit/managed", wt / ".devkit/managed", dirs_exist_ok=True)
    return repo, wt


@pytest.mark.parametrize("mode", ["accept_only", "accept_and_handoff"])
def test_accept_cli_commits_and_merges_exact_reviewed_plan(pending, mode):
    repo, planning = pending
    result = CliRunner().invoke(
        proposal_group,
        [
            "accept",
            "idea",
            "--by",
            "user",
            "--mode",
            mode,
            "--effort",
            "low",
            "-w",
            str(repo),
            "--format",
            "json",
        ],
    )
    assert result.exit_code in {0, 1}, result.output
    payload = json.loads(result.output)
    if mode == "accept_only":
        assert payload["status"] == "accepted", json.dumps(payload, indent=2)
        assert result.exit_code == 0
    else:
        assert payload["status"] in {"handed_off", "needs_recovery"}, json.dumps(payload, indent=2)
        assert result.exit_code == (0 if payload["status"] == "handed_off" else 1)
    assert payload["acceptance_authority"] == "user"
    assert "acceptance_commit" in payload["completed_steps"]
    assert "status: accepted" in (repo / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert not planning.exists()
    assert bool(git(repo, "branch", "--list", "dev-idea")) is (mode == "accept_and_handoff")
    if mode == "accept_and_handoff" and payload["status"] == "needs_recovery":
        assert (repo.parent / "repo-wt-dev-idea").exists()
        assert "worktree_setup" in payload["completed_steps"]


def test_accept_cli_refuses_invalid_mode(pending):
    repo, planning = pending
    before = git(repo, "show-ref")
    result = CliRunner().invoke(
        proposal_group,
        ["accept", "idea", "--by", "user", "--mode", "invalid_mode", "-w", str(repo)],
    )
    assert result.exit_code == 2
    assert "Invalid value for '--mode'" in result.output
    assert git(repo, "show-ref") == before and planning.exists()


def test_accept_cli_uses_plan_accept_auto_when_development_remains_ask(pending):
    repo, planning = pending
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nplan-accept = "auto"\ndev-integration = "ask"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate proposal acceptance to policy")
    git(planning, "merge", "--no-edit", "main")

    result = CliRunner().invoke(
        proposal_group,
        [
            "accept",
            "idea",
            "--by",
            "policy",
            "--mode",
            "accept_only",
            "-w",
            str(repo),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "accepted"
    assert payload["acceptance_authority"] == "policy"


def test_accept_cli_withdraws_its_writes_when_the_commit_gate_refuses(pending, tmp_path):
    repo, planning = pending
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit").write_text("#!/bin/sh\necho 'RULE-example refused the staged tree' >&2\nexit 1\n")
    (hooks / "pre-commit").chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))
    before = git(repo, "show-ref")

    result = CliRunner().invoke(
        proposal_group,
        ["accept", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo), "--format", "json"],
    )

    # Nothing was done: the command fails outright with one error document (ARCH-08-1 section 4).
    assert result.exit_code == 2, result.output
    error = json.loads(result.output)["error"]
    assert error["code"] == "SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED" and error["advisory"]["mode"] == "INPUT_ERROR"
    assert error["advisory"]["details"] == ["RULE-example refused the staged tree"]
    assert error["advisory"]["target_files"] == ["plan-idea"]
    text = CliRunner().invoke(
        proposal_group, ["accept", "idea", "--by", "user", "--mode", "accept_only", "-w", str(repo)]
    )
    assert text.exit_code == 2 and text.stdout == ""
    assert "SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED" in text.stderr
    assert git(planning, "status", "--porcelain") == ""
    assert "status: reviewing" in (planning / "docs/proposals/PROP-idea/proposal.md").read_text()
    assert git(repo, "show-ref") == before


def _accept_json(root: Path, *args: str) -> dict:
    result = CliRunner().invoke(proposal_group, ["accept", "idea", *args, "-w", str(root), "--format", "json"])
    assert result.exit_code == 2, result.output
    return json.loads(result.output)["error"]


def test_a_policy_acceptance_is_never_redirected_to_the_user(pending):
    repo, planning = pending
    # Under plan-accept=ask the policy refusal wins, even off the base checkout.
    for root in (repo, planning):
        error = _accept_json(root, "--by", "policy", "--mode", "accept_only")
        assert error["code"] == "SPEC_PROPOSAL_POLICY_NOT_AUTO" and "--by user" not in json.dumps(error)
    config = repo / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\nplan-accept = "auto"\n')
    git(repo, "add", ".devkit/config.toml")
    git(repo, "commit", "-m", "Delegate proposal acceptance to policy")
    git(planning, "merge", "--no-edit", "main")
    # Off the base checkout the fix keeps the caller's own --by policy command.
    error = _accept_json(planning, "--by", "policy", "--mode", "accept_only")
    assert error["code"] == "SPEC_PROPOSAL_WRONG_WORKTREE"
    assert "uv run devkit spec proposal accept idea --by policy --mode accept_only" in error["advisory"]["fix"]
    assert "--by user" not in json.dumps(error) and "<" not in error["advisory"]["fix"]


def _refuse_handoff_commit(repo: Path, tmp_path: Path) -> None:
    """Only the handoff commit on dev-idea is refused; the acceptance commit on plan-idea passes."""
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit").write_text(
        '#!/bin/sh\n[ "$(git rev-parse --abbrev-ref HEAD)" = dev-idea ] || exit 0\n'
        "echo 'RULE-example refused the handoff' >&2\nexit 1\n"
    )
    (hooks / "pre-commit").chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))


# SPEC-git-operator-result-readiness AC-03
def test_a_refused_handoff_commit_prints_the_stopped_acceptance_and_its_next_action(pending, tmp_path):
    repo, _planning = pending
    _refuse_handoff_commit(repo, tmp_path)

    result = CliRunner().invoke(
        proposal_group,
        ["accept", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low", "-w", str(repo)],
    )

    assert result.exit_code == 1, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith("[ACCEPTED_STOPPED: PROP-idea status=needs_recovery mode=accept_and_handoff")
    assert ",handoff" in lines[0] and "handoff_commit" not in lines[0] and lines[0].endswith(" commit=-]")
    assert lines[1].startswith("[NEXT_ACTION: ") and "[NEXT_CMD:" not in result.stdout
    assert "(SPEC_HANDOFF_COMMIT_REFUSED)" in result.stderr


# SPEC-git-operator-result-readiness AC-03
def test_a_refused_handoff_commit_stops_the_combined_acceptance_after_the_handoff(pending, tmp_path):
    repo, _planning = pending
    _refuse_handoff_commit(repo, tmp_path)
    args = ["accept", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low", "-w", str(repo)]

    result = CliRunner().invoke(proposal_group, [*args, "--format", "json"])

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "needs_recovery" and payload["commit"] is None
    assert "handoff" in payload["completed_steps"] and "handoff_commit" not in payload["completed_steps"]
    assert [error["code"] for error in payload["errors"]] == ["SPEC_HANDOFF_COMMIT_REFUSED"]
    assert payload["next_action"] == payload["errors"][0]["advisory"]["fix"]
    development = repo.parent / "repo-wt-dev-idea"
    assert git(development, "rev-parse", "HEAD") == git(repo, "rev-parse", "HEAD")
    assert git(development, "status", "--porcelain") != ""


# SPEC-git-operator-result-readiness AC-03
def test_a_combined_acceptance_commits_the_handoff_transaction(pending):
    repo, _planning = pending
    args = ["accept", "idea", "--by", "user", "--mode", "accept_and_handoff", "--effort", "low", "-w", str(repo)]

    result = CliRunner().invoke(proposal_group, [*args, "--format", "json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "handed_off", json.dumps(payload, indent=2)
    development = repo.parent / "repo-wt-dev-idea"
    head = git(development, "rev-parse", "HEAD")
    assert payload["commit"] == head
    assert git(development, "rev-list", "--parents", "-n", "1", head).split() == [head, git(repo, "rev-parse", "HEAD")]
    assert {"handoff", "handoff_commit"} <= set(payload["completed_steps"])
    assert git(development, "status", "--porcelain") == ""
