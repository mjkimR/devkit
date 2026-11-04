from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.maintenance_history.cli import cli
from devkit_agt.features.maintenance_history.models.errors import Deferred, GhUnavailable
from devkit_agt.features.maintenance_history.repositories.github import run_gh


def test_cli_discovery_json_and_advisory_channels(tmp_path: Path) -> None:
    runner = CliRunner()
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text('[maintenance.history]\nrepository = "owner/repo"\n')
    result = runner.invoke(cli, ["history", "init", "--format", "json", "--workspace-root", str(tmp_path)])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "HISTORY_AUTHORITY_MISSING"
    text_result = runner.invoke(cli, ["history", "init", "--workspace-root", str(tmp_path)])
    assert "HISTORY_AUTHORITY_MISSING" in text_result.stderr
    assert "[ACTION]" in text_result.stderr
    assert text_result.stdout == ""
    help_result = runner.invoke(cli, ["history", "finish", "--help"])
    assert "--file" in help_result.output
    process = subprocess.run(
        ["uv", "run", "--no-sync", "devkit", "maintenance", "history", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0
    for command in ("init", "start", "finish", "publish", "update", "list", "get"):
        assert command in process.stdout


def test_gh_runner_preserves_status_headers_and_request_body(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shim = tmp_path / "gh"
    trace = tmp_path / "request"
    shim.write_text(
        "#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\nPath("
        + repr(str(trace))
        + ').write_text(sys.stdin.read())\nsys.stdout.write("HTTP/2.0 403 Forbidden\\r\\nX-RateLimit-Remaining: 0\\r\\nRetry-After: 10\\r\\n\\r\\n{\\"message\\":\\"limited\\"}\\n")\nsys.exit(1)\n'
    )
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    response = run_gh("POST", "repos/owner/repo/git/blobs", {"encoding": "base64", "content": "YQ=="}, 1)
    assert response.status == 403
    assert response.headers["retry-after"] == "10"
    assert json.loads(trace.read_text()) == {"encoding": "base64", "content": "YQ=="}


def test_gh_runner_missing_logged_out_transport_and_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(GhUnavailable):
        run_gh("GET", "repos/owner/repo", None, 1)
    shim = tmp_path / "gh"
    shim.write_text("#!/bin/sh\nexit 1\n")
    shim.chmod(0o755)
    with pytest.raises(GhUnavailable):
        run_gh("GET", "repos/owner/repo", None, 1)
    shim.write_text('#!/bin/sh\nif [ "$1" = "auth" ]; then exit 0; fi\nexit 1\n')
    with pytest.raises(Deferred):
        run_gh("GET", "repos/owner/repo", None, 1)
    shim.write_text("#!/bin/sh\n/bin/sleep 1\n")
    with pytest.raises(subprocess.TimeoutExpired):
        run_gh("GET", "repos/owner/repo", None, 0.01)


def test_headerless_authenticated_gh_maps_uncertainty_at_reference_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from devkit_agt.features.maintenance_history.models.errors import PublishUnknown
    from devkit_agt.features.maintenance_history.services.publication import GitHubHistory

    shim = tmp_path / "gh"
    shim.write_text('#!/bin/sh\nif [ "$1" = "auth" ]; then exit 0; fi\nexit 1\n')
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    client = GitHubHistory("owner/repo", "maintenance-history")
    with pytest.raises(Deferred):
        client.request("GET", "git/ref/heads/maintenance-history")
    with pytest.raises(Deferred):
        client.request("POST", "git/blobs", {"content": "x"})
    with pytest.raises(PublishUnknown):
        client.request("PATCH", "git/refs/heads/maintenance-history", {"sha": "a" * 40}, reference=True)
    assert [item["result"] for item in client.attempts] == ["deferred", "deferred", "unknown"]
