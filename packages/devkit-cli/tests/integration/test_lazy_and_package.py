"""``LazyGroup`` imports on demand; the package imports nothing beyond its dependencies; the testing helper."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import click
import pytest
from devkit_cli import LazyGroup
from devkit_cli.testing import Outcome, invoke

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def lazy_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    package = tmp_path / "lazypkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    for name in ("scan", "report"):
        (package / f"{name}.py").write_text(
            f"import click\n\n@click.command()\ndef command() -> None:\n    click.echo('[{name.upper()}: ran]')\n"
        )
    (package / "broken.py").write_text("command = 'not a command'\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    for module in [name for name in sys.modules if name.startswith("lazypkg")]:
        monkeypatch.delitem(sys.modules, module)
    return "lazypkg"


def _group() -> click.Group:
    @click.group(
        cls=LazyGroup,
        lazy_commands={
            "scan": "lazypkg.scan:command",
            "report": "lazypkg.report:command",
            "broken": "lazypkg.broken:command",
        },
    )
    def cli() -> None:
        """A lazy tool."""

    @cli.command()
    def eager() -> None:
        click.echo("[EAGER: ran]")

    return cli


def test_a_lazy_command_is_imported_only_when_it_runs(lazy_package: str) -> None:  # AC-06
    outcome = invoke(_group(), ["scan"])
    assert (outcome.exit_code, outcome.stdout) == (0, "[SCAN: ran]\n")
    assert "lazypkg.scan" in sys.modules and "lazypkg.report" not in sys.modules
    assert invoke(_group(), ["eager"]).stdout == "[EAGER: ran]\n"


def test_listing_shows_eager_and_lazy_commands(lazy_package: str) -> None:
    group = _group()
    assert group.list_commands(click.Context(group)) == ["broken", "eager", "report", "scan"]


def test_a_target_that_is_not_a_command_is_a_type_error(lazy_package: str) -> None:  # AC-06
    group = _group()
    with pytest.raises(TypeError, match=r"lazypkg\.broken:command is not a click command"):
        group.get_command(click.Context(group), "broken")
    assert group.get_command(click.Context(group), "missing") is None


def test_importing_the_toolkit_loads_only_its_dependencies() -> None:  # AC-07
    script = textwrap.dedent(
        """
        import json, sys
        before = set(sys.modules)
        import devkit_cli
        print(json.dumps(sorted(set(sys.modules) - before)))
        """
    )
    loaded = json.loads(subprocess.run([sys.executable, "-c", script], capture_output=True, check=True).stdout)
    foreign = [name for name in loaded if name.split(".")[0] not in {*sys.stdlib_module_names, "click", "devkit_cli"}]
    foreign = [name for name in foreign if name != "devkit" and not name.startswith("devkit.advisory")]
    assert foreign == []
    assert "devkit_cli.testing" not in loaded


def test_the_public_names_are_pinned() -> None:
    # The semver surface (CAP-CLI-agent-cli-toolkit): removing or renaming a name is breaking (a minor bump within 0.x).
    import devkit_cli
    from devkit_cli import Boundary, LazyGroup, OutputSettings
    from devkit_cli import testing as cli_testing

    assert set(devkit_cli.__all__) == {
        "FORMAT_OPTION",
        "Boundary",
        "LazyGroup",
        "OutputSettings",
        "Reported",
        "echo_json",
        "echo_notices",
        "exit_on_problems",
        "exit_on_warnings",
        "highest_exit_code",
        "is_json",
        "output_settings",
        "report_exit_code",
    }
    assert all(hasattr(devkit_cli, name) for name in devkit_cli.__all__)
    boundary = Boundary("pinned")
    assert all(
        hasattr(boundary, name)
        for name in ("name", "quiet_env", "verbose_env", "strict_env", "output_options", "resolve_output")
    )
    assert hasattr(LazyGroup, "resolve_lazy")
    assert {"quiet", "verbose", "strict", "json"} == set(OutputSettings.__dataclass_fields__)
    assert {"invoke", "Outcome"} <= set(dir(cli_testing))


def test_the_distribution_depends_on_click_and_the_advisory_library_only() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert [requirement.split("=")[0].split(">")[0] for requirement in project["dependencies"]] == [
        "click",
        "devkit-advisory",
    ]
    assert f"devkit-advisory=={project['version']}" in project["dependencies"]
    assert "entry-points" not in project and "scripts" not in project


def test_outcome_reads_json_and_codes() -> None:  # AC-08
    stderr = "[WARN]   (DRIFTED) upstream changed\n[ACTION] CONTINUE\n[ERROR]  (THING_MISSING) gone\n"
    outcome = Outcome(exit_code=1, stdout='{"error": {"code": "THING_MISSING"}}\n', stderr=stderr)
    assert outcome.json() == {"error": {"code": "THING_MISSING"}}
    assert outcome.codes() == ["DRIFTED", "THING_MISSING"]
    with pytest.raises(AssertionError):
        Outcome(exit_code=0, stdout="[OK: done]\n", stderr="").json()
    with pytest.raises(AssertionError):
        Outcome(exit_code=0, stdout="[1, 2]", stderr="").json()


def test_invoke_keeps_an_escaped_exception() -> None:
    @click.command()
    def unguarded() -> None:
        raise RuntimeError("boom")

    outcome = invoke(unguarded)
    assert outcome.exit_code == 1 and isinstance(outcome.exception, RuntimeError)
