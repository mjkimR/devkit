from __future__ import annotations

import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit_distribution.bundles import BundleError, load_bundle
from devkit_distribution.cli import cli
from devkit_distribution.installation import discovery, transaction
from devkit_distribution.installation.discovery import InstalledBundle, discover_bundles
from devkit_distribution.installation.sync import recover_project, sync_project
from devkit_distribution.installation.transaction import JOURNAL, RECEIPT, Content, snapshot


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    root = tmp_path / "source"
    (root / "skills/review/scripts").mkdir(parents=True)
    (root / "skills/review/SKILL.md").write_text("# Review\n")
    script = root / "skills/review/scripts/check.py"
    script.write_text("raise RuntimeError('must not run at sync')\n")
    script.chmod(0o755)
    (root / "reviewer.toml").write_text('future_native_option = "preserve"\n')
    (root / "guide.md").write_text("# Guide\n")
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
    return root


def test_sync_noop_restore_and_package_removal(installed: list[InstalledBundle], target: Path) -> None:
    first = sync_project(target, installed, agents=["codex"])
    assert first["actions"]
    receipt = (target / RECEIPT).read_bytes()
    native = target / ".codex/agents/reviewer.toml"
    assert native.read_bytes() == (installed[0].bundle.root / "reviewer.toml").read_bytes()
    script = target / ".agents/skills/review/scripts/check.py"
    assert script.stat().st_mode & 0o777 == 0o755
    assert sync_project(target, installed)["actions"] == []
    assert (target / RECEIPT).read_bytes() == receipt
    native.unlink()
    assert sync_project(target, installed)["actions"] == [{"path": ".codex/agents/reviewer.toml", "action": "create"}]
    assert (target / RECEIPT).read_bytes() == receipt
    sync_project(target, [])
    assert not native.exists()
    assert not script.exists()
    assert json.loads((target / RECEIPT).read_text())["files"] == {}


def test_update_preset_and_reset(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    root = installed[0].bundle.root
    (root / "guide.md").write_text("updated")
    newer = [InstalledBundle("team-content", "0.2.0", load_bundle(root))]
    sync_project(target, newer, presets={"team": "minimal"})
    assert (target / ".devkit/managed/team/guide.md").read_text() == "updated"
    assert not (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    assert sync_project(target, newer)["actions"] == []
    sync_project(target, newer, all_assets=True)
    assert (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    assert json.loads((target / RECEIPT).read_text())["packages"][0]["package_version"] == "0.2.0"


@pytest.mark.parametrize("removal", [False, True])
def test_user_edit_blocks_all_writes(installed: list[InstalledBundle], target: Path, removal: bool) -> None:
    sync_project(target, installed)
    guide = target / ".devkit/managed/team/guide.md"
    guide.write_text("user edit")
    receipt = (target / RECEIPT).read_bytes()
    with pytest.raises(BundleError, match="user-modified"):
        sync_project(target, [] if removal else installed)
    assert guide.read_text() == "user edit"
    assert (target / RECEIPT).read_bytes() == receipt


def test_mode_edit_is_protected(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    (target / ".devkit/managed/team/guide.md").chmod(0o600)
    with pytest.raises(BundleError, match="user-modified"):
        sync_project(target, installed)


def test_unowned_native_collision_preserves_other_tool(installed: list[InstalledBundle], target: Path) -> None:
    agent = target / ".codex/agents/reviewer.toml"
    agent.parent.mkdir(parents=True)
    agent.write_text("owned by another tool")
    with pytest.raises(BundleError, match="unowned"):
        sync_project(target, installed, agents=["codex"])
    assert agent.read_text() == "owned by another tool"
    assert not (target / ".devkit").exists()


def test_dry_run_and_invalid_variant_are_read_only(installed: list[InstalledBundle], target: Path) -> None:
    assert sync_project(target, installed, dry_run=True)["actions"]
    assert list(target.iterdir()) == []
    with pytest.raises(BundleError, match="missing native variant"):
        sync_project(target, installed, agents=["claude-code"])
    assert list(target.iterdir()) == []


def test_destination_symlink_rejected(installed: list[InstalledBundle], target: Path, tmp_path: Path) -> None:
    (target / ".devkit").symlink_to(tmp_path / "source", target_is_directory=True)
    with pytest.raises(BundleError, match="deployment symlink"):
        sync_project(target, installed)


def test_receipt_path_escape_rejected(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    path = target / RECEIPT
    receipt = json.loads(path.read_text())
    receipt["files"][".devkit/managed/../../outside"] = {"sha256": "a" * 64, "mode": 0o644}
    path.write_text(json.dumps(receipt))
    with pytest.raises(BundleError, match="unsafe deployment path"):
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
    with pytest.raises(BundleError, match="pending transaction"):
        sync_project(target, installed)
    guide = target / ".devkit/managed/team/guide.md"
    guide.write_text("subsequent edit")
    with pytest.raises(BundleError, match="subsequent edit"):
        recover_project(target)
    assert guide.read_text() == "subsequent edit"
    guide.write_bytes((installed[0].bundle.root / "guide.md").read_bytes())
    assert recover_project(target) > 0
    assert snapshot(target, JOURNAL) is None
    assert snapshot(target, RECEIPT) is None
    assert not guide.exists()
    assert sync_project(target, installed)["actions"]


def test_failure_rolls_back(installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = transaction.atomic_write
    failed = False

    def fail_once(root: Path, name: str, content: Content | None) -> None:
        nonlocal failed
        if name == RECEIPT and not failed:
            failed = True
            raise OSError("write failure")
        original(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail_once)
    with pytest.raises(OSError, match="write failure"):
        sync_project(target, installed)
    assert snapshot(target, RECEIPT) is None
    assert snapshot(target, JOURNAL) is None
    assert not (target / ".devkit/managed/team/guide.md").exists()


def test_cli_check_and_catalog(installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit_distribution.cli.discover_bundles", found)
    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--target", str(target), "--check"])
    assert result.exit_code == 1
    assert json.loads(result.output)["dry_run"] is True
    assert list(target.iterdir()) == []
    assert runner.invoke(cli, ["sync", "--target", str(target)]).exit_code == 0
    assert runner.invoke(cli, ["sync", "--target", str(target), "--check"]).exit_code == 0
    result = runner.invoke(cli, ["list", "--target", str(target)])
    assert json.loads(result.output)["synchronized_assets"]
    assert runner.invoke(cli, ["sync", "--target", str(target), "--agent", "codex"]).exit_code == 0
    assert (target / ".codex/agents/reviewer.toml").exists()
    assert runner.invoke(cli, ["sync", "--target", str(target), "--no-agents"]).exit_code == 0
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
    with pytest.raises(BundleError, match="duplicate installed bundle"), discover_bundles():
        pass


def test_project_lock_contention(installed: list[InstalledBundle], target: Path) -> None:
    with transaction.project_lock(target), pytest.raises(BundleError, match="project lock"):
        sync_project(target, installed)


def test_native_name_collision_between_packages(installed: list[InstalledBundle], target: Path) -> None:
    from dataclasses import replace

    other = InstalledBundle("other-content", "0.1.0", replace(installed[0].bundle, name="other"))
    with pytest.raises(BundleError, match="destination collision"):
        sync_project(target, [*installed, other], agents=["codex"])
    assert list(target.iterdir()) == []
