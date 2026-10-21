"""Revision evidence and reviewer metadata at the envelope authoring boundary."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.models.errors import EnvelopeFindingsError
from devkit_agt.features.workflow.services.envelope import compose_envelope, load_envelopes, render_envelope
from testsupport.gate import git
from testsupport.workflow import write_config, write_unit


def _repository(root: Path) -> str:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "dev@example.com")
    git(root, "config", "user.name", "Dev")
    git(root, "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "seed")
    return git(root, "rev-parse", "HEAD").stdout.strip()


def _author(root: Path, *args: str):
    write_config(root, '[workflow]\ndefault = "direct-delivery"\n')
    return CliRunner().invoke(
        cli, ["envelope", "new", "-w", str(root), "--unit", "work/a", "--kind", "scout", "--summary", "scope", *args]
    )


def test_authoring_resolves_existing_scope_revisions(workspace: Path) -> None:
    sha = _repository(workspace)
    unit = write_unit(workspace, "work/a")
    result = _author(workspace, "--head", sha[:8], "--base", "main")
    assert result.exit_code == 0, result.output
    assert yaml.safe_load((unit / "envelopes/scout-01.yaml").read_text())["diff_scope"] == {"base": sha, "head": sha}


@pytest.mark.parametrize("flag", ["--head", "--base"])
@pytest.mark.parametrize("value", ["unknown", "tree", "option"])
def test_authoring_refuses_unknown_and_non_commit_scope(workspace: Path, flag: str, value: str) -> None:
    _repository(workspace)
    unit = write_unit(workspace, "work/a")
    revision = {
        "unknown": "0" * 40,
        "tree": git(workspace, "rev-parse", "HEAD^{tree}").stdout.strip(),
        "option": "--all",
    }[value]
    result = _author(workspace, flag, revision)
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_FLAG_INVALID" in result.stderr
    assert not (unit / "envelopes").exists()


def test_authoring_outside_git_keeps_lexical_scope(workspace: Path) -> None:
    unit = write_unit(workspace, "work/a")
    result = _author(workspace, "--head", "abc1234", "--base", "main")
    assert result.exit_code == 0, result.output
    assert yaml.safe_load((unit / "envelopes/scout-01.yaml").read_text())["diff_scope"] == {
        "base": "main",
        "head": "abc1234",
    }
    invalid = _author(workspace, "--head", "HEAD")
    assert invalid.exit_code == 2 and "ENVELOPE_FLAG_INVALID" in invalid.stderr


@pytest.mark.parametrize("severity", ["medium", "critical", "major", "P2"])
def test_finding_severity_survives_review_and_reverify(tmp_path: Path, severity: str) -> None:
    unit = write_unit(tmp_path, "work/a")
    draft = compose_envelope(
        unit_dir=unit,
        envelopes=load_envelopes(unit),
        kind="review",
        findings_yaml=f"- issue: bug\n  evidence: code.py:3\n  severity: {severity}\n- issue: other\n  evidence: code.py:5\n",
    )
    body = render_envelope(draft, "2026-10-17T00:00:00Z")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(body)
    loaded = load_envelopes(unit)
    review = loaded.latest("review")
    assert review is not None and review.open_findings() == 2
    assert review.to_dict()["findings"][0]["severity"] == severity
    assert "severity" not in review.to_dict()["findings"][1]
    again = compose_envelope(unit_dir=unit, envelopes=loaded, kind="reverify", source="latest", resolve=["all"])
    assert again.open_findings() == 0
    assert yaml.safe_load(render_envelope(again, "2026-10-17T00:00:01Z"))["findings"][0]["severity"] == severity


@pytest.mark.parametrize("value", ['""', '"  "', "null", "2", "true", "[]", "{}"])
def test_finding_severity_rejects_empty_and_non_string_values(tmp_path: Path, value: str) -> None:
    unit = write_unit(tmp_path, "work/a")
    with pytest.raises(EnvelopeFindingsError):
        compose_envelope(
            unit_dir=unit,
            envelopes=load_envelopes(unit),
            kind="review",
            findings_yaml=f"- {{issue: bug, evidence: code.py:3, severity: {value}}}",
        )
