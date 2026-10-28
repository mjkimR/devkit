"""General project status reuses hook diagnostics without running gates or changing hook files."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.gate.usecases.hooks import hooks
from devkit_agt.features.gate.usecases.status import GateStatusUseCase, status_check
from devkit_dist.features.distribution.services.installation import status_checks
from devkit_dist.features.distribution.usecases.status import get_project_status
from distsupport.distribution import cli
from testsupport.gate import git


def _snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode)
        for path in root.rglob("*")
        if path.is_file()
    }


def test_harness_metadata_registers_gate_check() -> None:
    [entry] = [e for e in metadata.entry_points(group=status_checks.GROUP) if e.name == "gate-hooks"]
    assert entry.value == "devkit_agt.features.gate.usecases.status:status_check"
    assert entry.load() is status_check


@pytest.mark.parametrize("damage", ["overwrite", "missing-entry", "nonexecutable-entry", "hooks-path"])
def test_hook_diagnostics_reach_general_status_without_mutation(
    repo: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    hooks.install(repo, sys.executable)
    hook = repo / ".git/hooks/pre-commit"
    entry = repo / ".git/hooks/pre-commit.d/20-devkit"
    if damage == "overwrite":
        hook.write_text("#!/bin/sh\n# pre-commit install -f replacement\nexit 0\n")
    elif damage == "missing-entry":
        entry.unlink()
    elif damage == "nonexecutable-entry":
        entry.chmod(0o644)
    else:
        git(repo, "config", "core.hooksPath", ".husky")
    from devkit_agt.features.gate.usecases import runner

    monkeypatch.setattr(runner, "run_stage", lambda *_: pytest.fail("status ran a gate"))
    before = _snapshot(repo / ".git")
    expected = [notice.to_dict() for notice in GateStatusUseCase().execute(repo).notices]
    assert [notice["code"] for notice in expected] == [
        "GATE_HOOKS_PATH_SET" if damage == "hooks-path" else "GATE_HOOK_ENTRY_MISSING"
    ]
    report = get_project_status(repo, [])
    assert report.errors == [] and report.host_hooks == []
    assert [notice.to_dict() for notice in report.notices] == expected
    assert _snapshot(repo / ".git") == before
    for options, code in (([], 0), (["--strict"], 1)):
        result = CliRunner().invoke(cli, ["status", "-w", str(repo), *options])
        assert result.exit_code == code, result.output
        assert result.stderr == ""
        assert json.loads(result.stdout)["notices"] == expected
    assert _snapshot(repo / ".git") == before


def test_baseline_with_provider_disabled_then_enabled(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hooks.install(repo, sys.executable)
    (repo / ".git/hooks/pre-commit").write_text("#!/bin/sh\nexit 0\n")
    before = _snapshot(repo / ".git")
    original = status_checks.metadata.entry_points
    with monkeypatch.context() as disabled:
        disabled.setattr(
            status_checks.metadata,
            "entry_points",
            lambda group: [] if group == status_checks.GROUP else original(group=group),
        )
        assert get_project_status(repo, []).notices == []
    assert [notice.code for notice in get_project_status(repo, []).notices] == ["GATE_HOOK_ENTRY_MISSING"]
    assert _snapshot(repo / ".git") == before


def test_healthy_disabled_and_non_git_projects(repo: Path, tmp_path: Path) -> None:
    hooks.install(repo, sys.executable)
    assert status_check(repo) == ()
    hooks.UninstallHooksUseCase().execute(repo)
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text(
        "[gates.settings.rules-check]\nenabled = false\n"
        "[gates.settings.verify-commands]\nenabled = false\n"
        "[gates.settings.message-nonempty]\nenabled = false\n"
    )
    assert status_check(repo) == ()
    outside = tmp_path / "outside"
    outside.mkdir()
    assert status_check(outside) == ()


def test_real_pre_commit_force_install_exposes_existing_warning(repo: Path, tmp_path: Path) -> None:
    executable = shutil.which("pre-commit")
    if executable is None:
        pytest.skip("pre-commit is not installed")
    hooks.install(repo, sys.executable)
    (repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    result = subprocess.run(
        [executable, "install", "-f"],
        cwd=repo,
        capture_output=True,
        text=True,
        env={**os.environ, "PRE_COMMIT_HOME": str(tmp_path / "pre-commit-home")},
    )
    assert result.returncode == 0, result.stderr
    assert (repo / ".git/hooks/pre-commit.d/20-devkit").is_file()
    before = _snapshot(repo / ".git")
    expected = [notice.to_dict() for notice in GateStatusUseCase().execute(repo).notices]
    assert [notice["code"] for notice in expected] == ["GATE_HOOK_ENTRY_MISSING"]
    assert [notice.to_dict() for notice in get_project_status(repo, []).notices] == expected
    assert _snapshot(repo / ".git") == before
