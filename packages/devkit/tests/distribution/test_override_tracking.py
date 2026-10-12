"""Override tracking over whole assets, override commands under one lock, and playbook overrides."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit.core.receipt import CONFIG_PATH, OVERRIDES_PATH
from devkit.distribution.errors import ConflictError, OverrideDriftError, SelectionError
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit.distribution.installation.playbook_search import search_playbooks
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.sync import sync_project
from testsupport.distribution import instruction, reload, write_bundle

MANIFEST = """schema = 1
name = "team"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "recovery"
kind = "playbook"
source = "playbooks/recovery.md"
[[assets]]
id = "policy"
kind = "rule"
source = "rules"
[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[[assets]]
id = "scaffold"
kind = "document"
seeded = true
source = "scaffold.md"
target = "docs/scaffold.md"
[presets.slim]
assets = ["guide"]
"""

FILES = {
    "playbooks/recovery.md": "---\nname: disaster-recovery\ndescription: Recover a replica.\n---\n1. Step\n",
    "rules/no_todo.py": "RULE = 'v1'\n",
    "rules/helpers.py": "HELP = 1\n",
    "skills/review/SKILL.md": "# Review\n",
    "skills/review/reference.md": "reference v1\n",
    "guide.md": instruction("guide"),
    "scaffold.md": "# Scaffold\n",
}


@pytest.fixture
def item(tmp_path: Path) -> InstalledBundle:
    return write_bundle(tmp_path / "source", MANIFEST, FILES)


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["claude-code"])
    return root


def _set_override_drift(target: Path, policy: str) -> None:
    config = target / CONFIG_PATH
    config.write_text(f'override_drift = "{policy}"\n' + config.read_text())


def test_overridden_playbook_is_searched_from_its_override(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:recovery")
    override = target / OVERRIDES_PATH / "team/playbooks/recovery.md"
    override.write_text("---\nname: disaster-recovery\ndescription: Recover a replica, our way.\n---\n1. Ours\n")
    sync_project(target, [item])
    (found,) = search_playbooks(target, "replica").to_dict()["results"]
    assert found["path"] == str(override.resolve())
    assert found["description"] == "Recover a replica, our way."


def test_directory_override_is_tracked_and_its_drift_can_block(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:policy")
    receipt = read_receipt(target)
    assert receipt is not None
    record = receipt.overrides["team"]["policy"]
    assert (record.kind, record.relative_path) == ("rule", "rules")
    assert [entry.asset for entry in list_overrides(target, [item])] == ["policy"]

    (item.bundle.root / "rules/helpers.py").write_text("HELP = 2  # upstream fix\n")
    newer = reload(item)
    drift = sync_project(target, [newer]).to_dict()["drift"]
    assert [(entry["bundle"], entry["asset"]) for entry in drift] == [("team", "policy")]
    _set_override_drift(target, "block")
    with pytest.raises(OverrideDriftError, match="team:policy"):
        sync_project(target, [newer])
    accept_override(target, [newer], "team:policy")
    assert sync_project(target, [newer]).to_dict()["drift"] == []


def test_drift_covers_every_upstream_file_of_an_overridden_skill(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:review")
    (item.bundle.root / "skills/review/reference.md").write_text("reference v2\n")
    newer = reload(item)
    assert [entry["asset"] for entry in sync_project(target, [newer]).to_dict()["drift"]] == ["review"]
    files = {entry["path"]: entry for entry in diff_override(target, [newer], "team:review").to_dict()["files"]}
    assert files["skills/review/SKILL.md"]["diff"] == ""  # overridden, unchanged
    changed = files["skills/review/reference.md"]
    assert "reference v2" in (changed["upstream_diff"] or "")
    assert "reference v2" in (changed["diff"] or "")


def test_accept_requires_a_tracked_override(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    with pytest.raises(SelectionError, match="no tracked override"):
        accept_override(target, [item], "team:guide")


def test_create_refuses_what_an_override_cannot_affect(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    with pytest.raises(SelectionError, match="seeded asset"):
        create_override(target, [item], "team:scaffold")
    update_config(target, presets={"team": ["slim"]})
    with pytest.raises(SelectionError, match="not part of the selected presets"):
        create_override(target, [item], "team:review")
    update_config(target, deselect=["team"])
    with pytest.raises(SelectionError, match="bundle is not selected"):
        create_override(target, [item], "team:guide")
    assert not (target / OVERRIDES_PATH).exists()


def test_create_rolls_back_when_the_sync_fails(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    (target / ".devkit/managed/team/rules/no_todo.py").write_text("edited by hand\n")
    with pytest.raises(ConflictError, match="user-modified"):
        create_override(target, [item], "team:guide")
    assert not (target / OVERRIDES_PATH).exists()


def test_create_force_restores_previous_override_on_failure(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    override = target / OVERRIDES_PATH / "team/guide.md"
    override.write_text(instruction("guide", "Ours.\n"))
    sync_project(target, [item])
    (target / ".devkit/managed/team/rules/no_todo.py").write_text("edited by hand\n")
    with pytest.raises(ConflictError, match="user-modified"):
        create_override(target, [item], "team:guide", force=True)
    assert override.read_text() == instruction("guide", "Ours.\n")


def test_remove_rolls_back_when_the_sync_fails(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:review")
    (target / ".devkit/managed/team/guide.md").write_text("edited by hand\n")
    with pytest.raises(ConflictError, match="user-modified"):
        remove_override(target, [item], "team:review")
    assert (target / OVERRIDES_PATH / "team/skills/review/SKILL.md").is_file()
    assert (target / OVERRIDES_PATH / ".baseline/team/skills/review/reference.md").is_file()


def test_remove_prunes_override_directories(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:review")
    result = remove_override(target, [item], "team:review").to_dict()
    assert result["paths"] == [
        f"{OVERRIDES_PATH}/team/skills/review/SKILL.md",
        f"{OVERRIDES_PATH}/team/skills/review/reference.md",
    ]
    assert not (target / OVERRIDES_PATH).exists()
    with pytest.raises(SelectionError, match="no override found"):
        remove_override(target, [item], "team:review")


def test_override_files_are_writable_copies(item: InstalledBundle, target: Path) -> None:
    upstream = item.bundle.root / "guide.md"
    upstream.chmod(0o444)
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    assert (target / OVERRIDES_PATH / "team/guide.md").stat().st_mode & 0o777 == 0o644


def test_deselected_bundle_keeps_its_override_baseline(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    update_config(target, deselect=["team"])
    sync_project(target, [item])
    (item.bundle.root / "guide.md").write_text(instruction("guide", "Upstream v2.\n"))
    newer = reload(item)
    update_config(target, presets={"team": ["all"]})
    assert [entry["asset"] for entry in sync_project(target, [newer]).to_dict()["drift"]] == ["guide"]


def test_variant_subagent_override_covers_every_variant(tmp_path: Path, target: Path) -> None:
    manifest = """schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/reviewer.toml"
claude-code = "native/reviewer.md"
"""
    item = write_bundle(
        tmp_path / "variants",
        manifest,
        {"native/reviewer.toml": 'model = "a"\n', "native/reviewer.md": "---\nname: reviewer\n---\nPrompt.\n"},
    )
    update_config(target, presets={"team": ["all"]}, agents=["claude-code", "codex"])
    sync_project(target, [item])
    created = create_override(target, [item], "team:reviewer").to_dict()
    assert created["paths"] == [
        f"{OVERRIDES_PATH}/team/native/reviewer.md",
        f"{OVERRIDES_PATH}/team/native/reviewer.toml",
    ]
    (target / OVERRIDES_PATH / "team/native/reviewer.toml").write_text('model = "ours"\n')
    sync_project(target, [item])
    assert (target / ".codex/agents/reviewer.toml").read_text() == 'model = "ours"\n'
    (item.bundle.root / "native/reviewer.md").write_text("---\nname: reviewer\n---\nPrompt v2.\n")
    newer = reload(item)
    files = {entry["path"]: entry for entry in diff_override(target, [newer], "team:reviewer").to_dict()["files"]}
    assert "Prompt v2." in (files["native/reviewer.md"]["upstream_diff"] or "")
    assert 'model = "ours"' in (files["native/reviewer.toml"]["diff"] or "")
