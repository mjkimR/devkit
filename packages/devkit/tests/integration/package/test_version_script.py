"""Release preparation uses one input and refuses stale or invalid metadata."""

from __future__ import annotations

import importlib.util
import subprocess
import tomllib
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture
def script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("release_version", ROOT / "scripts/version.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "VERSION").write_text("0.1.2\n")
    (tmp_path / "pyproject.toml").write_text('[tool.uv.workspace]\nmembers = ["packages/*", "tools/*"]\n')
    for relative, name in (("packages/core", "demo-core"), ("tools/extension", "demo-extension")):
        path = tmp_path / relative
        path.mkdir(parents=True)
        (path / "pyproject.toml").write_text(
            f'[project]\nname = "{name}"\nversion = "0.1.0" # keep comment\n'
            'dependencies = ["demo-core>=0.1,<0.2", "external==0.1.0"]\n'
            "[project.optional-dependencies]\nextra = [\"demo-core[extra]==0.1.0; python_version >= '3.12'\"]\n"
            '[tool.example]\nversion = "unchanged"\n'
        )
    bundle = tmp_path / "packages/core/src/demo/bundle"
    bundle.mkdir(parents=True)
    (bundle / "bundle.toml").write_text(
        'name = "demo"\nversion = "0.1.0" # keep bundle comment\n[[assets]]\nid = "demo"\n'
    )
    return tmp_path


def test_sync_preserves_external_metadata_and_refreshes_lock(script, workspace, monkeypatch, capsys):
    run = Mock()
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main([], root=workspace) == 0
    for path in workspace.glob("**/pyproject.toml"):
        if path == workspace / "pyproject.toml":
            continue
        text = path.read_text()
        data = tomllib.loads(text)
        assert data["project"]["name"] in {"demo-core", "demo-extension"}
        assert data["project"]["version"] == "0.1.2"
        assert data["project"]["dependencies"] == ["demo-core==0.1.2", "external==0.1.0"]
        assert data["project"]["optional-dependencies"]["extra"] == [
            "demo-core[extra]==0.1.2; python_version >= '3.12'"
        ]
        assert "# keep comment" in text
        assert data["tool"]["example"]["version"] == "unchanged"
    bundle = workspace / "packages/core/src/demo/bundle/bundle.toml"
    assert tomllib.loads(bundle.read_text())["version"] == "0.1.2"
    assert "# keep bundle comment" in bundle.read_text()
    run.assert_called_once()
    assert run.call_args.args[0] == ["uv", "lock"]
    assert capsys.readouterr().out == "[VERSION: 0.1.2 state=synced packages=2]\n"
    assert script.metadata_updates(workspace)[2] == {}


@pytest.mark.parametrize("version", ["v0.1.2", "01.1.2", "0.1", "0.1.2rc1", "0.1.2\n0.1.3", ""])
def test_invalid_input_never_writes_or_locks(script, workspace, monkeypatch, version, capsys):
    (workspace / "VERSION").write_text(version)
    before = {p: p.read_bytes() for p in workspace.glob("**/pyproject.toml")}
    run = Mock()
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main([], root=workspace) == 2
    assert all(p.read_bytes() == content for p, content in before.items())
    run.assert_not_called()
    result = capsys.readouterr()
    assert result.out == ""
    assert "VERSION_INPUT_INVALID" in result.err


def test_check_is_read_only_and_reports_staleness(script, workspace, monkeypatch, capsys):
    before = {p: p.read_bytes() for p in workspace.glob("**/pyproject.toml")}
    run = Mock()
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main(["--check"], root=workspace) == 1
    assert all(p.read_bytes() == content for p, content in before.items())
    run.assert_not_called()
    advisory = capsys.readouterr().err
    assert "just version-sync" in advisory
    assert "[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will\n" in advisory
    assert "         fail identically. Correct the flag, argument, or input file before rerunning." in advisory
    for path, text in script.metadata_updates(workspace)[2].items():
        path.write_text(text)
    assert script.main(["--check"], root=workspace) == 0
    run.assert_not_called()


def test_missing_version_never_locks(script, workspace, monkeypatch):
    (workspace / "VERSION").unlink()
    run = Mock()
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main([], root=workspace) == 2
    run.assert_not_called()


def test_lock_failure_is_not_success(script, workspace, monkeypatch, capsys):
    run = Mock(side_effect=subprocess.CalledProcessError(1, ["uv", "lock"]))
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main([], root=workspace) == 2
    result = capsys.readouterr()
    assert result.out == ""
    assert "VERSION_SYNC_FAILED" in result.err


def test_release_rejects_wrong_tag_before_building():
    result = subprocess.run(["bash", "scripts/release.sh", "v99.0.0"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 1
    assert "does not match VERSION" in result.stderr


def test_workspace_internal_requirements_match_version(script):
    assert script.metadata_updates(ROOT)[2] == {}


def test_stale_bundle_is_checked_even_with_current_package_versions(script, workspace, monkeypatch):
    for path, content in script.metadata_updates(workspace)[2].items():
        path.write_text(content)
    bundle = workspace / "packages/core/src/demo/bundle/bundle.toml"
    bundle.write_text(bundle.read_text().replace('version = "0.1.2"', 'version = "0.1.0"'))
    run = Mock()
    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.main(["--check"], root=workspace) == 1
    run.assert_not_called()
    assert list(script.metadata_updates(workspace)[2]) == [bundle]
