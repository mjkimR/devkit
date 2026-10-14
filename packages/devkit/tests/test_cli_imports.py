"""Lazy command loading of ``devkit.cli``: a command imports only its own area and the layers below it.

Each case runs in a fresh interpreter, because the test session itself has
already imported every area.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import click
import pytest
from devkit.cli import COMMANDS, cli
from devkit.distribution.cli import COMMANDS as DISTRIBUTION_COMMANDS
from test_layering import ALLOWED, DATA_AREAS

_PROBE = """
import contextlib, io, json, sys
from devkit.cli import cli
with contextlib.redirect_stdout(io.StringIO()):
    try:
        cli.main(sys.argv[1:], prog_name="devkit", standalone_mode=False)
    except SystemExit:
        pass
print(json.dumps(sorted({name.split(".")[1] for name in sys.modules if name.startswith("devkit.")})))
"""


def _loaded_areas(*args: str) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE, *args], capture_output=True, text=True, check=True, encoding="utf-8"
    )
    return set(json.loads(result.stdout.splitlines()[-1])) & set(ALLOWED)


def _area(name: str) -> str:
    return COMMANDS[name].split(".")[1]


def test_every_distribution_command_is_mapped() -> None:
    mapped = {name for name, target in COMMANDS.items() if _area(name) == "distribution"}
    assert mapped == {command.name for command in DISTRIBUTION_COMMANDS}


@pytest.mark.parametrize("name", sorted(COMMANDS))
def test_every_mapped_command_resolves(name: str) -> None:
    assert isinstance(cli.get_command(click.Context(cli), name), click.Command)


def test_unknown_commands_resolve_to_nothing() -> None:
    assert cli.get_command(click.Context(cli), "no-such-command") is None


def test_version_imports_no_area() -> None:
    assert _loaded_areas("--version") == set()


@pytest.mark.parametrize("name", sorted(COMMANDS))
def test_a_command_imports_only_its_area_and_lower_layers(name: str) -> None:
    area = _area(name)
    loaded = _loaded_areas(name, "--help")
    assert area in loaded and loaded <= {area, *ALLOWED[area]}


def test_bundle_discovery_loads_only_data_areas(tmp_path: Path) -> None:
    # Locating each built-in bundle imports its resource module: a data area, never the gate or rules engine.
    loaded = _loaded_areas("list", "--workspace-root", str(tmp_path))
    assert DATA_AREAS <= loaded <= {"distribution", *ALLOWED["distribution"], *DATA_AREAS}
