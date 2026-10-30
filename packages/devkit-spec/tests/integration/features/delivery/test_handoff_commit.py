"""The composed handoff commits its own transaction once (``ADR-composed-handoff-commits-its-own-transaction``).

A completed ``devkit spec proposal handoff <slug> --effort`` leaves ``dev-<slug>`` one clean direct child of the
reviewed base and reports HEAD as read after the hooks; a refused commit is a stopped handoff that keeps its writes;
the plain ``handoff <slug>`` stays write-only (``CAP-DLV-proposal-planning``).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from spec_support.delivery import _cli, _complete_proposal, _make_synced_repo, _start_worktree
from spec_support.scope import git

from devkit_spec.features.delivery.cli.proposals import proposal_group
from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

SUBJECT = "spec: hand off idea to Development"

# Rewrites the commit's metadata once, so the SHA `git commit` created is not the one HEAD names afterwards.
REWRITE = """#!/bin/sh
marker="$(git rev-parse --git-common-dir)/rewritten"
[ -f "$marker" ] && exit 0
git rev-parse HEAD > "$marker"
GIT_COMMITTER_DATE="2001-01-01T00:00:00Z" git commit -q --amend --no-edit --no-verify
"""
REFUSE = "#!/bin/sh\necho 'RULE-example refused the staged tree' >&2\nexit 1\n"


@pytest.fixture(scope="module")
def accepted_template(synced_template: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A base whose main holds an accepted proposal with completed Planning; copied per case."""
    root = tmp_path_factory.mktemp("handoff-commit-template")
    repo = _make_synced_repo(root, synced_template)
    _cli(repo, "sync")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "track complete synchronized projections")
    wt = _start_worktree(repo, "plan-idea", root / "wt-idea")
    _complete_proposal(wt)
    git(repo, "merge", "-q", "--ff-only", "plan-idea")
    git(repo, "worktree", "remove", "--force", str(wt))
    git(repo, "branch", "-q", "-D", "plan-idea")
    return repo


@pytest.fixture
def base(tmp_path: Path, accepted_template: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(accepted_template, repo, symlinks=True)
    return repo


def _hook(repo: Path, tmp_path: Path, name: str, body: str) -> None:
    hooks = tmp_path / "hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / name).write_text(body)
    (hooks / name).chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))


def _worktree(repo: Path) -> Path:
    return repo.parent / "repo-wt-dev-idea"


# AC-01
def test_a_completed_handoff_is_one_clean_child_of_the_reviewed_base(base: Path, tmp_path: Path) -> None:
    reviewed = git(base, "rev-parse", "HEAD")
    _hook(base, tmp_path, "post-commit", REWRITE)

    result = CliRunner().invoke(proposal_group, ["handoff", "idea", "--effort", "low", "-w", str(base)])

    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith("[HANDOFF: PROP-idea status=handed_off ")
    assert lines[1].startswith("[NEXT_CMD: uv run devkit workflow next --unit specs/")
    match = re.search(r" commit=([0-9a-f]{40})\]$", lines[0])
    assert match is not None, lines[0]
    worktree = _worktree(base)
    head = git(worktree, "rev-parse", "HEAD")
    original = (base / ".git/rewritten").read_text().strip()
    assert match.group(1) == head != original  # HEAD read after the rewriting hook, not the SHA git commit made
    assert git(worktree, "rev-list", "--parents", "-n", "1", head).split() == [head, reviewed]
    assert git(worktree, "log", "-1", "--format=%s") == SUBJECT
    assert git(worktree, "status", "--porcelain", "--untracked-files=all") == ""
    changed = git(worktree, "diff", "--name-only", "--no-renames", reviewed, head).splitlines()
    assert "docs/proposals/PROP-idea/proposal.md" in changed
    assert any(path.startswith("specs/") and path.endswith("/spec.md") for path in changed)


# AC-01
def test_the_result_commit_equals_head_and_the_base_is_untouched(base: Path) -> None:
    reviewed = git(base, "rev-parse", "HEAD")

    result = HandoffUseCase(base).execute("idea", "low")

    assert result["status"] == "handed_off", json.dumps(result, indent=2)
    assert result["commit"] == git(_worktree(base), "rev-parse", "HEAD")
    assert result["errors"] == [] and result["next_command"].startswith("uv run devkit workflow next --unit specs/")
    assert git(base, "rev-parse", "HEAD") == reviewed and git(base, "status", "--porcelain") == ""


# AC-02
def test_a_refused_commit_stops_with_the_dirty_paths_and_keeps_the_writes(base: Path, tmp_path: Path) -> None:
    reviewed = git(base, "rev-parse", "HEAD")
    _hook(base, tmp_path, "pre-commit", REFUSE)

    result = CliRunner().invoke(proposal_group, ["handoff", "idea", "--effort", "low", "-w", str(base)])

    assert result.exit_code == 1, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith("[HANDOFF_STOPPED: PROP-idea status=needs_recovery ")
    assert lines[0].endswith(" commit=-]")
    assert lines[1].startswith("[NEXT_ACTION: ") and "dev-idea" in lines[1] and "git -C" in lines[1]
    assert "[NEXT_CMD:" not in result.stdout and "[HANDOFF: " not in result.stdout
    assert "(SPEC_HANDOFF_COMMIT_REFUSED)" in result.stderr and "[ACTION] INPUT_ERROR" in result.stderr
    assert "[DETAIL] RULE-example refused the staged tree" in result.stderr
    target = next(line for line in result.stderr.splitlines() if line.startswith("[TARGET] "))
    assert "docs/proposals/PROP-idea/proposal.md" in target and "/spec.md" in target
    worktree = _worktree(base)
    assert git(worktree, "rev-parse", "HEAD") == reviewed
    status = git(worktree, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert status and all(line[0] != " " for line in status)  # every write kept, staged and uncommitted
    assert list((worktree / "specs").glob("*/*-idea/spec.md"))


# AC-02
def test_a_refused_commit_result_has_no_next_command(base: Path, tmp_path: Path) -> None:
    _hook(base, tmp_path, "pre-commit", REFUSE)

    result = HandoffUseCase(base).execute("idea", "low")

    assert result["status"] == "needs_recovery" and result["commit"] is None
    assert "next_command" not in result and result["handoff"]["next_command"] is None
    assert result["next_action"] == result["errors"][0]["advisory"]["fix"]
    error = result["errors"][0]
    assert error["code"] == "SPEC_HANDOFF_COMMIT_REFUSED"
    staged = git(_worktree(base), "diff", "--cached", "--name-only", "--no-renames").splitlines()
    assert set(error["advisory"]["target_files"]) == set(staged)


# AC-04
def test_the_plain_handoff_stays_write_only(base: Path) -> None:
    worktree = _start_worktree(base, "dev-idea", base.parent / "plain-dev-idea")
    before = git(worktree, "rev-parse", "HEAD")

    result = CliRunner().invoke(proposal_group, ["handoff", "idea", "-w", str(worktree)])

    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("[HANDOFF: PROP-idea spec=SPEC-idea ")
    assert " commit=" not in result.stdout.splitlines()[0]
    assert git(worktree, "rev-parse", "HEAD") == before
    assert git(worktree, "status", "--porcelain", "--untracked-files=all") != ""
