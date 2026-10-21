"""devkit-dist alone: the real ``devkit`` executable of an installation without devkit-agt.

These cases run only in the dist-only environment (``just test-dist``, CI); in the workspace, where devkit-agt is
installed, the harness commands are mounted and the cases are skipped. The in-process tests of the name-only list
and the engine notice (``test_cli_plugins``, ``distribution/test_engines``) run in both.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from importlib.metadata import entry_points, version
from pathlib import Path

import pytest
from devkit_dist.cli import COMMANDS, HARNESS_COMMANDS

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("devkit_agt") is not None,
    reason="devkit-agt is installed: not a standalone environment",
)


def _devkit(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args], capture_output=True, text=True, encoding="utf-8", cwd=cwd, env=env
    )


def test_version_and_help_list_only_the_distribution_commands() -> None:
    assert _devkit("--version").stdout == f"[VERSION: devkit {version('devkit-dist')}]\n"
    listing = _devkit("--help")
    assert listing.returncode == 0
    listed = {line.split()[0] for line in listing.stdout.split("Commands:")[1].splitlines() if line.strip()}
    assert listed == set(COMMANDS) - {"recover"} and not listed & set(HARNESS_COMMANDS)
    assert [entry.name for entry in entry_points(group="devkit.commands")] == []


@pytest.mark.parametrize("name", HARNESS_COMMANDS)
def test_each_harness_name_is_a_coded_error(name: str) -> None:
    result = _devkit(name, "--help")
    assert (result.returncode, result.stdout) == (2, "")
    assert "(HARNESS_COMMAND_UNAVAILABLE)" in result.stderr
    assert "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit" in result.stderr
    as_json = _devkit(name, "--format", "json")
    assert as_json.returncode == 2 and as_json.stderr == ""
    assert json.loads(as_json.stdout)["error"]["code"] == "HARNESS_COMMAND_UNAVAILABLE"


def test_an_unknown_name_keeps_the_usage_error() -> None:
    result = _devkit("no-such-command")
    assert result.returncode == 2 and "No such command" in result.stderr
    assert "HARNESS_COMMAND_UNAVAILABLE" not in result.stderr


def test_sync_deploys_only_distribution_guidance(tmp_path: Path) -> None:
    assert _devkit("sync", "-w", str(tmp_path)).returncode == 0
    receipt = json.loads((tmp_path / ".devkit/installation.json").read_text())
    assert receipt["tool"]["package"] == "devkit-dist"
    assert {record["bundle"]: record["package"] for record in receipt["packages"]} == {
        "advisory": "devkit-dist",
        "devkit": "devkit-dist",
    }
    context = json.loads(_devkit("get-context", "devkit", "-w", str(tmp_path)).stdout)
    texts = [context["constitution"], *(Path(entry["path"]).read_text() for entry in context["instructions"])]
    for command in ("devkit rules", "devkit gate", "devkit workflow", "devkit run"):
        assert not any(command in text for text in texts), command


def test_a_rule_asset_of_a_built_in_preset_raises_the_engine_notice(tmp_path: Path) -> None:
    # The advisory bundle's opt-in python preset ships a rule: deployed, reported, exit code unchanged.
    result = _devkit("add", "advisory:python", "-w", str(tmp_path), "--format", "json")
    assert result.returncode == 0, result.stderr
    codes = [notice["code"] for notice in json.loads(result.stdout)["notices"]]
    assert "HARNESS_ENGINE_MISSING" in codes
    status = json.loads(_devkit("status", "-w", str(tmp_path)).stdout)
    assert [notice["code"] for notice in status["notices"]] == ["HARNESS_ENGINE_MISSING"]
    assert (tmp_path / ".devkit/managed/advisory/rules/unique_code/rule.py").is_file()
