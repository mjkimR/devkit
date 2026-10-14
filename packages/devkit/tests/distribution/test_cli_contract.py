"""CLI contract: exit codes, the workspace root option, and configuration edits checked before syncing."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH
from devkit.distribution.errors import ConflictError
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.sync import sync_project
from devkit.distribution.installation.transaction import project_lock
from devkit.distribution.installation.workspace import DEPLOYED
from testsupport.distribution import cli, instruction, write_bundle

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
    (target / CONFIG_PATH).symlink_to(shared)
    result = _invoke("add", "team", "-w", str(target))
    assert result.exit_code == 2
    assert "config must be a regular file" in result.output
    assert not (target / RECEIPT_PATH).exists() and not (target / ".devkit/managed").exists()
    assert shared.read_text() == "schema = 1\n"


def test_sync_check_exit_codes(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    needed = _invoke("sync", "--check", "-w", str(target))
    assert needed.exit_code == int(ExitCode.FINDINGS)  # synchronization needed: a result, not an error
    assert needed.stdout.startswith("[SYNC: create=") and "[CHANGE: create " in needed.stdout
    assert not needed.stderr.startswith("[ERROR]")
    as_json = _invoke("sync", "--check", "--format", "json", "-w", str(target))
    assert as_json.exit_code == int(ExitCode.FINDINGS) and json.loads(as_json.stdout)["actions"]
    assert _invoke("sync", "-w", str(target)).exit_code == 0
    in_sync = _invoke("sync", "--check", "-w", str(target))
    # Nothing to write: two lines, not the deployed state again.
    assert in_sync.exit_code == 0 and in_sync.stdout == (
        "[SYNC: create=0 update=0 remove=0 seed=0 dry_run=yes]\n[OK: the workspace matches the selection]\n"
    )
    (target / ".devkit/managed/team/guide.md").write_text("edited")
    failed = _invoke("sync", "--check", "-w", str(target))
    assert failed.exit_code == 2 and "user-modified" in failed.output


def test_errors_exit_2_on_every_command(item: InstalledBundle, target: Path) -> None:
    assert _invoke("get-context", "team", "-w", str(target)).exit_code == 2
    assert _invoke("override", "accept", "team:guide", "-w", str(target)).exit_code == 2
    assert _invoke("remove", "team", "-w", str(target)).exit_code == 2


def test_an_error_is_one_json_document_on_stdout_and_nothing_on_stderr(item: InstalledBundle, target: Path) -> None:
    result = _invoke("get-context", "team", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["exit_code"], error["advisory"]["mode"]) == ("NOT_SYNCHRONIZED", 2, "AUTO")
    assert error["advisory"]["fix"] == "devkit sync"
    assert error["advisory"]["action"].startswith("AUTO — Run the [FIX] command once")
    assert result.stderr == ""  # one channel: the JSON document carries the directive


@pytest.mark.parametrize(
    ("args", "code", "mode"),
    [
        (("override", "create", "team", "-w", "{target}"), "ARGUMENT_INVALID", "INPUT_ERROR"),
        (("add", "missing", "--format", "json", "-w", "{target}"), "SELECTION_INVALID", "INPUT_ERROR"),
        (("remove", "team", "--format", "json", "-w", "{target}"), "SELECTION_INVALID", "INPUT_ERROR"),
    ],
)
def test_error_codes_reach_the_cli(
    item: InstalledBundle, target: Path, args: tuple[str, ...], code: str, mode: str
) -> None:
    result = _invoke(*(arg.format(target=target) for arg in args))
    assert result.exit_code == int(ExitCode.ERROR), result.output
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == (code, mode)


@pytest.mark.parametrize(
    "args",
    [
        ("sync", "--agent", "codex", "--no-agents", "--format", "json", "-w", "{target}"),
        ("add", "Bad Slug!", "--format", "json", "-w", "{target}"),
        ("sync", "--preset", "team:Bad", "--format", "json", "-w", "{target}"),
        ("status", "-w", "{target}/missing"),
    ],
)
def test_argument_errors_are_one_json_document_and_exit_2(
    item: InstalledBundle, target: Path, args: tuple[str, ...]
) -> None:
    result = _invoke(*(arg.format(target=target) for arg in args))
    assert result.exit_code == int(ExitCode.ERROR), result.output
    error = json.loads(result.stdout)["error"]  # exactly one JSON document on stdout
    assert (error["code"], error["advisory"]["mode"]) == ("ARGUMENT_INVALID", "INPUT_ERROR")
    assert result.stderr == ""


def test_syntax_errors_stay_click_usage_errors(item: InstalledBundle) -> None:
    result = _invoke("sync", "--no-such-flag")
    assert result.exit_code == 2 and result.stdout == ""


def test_every_json_command_prints_one_object(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    assert _invoke("sync", "-w", str(target)).exit_code == 0
    for args in (("list",), ("status",), ("override", "list"), ("get-context", "team"), ("recover",)):
        result = _invoke(*args, "-w", str(target))
        assert result.exit_code == 0, (args, result.output)
        assert isinstance(json.loads(result.stdout), dict), args
    assert json.loads(_invoke("override", "list", "-w", str(target)).stdout) == {"overrides": []}


def test_a_held_lock_defers_and_exits_2(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    with project_lock(target):
        result = _invoke("sync", "--format", "json", "-w", str(target))
        as_text = _invoke("sync", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == ("LOCK_HELD", "DEFER")
    assert error["advisory"]["retry_after"] == "the running devkit command finishes"
    assert as_text.exit_code == int(ExitCode.ERROR) and as_text.stdout == ""
    assert "[WHEN]   Not before: the running devkit command finishes" in as_text.stderr


def test_unexpected_errors_are_maintenance_and_exit_2(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("devkit.distribution.cli.get_project_status", explode)
    result = _invoke("status", "-w", str(target))
    assert result.exit_code == int(ExitCode.ERROR)
    assert json.loads(result.stdout)["error"]["advisory"]["action"].startswith("MAINTENANCE — ")


def test_workspace_root_defaults_to_the_project_root(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    nested = target / "src/module"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert _invoke("sync").exit_code == 0
    assert (target / RECEIPT_PATH).is_file() and not (nested / ".devkit").exists()
    context = _invoke("get-context", "team")
    assert context.exit_code == 0, context.output
    assert json.loads(context.output)["instructions"][0]["path"] == str(
        (target / ".devkit/managed/team/guide.md").resolve()
    )


def test_dry_run_validates_but_never_saves(item: InstalledBundle, target: Path) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    before = (target / CONFIG_PATH).read_text()
    result = _invoke("remove", "team", "--dry-run", "-w", str(target))
    assert result.exit_code == 0, result.output
    assert (target / CONFIG_PATH).read_text() == before
    assert _invoke("remove", "missing", "--dry-run", "-w", str(target)).exit_code == 2


def test_selection_edits_preserve_inline_tables_and_comments(target: Path) -> None:
    (target / CONFIG_PATH).write_text(
        'schema = 1\n# selected bundles\npresets = { team = "all", other = "core" }  # inline\n'
    )
    update_config(target, presets={"extra": ["a", "b"]}, deselect=["other"])
    text = (target / CONFIG_PATH).read_text()
    assert "# selected bundles" in text and "# inline" in text
    assert 'team = "all"' in text and "other" not in text and 'extra = ["a", "b"]' in text
    update_config(target, deselect=["team", "extra"])
    assert "team" not in (target / CONFIG_PATH).read_text()


def test_status_with_problems_exits_one_whatever_their_own_codes(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A status report ran: its problems exit 1 even when a problem's own exit code is 2.
    from types import SimpleNamespace

    from devkit.core.errors import ConfigError

    problem = ConfigError("broken config")
    assert problem.exit_code == ExitCode.ERROR
    report = SimpleNamespace(errors=(problem,), notices=(), to_dict=lambda: {"errors": [problem.to_dict()]})
    monkeypatch.setattr("devkit.distribution.cli.get_project_status", lambda *args, **kwargs: report)
    result = _invoke("status", "-w", str(target))
    assert result.exit_code == int(ExitCode.FINDINGS)
    assert json.loads(result.stdout)["errors"][0]["code"] == "CONFIG_INVALID"
    assert result.stderr == ""


def test_sync_locked_restores_recorded_files_and_never_changes_committed_ones(
    item: InstalledBundle, target: Path
) -> None:
    update_config(target, presets={"team": ["all"]}, agents=[])
    fresh = _invoke("sync", "--locked", "-w", str(target))  # no receipt yet: nothing to restore from
    assert fresh.exit_code == int(ExitCode.FINDINGS) and fresh.stdout == ""  # a refusal: the error is the output
    assert fresh.stderr.startswith("[ERROR]  (RECEIPT_STALE) there is no committed receipt to restore from;")
    assert "[ACTION] INTERACTION" in fresh.stderr and "[FIX]    devkit sync, then commit" in fresh.stderr
    assert "[DETAIL] would create .devkit/managed/team/guide.md" in fresh.stderr
    assert not (target / RECEIPT_PATH).exists() and not (target / ".devkit/managed").exists()
    assert _invoke("sync", "-w", str(target)).exit_code == 0

    # A fresh clone: the ignored managed copy is missing; the receipt (from another devkit version) is kept as is.
    receipt = target / RECEIPT_PATH
    data = json.loads(receipt.read_text())
    data["tool"]["version"] = "0.0.0-other"
    receipt.write_text(json.dumps(data, indent=2) + "\n")
    committed = receipt.read_bytes()
    managed = target / ".devkit/managed/team/guide.md"
    managed.unlink()
    restored = _invoke("sync", "--locked", "-w", str(target))
    assert restored.exit_code == 0, restored.output
    assert restored.stdout == (
        "[SYNC: create=1 update=0 remove=0 seed=0 dry_run=no]\n[CHANGE: create .devkit/managed/team/guide.md]\n"
    )
    assert managed.is_file() and receipt.read_bytes() == committed
    assert _invoke("sync", "--locked", "-w", str(target)).stdout.endswith("[OK: the workspace matches the selection]\n")

    # The bundle changed upstream: the committed receipt is stale, so nothing is written.
    (item.bundle.root / "guide.md").write_text(instruction("guide", "Body v2.\n"))
    managed.unlink()
    stale = _invoke("sync", "--locked", "--format", "json", "-w", str(target))
    assert stale.exit_code == int(ExitCode.FINDINGS)
    error = json.loads(stale.stdout)["error"]
    assert (error["code"], error["level"], error["exit_code"]) == ("RECEIPT_STALE", "ERROR", 1)
    assert error["message"].startswith("the installed bundles no longer match the committed receipt;")
    # Only committed state is a target; the ignored managed copy is a planned write in the details.
    assert error["advisory"]["target_files"] == [RECEIPT_PATH]
    assert error["advisory"]["details"] == ["would create .devkit/managed/team/guide.md"]
    assert not managed.exists() and receipt.read_bytes() == committed

    # The guidance block is committed state too.
    (item.bundle.root / "guide.md").write_text(instruction("guide"))
    assert _invoke("sync", "-w", str(target)).exit_code == 0
    (target / "AGENTS.md").unlink()
    block = _invoke("sync", "--locked", "-w", str(target))
    assert block.exit_code == int(ExitCode.FINDINGS)
    assert block.stderr.startswith("[ERROR]  (RECEIPT_STALE) committed files no longer match the receipt;")
    assert "[TARGET] AGENTS.md" in block.stderr and "[DETAIL] would create AGENTS.md" in block.stderr
    assert not (target / "AGENTS.md").exists()


def test_sync_locked_brings_stale_ignored_copies_to_a_pulled_receipt(tmp_path: Path, target: Path) -> None:
    # Another clone committed the receipt for v2; this clone's ignored copies are still v1, as its last sync left them.
    two_assets = MANIFEST + '[[assets]]\nid = "extra"\nkind = "instruction"\nsource = "extra.md"\n'
    source = tmp_path / "source"
    v1 = write_bundle(source, two_assets, {"guide.md": instruction("guide"), "extra.md": instruction("extra")})
    update_config(target, presets={"team": ["all"]}, agents=[])
    sync_project(target, [v1])
    guide, extra = target / ".devkit/managed/team/guide.md", target / ".devkit/managed/team/extra.md"
    local = {path: path.read_bytes() for path in (guide, extra, target / DEPLOYED)}
    v2 = write_bundle(source, MANIFEST, {"guide.md": instruction("guide", "Body v2.\n")})
    sync_project(target, [v2])
    committed = (target / RECEIPT_PATH).read_bytes()
    for path, data in local.items():
        path.write_bytes(data)

    result = sync_project(target, [v2], locked=True)
    assert [(item.path, item.action) for item in result.actions] == [
        (".devkit/managed/team/extra.md", "remove"),
        (".devkit/managed/team/guide.md", "update"),
    ]
    assert guide.read_text() == instruction("guide", "Body v2.\n") and not extra.exists()
    assert (target / RECEIPT_PATH).read_bytes() == committed
    assert sync_project(target, [v2], dry_run=True).actions == []

    # A hand edit of a stale copy is still a conflict, never overwritten.
    for path, data in local.items():
        path.write_bytes(data)
    guide.write_text("edited")
    with pytest.raises(ConflictError):
        sync_project(target, [v2], locked=True)
    assert guide.read_text() == "edited" and (target / RECEIPT_PATH).read_bytes() == committed


def test_sync_dry_run_and_check_take_the_shared_lock(item: InstalledBundle, target: Path, tmp_path: Path) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    checked = _invoke("sync", "--check", "-w", str(bare))
    # A project never synced needs a sync: the check exits 1 and names the receipt it would create.
    assert checked.exit_code == 1, checked.output
    assert "[CHANGE: create .devkit/installation.json]" in checked.stdout
    assert _invoke("sync", "--dry-run", "-w", str(bare)).exit_code == 0
    assert not (bare / ".devkit").exists()  # a read-only check never creates devkit state

    update_config(target, presets={"team": ["all"]}, agents=[])
    assert _invoke("sync", "-w", str(target)).exit_code == 0
    with project_lock(target, shared=True):  # another reader: concurrent checks never fail with LOCK_HELD
        assert _invoke("sync", "--check", "-w", str(target)).exit_code == 0
        assert _invoke("add", "team", "--dry-run", "-w", str(target)).exit_code == 0
        written = _invoke("sync", "-w", str(target))
        assert written.exit_code == 2 and "LOCK_HELD" in written.output


@pytest.mark.parametrize("flag", ["--check", "--dry-run", "--no-save", "--no-agents", "--preset=team"])
def test_sync_locked_takes_no_other_mode_or_selection(item: InstalledBundle, target: Path, flag: str) -> None:
    result = _invoke("sync", "--locked", flag, "-w", str(target))
    assert result.exit_code == 2 and "--locked cannot be combined with" in result.output
    assert not (target / RECEIPT_PATH).exists()


def test_a_receipt_stale_refusal_lists_at_most_twenty_planned_writes() -> None:
    from types import SimpleNamespace

    from devkit.distribution.installation.results import Action
    from devkit.distribution.installation.sync import _receipt_stale

    actions = [Action(f".devkit/managed/team/{index:02}.md", "create") for index in range(23)]
    error = _receipt_stale(None, SimpleNamespace(file_records={}), actions, {})  # type: ignore[arg-type]
    assert error.code == "RECEIPT_STALE" and error.exit_code == ExitCode.FINDINGS
    assert len(error.details) == 21 and error.details[-1].startswith("and 3 more")
    assert error.target_files[0] == RECEIPT_PATH
