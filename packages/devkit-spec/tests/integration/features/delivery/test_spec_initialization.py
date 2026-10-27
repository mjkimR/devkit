"""Spec creation owns binding and scope registration, including partial-success recovery."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli
from spec_support.proposals import TODAY, write_workflow
from spec_support.scope import git, make_repo

from devkit_spec.features.delivery.usecases.specs import CreateSpecUseCase
from devkit_spec.features.scope import load_token, open_session


def development_worktree(tmp_path: Path) -> Path:
    base = make_repo(tmp_path / "base")
    write_workflow(base, "sdd-spec-feature")
    git(base, "add", ".devkit")
    git(base, "commit", "-q", "-m", "workflow")
    task = tmp_path / "task"
    git(base, "worktree", "add", "-q", "-b", "dev-fresh", str(task))
    return task


def test_spec_new_registers_its_created_bundle_without_an_extra_command(tmp_path: Path) -> None:
    task = development_worktree(tmp_path)
    result = CliRunner().invoke(cli, ["spec", "new", "fresh", "-w", str(task), "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert (task / data["dir"] / "spec.md").is_file()
    assert data["workflow"] == "sdd-spec-feature"
    assert data["scope"]["spec"] == data["dir"]
    assert load_token(open_session(task).location.token_path) == data["scope"]["token"]


def test_registration_failure_keeps_created_spec_and_existing_owner_token(tmp_path: Path) -> None:
    task = development_worktree(tmp_path)
    session = open_session(task)
    session.location.token_path.write_text("existing-token\n")
    initialized = CreateSpecUseCase().execute(task, "fresh", day=TODAY)
    assert initialized.registered is None
    assert (task / initialized.spec.dir / "spec.md").is_file()
    assert load_token(session.location.token_path) == "existing-token"
    assert all(not notice.code.startswith("SPEC_SCOPE_") for notice in initialized.notices)


@pytest.mark.parametrize("output", ["json", "text"])
@pytest.mark.parametrize("strict", [False, True])
def test_spec_creation_registration_failure_preserves_primary_output(tmp_path: Path, output: str, strict: bool) -> None:
    task = development_worktree(tmp_path)
    session = open_session(task)
    session.location.token_path.write_text("already-owned\n")
    args = ["spec", "new", "fresh", "-w", str(task), "--format", output]
    if strict:
        args.append("--strict")
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert "SPEC_SCOPE_" not in result.output and "SCOPE_ACK" not in result.output
