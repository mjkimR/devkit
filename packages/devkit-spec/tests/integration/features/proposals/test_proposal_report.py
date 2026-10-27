from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli

from devkit_spec.features.proposals.usecases import report as reports


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode().strip()


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, str]:
    git(tmp_path, "init", "-b", "plan-example")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    unit = tmp_path / "docs/proposals/PROP-example"
    (unit / "decisions").mkdir(parents=True)
    (unit / "envelopes").mkdir()
    (unit / "proposal.md").write_text(
        "---\nid: PROP-example\ntitle: Example\nstatus: reviewing\nplanning_effort: medium\ndev_effort: high\n---\nProposal\n"
    )
    (unit / "decisions/PADR-choice.md").write_text("---\nid: PADR-choice\n---\nChoice\n")
    (unit / "envelopes/review-01.yaml").write_text("kind: review\nactivity_effort: medium\n")
    (tmp_path / ".gitignore").write_text(".devkit_dist/features/shared/\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path, git(tmp_path, "rev-parse", "HEAD")


def _cli(*args: str, input: str | None = None):
    return CliRunner().invoke(cli, ["spec", "proposal", "report", *args], input=input)


def test_cli_report_template_prints(repo):
    root, sha = repo
    text = _cli("example", "--source-sha", sha, "--workspace-root", str(root))
    assert text.exit_code == 0, text.output
    assert text.output == reports.template(root, "example", sha)
    for token in ("proposal: PROP-example", f"source_sha: {sha}", "### PADR-choice"):
        assert token in text.output
    assert "Proposed approval effects" in text.output
    assert "high" in text.output

    data = _cli("example", "--source-sha", sha, "--workspace-root", str(root), "--format", "json")
    assert data.exit_code == 0, data.output
    assert json.loads(data.output) == {"proposal": "PROP-example", "source_sha": sha, "report": text.output}
    head = _cli("example", "--workspace-root", str(root), "--format", "json")
    assert head.exit_code == 0, head.output
    assert json.loads(head.output) == {"proposal": "PROP-example", "source_sha": sha, "report": text.output}
    assert _cli("example", "--template", "--workspace-root", str(root)).exit_code == 2


def test_accepted_base_and_wrong_branch(repo):
    root, sha = repo
    git(root, "branch", "-m", "main")
    with pytest.raises(reports.ReportInvalidError):
        reports.template(root, "example", sha)
    proposal = root / "docs/proposals/PROP-example/proposal.md"
    proposal.write_text(proposal.read_text().replace("status: reviewing", "status: accepted"))
    git(root, "add", ".")
    git(root, "commit", "-m", "accepted")
    sha = git(root, "rev-parse", "HEAD")
    text = reports.template(root, "example", sha)
    assert "proposal: PROP-example" in text


def test_composed_handoff_advisories_are_emitted_once():
    from devkit_spec.features.delivery.cli.proposals import _result_advisories

    advisory = {
        "code": "SPEC_SCOPE_REGISTER_FAILED",
        "message": "scope registration failed",
        "level": "WARNING",
        "advisory": {"actor": "USER", "retry": "SAFE"},
    }
    assert len(_result_advisories({"notices": [advisory], "handoff": {"notices": [advisory]}})) == 1


@pytest.mark.parametrize("name", ["diagram.png", "한글.md"])
def test_source_skips_materials_it_does_not_read(repo, name):
    # A binary material or a non-ASCII file name is committed unit content the report never decodes.
    root, _sha = repo
    materials = root / "docs/proposals/PROP-example/materials"
    materials.mkdir()
    (materials / name).write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
    git(root, "add", ".")
    git(root, "commit", "-m", "material")
    sha = git(root, "rev-parse", "HEAD")
    assert reports.source(root, "example", sha).padrs == ("PADR-choice",)


def test_source_still_refuses_a_non_regular_material(repo):
    root, _sha = repo
    materials = root / "docs/proposals/PROP-example/materials"
    materials.mkdir()
    (materials / "한글-link.md").symlink_to("../proposal.md")
    git(root, "add", ".")
    git(root, "commit", "-m", "link")
    with pytest.raises(reports.ReportInvalidError, match="regular files"):
        reports.source(root, "example", git(root, "rev-parse", "HEAD"))
