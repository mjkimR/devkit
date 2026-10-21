from __future__ import annotations

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from devkit_dist.features.shared.repositories.local import LocalAdapter, discover

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


def briefing(root: Path, sha: str) -> str:
    # Complete each required section with authored evidence, preserving template identity.
    text = reports.template(root, "example", sha)
    return (
        "\n".join(line + "\nEvidence." if line.startswith(("## ", "#### ")) else line for line in text.splitlines())
        + "\n"
    )


@pytest.mark.parametrize("language", ["en", "ko"])
def test_publication_retry_validation_and_language(repo, monkeypatch, language):
    root, sha = repo
    monkeypatch.setattr(reports, "approval_language", lambda _: language)
    body = briefing(root, sha)
    first = reports.publish(root, "example", sha, body)
    assert reports.publish(root, "example", sha, body) == first
    assert reports.validate(root, "example", sha, first.metadata.artifact_uri) == first
    assert git(root, "status", "--porcelain") == ""
    monkeypatch.setattr(reports, "approval_language", lambda _: "ko" if language == "en" else "en")
    with pytest.raises(reports.ReviewRefreshRequiredError):
        reports.validate(root, "example", sha, first.metadata.artifact_uri)


@pytest.mark.parametrize(
    "replace", ["PADR-choice", "review-01.yaml", "Consequences", "source_sha", "repository_namespace"]
)
def test_incomplete_or_false_report_refused(repo, replace):
    root, sha = repo
    body = briefing(root, sha).replace(replace, "wrong")
    with pytest.raises(reports.ReportInvalidError):
        reports.publish(root, "example", sha, body)


def test_dirty_false_sha_and_stale_source(repo):
    root, sha = repo
    body = briefing(root, sha)
    artifact = reports.publish(root, "example", sha, body)
    with pytest.raises(reports.ReportInvalidError):
        reports.publish(root, "example", "a" * 40, body)
    (root / "new").write_text("dirty")
    with pytest.raises(reports.ReportInvalidError):
        reports.publish(root, "example", sha, body)
    git(root, "add", ".")
    git(root, "commit", "-m", "new")
    with pytest.raises(reports.ReviewRefreshRequiredError):
        reports.validate(root, "example", sha, artifact.metadata.artifact_uri)
    assert reports.validate_artifact(root, "example", sha, artifact.metadata.artifact_uri) == artifact


def test_expired_retry_new_generation(repo, monkeypatch):
    root, sha = repo
    now = datetime.now(UTC)
    local = LocalAdapter(discover(root), clock=lambda: now)
    monkeypatch.setattr(reports, "adapter", lambda _: local)
    body = briefing(root, sha)
    first = reports.publish(root, "example", sha, body)
    now += timedelta(days=8)
    with pytest.raises(reports.ReviewRefreshRequiredError):
        reports.validate(root, "example", sha, first.metadata.artifact_uri)
    second = reports.publish(root, "example", sha, body)
    assert first.metadata.artifact_uri != second.metadata.artifact_uri


def test_size_and_wrong_repository(repo, tmp_path_factory):
    root, sha = repo
    body = briefing(root, sha)
    with pytest.raises(reports.ReportInvalidError):
        reports.publish(root, "example", sha, body + "x" * reports.MAX_BYTES)
    artifact = reports.publish(root, "example", sha, body)
    uri = artifact.metadata.artifact_uri.replace(artifact.metadata.repository_namespace, "0" * 64)
    with pytest.raises(reports.ReviewRefreshRequiredError):
        reports.validate(root, "example", sha, uri)


def test_cli_and_mcp_publish_same_artifact(repo):
    import asyncio
    import json

    from click.testing import CliRunner
    from devkit_dist.cli import cli

    from devkit_spec.features.proposals.mcp.report import create_tools

    root, sha = repo
    body = briefing(root, sha)
    result = CliRunner().invoke(
        cli,
        [
            "spec",
            "proposal",
            "report",
            "example",
            "--source-sha",
            sha,
            "--body-file",
            "-",
            "--workspace-root",
            str(root),
            "--format",
            "json",
        ],
        input=body,
    )
    assert result.exit_code == 0, result.output

    async def forbidden_confirm(*args):
        raise AssertionError("report publication must not request approval")

    tool = create_tools(root)[0]
    assert tool.execution == "bounded_write"

    async def invoke():
        return await tool.invoke({"slug": "example", "source_sha": sha, "body": body}, forbidden_confirm)

    response = asyncio.run(invoke())
    assert response == json.loads(result.output)
    assert "content" not in response
    artifact = reports.publish_workspace_report(root, "example", sha, body)
    assert artifact.content == body
    assert reports.validate(root, "example", sha, response["artifact_uri"]) == artifact
    assert response == artifact.receipt_dict()


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
    report = reports.publish(root, "example", sha, briefing(root, sha))
    assert reports.validate(root, "example", sha, report.metadata.artifact_uri) == report
