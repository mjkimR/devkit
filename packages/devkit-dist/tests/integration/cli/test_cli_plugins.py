"""Command plugins of ``devkit_dist.cli``: commands that installed packages mount through ``devkit.commands``.

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
from types import SimpleNamespace

import click
import pytest
from click.testing import CliRunner
from devkit_dist import cli as root
from devkit_dist.base.errors import HARNESS_INSTALL_FIX, MCP_INSTALL_FIX

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
        [sys.executable, "-m", "devkit_dist", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
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


# The name-only harness list: consulted only when neither the built-in map nor an entry point has the name. The
# entry points are replaced in process, so these cases hold with and without devkit-agt installed.


def _entry(value: str, package: str = "third-party") -> SimpleNamespace:
    return SimpleNamespace(name=value.split(":")[0], value=value, dist=SimpleNamespace(name=package), load=None)


@pytest.fixture
def no_plugins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(root, "plugin_entry_points", lambda: {})


@pytest.mark.parametrize("name", root.HARNESS_COMMANDS)
@pytest.mark.usefixtures("no_plugins")
def test_a_harness_name_without_its_command_is_a_coded_error(name: str) -> None:
    result = CliRunner().invoke(root.cli, [name, "check", "--staged"])
    assert result.exit_code == 2 and result.stdout == ""
    assert result.stderr.startswith("[ERROR]")
    assert f"(HARNESS_COMMAND_UNAVAILABLE) command {name}: not installed" in result.stderr
    assert f"[FIX]    {HARNESS_INSTALL_FIX}" in result.stderr
    helped = CliRunner().invoke(root.cli, [name, "--help"])
    assert helped.exit_code == 2 and "HARNESS_COMMAND_UNAVAILABLE" in helped.stderr


@pytest.mark.usefixtures("no_plugins")
def test_a_harness_name_reports_json_when_asked() -> None:
    result = CliRunner().invoke(root.cli, ["run", "--format", "json", "--", "pytest"])
    assert result.exit_code == 2 and result.stderr == ""
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "HARNESS_COMMAND_UNAVAILABLE" and error["advisory"]["fix"] == HARNESS_INSTALL_FIX


@pytest.mark.usefixtures("no_plugins")
def test_an_extra_command_without_its_extra_names_the_extra() -> None:
    result = CliRunner().invoke(root.cli, ["mcp", "status"])
    assert result.exit_code == 2 and result.stdout == ""
    assert "(EXTRA_COMMAND_UNAVAILABLE) command mcp: not installed" in result.stderr
    assert f"[FIX]    {MCP_INSTALL_FIX}" in result.stderr
    # devkit-dist declares no mcp extra: a distribution-only project adds devkit-mcp itself
    assert "devkit-dist[mcp]" not in MCP_INSTALL_FIX and "subdirectory=packages/devkit-mcp" in MCP_INSTALL_FIX


@pytest.mark.usefixtures("no_plugins")
def test_the_harness_names_are_never_listed_and_other_names_stay_usage_errors() -> None:
    listing = CliRunner().invoke(root.cli, ["--help"])
    assert listing.exit_code == 0
    listed = {line.split()[0] for line in listing.stdout.split("Commands:")[1].splitlines() if line.strip()}
    assert listed == set(root.COMMANDS) - {"recover"}
    unknown = CliRunner().invoke(root.cli, ["no-such-command"])
    assert unknown.exit_code == 2 and "No such command" in unknown.stderr
    assert "HARNESS_COMMAND_UNAVAILABLE" not in unknown.stderr


def test_the_install_directive_names_full_git_requirements() -> None:
    assert "'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'" in HARNESS_INSTALL_FIX
    assert (
        "uv tool install --reinstall 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist'"
        " --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'"
    ) in HARNESS_INSTALL_FIX


def test_an_installed_command_of_a_harness_name_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    entry = _entry("rules:hello")
    entry.load = lambda: click.Command("rules", callback=lambda: click.echo("[HELLO: rules]"))
    monkeypatch.setattr(root, "plugin_entry_points", lambda: {"rules": (entry,)})
    assert CliRunner().invoke(root.cli, ["rules"]).stdout == "[HELLO: rules]\n"


def test_a_harness_name_declared_twice_is_an_unusable_plugin(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = (_entry("devkit_agt.features.rules.cli:cli", "devkit-agt"), _entry("other_rules:cli", "other-pkg"))
    monkeypatch.setattr(root, "plugin_entry_points", lambda: {"rules": entries})
    result = CliRunner().invoke(root.cli, ["rules", "check"])
    assert result.exit_code == 2 and "(COMMAND_PLUGIN_INVALID)" in result.stderr
    assert "devkit_agt.features.rules.cli:cli (package devkit-agt)" in result.stderr
    assert "other_rules:cli (package other-pkg)" in result.stderr
