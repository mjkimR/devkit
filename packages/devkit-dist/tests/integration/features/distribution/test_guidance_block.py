from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import Level
from devkit_dist.base.errors import ConfigError, ReceiptError
from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.errors import ConflictError, DistributionError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation import guidance_block, transaction
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.workspace import AGENTS_FILE, JOURNAL
from devkit_dist.features.distribution.usecases.sync import RecoverProject, sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, RECEIPT_PATH
from distsupport.distribution import cli

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


def test_block_is_created_with_the_selection(installed: list[InstalledBundle], target: Path) -> None:
    result = sync_project(target, installed).to_dict()
    assert {"path": AGENTS_FILE, "action": "create"} in result["actions"]
    text = (target / AGENTS_FILE).read_text()
    assert text.startswith(START + "\n") and text.endswith(END + "\n")
    assert "Installed: `team`." in text
    assert "Entry skill" not in text  # the host lists skill descriptions itself
    assert "Managed by `devkit sync`" in text
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
    assert all(action["path"] != AGENTS_FILE for action in result["actions"])  # the bundle list did not change
    sync_project(target, [], deselect=["team"])
    text = (target / AGENTS_FILE).read_text()
    assert "No bundle is selected" in text and "`team`" not in text
    assert "guidance_block" in json.loads((target / RECEIPT_PATH).read_text())


def test_block_names_the_get_context_rule_only_with_a_selection(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    text = (target / AGENTS_FILE).read_text()
    assert "Before using assets from the following bundles, run `uv run devkit get-context <bundle>`" in text
    assert "unselected source bundle" not in text  # bundle authors read it in the authoring instruction


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


def test_opt_out_leaves_an_edited_block_with_a_warning(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    agents = target / AGENTS_FILE
    edited = agents.read_text().replace("## devkit", "## mine")
    agents.write_text(edited)
    write_config(target, extra="guidance_block = false")
    result = sync_project(target, installed)
    (notice,) = result.notices
    assert (notice.code, notice.level, notice.target_files) == ("ORPHAN_LEFT", Level.WARNING, (AGENTS_FILE,))
    assert agents.read_text() == edited
    assert all(action.path != AGENTS_FILE for action in result.actions)
    assert "guidance_block" not in json.loads((target / RECEIPT_PATH).read_text())
    assert sync_project(target, installed).to_dict()["notices"] == []


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
    assert RecoverProject().execute(target) == 0


def test_cli_check_reports_stale_block(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", found)
    runner = CliRunner()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"]).exit_code == 0
    (target / AGENTS_FILE).unlink()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"])
    assert result.exit_code == 1 and f"[CHANGE: create {AGENTS_FILE}]" in result.stdout
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check", "--format", "json"])
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


@pytest.mark.parametrize(
    "source", ["none", "constitution", "constitution-template", "instruction", "instruction-template", "documents"]
)
def test_context_requirement_agrees_across_entry_paths(tmp_path: Path, source: str) -> None:
    from devkit_dist.features.distribution.usecases.context import GetContext
    from devkit_dist.features.distribution.usecases.playbook_get import GetPlaybook
    from distsupport.distribution import instruction, write_bundle

    manifest = 'schema = 1\nname = "team"\nversion = "0.1.0"\n'
    files = {
        "skills/release/SKILL.md": instruction("release"),
        "run.md": "---\nname: run\ndescription: Run it.\naliases: [old-run]\n---\nRun.\n",
    }
    if source == "documents":
        manifest += 'context_documents = "docs/context"\n'
    if source.startswith("constitution"):
        files["AGENTS.md.jinja" if source.endswith("template") else "AGENTS.md"] = "Shared context.\n"
    manifest += '[[assets]]\nid = "release"\nkind = "skill"\nsource = "skills/release"\n'
    manifest += '[[assets]]\nid = "run"\nkind = "playbook"\nsource = "run.md"\n'
    if source.startswith("instruction"):
        filename = "guide.md.jinja" if source.endswith("template") else "guide.md"
        files[filename] = instruction("guide")
        manifest += f'[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "{filename}"\n'
    manifest += '[presets.bare]\nassets = ["release", "run"]\n'
    item = write_bundle(tmp_path / "source", manifest, files)
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["codex"])

    for preset in ["all", "bare", "all"]:
        update_config(root, presets={"team": [preset]})
        sync_project(root, [item])
        required = source not in {"none", "instruction", "instruction-template"} or (
            source.startswith("instruction") and preset == "all"
        )
        text = (root / AGENTS_FILE).read_text()
        skill = (root / ".agents/skills/release/SKILL.md").read_text()
        assert ("get-context <bundle>" in text) is required
        assert ("<!-- DEVKIT:CONTEXT -->" in skill) is required
        for selector in ["team/run", "team/old-run"]:
            context = GetPlaybook().execute(root, selector).to_dict()["context"]
            assert context == {
                "bundle": "team",
                "argv": ["uv", "run", "devkit", "get-context", "team"],
                "policy": "once-per-agent-context",
                "required": required,
            }
        if source == "documents":
            assert GetContext().execute(root, "team").documents == []
            directory = root / "docs/context"
            directory.mkdir(parents=True, exist_ok=True)
            assert GetContext().execute(root, "team").documents == []
            doc = directory / "guide.md"
            doc.write_text("---\ntitle: Runtime\nsummary: Runtime discovery.\n---\n")
            assert len(GetContext().execute(root, "team").documents) == 1
            doc.rename(directory / "README.md")


def test_mixed_context_sources_and_manifest_validation(tmp_path: Path) -> None:
    from devkit_dist.features.distribution.models.errors import NotSynchronizedError
    from devkit_dist.features.distribution.usecases.playbook_get import GetPlaybook
    from distsupport.distribution import write_bundle

    items = []
    for name, context in [("empty", ""), ("docs", 'context_documents = "missing"\n')]:
        items.append(
            write_bundle(
                tmp_path / name,
                f'schema = 1\nname = "{name}"\nversion = "0.1.0"\n{context}'
                '[[assets]]\nid = "run"\nkind = "playbook"\nsource = "run.md"\n',
                {"run.md": "---\nname: run\ndescription: Run.\n---\nRun.\n"},
            )
        )
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"empty": ["all"], "docs": ["all"]}, agents=[])
    sync_project(root, items)
    text = (root / AGENTS_FILE).read_text()
    assert "Installed: `docs`, `empty`." in text
    assert "after context loss: `docs`." in text
    assert GetPlaybook().execute(root, "empty/run").context_required is False
    assert GetPlaybook().execute(root, "docs/run").context_required is True
    manifest = root / ".devkit/managed/empty/bundle.toml"
    manifest.write_text(manifest.read_text() + "# modified\n")
    with pytest.raises(NotSynchronizedError):
        GetPlaybook().execute(root, "empty/run")
