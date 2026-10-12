from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.core.errors import ConfigError, ReceiptError
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.content import Content
from devkit.distribution.errors import ConflictError, DistributionError
from devkit.distribution.installation import guidance_block, transaction
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.sync import recover_project, sync_project
from devkit.distribution.installation.workspace import AGENTS_FILE, JOURNAL
from testsupport.distribution import cli

START, END = guidance_block.START, guidance_block.END


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    root = tmp_path / "source"
    (root / "playbooks").mkdir(parents=True)
    (root / "playbooks/on-call.md").write_text("---\nname: on-call\ndescription: Handle an incident.\n---\n# On call\n")
    (root / "guide.md").write_text("---\nname: guide\ndescription: Team guide.\n---\n# Guide\n")
    (root / "bundle.toml").write_text("""schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[[assets]]
id = "on-call"
kind = "playbook"
source = "playbooks/on-call.md"
[presets.minimal]
assets = ["guide"]
""")
    return [InstalledBundle("team-content", "0.1.0", load_bundle(root))]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["codex"])
    return root


def write_config(root: Path, *, presets: str = 'team = "all"', extra: str = "") -> None:
    (root / CONFIG_PATH).write_text(f'schema = 1\nagents = ["codex"]\n{extra}\n[presets]\n{presets}\n')


def block_of(root: Path) -> str | None:
    path = root / AGENTS_FILE
    return guidance_block.extract(path.read_text()) if path.exists() else None


def test_block_is_created_with_selection_and_entry_skills(installed: list[InstalledBundle], target: Path) -> None:
    result = sync_project(target, installed).to_dict()
    assert {"path": AGENTS_FILE, "action": "create"} in result["actions"]
    text = (target / AGENTS_FILE).read_text()
    assert text.startswith(START + "\n") and text.endswith(END + "\n")
    assert "Installed bundles: `team`." in text
    assert "`devkit-playbook`" in text and "`devkit-workflow`" not in text
    assert "managed by `devkit sync`" in text
    assert len(text.encode()) < 1024
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    assert receipt["guidance_block"] == guidance_block.digest(block_of(target) or "")
    assert AGENTS_FILE not in receipt["files"]
    # Deterministic: a second sync is a no-op and preserves the receipt bytes.
    before = (target / RECEIPT_PATH).read_bytes()
    assert sync_project(target, installed).to_dict()["actions"] == []
    assert (target / RECEIPT_PATH).read_bytes() == before


def test_block_follows_selection_changes(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    update_config(target, presets={"team": ["minimal"]})
    result = sync_project(target, installed).to_dict()
    assert {"path": AGENTS_FILE, "action": "update"} in result["actions"]
    assert "`devkit-playbook`" not in (target / AGENTS_FILE).read_text()
    sync_project(target, [], deselect=["team"])
    text = (target / AGENTS_FILE).read_text()
    assert "No bundle is selected" in text and "`team`" not in text
    assert "guidance_block" in json.loads((target / RECEIPT_PATH).read_text())


def test_bytes_outside_markers_are_preserved(installed: list[InstalledBundle], target: Path) -> None:
    agents = target / AGENTS_FILE
    agents.write_text("# My project\n\nHouse rules.\n")
    sync_project(target, installed)
    text = agents.read_text()
    assert text.startswith("# My project\n\nHouse rules.\n\n" + START)
    agents.write_text(text.replace("House rules.", "House rules, revised.") + "\n## Appendix\n")
    update_config(target, presets={"team": ["minimal"]})
    sync_project(target, installed)
    text = agents.read_text()
    assert text.startswith("# My project\n\nHouse rules, revised.\n\n" + START)
    assert text.endswith(END + "\n\n## Appendix\n")
    assert text.count(START) == 1


def test_hand_edited_block_blocks_all_writes(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    agents = target / AGENTS_FILE
    edited = agents.read_text().replace("## devkit", "## devkit (edited)")
    agents.write_text(edited)
    receipt = (target / RECEIPT_PATH).read_bytes()
    update_config(target, presets={"team": ["minimal"]})
    with pytest.raises(ConflictError, match="user-modified guidance block"):
        sync_project(target, installed)
    assert agents.read_text() == edited
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    assert (target / ".devkit/managed/team/playbooks/on-call.md").exists()


def test_removed_block_is_written_again(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    (target / AGENTS_FILE).write_text("# Only mine\n")
    result = sync_project(target, installed).to_dict()
    assert {"path": AGENTS_FILE, "action": "update"} in result["actions"]
    assert (target / AGENTS_FILE).read_text().startswith("# Only mine\n\n" + START)
    (target / AGENTS_FILE).unlink()
    assert {"path": AGENTS_FILE, "action": "create"} in sync_project(target, installed).to_dict()["actions"]


def test_unowned_or_malformed_block_is_rejected(installed: list[InstalledBundle], target: Path) -> None:
    (target / AGENTS_FILE).write_text(f"{START}\nhand written\n{END}\n")
    with pytest.raises(ConflictError, match="unowned guidance block"):
        sync_project(target, installed)
    assert not (target / RECEIPT_PATH).exists()
    (target / AGENTS_FILE).write_text(f"{START}\n{END}\n{START}\n{END}\n")
    with pytest.raises(DistributionError, match="malformed guidance block"):
        sync_project(target, installed)
    (target / AGENTS_FILE).write_text(f"{END}\n{START}\n")
    with pytest.raises(DistributionError, match="malformed guidance block"):
        sync_project(target, installed)


def test_opt_out_removes_block_and_stops_recording(installed: list[InstalledBundle], target: Path) -> None:
    (target / AGENTS_FILE).write_text("# My project\n")
    sync_project(target, installed)
    write_config(target, extra="guidance_block = false")
    result = sync_project(target, installed).to_dict()
    assert {"path": AGENTS_FILE, "action": "update"} in result["actions"]
    assert (target / AGENTS_FILE).read_text() == "# My project\n"
    assert "guidance_block" not in json.loads((target / RECEIPT_PATH).read_text())
    assert sync_project(target, installed).to_dict()["actions"] == []
    # A file that held only the block is removed.
    write_config(target)
    (target / AGENTS_FILE).unlink()
    sync_project(target, installed)
    write_config(target, extra="guidance_block = false")
    assert {"path": AGENTS_FILE, "action": "remove"} in sync_project(target, installed).to_dict()["actions"]
    assert not (target / AGENTS_FILE).exists()


def test_opt_out_refuses_to_remove_edited_block(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    agents = target / AGENTS_FILE
    agents.write_text(agents.read_text().replace("## devkit", "## mine"))
    write_config(target, extra="guidance_block = false")
    with pytest.raises(ConflictError, match="user-modified guidance block"):
        sync_project(target, installed)


def test_opt_out_from_the_start_writes_nothing(installed: list[InstalledBundle], target: Path) -> None:
    write_config(target, extra="guidance_block = false")
    sync_project(target, installed)
    assert not (target / AGENTS_FILE).exists()
    assert "guidance_block" not in json.loads((target / RECEIPT_PATH).read_text())


def test_invalid_config_and_receipt_values(installed: list[InstalledBundle], target: Path) -> None:
    write_config(target, extra='guidance_block = "no"')
    with pytest.raises(ConfigError, match="guidance_block must be a boolean"):
        sync_project(target, installed)
    write_config(target)
    sync_project(target, installed)
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    receipt["guidance_block"] = "short"
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match="guidance_block: expected a lowercase hex SHA-256"):
        sync_project(target, installed)
    receipt["guidance_block"] = "a" * 64
    receipt["files"][AGENTS_FILE] = {"sha256": "a" * 64, "mode": 0o644}
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match="receipt cannot own installation metadata"):
        sync_project(target, installed)


def test_block_write_is_journaled_and_rolled_back(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (target / AGENTS_FILE).write_text("# My project\n")
    original = transaction.atomic_write
    failed = False

    def fail_once(root: Path, name: str, content: Content | None) -> None:
        nonlocal failed
        if name == RECEIPT_PATH and not failed:
            failed = True
            raise OSError("write failure")
        original(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail_once)
    with pytest.raises(OSError, match="write failure"):
        sync_project(target, installed)
    assert (target / AGENTS_FILE).read_text() == "# My project\n"
    assert not (target / JOURNAL).exists()
    monkeypatch.setattr(transaction, "atomic_write", original)
    assert recover_project(target) == 0


def test_cli_check_reports_stale_block(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    runner = CliRunner()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"]).exit_code == 0
    (target / AGENTS_FILE).unlink()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"])
    assert result.exit_code == 1
    assert {"path": AGENTS_FILE, "action": "create"} in json.loads(result.output)["actions"]
    assert not (target / AGENTS_FILE).exists()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    assert (target / AGENTS_FILE).exists()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (None, "B\n"),
        ("", "B\n"),
        ("x", "x\n\nB\n"),
        ("x\n", "x\n\nB\n"),
        ("x\n\n", "x\n\nB\n"),
        ("a\nOLD\nb\n", "a\nB\nb\n"),
    ],
)
def test_compose_and_strip(text: str | None, expected: str) -> None:
    block = f"{START}\nbody\n{END}"
    source = text.replace("OLD", f"{START}\nold\n{END}") if text else text
    composed = guidance_block.compose(source, block)
    assert composed == expected.replace("B", block)
    stripped = guidance_block.strip(composed)
    if text in (None, ""):
        assert stripped is None
    elif text == "a\nOLD\nb\n":
        assert stripped == "a\nb\n"
    else:
        assert stripped == "x\n"
