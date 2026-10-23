from __future__ import annotations

import json
import tomllib
from dataclasses import replace
from pathlib import Path

import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
from click.testing import CliRunner
from devkit_agt.features.integration import IntegrationService
from devkit_agt.features.integration.cli import cli
from devkit_agt.features.worktree import RemoveFailedError
from testsupport.rules import git

from .test_pull_request import FakeGitHub


def test_lifecycle_mcp_service_registration_is_removed():
    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    entries = tomllib.loads(pyproject.read_text("utf-8"))["project"].get("entry-points", {})
    assert "devkit.host.services" not in entries


def test_integrate_cli_executes_after_host_conversation(repo):
    base, worktree = repo
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "completed"
    assert payload["authority"] == "host-conversation"
    assert not worktree.exists()


def test_integrate_cli_reads_automatic_authority_from_base(repo):
    base, worktree = repo
    config = base / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\ndev-integration = "auto"\n')
    from testsupport.rules import git

    git(base, "add", ".devkit/config.toml")
    git(base, "commit", "-qm", "enable automatic integration")
    # The source worktree follows the configured base before the operation is prepared.
    git(worktree, "merge", "-q", "main")
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["authority"] == "policy"
    assert not worktree.exists()


def test_integrate_cli_executes_pull_request_route(repo, tmp_path, ready_provider, monkeypatch):
    base, worktree = repo
    original_check = ready_provider.check
    monkeypatch.setattr(
        ready_provider,
        "check",
        lambda context: replace(original_check(context), landed_check="devkit rules check"),
    )
    remote = tmp_path / "remote.git"
    git(base, "init", "--bare", str(remote))
    git(base, "remote", "add", "origin", str(remote))
    git(base, "push", "-u", "origin", "main")
    service = IntegrationService(base)
    fake = FakeGitHub(base, remote)
    service.github = fake
    monkeypatch.setattr("devkit_agt.features.integration.cli.IntegrationService", lambda _root: service)

    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--route",
            "pull-request",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "completed"
    assert payload["authority"] == "host-conversation"
    assert payload["request"]["route"] == "pull-request"
    assert fake.merge_calls == 1 and not worktree.exists()


def test_integrate_cli_retries_observed_cleanup_without_merging_twice(repo, monkeypatch):
    base, worktree = repo
    original_remove = lifecycle._remove
    remove_attempts = 0

    def fail_once(root, path):
        nonlocal remove_attempts
        remove_attempts += 1
        if remove_attempts == 1:
            raise RemoveFailedError("temporary permission failure")
        return original_remove(root, path)

    monkeypatch.setattr(lifecycle, "_remove", fail_once)
    service = IntegrationService(base)
    monkeypatch.setattr("devkit_agt.features.integration.cli.IntegrationService", lambda _root: service)
    base_before = git(base, "rev-parse", "HEAD")

    def invoke():
        return CliRunner().invoke(
            cli,
            [
                "integrate",
                "dev-demo",
                "--task-kind",
                "session",
                "--task-id",
                "fixture",
                "--workspace-root",
                str(base),
                "--format",
                "json",
            ],
        )

    first = invoke()
    assert first.exit_code == 1, first.output
    first_payload = json.loads(first.output)
    assert first_payload["status"] == "partial"
    assert first_payload["steps"]["merge"] == "completed"
    assert worktree.exists()
    landed = git(base, "rev-parse", "HEAD")
    assert landed != base_before

    second = invoke()
    assert second.exit_code == 0, second.output
    second_payload = json.loads(second.output)
    assert second_payload["status"] == "completed"
    assert second_payload["steps"]["merge"] == "skipped"
    assert git(base, "rev-parse", "HEAD") == landed
    assert remove_attempts == 2
    assert not worktree.exists()
