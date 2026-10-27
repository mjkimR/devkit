"""Override tracking over whole assets, override commands under one lock, and playbook overrides."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.errors import ConflictError, OverrideDriftError, SelectionError
from devkit_dist.features.distribution.services.installation import transaction
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.overrides import record_overridden, record_source
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.workspace import JOURNAL
from devkit_dist.features.distribution.usecases.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit_dist.features.distribution.usecases.playbook_search import SearchPlaybooks
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.models.receipt import OverrideRecord
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, OVERRIDES_PATH, RECEIPT_PATH
from distsupport.distribution import instruction, reload, write_bundle

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
    (found,) = SearchPlaybooks().execute(target, "replica").to_dict()["results"]
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


def test_accept_synchronizes_the_merged_override(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    (item.bundle.root / "guide.md").write_text(instruction("guide", "Upstream v2.\n"))
    newer = reload(item)
    # The agent merges the upstream change into the override, then accepts it.
    (target / OVERRIDES_PATH / "team/guide.md").write_text(instruction("guide", "Upstream v2, ours.\n"))
    change = accept_override(target, [newer], "team:guide")
    assert change.status == "accepted" and change.accepted_upstream_sha256 is not None
    assert sync_project(target, [newer], dry_run=True).actions == []  # nothing left for `sync --check`
    assert [entry.drift_detected for entry in list_overrides(target, [newer])] == [False]


def test_accept_of_an_undeployed_override_records_the_baseline(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    update_config(target, deselect=["team"])
    sync_project(target, [item])
    (item.bundle.root / "guide.md").write_text(instruction("guide", "Upstream v2.\n"))
    newer = reload(item)
    accept_override(target, [newer], "team:guide")
    assert [entry.drift_detected for entry in list_overrides(target, [newer])] == [False]


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


def test_remove_keeps_project_files_the_override_does_not_track(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:review")
    notes = target / OVERRIDES_PATH / "team/skills/review/notes/ours.md"
    notes.parent.mkdir()
    notes.write_text("project notes\n")
    result = remove_override(target, [item], "team:review")
    assert result.paths == [
        f"{OVERRIDES_PATH}/team/skills/review/SKILL.md",
        f"{OVERRIDES_PATH}/team/skills/review/reference.md",
    ]
    assert notes.read_text() == "project notes\n"
    assert not (target / OVERRIDES_PATH / "team/skills/review/SKILL.md").exists()
    assert not (target / OVERRIDES_PATH / ".baseline").exists()
    (left,) = [notice for notice in result.notices if notice.code == "ORPHAN_LEFT"]
    assert left.target_files == (f"{OVERRIDES_PATH}/team/skills/review/notes/ours.md",)
    receipt = read_receipt(target)
    assert receipt is not None and "review" not in receipt.overrides.get("team", {})
    with pytest.raises(SelectionError, match="no override found"):
        remove_override(target, [item], "team:review")


def test_accept_rolls_back_the_baseline_when_the_receipt_write_fails(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    (item.bundle.root / "guide.md").write_text(instruction("guide", "Upstream v2.\n"))
    item = reload(item)
    baseline = target / OVERRIDES_PATH / ".baseline/team/guide.md"
    receipt_path = target / RECEIPT_PATH
    before = (baseline.read_bytes(), receipt_path.read_bytes())
    original = transaction.atomic_write
    failed = False

    def fail_receipt(root: Path, name: str, content: Content | None) -> None:
        nonlocal failed
        if name == RECEIPT_PATH and not failed:
            failed = True
            raise OSError("receipt write failure")
        original(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail_receipt)
    with pytest.raises(OSError, match="receipt write failure"):
        accept_override(target, [item], "team:guide")
    monkeypatch.setattr(transaction, "atomic_write", original)
    assert (baseline.read_bytes(), receipt_path.read_bytes()) == before
    assert not (target / JOURNAL).exists()
    assert [entry.drift_detected for entry in list_overrides(target, [item])] == [True]


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


def _without_asset(item: InstalledBundle, asset_id: str) -> InstalledBundle:
    """``item`` reloaded after upstream dropped ``asset_id`` from its manifest."""
    manifest = item.bundle.root / "bundle.toml"
    blocks = manifest.read_text().split("[[assets]]\n")
    manifest.write_text("[[assets]]\n".join(block for block in blocks if not block.startswith(f'id = "{asset_id}"\n')))
    return reload(item)


def test_record_of_a_removed_asset_follows_its_own_override_files(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    create_override(target, [item], "team:review")
    newer = _without_asset(item, "review")
    sync_project(target, [newer])
    receipt = read_receipt(target)
    assert receipt is not None and set(receipt.overrides["team"]) == {"guide", "review"}
    # Deleting the removed asset's override files drops its record, although another override of the bundle remains.
    for name in ("team/skills", ".baseline/team/skills"):
        shutil.rmtree(target / OVERRIDES_PATH / name)
    sync_project(target, [newer])
    receipt = read_receipt(target)
    assert receipt is not None and set(receipt.overrides["team"]) == {"guide"}


def test_remove_drops_the_override_of_a_removed_asset(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    create_override(target, [item], "team:review")
    newer = _without_asset(item, "review")
    sync_project(target, [newer])
    result = remove_override(target, [newer], "team:review")
    assert result.paths == [
        f"{OVERRIDES_PATH}/team/skills/review/SKILL.md",
        f"{OVERRIDES_PATH}/team/skills/review/reference.md",
    ]
    assert not (target / OVERRIDES_PATH / "team/skills").exists()
    assert not (target / OVERRIDES_PATH / ".baseline/team/skills").exists()
    receipt = read_receipt(target)
    assert receipt is not None and set(receipt.overrides["team"]) == {"guide"}
    assert [entry.asset for entry in list_overrides(target, [newer])] == ["guide"]
    with pytest.raises(SelectionError, match="asset not found"):
        remove_override(target, [newer], "team:review")


@pytest.mark.parametrize(
    ("relative_path", "expected"),
    [("skills/review/SKILL.md", "skills/review"), ("instructions/a.md", "instructions/a.md"), ("SKILL.md", None)],
)
def test_record_source_never_names_the_bundle_root(relative_path: str, expected: str | None) -> None:
    # A record at the bundle root would make override remove delete every override of the bundle.
    assert record_source(OverrideRecord("skill", relative_path, "a" * 64, "b" * 64)) == expected


def test_a_bundle_root_record_is_not_kept_by_other_overrides(tmp_path: Path) -> None:
    # A root record names no asset's own override directory; other overrides of the bundle must not keep it alive.
    other = tmp_path / OVERRIDES_PATH / "team/skills/guide/SKILL.md"
    other.parent.mkdir(parents=True)
    other.write_text("override\n", encoding="utf-8")
    assert not record_overridden(tmp_path, "team", OverrideRecord("skill", "SKILL.md", "a" * 64, "b" * 64))
