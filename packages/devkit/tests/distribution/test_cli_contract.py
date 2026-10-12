"""CLI contract: exit codes, the workspace root option, and configuration edits checked before syncing."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit.distribution.cli import cli
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.transaction import project_lock
from devkit.distribution.installation.workspace import CONFIG, RECEIPT
from testsupport.distribution import instruction, write_bundle

MANIFEST = """schema = 1
name = "team"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
"""


@pytest.fixture
def item(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> InstalledBundle:
    installed = write_bundle(tmp_path / "source", MANIFEST, {"guide.md": instruction("guide")})

    @contextmanager
    def found():
        yield [installed]

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    return installed


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    (root / ".devkit").mkdir(parents=True)
    return root


def _invoke(*args: str):
    return CliRunner().invoke(cli, list(args))


def test_add_checks_the_configuration_before_syncing(item: InstalledBundle, target: Path, tmp_path: Path) -> None:
    shared = tmp_path / "shared.toml"
    shared.write_text("schema = 1\n")
    (target / CONFIG).symlink_to(shared)
    result = _invoke("add", "team", "-w", str(target))
    assert result.exit_code == 2
    assert "config must be a regular file" in result.output
    assert not (target / RECEIPT).exists() and not (target / ".devkit/managed").exists()
    assert shared.read_text() == "schema = 1\n"


def test_sync_check_exit_codes(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    needed = _invoke("sync", "--check", "-w", str(target))
    assert needed.exit_code == int(ExitCode.FINDINGS)  # synchronization needed: a result, not an error
    assert json.loads(needed.stdout)["actions"] and not needed.stderr.startswith("[ERROR]")
    assert _invoke("sync", "-w", str(target)).exit_code == 0
    assert _invoke("sync", "--check", "-w", str(target)).exit_code == 0
    (target / ".devkit/managed/team/guide.md").write_text("edited")
    failed = _invoke("sync", "--check", "-w", str(target))
    assert failed.exit_code == 2 and "user-modified" in failed.output


def test_errors_exit_2_on_every_command(item: InstalledBundle, target: Path) -> None:
    assert _invoke("get-context", "team", "-w", str(target)).exit_code == 2
    assert _invoke("override", "accept", "team:guide", "-w", str(target)).exit_code == 2
    assert _invoke("remove", "team", "-w", str(target)).exit_code == 2


def test_an_error_is_one_json_document_on_stdout_and_an_advisory_on_stderr(item: InstalledBundle, target: Path) -> None:
    result = _invoke("get-context", "team", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["exit_code"], error["advisory"]["mode"]) == ("NOT_SYNCHRONIZED", 2, "AUTO")
    assert error["advisory"]["fix"] == "devkit sync"
    assert result.stderr.startswith("[ERROR]  (NOT_SYNCHRONIZED) no synchronized project found")
    assert "[ACTION] AUTO" in result.stderr


@pytest.mark.parametrize(
    ("args", "code", "mode"),
    [
        (("override", "create", "team", "-w", "{target}"), "ARGUMENT_INVALID", "INPUT_ERROR"),
        (("add", "missing", "-w", "{target}"), "SELECTION_INVALID", "INPUT_ERROR"),
        (("remove", "team", "-w", "{target}"), "SELECTION_INVALID", "INPUT_ERROR"),
    ],
)
def test_error_codes_reach_the_cli(
    item: InstalledBundle, target: Path, args: tuple[str, ...], code: str, mode: str
) -> None:
    result = _invoke(*(arg.format(target=target) for arg in args))
    assert result.exit_code == int(ExitCode.ERROR), result.output
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == (code, mode)


def test_usage_errors_exit_2(item: InstalledBundle, target: Path) -> None:
    assert _invoke("sync", "--agent", "codex", "--no-agents", "-w", str(target)).exit_code == 2
    assert _invoke("add", "Bad Slug!", "-w", str(target)).exit_code == 2
    assert _invoke("sync", "--no-such-flag").exit_code == 2


def test_a_held_lock_defers_and_exits_2(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    with project_lock(target):
        result = _invoke("sync", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == ("LOCK_HELD", "DEFER")
    assert "[WHEN]   Not before: the running devkit command finishes" in result.stderr


def test_unexpected_errors_are_maintenance_and_exit_2(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("devkit.distribution.cli.project_status", explode)
    result = _invoke("status", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    assert json.loads(result.stdout)["error"]["code"] == "UNEXPECTED_ERROR"
    assert "[ACTION] MAINTENANCE" in result.stderr


def test_workspace_root_defaults_to_the_project_root(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    nested = target / "src/module"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert _invoke("sync").exit_code == 0
    assert (target / RECEIPT).is_file() and not (nested / ".devkit").exists()
    context = _invoke("get-context", "team")
    assert context.exit_code == 0, context.output
    assert json.loads(context.output)["instructions"][0]["path"] == str(
        (target / ".devkit/managed/team/guide.md").resolve()
    )


def test_dry_run_validates_but_never_saves(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    before = (target / CONFIG).read_text()
    result = _invoke("remove", "team", "--dry-run", "-w", str(target))
    assert result.exit_code == 0, result.output
    assert (target / CONFIG).read_text() == before
    assert _invoke("remove", "missing", "--dry-run", "-w", str(target)).exit_code == 2


def test_selection_edits_preserve_inline_tables_and_comments(target: Path) -> None:
    (target / CONFIG).write_text(
        'schema = 1\n# selected bundles\npresets = { team = "all", other = "core" }  # inline\n'
    )
    update_config(target, presets={"extra": ["a", "b"]}, deselect=["other"])
    text = (target / CONFIG).read_text()
    assert "# selected bundles" in text and "# inline" in text
    assert 'team = "all"' in text and "other" not in text and 'extra = ["a", "b"]' in text
    update_config(target, deselect=["team", "extra"])
    assert "team" not in (target / CONFIG).read_text()
