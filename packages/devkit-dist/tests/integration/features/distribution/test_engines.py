"""``HARNESS_ENGINE_MISSING``: deployed rule, gate or workflow assets that no installed engine runs.

Engine presence is the name of a ``devkit.commands`` entry point (``rules``, ``gate``, ``workflow``), replaced here in
process, so the cases hold with and without devkit-agt installed.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit_dist.base.errors import HARNESS_INSTALL_FIX
from devkit_dist.features.distribution.services.installation import engines
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.status import get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH
from distsupport.distribution import cli, harness_assets_bundle


def _commands(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    entries = [SimpleNamespace(name=name) for name in names]
    monkeypatch.setattr(
        engines.metadata, "entry_points", lambda group: entries if group == engines.COMMAND_ENTRY_POINTS else []
    )


@pytest.fixture
def team(tmp_path: Path) -> InstalledBundle:
    return harness_assets_bundle(tmp_path)


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=[])
    return root


def _engine_notices(notices: list[dict]) -> list[dict]:
    return [notice for notice in notices if notice["code"] == "HARNESS_ENGINE_MISSING"]


def test_without_engines_sync_and_status_warn_and_deploy_as_before(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch, "spec")  # another package's command, no engine
    result = sync_project(target, [team]).to_dict()
    [notice] = _engine_notices(result["notices"])
    assert notice["level"] == "WARNING" and notice["exit_code"] == 0
    assert notice["message"] == "deployed assets that no installed engine runs: team (gate, rule, workflow)"
    assert notice["advisory"]["details"] == ["team: gate, rule, workflow assets need devkit gate, rules, workflow"]
    assert notice["advisory"]["fix"] == HARNESS_INSTALL_FIX
    deployed = {asset["kind"] for asset in json.loads((target / RECEIPT_PATH).read_text())["assets"]}
    assert deployed == {"rule", "gate", "workflow", "instruction"}
    assert (target / ".devkit/managed/team/rules/check/rule.py").is_file()
    status = get_project_status(target, [team])
    assert status.ok and [notice.code for notice in status.notices] == ["HARNESS_ENGINE_MISSING"]


def test_the_cli_keeps_its_exit_codes_except_under_strict(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch)
    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", lambda: _found([team]))
    synced = CliRunner().invoke(cli, ["sync", "-w", str(target)])
    assert synced.exit_code == 0 and "(HARNESS_ENGINE_MISSING)" in synced.stderr
    status = CliRunner().invoke(cli, ["status", "-w", str(target)])
    assert status.exit_code == 0
    assert [notice["code"] for notice in json.loads(status.stdout)["notices"]] == ["HARNESS_ENGINE_MISSING"]
    assert CliRunner().invoke(cli, ["status", "-w", str(target), "--strict"]).exit_code == 1


def test_only_the_kinds_whose_engine_is_missing_are_named(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch, "rules", "workflow")
    [notice] = _engine_notices(sync_project(target, [team]).to_dict()["notices"])
    assert notice["message"] == "deployed assets that no installed engine runs: team (gate)"


def test_with_every_engine_installed_there_is_no_notice(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch, "rules", "gate", "workflow")
    assert _engine_notices(sync_project(target, [team]).to_dict()["notices"]) == []
    assert get_project_status(target, [team]).notices == []


def test_assets_that_are_not_deployed_raise_no_notice(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch)
    update_config(target, presets={"team": ["guide"]})
    assert _engine_notices(sync_project(target, [team]).to_dict()["notices"]) == []


def _found(installed: list[InstalledBundle]):
    from contextlib import contextmanager

    @contextmanager
    def found():
        yield installed

    return found()


def test_dry_run_and_locked_syncs_report_it_too(
    monkeypatch: pytest.MonkeyPatch, team: InstalledBundle, target: Path
) -> None:
    _commands(monkeypatch)
    assert _engine_notices(sync_project(target, [team], dry_run=True).to_dict()["notices"])
    sync_project(target, [team])
    assert _engine_notices(sync_project(target, [team], locked=True).to_dict()["notices"])
