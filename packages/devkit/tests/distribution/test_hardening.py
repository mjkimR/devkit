"""Post-sync hooks, override drift policy, orphans, ``devkit status`` and tool identity."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode, AdvisoryError, ExitCode, Level
from devkit.core.errors import ConfigError, ReceiptError
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH, ToolRecord
from devkit.distribution.bundles import load_bundle
from devkit.distribution.errors import ConflictError, OverrideDriftError
from devkit.distribution.installation import discovery, hooks
from devkit.distribution.installation import status as status_module
from devkit.distribution.installation import sync as sync_module
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.override_commands import create_override
from devkit.distribution.installation.status import get_project_status
from devkit.distribution.installation.sync import sync_project, tool_identity
from devkit.distribution.installation.workspace import AGENTS_FILE, JOURNAL
from testsupport.distribution import cli


@pytest.fixture
def source(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    (root / "skills/review").mkdir(parents=True)
    (root / "skills/review/SKILL.md").write_text("# Review\n")
    (root / "guide.md").write_text("---\nname: guide\ndescription: Upstream guide.\n---\n# Guide v1\n")
    (root / "scaffold.md").write_text("# Seeded\n")
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
id = "scaffold"
kind = "document"
source = "scaffold.md"
seeded = true
target = "docs/scaffold.md"
[presets.minimal]
assets = ["guide"]
""")
    return root


@pytest.fixture
def installed(source: Path) -> list[InstalledBundle]:
    return [InstalledBundle("team-content", "0.1.0", load_bundle(source))]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["codex"])
    return root


def write_config(root: Path, extra: str = "", presets: str = 'team = "all"') -> None:
    (root / CONFIG_PATH).write_text(f'schema = 1\nagents = ["codex"]\n{extra}\n[presets]\n{presets}\n')


@contextmanager
def fake_discovery(installed: list[InstalledBundle]):
    yield installed


def _entry(name: str, hook: object) -> SimpleNamespace:
    return SimpleNamespace(name=name, value=f"fake:{name}", load=lambda: hook)


# --- post-sync hooks ---------------------------------------------------------


def test_post_sync_hooks_run_in_name_order_and_never_fail_the_sync(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[tuple[str, Path, list[str]]] = []

    def first(root: Path, result: dict) -> list[str]:
        seen.append(("a", root, [a["path"] for a in result["actions"]]))
        return ["first says hi"]

    def broken(root: Path, result: dict) -> list[str]:
        raise RuntimeError("boom")

    def silent(root: Path, result: dict) -> None:
        seen.append(("c", root, []))
        return None

    def wrong(root: Path, result: dict) -> object:
        return "not a list"

    entries = [
        _entry("c-silent", silent),
        _entry("b-broken", broken),
        _entry("a-first", first),
        _entry("d-wrong", wrong),
    ]
    monkeypatch.setattr(hooks.metadata, "entry_points", lambda group: entries if group == hooks.GROUP else [])

    result = sync_project(target, installed)
    assert [name for name, _, _ in seen] == ["a", "c"]
    assert seen[0][1] == target.resolve()
    assert RECEIPT_PATH in seen[0][2]
    assert [(notice.code, notice.message) for notice in result.notices] == [
        ("POST_SYNC_NOTICE", "first says hi"),
        ("POST_SYNC_HOOK_FAILED", "post-sync hook b-broken failed: boom"),
        (
            "POST_SYNC_HOOK_FAILED",
            "post-sync hook d-wrong failed: returned str, expected list[str | AdvisoryError]",
        ),
    ]
    assert result.notices[0].details == ("hook: a-first",)
    assert [notice["level"] for notice in result.to_dict()["notices"]] == ["NOTICE", "WARNING", "WARNING"]
    assert result.to_dict()["notices"][1]["advisory"]["mode"] == "CONTINUE"
    assert (target / RECEIPT_PATH).is_file()


def test_post_sync_hooks_do_not_run_on_dry_run_or_check(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    entries = [_entry("hook", lambda root, result: calls.append("ran") or ["x"])]
    monkeypatch.setattr(hooks.metadata, "entry_points", lambda group: entries)
    assert sync_project(target, installed, dry_run=True).to_dict()["notices"] == []
    assert calls == []
    monkeypatch.setattr(discovery, "discover_bundles", lambda: fake_discovery(installed))
    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", lambda: fake_discovery(installed))
    runner = CliRunner()
    checked = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"])
    assert checked.exit_code == 1 and calls == []
    synced = runner.invoke(cli, ["sync", "--workspace-root", str(target)])
    assert synced.exit_code == 0, synced.output
    assert calls == ["ran"] and "[NOTICE] (POST_SYNC_NOTICE) x\n[ACTION] NOTE — " in synced.stderr


def test_post_sync_hooks_may_return_coded_notices_and_reach_override_commands(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    coded = AdvisoryError("units need review", code="UNITS_STALE")  # an ERROR: a hook cannot fail the sync
    kept = AdvisoryError("units checked", code="UNITS_CHECKED", level=Level.NOTICE)
    entries = [_entry("coded", lambda root, result: [coded, kept, "plain"])]
    monkeypatch.setattr(hooks.metadata, "entry_points", lambda group: entries if group == hooks.GROUP else [])
    notices = sync_project(target, installed).notices
    assert [(notice.code, notice.level) for notice in notices] == [
        ("UNITS_STALE", Level.WARNING),
        ("UNITS_CHECKED", Level.NOTICE),
        ("POST_SYNC_NOTICE", Level.NOTICE),
    ]
    assert coded.level is Level.ERROR and notices[1] is kept
    change = create_override(target, installed, "team:guide")
    assert change.notices[1] is kept
    assert [notice["code"] for notice in change.to_dict()["notices"]] == [
        "UNITS_STALE",
        "UNITS_CHECKED",
        "POST_SYNC_NOTICE",
    ]


# --- override drift policy ---------------------------------------------------


def _drift(source: Path, installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    create_override(target, installed, "team:guide")
    (source / "guide.md").write_text("---\nname: guide\ndescription: Upstream guide.\n---\n# Guide v2\n")


def test_override_drift_warns_by_default(source: Path, installed: list[InstalledBundle], target: Path) -> None:
    _drift(source, installed, target)
    result = sync_project(target, installed).to_dict()
    assert [d["asset"] for d in result["drift"]] == ["guide"]


def test_override_drift_block_aborts_before_writes(
    source: Path, installed: list[InstalledBundle], target: Path
) -> None:
    _drift(source, installed, target)
    write_config(target, extra='override_drift = "block"')
    receipt = (target / RECEIPT_PATH).read_bytes()
    with pytest.raises(OverrideDriftError, match=r"override_drift = \"block\"\): team:guide$") as raised:
        sync_project(target, installed)
    assert raised.value.fix is not None and "`devkit override diff team:guide`" in raised.value.fix
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    assert not (target / JOURNAL).exists()


def test_override_drift_config_is_validated(installed: list[InstalledBundle], target: Path) -> None:
    write_config(target, extra='override_drift = "ignore"')
    with pytest.raises(ConfigError, match="override_drift must be one of"):
        sync_project(target, installed)


# --- orphans -----------------------------------------------------------------


def test_modified_file_removed_upstream_becomes_an_orphan(
    source: Path, installed: list[InstalledBundle], target: Path
) -> None:
    sync_project(target, installed)
    skill = target / ".agents/skills/review/SKILL.md"
    skill.write_text("# my review\n")
    # Upstream drops the skill asset entirely.
    (source / "bundle.toml").write_text("""schema = 1
name = "team"
version = "0.2.0"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
""")
    newer = [InstalledBundle("team-content", "0.2.0", load_bundle(source))]
    synced = sync_project(target, newer)
    result = synced.to_dict()
    # Only the edited projection is left behind; the untouched managed copy is removed as usual.
    (orphan,) = synced.notices
    assert (orphan.code, orphan.target_files) == ("ORPHAN_LEFT", (".agents/skills/review/SKILL.md",))
    assert (result["notices"][0]["level"], result["notices"][0]["advisory"]["mode"]) == ("WARNING", "CONTINUE")
    assert skill.read_text() == "# my review\n"
    assert not (target / ".devkit/managed/team/skills/review/SKILL.md").exists()
    files = json.loads((target / RECEIPT_PATH).read_text())["files"]
    assert not any(name.endswith("review/SKILL.md") for name in files)
    assert all(a["path"] != ".agents/skills/review/SKILL.md" for a in result["actions"])
    # Still desired and modified: abort, as before.
    (target / ".devkit/managed/team/guide.md").write_text("edited")
    with pytest.raises(ConflictError, match="user-modified deployment file"):
        sync_project(target, newer)


def test_orphan_alone_does_not_fail_check(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, installed)
    (target / ".devkit/managed/team/guide.md").write_text("edited")
    write_config(target, presets="")
    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", lambda: fake_discovery(installed))
    runner = CliRunner()
    first = runner.invoke(cli, ["sync", "--workspace-root", str(target)])
    assert first.exit_code == 0, first.output
    assert "[WARN]   (ORPHAN_LEFT) left modified file in place: .devkit/managed/team/guide.md" in first.stderr
    # Nothing left to sync: the orphan is reported, not pending.
    check = runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"])
    assert check.exit_code == 0, check.output
    assert json.loads(check.stdout)["actions"] == []
    # It is now an unmanaged file under the managed root.
    assert json.loads(check.stdout)["stray"] == [".devkit/managed/team/guide.md"]


# --- tool identity -----------------------------------------------------------


def test_tool_version_alone_is_no_change_and_is_recorded_with_the_next_write(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = sync_project(target, installed).to_dict()
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    assert receipt["tool"] == {"package": "devkit", "version": tool_identity().version}
    assert result["notices"] == []
    monkeypatch.setattr(sync_module, "tool_identity", lambda: ToolRecord("devkit", "9.9.9"))
    before = (target / RECEIPT_PATH).read_bytes()
    result = sync_project(target, installed).to_dict()
    # A different devkit version alone is not drift: no write, no notice, ``--check`` stays clean.
    assert result["actions"] == [] and result["notices"] == []
    assert (target / RECEIPT_PATH).read_bytes() == before
    result = sync_project(target, installed, agents=[]).to_dict()
    (notice,) = result["notices"]
    assert notice["code"] == "TOOL_VERSION_CHANGED" and notice["exit_code"] == 0
    assert notice["message"].startswith(f"devkit {receipt['tool']['version']} -> 9.9.9")
    assert json.loads((target / RECEIPT_PATH).read_text())["tool"]["version"] == "9.9.9"
    assert sync_project(target, installed, agents=[]).to_dict()["notices"] == []


def test_receipt_tool_field_is_validated(installed: list[InstalledBundle], target: Path) -> None:
    sync_project(target, installed)
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    receipt["tool"] = {"package": "devkit"}
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match="tool: missing keys"):
        sync_project(target, installed)


# --- status ------------------------------------------------------------------


def test_status_without_receipt(installed: list[InstalledBundle], target: Path) -> None:
    result = get_project_status(target, installed).to_dict()
    assert result["receipt"] is False and result["schema"] is None
    assert result["opted_out"] == [] and result["selection"] == {"agents": [], "presets": {}}
    assert result["files"]["counts"] == {"ok": 0, "missing": 0, "modified": 0, "mode-mismatch": 0}
    assert result["guidance_block"] == "missing" and result["seeded"] == [] and result["override_drift"] == []
    assert result["pending_journal"] is False and result["errors"] == []
    assert result["tool"] == {
        "running": {"package": "devkit", "version": tool_identity().version},
        "recorded": None,
        "match": None,
    }


def test_status_reports_every_dimension(
    source: Path, installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, installed)
    clean = get_project_status(target, installed).to_dict()
    assert clean["receipt"] is True and clean["schema"] == 1
    assert clean["selection"]["presets"] == {"team": ["all"]}
    assert clean["files"]["counts"] == {
        "ok": clean["files"]["counts"]["ok"],
        "missing": 0,
        "modified": 0,
        "mode-mismatch": 0,
    }
    assert clean["files"]["counts"]["ok"] > 0
    assert clean["override_drift"] == [] and clean["guidance_block"] == "ok"
    assert clean["seeded"] == [{"bundle": "team", "id": "scaffold", "path": "docs/scaffold.md", "present": True}]
    assert clean["pending_journal"] is False and clean["tool"]["match"] is True
    assert clean["errors"] == []
    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", lambda: fake_discovery(installed))
    assert CliRunner().invoke(cli, ["status", "-w", str(target)]).exit_code == 0

    (target / ".devkit/managed/team/guide.md").write_text("edited")
    (target / ".agents/skills/review/SKILL.md").unlink()
    (target / ".devkit/managed/team/bundle.toml").chmod(0o755)
    (target / "docs/scaffold.md").unlink()
    text = (target / AGENTS_FILE).read_text()
    (target / AGENTS_FILE).write_text(text.replace("## devkit", "## devkit (edited)"))
    (target / JOURNAL).parent.mkdir(parents=True, exist_ok=True)
    (target / JOURNAL).write_text("{}")
    monkeypatch.setattr(status_module, "tool_identity", lambda: ToolRecord("devkit", "9.9.9"))

    dirty = get_project_status(target, installed).to_dict()
    assert dirty["files"]["counts"]["modified"] == 1 and dirty["files"]["modified"] == [".devkit/managed/team/guide.md"]
    assert dirty["files"]["missing"] == [".agents/skills/review/SKILL.md"]
    assert dirty["files"]["mode-mismatch"] == [".devkit/managed/team/bundle.toml"]
    assert dirty["guidance_block"] == "modified"
    assert dirty["seeded"][0]["present"] is False
    assert dirty["pending_journal"] is True
    assert dirty["tool"]["match"] is False and dirty["tool"]["running"]["version"] == "9.9.9"
    problems = [(error["code"], error["exit_code"], error["advisory"]["target_files"]) for error in dirty["errors"]]
    assert problems == [
        ("NOT_SYNCHRONIZED", 1, [".agents/skills/review/SKILL.md"]),
        ("SYNC_CONFLICT", 1, [".devkit/managed/team/guide.md"]),
        ("SYNC_CONFLICT", 1, [".devkit/managed/team/bundle.toml"]),
        ("TRANSACTION_PENDING", 1, [".devkit/transient/sync-journal.json"]),
    ]
    result = CliRunner().invoke(cli, ["status", "-w", str(target)])
    assert result.exit_code == 1 and json.loads(result.stdout)["pending_journal"] is True
    assert "[ERROR]  (TRANSACTION_PENDING)" in result.stderr and "[FIX]    devkit sync" in result.stderr


def test_status_reports_override_drift_disabled_block_and_cli(
    source: Path, installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _drift(source, installed, target)
    assert get_project_status(target, installed).to_dict()["override_drift"] == [{"bundle": "team", "asset": "guide"}]
    write_config(target, extra="guidance_block = false")
    synced = sync_project(target, installed)
    (warning,) = [notice for notice in synced.notices if notice.code == "OVERRIDE_DRIFT"]
    assert (warning.level, warning.exit_code, warning.mode) == (Level.WARNING, ExitCode.OK, ActionMode.CONTINUE)
    assert warning.message == "upstream drift behind an override: team:guide"
    assert warning.fix is not None and "devkit override diff team:guide" in warning.fix
    assert get_project_status(target, installed).to_dict()["guidance_block"] == "disabled"
    write_config(target)
    (target / AGENTS_FILE).unlink(missing_ok=True)
    assert get_project_status(target, installed).to_dict()["guidance_block"] == "missing"
    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", lambda: fake_discovery(installed))
    result = CliRunner().invoke(cli, ["status", "--workspace-root", str(target)])
    assert result.exit_code == 1, result.output  # override drift is a problem to act on
    report = json.loads(result.stdout)
    assert report["guidance_block"] == "missing"
    (drift,) = report["errors"]
    assert (drift["code"], drift["exit_code"], drift["advisory"]["mode"]) == ("OVERRIDE_DRIFT", 1, "INTERACTION")
    assert "[ERROR]  (OVERRIDE_DRIFT) upstream changed behind overrides: team:guide" in result.stderr
    assert not (target / AGENTS_FILE).exists()  # status never writes
