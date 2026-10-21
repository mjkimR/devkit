"""Lazy command loading of ``devkit_dist.cli``: a built-in command imports only its own area and the layers below it,
never an area of another wheel.

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
from devkit_dist.cli import COMMANDS, cli
from devkit_dist.features.distribution.cli import COMMANDS as DISTRIBUTION_COMMANDS
from distsupport.layering import DATA_AREAS, LAZY_IMPORT_AREAS, TOP_LEVEL, area_of

_PROBE = """
import contextlib, io, json, sys
sys.path.insert(0, '/Users/mj/workspace/workbench/repos/devkit/packages/devkit-dist/tests')
from distsupport.layering import area_of
from devkit_dist.cli import cli
with contextlib.redirect_stdout(io.StringIO()):
    try:
        cli.main(sys.argv[1:], prog_name="devkit", standalone_mode=False)
    except SystemExit:
        pass
print(json.dumps(sorted({area_of(name) for name in sys.modules if area_of(name) is not None})))
"""


def _loaded_areas(*args: str) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE, *args], capture_output=True, text=True, check=True, encoding="utf-8"
    )
    # The command line itself and devkit-advisory, below every area, are not areas of a wheel.
    return set(json.loads(result.stdout.splitlines()[-1])) - {*TOP_LEVEL, "advisory"}


def _area(name: str) -> str:
    area = area_of(COMMANDS[name].split(":", 1)[0])
    assert area is not None
    return area


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
    assert area in loaded and loaded <= {area, *LAZY_IMPORT_AREAS[area]}


def test_bundle_discovery_loads_only_data_areas(tmp_path: Path) -> None:
    # Locating each built-in bundle imports its resource module: a data area (``*_guide``, of either wheel), never an
    # engine.
    loaded = _loaded_areas("list", "--workspace-root", str(tmp_path))
    engines = {area for area in loaded if not area.startswith("bundles.")}
    assert loaded >= DATA_AREAS and engines <= {"distribution", *LAZY_IMPORT_AREAS["distribution"]}
