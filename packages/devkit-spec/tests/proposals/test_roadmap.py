"""CLI authoring validates roadmap metadata before writes and handoff preserves origins."""

import inspect
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.cli import cli
from devkit_core.core import ArgumentError
from devkit_core.core.frontmatter import parse
from proposals.support import TODAY, accept

from devkit_spec.errors import ProposalInPlanningError
from devkit_spec.proposals import create_proposal, create_spec, handoff_proposal


def milestone(root: Path) -> None:
    path = root / "docs/roadmap/MS-foundation.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nid: MS-foundation\nstatus: planned\n---\n")


@pytest.mark.parametrize("value", ["Phase 1", "MS-missing", "", "PROP-parent"])
def test_invalid_milestone_never_creates_bundle(workspace: Path, value: str) -> None:
    with pytest.raises(ArgumentError):
        create_proposal(workspace, "child", milestone=value)
    assert "milestone" not in inspect.signature(create_spec).parameters
    assert not (workspace / "docs/proposals/PROP-child").exists()
    assert not (workspace / "specs").exists()


def test_cli_and_handoff_preserve_provenance(workspace: Path) -> None:
    milestone(workspace)
    create_proposal(workspace, "parent")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "spec",
            "proposal",
            "new",
            "child",
            "--milestone",
            "MS-foundation",
            "--decomposed-from",
            "PROP-parent",
            "-w",
            str(workspace),
        ],
    )
    assert result.exit_code == 0, result.output
    anchor = workspace / "docs/proposals/PROP-child/proposal.md"
    accept(anchor, "\nsupersedes: PROP-retired")
    handed = handoff_proposal(workspace, "child", today=TODAY)
    data = parse((workspace / handed.dir / "spec.md").read_text()).data
    assert data is not None
    assert {key: data[key] for key in ("decomposed_from", "supersedes")} == {
        "decomposed_from": "PROP-parent",
        "supersedes": "PROP-retired",
    }
    assert "milestone" not in data
    created = runner.invoke(cli, ["spec", "new", "independent", "--milestone", "MS-foundation", "-w", str(workspace)])
    assert created.exit_code == 2
    assert "No such option '--milestone'" in created.output


def test_decomposition_rejects_noneditable_parent(workspace: Path) -> None:
    parent = workspace / create_proposal(workspace, "parent").path
    accept(parent)
    with pytest.raises(ProposalInPlanningError):
        create_proposal(workspace, "child", decomposed_from="PROP-parent")
    assert not (workspace / "docs/proposals/PROP-child").exists()


def test_decomposition_rejects_planning_branch(workspace: Path) -> None:
    create_proposal(workspace, "parent")
    subprocess.run(["git", "init", "-q", str(workspace)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-qm",
            "init",
        ],
        check=True,
    )
    subprocess.run(["git", "-C", str(workspace), "branch", "plan-parent"], check=True)
    with pytest.raises(ProposalInPlanningError):
        create_proposal(workspace, "child", decomposed_from="PROP-parent")
