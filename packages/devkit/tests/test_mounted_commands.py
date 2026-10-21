"""The commands devkit-agt mounts under the ``devkit`` executable of devkit-dist through ``devkit.commands``.

Each lazy-import case runs in a fresh interpreter, because the test session itself has already imported every area.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from importlib.metadata import distribution, entry_points
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from devkit_dist import cli as root
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.usecases.status import get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import harness_assets_bundle
from testsupport.layering import LAZY_IMPORT_AREAS, PYPROJECT

_PROBE = """
import contextlib, io, json, sys
from devkit_dist.cli import cli
with contextlib.redirect_stdout(io.StringIO()):
    try:
        cli.main(sys.argv[1:], prog_name="devkit", standalone_mode=False)
    except SystemExit:
        pass
print(json.dumps(sorted({name.split(".")[2] for name in sys.modules if name.startswith("devkit_agt.features.")})))
"""

MOUNTED: dict[str, str] = tomllib.loads(PYPROJECT.read_text("utf-8"))["project"]["entry-points"]["devkit.commands"]


def _loaded_areas(*args: str) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE, *args], capture_output=True, text=True, check=True, encoding="utf-8"
    )
    return set(json.loads(result.stdout.splitlines()[-1])) - {"cli", "__main__", "advisory"}


def test_every_harness_command_keeps_its_name_and_target() -> None:
    assert MOUNTED == {
        "gate": "devkit_agt.features.gate.cli:cli",
        "generated": "devkit_agt.features.generated.cli:cli",
        "integration": "devkit_agt.features.integration.cli:cli",
        "rules": "devkit_agt.features.rules.cli:cli",
        "run": "devkit_agt.features.compact.cli:run_cmd",
        "workflow": "devkit_agt.features.workflow.cli:cli",
        "worktree": "devkit_agt.features.worktree.cli:cli",
    }
    declared = {
        entry.name
        for entry in entry_points(group="devkit.commands")
        if entry.dist is not None and entry.dist.name == "devkit-agt"
    }
    assert declared == set(MOUNTED)


@pytest.mark.parametrize("name", sorted(MOUNTED))
def test_a_mounted_command_resolves_to_its_click_command(name: str) -> None:
    command = root.cli.get_command(click.Context(root.cli), name)
    module, _, attribute = MOUNTED[name].partition(":")
    assert command is getattr(__import__(module, fromlist=[attribute]), attribute)
    assert name in root.cli.list_commands(click.Context(root.cli))


@pytest.mark.parametrize("name", sorted(MOUNTED))
def test_a_mounted_command_imports_only_its_area_and_lower_layers(name: str) -> None:
    area = MOUNTED[name].split(".")[2]
    loaded = _loaded_areas(name, "--help")
    assert area in loaded and loaded <= {area, *LAZY_IMPORT_AREAS[area]}


def test_devkit_agt_ships_no_console_script() -> None:
    assert [entry for entry in distribution("devkit-agt").entry_points if entry.group == "console_scripts"] == []
    owners = [
        entry.dist.name for entry in entry_points(group="console_scripts", name="devkit") if entry.dist is not None
    ]
    assert owners == ["devkit-dist"]


def test_with_devkit_agt_deployed_harness_assets_raise_no_engine_notice(tmp_path: Path) -> None:
    team = harness_assets_bundle(tmp_path)
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=[])
    result = sync_project(target, [team]).to_dict()
    assert [notice for notice in result["notices"] if notice["code"] == "HARNESS_ENGINE_MISSING"] == []
    assert get_project_status(target, [team]).notices == []


def test_version_lives_only_on_the_root_group() -> None:
    runner = CliRunner()
    for group in ("rules", "workflow", "gate"):
        result = runner.invoke(root.cli, [group, "--version"])
        assert result.exit_code == 2 and "No such option" in result.output


@pytest.mark.parametrize("name", sorted(MOUNTED))
def test_each_mounted_command_shows_its_help_through_the_root_group(name: str) -> None:
    result = CliRunner().invoke(root.cli, [name, "--help"])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith(f"Usage: devkit {name}")
