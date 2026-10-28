"""CLI authoring validates roadmap metadata before writes and handoff preserves origins."""

import inspect
import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_core.core import ArgumentError
from devkit_core.core.frontmatter import parse
from devkit_dist.cli import cli
from spec_support.proposals import TODAY, accept

from devkit_spec.base.errors import ProposalInPlanningError
from devkit_spec.features.proposals import create_proposal, create_spec, handoff_proposal


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


@pytest.mark.parametrize("value", ["PROP-parent", " PROP-parent:", "PROP-Parent", "PROP-parent.md"])
def test_decomposition_records_the_normalized_parent_id(workspace: Path, value: str) -> None:
    create_proposal(workspace, "parent")
    created = create_proposal(workspace, "child", decomposed_from=value)
    data = parse((workspace / created.path).read_text()).data
    assert data is not None and data["decomposed_from"] == "PROP-parent"


@pytest.mark.parametrize("value", ["PROP-child:", "PROP-Child"])
def test_decomposition_rejects_the_proposal_itself_in_any_spelling(workspace: Path, value: str) -> None:
    with pytest.raises(ArgumentError):
        create_proposal(workspace, "child", decomposed_from=value)


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


@pytest.mark.parametrize("status", ["done", "dropped", "active", "planned"])
@pytest.mark.parametrize("alias", [False, True])
def test_milestone_membership_notices_preserve_milestone(workspace: Path, status: str, alias: bool) -> None:
    milestone(workspace)
    path = workspace / (
        "docs/roadmap/_archive/MS-foundation.md" if status in {"done", "dropped"} else "docs/roadmap/MS-foundation.md"
    )
    if status in {"done", "dropped"}:
        (workspace / "docs/roadmap/MS-foundation.md").unlink()
        path.parent.mkdir(parents=True)
    path.write_text(
        f"---\nid: MS-foundation\naliases: [MS-old]\nstatus: {status}\n"
        "scope_confirmed: true\ndecomposition_confirmed: true\n---\n"
    )
    before = path.read_bytes()
    result = create_proposal(workspace, "member", milestone="MS-old" if alias else "MS-foundation")
    data = parse((workspace / result.path).read_text()).data
    assert data is not None and data["milestone"] == "MS-foundation"
    assert path.read_bytes() == before
    notices = [notice.to_dict() for notice in result.notices if notice.code == "SPEC_PROPOSAL_MILESTONE_INACTIVE"]
    assert len(notices) == (1 if status in {"done", "dropped"} else 0)
    if notices:
        assert notices[0]["level"] == "NOTICE"
        assert "MS-foundation" in notices[0]["message"] and status in notices[0]["message"]
        assert "membership" in notices[0]["advisory"]["fix"]


@pytest.mark.parametrize("format", ["text", "json"])
@pytest.mark.parametrize("status", ["done", "dropped"])
def test_inactive_milestone_cli_notice_is_nonblocking_under_strict(workspace: Path, format: str, status: str) -> None:
    milestone(workspace)
    path = workspace / (
        "docs/roadmap/_archive/MS-foundation.md" if status in {"done", "dropped"} else "docs/roadmap/MS-foundation.md"
    )
    if status in {"done", "dropped"}:
        (workspace / "docs/roadmap/MS-foundation.md").unlink()
        path.parent.mkdir(parents=True)
    path.write_text(f"---\nid: MS-foundation\nstatus: {status}\n---\n")
    result = CliRunner().invoke(
        cli,
        [
            "spec",
            "proposal",
            "new",
            "member",
            "--milestone",
            "MS-foundation",
            "--strict",
            "--format",
            format,
            "-w",
            str(workspace),
        ],
    )
    assert result.exit_code == 0, result.output
    if format == "json":
        payload = json.loads(result.stdout)
        notices = [notice["advisory"] for notice in payload["notices"]]
        assert any(
            notice["code"] == "SPEC_PROPOSAL_MILESTONE_INACTIVE" and notice["level"] == "NOTICE" for notice in notices
        )
    else:
        assert "SPEC_PROPOSAL_MILESTONE_INACTIVE" in result.stderr and "[NOTICE]" in result.stderr


@pytest.mark.parametrize(
    ("location", "status"),
    [
        ("docs/roadmap", "done"),
        ("docs/roadmap/_archive", "active"),
        ("docs/roadmap/nested", "done"),
        ("docs/roadmap/_archive/year", "dropped"),
    ],
)
def test_invalid_milestone_placement_never_writes(workspace: Path, location: str, status: str) -> None:
    path = workspace / location / "MS-foundation.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\nid: MS-foundation\nstatus: {status}\n---\n")
    with pytest.raises(ArgumentError):
        create_proposal(workspace, "member", milestone="MS-foundation")
    assert not (workspace / "docs/proposals").exists()


def test_duplicate_milestone_identity_never_writes(workspace: Path) -> None:
    milestone(workspace)
    path = workspace / "docs/roadmap/_archive/MS-foundation.md"
    path.parent.mkdir()
    path.write_text("---\nid: MS-foundation\nstatus: done\n---\n")
    with pytest.raises(ArgumentError):
        create_proposal(workspace, "member", milestone="MS-foundation")
    assert not (workspace / "docs/proposals").exists()


@pytest.mark.parametrize("alias_owner", ["root", "archive"])
@pytest.mark.parametrize("status", ["done", "dropped"])
def test_alias_to_duplicate_canonical_milestone_never_writes(workspace: Path, alias_owner: str, status: str) -> None:
    for owner, directory, state in [("root", "docs/roadmap", "active"), ("archive", "docs/roadmap/_archive", status)]:
        path = workspace / directory / "MS-foundation.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        alias = "aliases: [MS-unique]\n" if owner == alias_owner else ""
        path.write_text(f"---\nid: MS-foundation\nstatus: {state}\n{alias}---\n")
    with pytest.raises(ArgumentError):
        create_proposal(workspace, "member", milestone="MS-unique")
    assert not (workspace / "docs/proposals").exists()
