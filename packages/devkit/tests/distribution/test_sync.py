from __future__ import annotations

import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.core.errors import ConfigError, ReceiptError
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.content import Content
from devkit.distribution.errors import (
    ConflictError,
    LockHeldError,
    PackageError,
    PendingTransactionError,
    RecoveryError,
    SelectionError,
    UnsafeWorkspaceError,
)
from devkit.distribution.installation import discovery, transaction
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle, discover_bundles
from devkit.distribution.installation.sync import recover_project, sync_project
from devkit.distribution.installation.workspace import JOURNAL, snapshot
from testsupport.distribution import cli


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    root = tmp_path / "source"
    (root / "skills/review/scripts").mkdir(parents=True)
    (root / "skills/review/SKILL.md").write_text("# Review\n")
    script = root / "skills/review/scripts/check.py"
    script.write_text("raise RuntimeError('must not run at sync')\n")
    script.chmod(0o755)
    (root / "reviewer.toml").write_text('future_native_option = "preserve"\n')
    (root / "guide.md").write_text("---\nname: guide\ndescription: Team guide.\n---\n# Guide\n")
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


@pytest.fixture
def bare(tmp_path: Path) -> Path:
    root = tmp_path / "bare"
    root.mkdir()
    return root


def write_config(root: Path, content: str) -> None:
    path = root / CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_sync_noop_restore_and_package_removal(installed: list[InstalledBundle], target: Path) -> None:
    update_config(target, agents=["codex"])
    first = sync_project(target, installed).to_dict()
    assert first["actions"]
    receipt = (target / RECEIPT_PATH).read_bytes()
    native = target / ".codex/agents/reviewer.toml"
    assert native.read_bytes() == (installed[0].bundle.root / "reviewer.toml").read_bytes()
    script = target / ".agents/skills/review/scripts/check.py"
    assert script.stat().st_mode & 0o777 == 0o755
    assert sync_project(target, installed).to_dict()["actions"] == []
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    native.unlink()
    assert sync_project(target, installed).to_dict()["actions"] == [
        {"path": ".codex/agents/reviewer.toml", "action": "create"}
    ]
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    sync_project(target, [], deselect=["team"])
    assert not native.exists()
    assert not script.exists()
    assert json.loads((target / RECEIPT_PATH).read_text())["files"] == {}


def test_update_preset_and_reset(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    root = installed[0].bundle.root
    (root / "guide.md").write_text("---\nname: guide\ndescription: Team guide.\n---\nupdated\n")
    newer = [InstalledBundle("team-content", "0.2.0", load_bundle(root))]
    update_config(target, presets={"team": ["minimal"]})
    sync_project(target, newer)
    assert (target / ".devkit/managed/team/guide.md").read_text().endswith("updated\n")
    assert not (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    assert sync_project(target, newer).to_dict()["actions"] == []
    sync_project(target, newer, presets={"team": ["all"]})
    assert (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    assert json.loads((target / RECEIPT_PATH).read_text())["packages"][0]["package_version"] == "0.2.0"


@pytest.mark.parametrize("removal", [False, True])
def test_user_edit_blocks_all_writes(installed: list[InstalledBundle], target: Path, removal: bool) -> None:
    sync_project(target, installed)
    guide = target / ".devkit/managed/team/guide.md"
    guide.write_text("user edit")
    receipt = (target / RECEIPT_PATH).read_bytes()
    if removal:
        # No longer desired: the edited file becomes an orphan, everything else proceeds.
        result = sync_project(target, [], deselect=["team"])
        (orphan,) = result.notices
        assert (orphan.code, orphan.target_files) == ("ORPHAN_LEFT", (".devkit/managed/team/guide.md",))
        assert "left modified file in place" in orphan.message
        assert guide.read_text() == "user edit"
        assert ".devkit/managed/team/guide.md" not in json.loads((target / RECEIPT_PATH).read_text())["files"]
        return
    with pytest.raises(ConflictError, match="user-modified"):
        sync_project(target, installed)
    assert guide.read_text() == "user edit"
    assert (target / RECEIPT_PATH).read_bytes() == receipt


def test_mode_edit_is_protected(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    (target / ".devkit/managed/team/guide.md").chmod(0o755)
    with pytest.raises(ConflictError, match="user-modified"):
        sync_project(target, installed)


@pytest.mark.parametrize("mode", [0o664, 0o600, 0o640])
def test_permission_noise_is_not_an_edit(installed: list[InstalledBundle], target: Path, mode: int) -> None:
    # A checkout under umask 002 writes 0o664; only the execute bit is part of a file's signature.
    sync_project(target, installed)
    (target / ".devkit/managed/team/guide.md").chmod(mode)
    script = target / ".agents/skills/review/scripts/check.py"
    script.chmod(0o775)
    assert sync_project(target, installed).to_dict()["actions"] == []


def test_unowned_native_collision_preserves_other_tool(installed: list[InstalledBundle], target: Path) -> None:
    agent = target / ".codex/agents/reviewer.toml"
    agent.parent.mkdir(parents=True)
    agent.write_text("owned by another tool")
    with pytest.raises(ConflictError, match="unowned"):
        sync_project(target, installed, agents=["codex"])
    assert agent.read_text() == "owned by another tool"
    assert not (target / RECEIPT_PATH).exists()


def test_dry_run_is_read_only_and_missing_variant_is_reported(installed: list[InstalledBundle], target: Path) -> None:
    assert sync_project(target, installed, dry_run=True).to_dict()["actions"]
    assert not (target / RECEIPT_PATH).exists()
    result = sync_project(target, installed, agents=["claude-code"], dry_run=True).to_dict()
    assert result["unprojected"] == [{"bundle": "team", "asset": "reviewer", "agent": "claude-code"}]
    assert not any(a["path"].startswith(".claude/agents/") for a in result["actions"])
    assert not (target / ".devkit/managed").exists()


def test_destination_symlink_rejected(installed: list[InstalledBundle], target: Path, tmp_path: Path) -> None:
    (target / ".devkit/managed").symlink_to(tmp_path / "source", target_is_directory=True)
    with pytest.raises(UnsafeWorkspaceError, match="deployment symlink"):
        sync_project(target, installed)


def test_receipt_path_escape_rejected(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    path = target / RECEIPT_PATH
    receipt = json.loads(path.read_text())
    receipt["files"][".devkit/managed/../../outside"] = {"sha256": "a" * 64, "mode": 0o644}
    path.write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match="unsafe path"):
        sync_project(target, installed)


def test_interruption_recovery_and_later_edit_protection(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = transaction.atomic_write

    def interrupt(root: Path, name: str, content: Content | None) -> None:
        original(root, name, content)
        if name == ".devkit/managed/team/guide.md":
            raise SystemExit("simulated process interruption")

    monkeypatch.setattr(transaction, "atomic_write", interrupt)
    with pytest.raises(SystemExit):
        sync_project(target, installed)
    monkeypatch.setattr(transaction, "atomic_write", original)
    assert (target / JOURNAL).exists()
    with pytest.raises(PendingTransactionError, match="interrupted synchronization"):
        sync_project(target, installed)
    guide = target / ".devkit/managed/team/guide.md"
    guide.write_text("subsequent edit")
    with pytest.raises(RecoveryError, match="subsequent edit"):
        recover_project(target)
    assert guide.read_text() == "subsequent edit"
    guide.write_bytes((installed[0].bundle.root / "guide.md").read_bytes())
    assert recover_project(target) > 0
    assert snapshot(target, JOURNAL) is None
    assert snapshot(target, RECEIPT_PATH) is None
    assert not guide.exists()
    assert sync_project(target, installed).to_dict()["actions"]


def test_failure_rolls_back(installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert snapshot(target, RECEIPT_PATH) is None
    assert snapshot(target, JOURNAL) is None
    assert not (target / ".devkit/managed/team/guide.md").exists()


def test_cli_check_and_catalog(installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"])
    assert result.exit_code == 1
    assert json.loads(result.output)["dry_run"] is True
    assert not (target / RECEIPT_PATH).exists()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"]).exit_code == 0
    result = runner.invoke(cli, ["list", "--workspace-root", str(target)])
    assert json.loads(result.output)["synchronized_assets"]
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--agent", "codex"]).exit_code == 0
    assert (target / ".codex/agents/reviewer.toml").exists()
    assert 'agents = ["codex"]' in (target / CONFIG_PATH).read_text()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    assert (target / ".codex/agents/reviewer.toml").exists()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--no-agents"]).exit_code == 0
    assert not (target / ".codex/agents/reviewer.toml").exists()


def test_discovery_uses_resource_module_and_rejects_duplicate(
    installed: list[InstalledBundle], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "module"
    shutil.copytree(installed[0].bundle.root, module / "bundle")
    starter = SimpleNamespace(
        name="team",
        value="team_content",
        module="team_content",
        attr=None,
        extras=[],
        dist=SimpleNamespace(metadata={"Name": "team-content"}, version="0.1.0"),
    )
    monkeypatch.setattr(discovery.resources, "files", lambda name: module)
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [starter])
    with discover_bundles() as found:
        assert found[0].package == "team-content"
        assert found[0].bundle.name == "team"
        assert (found[0].bundle.root / "skills/review/SKILL.md").is_file()
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [starter, starter])
    with pytest.raises(PackageError, match="duplicate installed bundle"), discover_bundles():
        pass


def test_project_lock_contention(installed: list[InstalledBundle], target: Path) -> None:
    with transaction.project_lock(target), pytest.raises(LockHeldError, match="project lock"):
        sync_project(target, installed)


def test_native_name_collision_between_packages(installed: list[InstalledBundle], target: Path) -> None:
    from dataclasses import replace

    other = InstalledBundle("other-content", "0.1.0", replace(installed[0].bundle, name="other"))
    with pytest.raises(ConflictError, match="destination collision"):
        sync_project(target, [*installed, other], agents=["codex"], presets={"other": ["all"]})
    assert not (target / RECEIPT_PATH).exists()


def test_sync_reads_project_config(installed: list[InstalledBundle], bare: Path) -> None:
    write_config(
        bare,
        """schema = 1
agents = ["codex"]

[presets]
team = "minimal"
""",
    )
    sync_project(bare, installed)
    assert (bare / ".devkit/managed/team/guide.md").exists()
    assert not (bare / ".devkit/managed/team/skills/review/SKILL.md").exists()
    # "reviewer" is not in the "minimal" preset, so its projection does not exist
    assert not (bare / ".codex/agents/reviewer.toml").exists()
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert receipt["schema"] == 1
    assert receipt["selection"] == {"agents": ["codex"], "presets": {"team": ["minimal"]}}


def test_unselected_bundles_are_not_deployed(installed: list[InstalledBundle], bare: Path) -> None:
    result = sync_project(bare, installed).to_dict()
    assert not (bare / ".devkit/managed").exists()
    assert result["packages"] == []
    assert result["unselected"] == [
        {"bundle": "team", "package": "team-content", "presets": ["all", "minimal"], "default_preset": None}
    ]
    # Without an ``agents`` entry every supported agent is a projection target.
    assert json.loads((bare / RECEIPT_PATH).read_text())["selection"] == {
        "agents": ["antigravity", "claude-code", "codex"],
        "presets": {},
    }


def test_preset_union_and_one_run_selection(installed: list[InstalledBundle], target: Path, tmp_path: Path) -> None:
    root = installed[0].bundle.root
    with (root / "bundle.toml").open("a") as stream:
        stream.write('[presets.skills]\nassets = ["review"]\n')
    union = [InstalledBundle("team-content", "0.1.0", load_bundle(root))]
    update_config(target, presets={"team": ["minimal", "skills"]})
    assert 'team = ["minimal", "skills"]' in (target / CONFIG_PATH).read_text()
    sync_project(target, union)
    assert (target / ".devkit/managed/team/guide.md").exists()
    assert (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    assert not (target / ".devkit/managed/team/reviewer.toml").exists()
    # One-run selections are not persisted: the next plain sync converges back to config.
    sync_project(target, union, presets={"team": ["minimal"]})
    assert not (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    sync_project(target, union)
    assert (target / ".devkit/managed/team/skills/review/SKILL.md").exists()


def test_selected_bundle_must_be_installed(installed: list[InstalledBundle], target: Path) -> None:
    with pytest.raises(SelectionError, match=r"selected bundle is not installed: \['team'\]"):
        sync_project(target, [])
    with pytest.raises(SelectionError, match="unknown preset missing"):
        sync_project(target, installed, presets={"team": ["missing"]})


@pytest.mark.parametrize(
    ("content", "error_match"),
    [
        ("schema = 2\n", "unsupported config schema"),
        ("schema = 'bad'\n", "unsupported config schema"),
        ("agents = ['unsupported']\n", "config: invalid agents"),
        ("[presets]\n'bad slug!' = 'minimal'\n", "config: invalid presets"),
        ("[presets]\nteam = []\n", "config: invalid presets"),
        ("[presets]\nteam = ['minimal', 'minimal']\n", "config: invalid presets"),
        ("[presets]\nteam = 1\n", "config: invalid presets"),
        ("unknown_field = 42\n", "config: unknown fields"),
        ("exclude_bundles = ['team']\n", "config: unknown fields"),
        ("[selection]\nagents = []\n", "config: unknown fields"),
        ("[playbooks]\nunknown_subfield = true\n", "config playbooks: unknown fields"),
        ("tool = 1\n", "config tool: expected a table"),
        ("[tool]\nspecrig = 'on'\n", "config tool.specrig: expected a table"),
        ("[tool.'Bad Name']\nx = 1\n", "config tool: invalid tool name"),
        ("[playbooks]\nlimit = 0\n", "config playbooks: limit must be an integer between 1 and 20"),
        ("[playbooks]\nmin_score = -1\n", "config playbooks: min_score must be a finite nonnegative number"),
        ("[playbooks]\nmax_bytes = 100\n", "config playbooks: max_bytes must be an integer between 1024 and 65536"),
        ("invalid toml [[\n", "invalid config"),
    ],
)
def test_invalid_project_config(installed: list[InstalledBundle], bare: Path, content: str, error_match: str) -> None:
    write_config(bare, content)
    with pytest.raises(ConfigError, match=error_match):
        sync_project(bare, installed)


def test_sync_passes_tool_tables_through_unread(installed: list[InstalledBundle], bare: Path) -> None:
    write_config(
        bare,
        """schema = 1

[presets]
team = "minimal"

[tool.specrig]
worktree = "on"
unknown_to_devkit = { nested = [1, 2] }

[tool.my_other-tool]
anything = true
""",
    )
    sync_project(bare, installed)
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert receipt["selection"]["presets"] == {"team": ["minimal"]}
    # The receipt's ``tool`` is the distributor's identity, never the config's [tool.*] tables.
    assert receipt["tool"]["package"] == "devkit"
    assert "specrig" not in json.dumps(receipt)


def test_sync_accepts_playbooks_config(installed: list[InstalledBundle], bare: Path) -> None:
    write_config(
        bare,
        """schema = 1
agents = ["codex"]

[presets]
team = "minimal"

[playbooks]
min_score = 0.2
limit = 3
max_bytes = 4096
""",
    )
    sync_project(bare, installed)
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert receipt["selection"] == {"agents": ["codex"], "presets": {"team": ["minimal"]}}


def test_sync_ignores_rules_table_owned_by_rule_engine(installed: list[InstalledBundle], bare: Path) -> None:
    write_config(
        bare,
        """schema = 1
agents = ["codex"]

[rules.phase_overrides]
RULE-markdown-link = "hygiene"
""",
    )
    sync_project(bare, installed)
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert receipt["selection"]["agents"] == ["codex"]


def test_sync_ignores_workflow_table_owned_by_workflow_engine(installed: list[InstalledBundle], bare: Path) -> None:
    write_config(
        bare,
        """schema = 1
agents = ["codex"]

[workflow]
anchor = "task.md"

[workflow.approvals]
integration = "ask"
""",
    )
    sync_project(bare, installed)
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert receipt["selection"]["agents"] == ["codex"]


def test_sync_deploys_gate_assets_and_ignores_gates_table(tmp_path: Path, bare: Path) -> None:
    root = tmp_path / "gate_source"
    (root / "gates").mkdir(parents=True)
    (root / "gates/block.py").write_text("raise RuntimeError('must not run at sync')\n")
    (root / "bundle.toml").write_text("""schema = 1
name = "gates"
version = "0.1.0"
[[assets]]
id = "block"
kind = "gate"
source = "gates/block.py"
""")
    write_config(
        bare,
        """schema = 1
[presets]
gates = "all"

[gates.settings.block]
enabled = true
""",
    )
    sync_project(bare, [InstalledBundle("gate-content", "0.1.0", load_bundle(root))])
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert {"bundle": "gates", "id": "block", "kind": "gate", "paths": [".devkit/managed/gates/gates/block.py"]} in (
        receipt["assets"]
    )
    assert (bare / ".devkit/managed/gates/gates/block.py").is_file()


def test_sync_records_workflow_check_assets_like_rules(tmp_path: Path, bare: Path) -> None:
    root = tmp_path / "checks-source"
    (root / "checks").mkdir(parents=True)
    (root / "checks/materials.py").write_text("raise RuntimeError('must not run at sync')\n")
    (root / "bundle.toml").write_text("""schema = 1
name = "sdd"
version = "0.1.0"
[[assets]]
id = "materials-present"
kind = "workflow-check"
source = "checks/materials.py"
""")
    write_config(bare, 'schema = 1\n[presets]\nsdd = "all"\n')
    sync_project(bare, [InstalledBundle("sdd-content", "0.1.0", load_bundle(root))])
    receipt = json.loads((bare / RECEIPT_PATH).read_text())
    assert {
        "bundle": "sdd",
        "id": "materials-present",
        "kind": "workflow-check",
        "paths": [".devkit/managed/sdd/checks/materials.py"],
    } in receipt["assets"]
    assert (bare / ".devkit/managed/sdd/checks/materials.py").is_file()


def test_receipt_cannot_own_config(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    path = target / RECEIPT_PATH
    receipt = json.loads(path.read_text())
    receipt["files"][CONFIG_PATH] = {"sha256": "a" * 64, "mode": 0o644}
    path.write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match="receipt cannot own installation metadata"):
        sync_project(target, installed)


def test_receipt_rejects_invalid_presets(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    path = target / RECEIPT_PATH
    receipt = json.loads(path.read_text())
    receipt["selection"]["presets"] = {"team": "minimal"}
    path.write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=r"selection\.presets"):
        sync_project(target, installed)


def make_extra_bundle(tmp_path: Path, default_preset: str | None = None) -> InstalledBundle:
    root = tmp_path / "extra_source"
    root.mkdir(parents=True, exist_ok=True)
    default = f'default_preset = "{default_preset}"\n' if default_preset else ""
    (root / "bundle.toml").write_text(f"""schema = 1
name = "extra"
version = "0.1.0"
{default}[[assets]]
id = "note"
kind = "instruction"
source = "note.md"
[[assets]]
id = "extended"
kind = "instruction"
source = "extended.md"
[presets.core]
assets = ["note"]
""")
    (root / "note.md").write_text("---\nname: note\ndescription: A note.\n---\n# Note\n")
    (root / "extended.md").write_text("---\nname: extended\ndescription: More.\n---\n# Extended\n")
    return InstalledBundle("extra-content", "0.1.0", load_bundle(root))


def mock_discovery(monkeypatch: pytest.MonkeyPatch, installed: list[InstalledBundle]) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)


def test_cli_add_resolves_default_preset_and_remove(
    installed: list[InstalledBundle], target: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    all_installed = [*installed, make_extra_bundle(tmp_path, default_preset="core")]
    mock_discovery(monkeypatch, all_installed)
    (target / CONFIG_PATH).write_text(
        (target / CONFIG_PATH).read_text() + '\n# phase overrides\n[rules.phase_overrides]\nRULE-x = "hygiene"\n'
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target)])
    assert result.exit_code == 0, result.output
    assert "[NOTICE: installed bundles not selected: extra;" in result.stderr

    result = runner.invoke(cli, ["add", "extra", "--workspace-root", str(target)])
    assert result.exit_code == 0, result.output
    config = (target / CONFIG_PATH).read_text()
    assert 'extra = "core"' in config
    assert "# phase overrides" in config and 'RULE-x = "hygiene"' in config
    assert (target / ".devkit/managed/extra/note.md").exists()
    assert not (target / ".devkit/managed/extra/extended.md").exists()
    assert "NOTICE" not in result.stderr

    listed = json.loads(runner.invoke(cli, ["list", "--workspace-root", str(target)]).output)
    extra = next(item for item in listed["installed"] if item["bundle"] == "extra")
    assert extra["selected"] == ["core"]
    assert extra["default_preset"] == "core"

    result = runner.invoke(cli, ["remove", "extra", "--workspace-root", str(target)])
    assert result.exit_code == 0, result.output
    assert "extra" not in (target / CONFIG_PATH).read_text().split("[presets]")[1].split("[rules")[0]
    assert not (target / ".devkit/managed/extra/note.md").exists()

    result = runner.invoke(cli, ["remove", "extra", "--workspace-root", str(target)])
    assert result.exit_code != 0
    assert "not selected" in result.output


def test_cli_add_requires_preset_without_default(
    installed: list[InstalledBundle], bare: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_discovery(monkeypatch, installed)
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "team", "--workspace-root", str(bare)])
    assert result.exit_code != 0
    assert "team: the bundle declares no default preset" in result.output
    assert "[FIX]    Select one of: team:all, team:minimal" in result.stderr
    assert not (bare / CONFIG_PATH).exists()
    result = runner.invoke(cli, ["add", "team:minimal", "--workspace-root", str(bare), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert not (bare / CONFIG_PATH).exists()
    assert not (bare / RECEIPT_PATH).exists()
    result = runner.invoke(cli, ["add", "team:minimal", "team:all", "--workspace-root", str(bare)])
    assert result.exit_code == 0, result.output
    assert 'team = ["minimal", "all"]' in (bare / CONFIG_PATH).read_text()
    assert (bare / CONFIG_PATH).read_text().startswith("schema = 1\n")


def test_cli_sync_preset_saves_unless_no_save(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_discovery(monkeypatch, installed)
    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--preset", "team:minimal", "--no-save"])
    assert result.exit_code == 0, result.output
    assert 'team = "all"' in (target / CONFIG_PATH).read_text()
    assert not (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--preset", "team:minimal"])
    assert result.exit_code == 0, result.output
    assert 'team = "minimal"' in (target / CONFIG_PATH).read_text()
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--preset", "team"])
    assert result.exit_code != 0
    assert "no default preset" in result.output
    result = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--preset", "Bad!"])
    assert result.exit_code != 0


def test_stray_files_under_managed_root_are_reported_not_touched(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert sync_project(target, installed).to_dict()["stray"] == []
    stray = target / ".devkit/managed/team/rules/local_rule.py"
    stray.parent.mkdir(parents=True)
    stray.write_text("# hand-placed\n")
    result = sync_project(target, installed).to_dict()
    assert result["stray"] == [".devkit/managed/team/rules/local_rule.py"]
    assert result["actions"] == []
    assert stray.exists()

    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    out = CliRunner().invoke(cli, ["sync", "--workspace-root", str(target)])
    assert out.exit_code == 0
    assert (
        "[WARNING: (MANAGED_FILE_STRAY) unmanaged files under .devkit/managed/: .devkit/managed/team/rules/local_rule.py"
        in out.stderr
    )


def test_agents_default_to_every_host_and_empty_list_disables_projection(
    installed: list[InstalledBundle], bare: Path
) -> None:
    write_config(bare, 'schema = 1\n[presets]\nteam = "all"\n')
    result = sync_project(bare, installed).to_dict()
    assert result["selection"]["agents"] == ["antigravity", "claude-code", "codex"]
    for path in [".agents/skills/review/SKILL.md", ".claude/skills/review/SKILL.md", ".codex/agents/reviewer.toml"]:
        assert (bare / path).exists(), path
    # The only-codex variant is skipped, not converted, for the other two hosts.
    assert {(u["agent"]) for u in result["unprojected"]} == {"antigravity", "claude-code"}
    assert not (bare / ".agents/agents/reviewer.md").exists()

    write_config(bare, 'schema = 1\nagents = []\n[presets]\nteam = "all"\n')
    result = sync_project(bare, installed).to_dict()
    assert result["selection"]["agents"] == [] and result["unprojected"] == []
    assert not (bare / ".agents/skills/review/SKILL.md").exists()
    assert (bare / ".devkit/managed/team/skills/review/SKILL.md").exists()


def test_codex_and_antigravity_share_skill_projections(installed: list[InstalledBundle], target: Path) -> None:
    result = sync_project(target, installed, agents=["codex", "antigravity"]).to_dict()
    skill = target / ".agents/skills/review/SKILL.md"
    assert skill.exists()
    assert [a["path"] for a in result["actions"]].count(".agents/skills/review/SKILL.md") == 1
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    review = next(a for a in receipt["assets"] if a["id"] == "reviewer")
    assert review["paths"] == [".codex/agents/reviewer.toml", ".devkit/managed/team/reviewer.toml"]
    # Dropping Antigravity keeps the shared projection because Codex still needs it.
    sync_project(target, installed, agents=["codex"])
    assert skill.exists()
    sync_project(target, installed, agents=["antigravity"])
    assert skill.exists() and not (target / ".codex/agents/reviewer.toml").exists()


def test_antigravity_native_variant_is_copied(installed: list[InstalledBundle], target: Path) -> None:
    root = installed[0].bundle.root
    (root / "reviewer-ag.md").write_text("---\nname: reviewer\nsubagent: true\n---\nnative\n")
    (root / "bundle.toml").write_text(
        (root / "bundle.toml")
        .read_text()
        .replace('codex = "reviewer.toml"', 'codex = "reviewer.toml"\nantigravity = "reviewer-ag.md"')
    )
    bundle = [InstalledBundle("team-content", "0.1.0", load_bundle(root))]
    result = sync_project(target, bundle, agents=["antigravity"]).to_dict()
    assert result["unprojected"] == []
    assert (target / ".agents/agents/reviewer.md").read_text() == "---\nname: reviewer\nsubagent: true\n---\nnative\n"
