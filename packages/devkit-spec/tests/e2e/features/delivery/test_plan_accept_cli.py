from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from spec_support.delivery import _cli, _make_synced_repo, _start_worktree
from spec_support.scope import git

from devkit_spec.features.delivery.cli.proposals import proposal_group
from devkit_spec.features.proposals.usecases.report import publish, template


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
    sha = git(wt, "rev-parse", "HEAD")
    body = template(wt, "idea", sha)
    body = (
        "\n".join(
            line + "\nEvidence reviewed." if line.startswith(("## ", "#### ")) else line for line in body.splitlines()
        )
        + "\n"
    )
    return repo, wt, publish(wt, "idea", sha, body).metadata.artifact_uri


@pytest.mark.parametrize("mode", ["accept_only", "accept_and_handoff"])
def test_accept_cli_commits_and_merges_exact_reviewed_plan(pending, mode):
    repo, planning, uri = pending
    result = CliRunner().invoke(
        proposal_group,
        [
            "accept",
            "idea",
            "--by",
            "user",
            "--report-uri",
            uri,
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


def test_accept_cli_refuses_changed_report_before_writing(pending):
    repo, planning, uri = pending
    before = git(repo, "show-ref")
    result = CliRunner().invoke(
        proposal_group,
        ["accept", "idea", "--by", "user", "--report-uri", uri + "-stale", "--mode", "accept_only", "-w", str(repo)],
    )
    assert result.exit_code == 2
    assert "PROPOSAL_REVIEW" in result.output
    assert git(repo, "show-ref") == before and planning.exists()
