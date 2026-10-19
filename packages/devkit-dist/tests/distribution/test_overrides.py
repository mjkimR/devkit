from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.core.errors import ArgumentError
from devkit.core.receipt import OVERRIDES_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.errors import SelectionError
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.sync import sync_project
from distsupport.distribution import cli


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    root = tmp_path / "source"
    (root / "skills/review/scripts").mkdir(parents=True)
    (root / "skills/review/SKILL.md").write_text("# Review Skill\n")
    (root / "reviewer.toml").write_text('system_prompt = "upstream prompt"\n')
    (root / "guide.md").write_text("---\nname: guide\ndescription: upstream guide description\n---\n# Upstream Guide\n")
    (root / "playbooks").mkdir(parents=True)
    (root / "playbooks/recovery.md").write_text(
        "---\nname: disaster-recovery\ndescription: upstream recovery steps\naliases: [recovery]\n---\n1. Step One\n"
    )
    (root / "bundle.toml").write_text("""schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "reviewer.toml"
[[assets]]
id = "disaster-recovery"
kind = "playbook"
source = "playbooks/recovery.md"
""")
    return [InstalledBundle("team-content", "0.1.0", load_bundle(root))]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]})
    return root


def test_override_create_and_sync_instruction(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    # Initially get-context shows upstream header
    ctx = get_context(target, "team").to_dict()
    assert "upstream guide description" in ctx["instructions"][0]["header"]

    # Create override for guide
    result = create_override(target, installed, "team:guide").to_dict()
    assert result["bundle"] == "team"
    assert result["asset"] == "guide"
    override_file = target / OVERRIDES_PATH / "team/guide.md"
    assert override_file.is_file()

    # Edit override
    override_file.write_text("---\nname: guide\ndescription: customized guide description\n---\n# Custom Guide\n")
    sync_result = sync_project(target, installed)
    assert not sync_result.drift

    # Verify receipt tracks override
    receipt = read_receipt(target)
    assert receipt is not None
    override_meta = receipt.overrides["team"]["guide"]
    assert override_meta.kind == "instruction"
    assert override_meta.relative_path == "guide.md"

    # get-context now returns the customized instruction
    ctx_after = get_context(target, "team").to_dict()
    assert "customized guide description" in ctx_after["instructions"][0]["header"]
    assert (target / OVERRIDES_PATH / "team/guide.md").as_posix() in ctx_after["instructions"][0]["path"]

    # Managed pristine file remains upstream content
    assert "upstream guide description" in (target / ".devkit/managed/team/guide.md").read_text()


def test_override_native_subagent_projection(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed, agents=["codex"])
    codex_agent = target / ".codex/agents/reviewer.toml"
    assert codex_agent.read_text() == 'system_prompt = "upstream prompt"\n'

    create_override(target, installed, "team:reviewer")
    override_file = target / OVERRIDES_PATH / "team/reviewer.toml"
    assert override_file.is_file()
    override_file.write_text('system_prompt = "custom team prompt"\n')

    sync_project(target, installed, agents=["codex"])
    # Native projection updated from override
    assert codex_agent.read_text() == 'system_prompt = "custom team prompt"\n'
    # Managed file remains pristine upstream
    assert (target / ".devkit/managed/team/reviewer.toml").read_text() == 'system_prompt = "upstream prompt"\n'


def test_override_drift_diff_accept_and_remove(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    create_override(target, installed, "team:guide")
    override_file = target / OVERRIDES_PATH / "team/guide.md"
    override_file.write_text("---\nname: guide\ndescription: customized guide description\n---\n# Custom Guide\n")
    sync_project(target, installed)

    # Simulate upstream wheel upgrade
    root = installed[0].bundle.root
    (root / "guide.md").write_text(
        "---\nname: guide\ndescription: upstream v2 security update\n---\n# Upstream Guide v2\n"
    )
    newer = [InstalledBundle("team-content", "0.2.0", load_bundle(root))]

    # Sync detects upstream drift
    sync_res = sync_project(target, newer)
    drift = sync_res.drift
    assert drift
    assert (drift[0].bundle, drift[0].asset) == ("team", "guide")

    # Diff shows drift: upstream vs override, and baseline vs new upstream
    diff_res = diff_override(target, newer, "team:guide").to_dict()
    assert diff_res["drift_detected"] is True
    (changed,) = diff_res["files"]
    assert changed["path"] == "guide.md"
    assert "upstream v2 security update" in (changed["diff"] or "")
    assert "upstream v2 security update" in (changed["upstream_diff"] or "")

    # List overrides shows drift
    listed = list_overrides(target, newer)
    assert len(listed) == 1
    assert listed[0].drift_detected is True

    # Accept updates the baseline digest
    accept_res = accept_override(target, newer, "team:guide").to_dict()
    assert accept_res["status"] == "accepted"

    # Sync now has zero drift
    sync_after_accept = sync_project(target, newer)
    assert not sync_after_accept.drift

    # Remove override
    remove_override(target, newer, "team:guide")
    assert not override_file.exists()
    receipt_after_remove = read_receipt(target)
    assert receipt_after_remove is not None
    assert "guide" not in receipt_after_remove.overrides.get("team", {})

    # get-context reverts to upstream content
    ctx_reverted = get_context(target, "team").to_dict()
    assert "upstream v2 security update" in ctx_reverted["instructions"][0]["header"]


def test_override_cli_commands(installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    runner = CliRunner()
    runner.invoke(cli, ["sync", "--workspace-root", str(target)])

    # CLI create
    res = runner.invoke(cli, ["override", "create", "team:guide", "--workspace-root", str(target)])
    assert res.exit_code == 0
    assert (target / OVERRIDES_PATH / "team/guide.md").is_file()

    # CLI duplicate without force fails
    res_dup = runner.invoke(cli, ["override", "create", "team:guide", "--workspace-root", str(target)])
    assert res_dup.exit_code != 0
    assert "override already exists" in res_dup.output

    # CLI duplicate with force succeeds
    res_force = runner.invoke(cli, ["override", "create", "team:guide", "--workspace-root", str(target), "--force"])
    assert res_force.exit_code == 0

    # CLI list
    res_list = runner.invoke(cli, ["override", "list", "--workspace-root", str(target)])
    assert res_list.exit_code == 0
    data = json.loads(res_list.output)["overrides"]
    assert len(data) == 1
    assert data[0]["asset"] == "guide"

    # CLI diff
    res_diff = runner.invoke(cli, ["override", "diff", "team:guide", "--workspace-root", str(target)])
    assert res_diff.exit_code == 0
    diff_data = json.loads(res_diff.output)
    assert diff_data["drift_detected"] is False

    # CLI accept
    res_accept = runner.invoke(cli, ["override", "accept", "team:guide", "--workspace-root", str(target)])
    assert res_accept.exit_code == 0

    # CLI remove
    res_remove = runner.invoke(cli, ["override", "remove", "team:guide", "--workspace-root", str(target)])
    assert res_remove.exit_code == 0
    assert not (target / OVERRIDES_PATH / "team/guide.md").exists()


def test_override_validation_errors(installed: list[InstalledBundle], target: Path) -> None:
    with pytest.raises(ArgumentError, match="expected bundle:asset selector"):
        create_override(target, installed, "invalid")

    with pytest.raises(SelectionError, match="bundle is not installed"):
        create_override(target, installed, "unknown:asset")

    with pytest.raises(SelectionError, match="asset not found"):
        create_override(target, installed, "team:unknown")
