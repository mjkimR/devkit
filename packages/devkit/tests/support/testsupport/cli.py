"""The commands devkit-agt mounts, in one click group named ``devkit``, without reading entry points.

Under the real ``devkit`` executable these commands are ``devkit.commands`` plugins, looked up through
``importlib.metadata`` (``test_mounted_commands``). Tests that replace ``importlib.metadata.entry_points`` for an
extension group of their own invoke this group instead, so their stand-in never hides the command under test.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

import click

_PYPROJECT = Path(__file__).resolve().parents[3] / "pyproject.toml"
MOUNTED: dict[str, str] = tomllib.loads(_PYPROJECT.read_text("utf-8"))["project"]["entry-points"]["devkit.commands"]


@click.group(name="devkit")
def cli() -> None:
    """The devkit-agt commands, as the root ``devkit`` group serves them."""


for _name, _target in sorted(MOUNTED.items()):
    _module, _, _attribute = _target.partition(":")
    cli.add_command(getattr(importlib.import_module(_module), _attribute), _name)
