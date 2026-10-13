"""Command plugins of ``devkit.cli``: commands that installed packages mount through ``devkit.commands``.

Each case installs fake distributions (a ``.dist-info`` directory with ``entry_points.txt``, beside the module it
names) into a temporary directory and runs ``devkit`` in a fresh interpreter with that directory on ``PYTHONPATH``,
because the entry points are read once per process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import click
import pytest
from devkit import cli as root

HELLO = """
import click

@click.command()
@click.option("--name", default="world")
def cli(name):
    click.echo(f"[HELLO: {name}]")

not_a_command = 42
"""


def _dist(site: Path, package: str, commands: dict[str, str]) -> None:
    info = site / f"{package.replace('-', '_')}-0.1.0.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(f"Metadata-Version: 2.1\nName: {package}\nVersion: 0.1.0\n", encoding="utf-8")
    lines = [f"{name} = {target}" for name, target in commands.items()]
    (info / "entry_points.txt").write_text("[devkit.commands]\n" + "\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture
def site(tmp_path: Path) -> Path:
    (tmp_path / "hello_plugin.py").write_text(HELLO, encoding="utf-8")
    (tmp_path / "broken_plugin.py").write_text("raise ImportError('boom')\n", encoding="utf-8")
    return tmp_path


def _devkit(site: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(site), os.environ.get("PYTHONPATH", "")])}
    return subprocess.run(
        [sys.executable, "-m", "devkit", *args], capture_output=True, text=True, encoding="utf-8", env=env, check=False
    )


def test_a_plugin_mounts_as_a_top_level_command(site: Path) -> None:
    _dist(site, "hello-pkg", {"hello": "hello_plugin:cli"})
    result = _devkit(site, "hello", "--name", "spec")
    assert (result.returncode, result.stdout) == (0, "[HELLO: spec]\n")
    assert "hello" in _devkit(site, "--help").stdout


def test_built_in_names_are_reserved(site: Path) -> None:
    _dist(site, "hello-pkg", {"sync": "hello_plugin:cli"})
    result = _devkit(site, "sync", "--help")
    assert result.returncode == 0 and "Synchronize" in result.stdout and "HELLO" not in result.stdout


@pytest.mark.parametrize(
    ("commands", "message"),
    [
        ({"hello": "broken_plugin:cli"}, "cannot be loaded: ImportError: boom"),
        ({"hello": "hello_plugin:not_a_command"}, "is not a click command"),
        ({"hello": "hello_plugin:missing"}, "cannot be loaded: AttributeError"),
    ],
)
def test_an_unusable_plugin_fails_only_its_own_command(site: Path, commands: dict[str, str], message: str) -> None:
    _dist(site, "hello-pkg", commands)
    result = _devkit(site, "hello", "--name", "x")
    assert result.returncode == 2 and result.stdout == ""
    assert "(COMMAND_PLUGIN_INVALID)" in result.stderr and message in result.stderr
    assert "[ACTION] MAINTENANCE" in result.stderr
    assert _devkit(site, "--version").returncode == 0
    listing = _devkit(site, "--help")
    assert listing.returncode == 0 and "Unusable plugin command (COMMAND_PLUGIN_INVALID)" in listing.stdout


def test_an_unusable_plugin_reports_json_when_asked(site: Path) -> None:
    _dist(site, "hello-pkg", {"hello": "broken_plugin:cli"})
    result = _devkit(site, "hello", "--format", "json")
    assert result.returncode == 2 and result.stderr == ""
    assert json.loads(result.stdout)["error"]["code"] == "COMMAND_PLUGIN_INVALID"


def test_two_packages_declaring_one_name_conflict(site: Path) -> None:
    _dist(site, "first-pkg", {"hello": "hello_plugin:cli"})
    _dist(site, "second-pkg", {"hello": "hello_plugin:other"})
    result = _devkit(site, "hello")
    assert result.returncode == 2 and "declared by more than one package" in result.stderr
    assert "hello_plugin:cli (package first-pkg)" in result.stderr
    assert "hello_plugin:other (package second-pkg)" in result.stderr


def test_the_same_target_declared_twice_counts_once(site: Path) -> None:
    _dist(site, "first-pkg", {"hello": "hello_plugin:cli"})
    _dist(site, "second-pkg", {"hello": "hello_plugin:cli"})
    assert _devkit(site, "hello").stdout == "[HELLO: world]\n"


def test_built_in_commands_never_read_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail() -> dict[str, object]:
        raise AssertionError("entry points read for a built-in command")

    monkeypatch.setattr(root, "plugin_entry_points", fail)
    for name in root.COMMANDS:
        assert isinstance(root.cli.get_command(click.Context(root.cli), name), click.Command)
