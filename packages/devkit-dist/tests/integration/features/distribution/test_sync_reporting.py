"""What sync, remove and status report to a consumer: configuration writes, fresh-clone notices, MCP registration
left for a later step, overrides a removed bundle leaves behind, and the agent-facing command form."""

from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.workspace import SEEN_BUNDLES
from devkit_dist.features.distribution.usecases import commands as operations
from devkit_dist.features.distribution.usecases.commands import AddSelection, RemoveSelection, SyncSelection
from devkit_dist.features.distribution.usecases.override_commands import create_override
from devkit_dist.features.distribution.usecases.status import get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.host.usecases import registrations
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, OVERRIDES_PATH
from distsupport.distribution import cli, instruction, write_bundle

MANIFEST = """schema = 1
name = "{name}"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
"""


def _bundle(tmp_path: Path, name: str) -> InstalledBundle:
    return write_bundle(
        tmp_path / f"{name}-source", MANIFEST.format(name=name), {"guide.md": instruction("guide")}, package=name
    )


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    return [_bundle(tmp_path, "team"), _bundle(tmp_path, "extra")]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    return root


@pytest.fixture
def discovered(monkeypatch: pytest.MonkeyPatch, installed: list[InstalledBundle]) -> list[InstalledBundle]:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr(operations, "discover_bundles", found)
    return installed


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


# --- the configuration a selection command writes -------------------------------------------------------------------


def test_a_first_selection_lists_the_configuration_it_creates(discovered: list[InstalledBundle], project: Path) -> None:
    preview = AddSelection().execute(project, {"team": [""]}, dry_run=True)
    assert (CONFIG_PATH, "create") in [(item.path, item.action) for item in preview.actions]
    assert not (project / CONFIG_PATH).exists()
    added = AddSelection().execute(project, {"team": [""]})
    assert (CONFIG_PATH, "create") in [(item.path, item.action) for item in added.actions]
    assert (project / CONFIG_PATH).exists()
    again = SyncSelection().execute(project, agents=["codex"])
    assert (CONFIG_PATH, "update") in [(item.path, item.action) for item in again.actions]
    assert CONFIG_PATH not in [item.path for item in SyncSelection().execute(project, agents=["codex"]).actions]


def test_sync_text_names_the_configuration_it_creates(discovered: list[InstalledBundle], project: Path) -> None:
    result = CliRunner().invoke(cli, ["sync", "--agent", "codex", "--dry-run", "-w", str(project)])
    assert result.exit_code == 0, result.output
    assert f"[CHANGE: create {CONFIG_PATH}]" in result.stdout


# --- notices of a fresh clone ---------------------------------------------------------------------------------------


def test_locked_sync_never_announces_unselected_bundles(installed: list[InstalledBundle], project: Path) -> None:
    update_config(project, presets={"team": ["all"]})
    first = sync_project(project, installed)
    assert [notice.code for notice in first.notices] == ["BUNDLE_UNSELECTED"]
    (project / SEEN_BUNDLES).unlink()  # a fresh clone has no record of what it was told
    locked = sync_project(project, installed, locked=True)
    assert [notice.code for notice in locked.notices] == []
    assert [item.bundle for item in locked.unselected] == ["extra"]


def test_command_suggestions_use_the_agent_facing_invocation(installed: list[InstalledBundle], project: Path) -> None:
    update_config(project, presets={"team": ["all"]})
    (notice,) = sync_project(project, installed).notices
    assert notice.fix == "uv run devkit add extra"
    assert notice.details[0].startswith("uv run devkit add extra  (package extra;")


# --- remove ---------------------------------------------------------------------------------------------------------


def test_remove_names_the_overrides_it_leaves(discovered: list[InstalledBundle], project: Path) -> None:
    AddSelection().execute(project, {"team": [""], "extra": [""]})
    create_override(project, discovered, "team:guide")
    removed = RemoveSelection().execute(project, ("team",))
    (notice,) = [notice for notice in removed.notices if notice.code == "OVERRIDE_RETAINED"]
    assert notice.target_files == (f"{OVERRIDES_PATH}/team/",)
    assert notice.level.name == "NOTICE" and notice.exit_code == 0
    assert (project / OVERRIDES_PATH / "team/guide.md").exists()
    plain = RemoveSelection().execute(project, ("extra",))
    assert "OVERRIDE_RETAINED" not in [notice.code for notice in plain.notices]


# --- MCP registration a locked sync leaves to a later step ------------------------------------------------------------


@pytest.fixture
def clone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "clone"
    root.mkdir()
    _git(root, "init", "-b", "main")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    monkeypatch.setattr(registrations, "collisions", lambda *args: [])
    launch = registrations.LaunchDescriptor(
        "/retained/python", ("-m", "devkit_dist", "mcp", "serve"), str(root), str(root), "local"
    )
    entry = SimpleNamespace(load=lambda: lambda *a, **k: launch)
    others = registrations.metadata.entry_points
    monkeypatch.setattr(
        registrations.metadata,
        "entry_points",
        lambda group: [entry] if group == registrations.GROUP else others(group=group),
    )
    return root


def test_locked_sync_and_status_report_a_registration_left_for_later(
    installed: list[InstalledBundle], clone: Path
) -> None:
    update_config(clone, presets={"team": ["all"]}, agents=["claude-code"])
    sync_project(clone, installed[:1])
    ledger = json.loads((clone / registrations.LEDGER).read_text())
    assert sorted(ledger["entries"]) == ["claude"]
    # A teammate's clone: committed files are present, the clone-local registration is not.
    (clone / ".mcp.json").unlink()
    (clone / registrations.LEDGER).unlink()
    locked = sync_project(clone, installed[:1], locked=True)
    (notice,) = [notice for notice in locked.notices if notice.code == "MCP_REGISTRATION_PENDING"]
    assert notice.fix == "uv run devkit sync --registrations-only" and notice.level.name == "NOTICE"
    assert not (clone / ".mcp.json").exists()
    status = get_project_status(clone, installed[:1])
    assert status.errors == []
    assert [notice.code for notice in status.notices] == ["MCP_REGISTRATION_PENDING"]
    sync_project(clone, installed[:1])
    assert "MCP_REGISTRATION_PENDING" not in [
        notice.code for notice in get_project_status(clone, installed[:1]).notices
    ]


def test_sync_names_each_registration_change_with_its_kind(installed: list[InstalledBundle], clone: Path) -> None:
    update_config(clone, presets={"team": ["all"]}, agents=["claude-code"])
    actions = [(item.path, item.action) for item in sync_project(clone, installed[:1]).actions]
    assert (".mcp.json", "create") in actions and (".git/info/exclude", "update") in actions


def test_registrations_only_json_names_each_change_with_its_kind(installed: list[InstalledBundle], clone: Path) -> None:
    update_config(clone, presets={"team": ["all"]}, agents=["claude-code"])
    sync_project(clone, installed[:1])
    (clone / ".mcp.json").unlink()
    (clone / registrations.LEDGER).unlink()
    result = CliRunner().invoke(cli, ["sync", "--registrations-only", "--format", "json", "-w", str(clone)])
    assert result.exit_code == 0, result.output
    actions = json.loads(result.stdout)["actions"]
    assert {"path": ".mcp.json", "action": "create"} in actions
    assert all(set(item) == {"path", "action"} for item in actions)
