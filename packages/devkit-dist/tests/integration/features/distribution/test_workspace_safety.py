"""Path safety, the project lock, the root guidance block, pruning and bundle source hygiene."""

from __future__ import annotations

import errno
import json
import os
import threading
from pathlib import Path

import pytest
from devkit_core.core import LockHeldError as CoreLockHeldError
from devkit_core.core import extensions as core_extensions
from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.errors import (
    BundleError,
    DistributionError,
    LockHeldError,
    RecoveryError,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection
from devkit_dist.features.distribution.services.installation import extensions, transaction
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.guidance_block import START
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.workspace import AGENTS_FILE, LOCK, project_path
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.sync import RecoverProject, sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, RECEIPT_PATH
from distsupport.distribution import instruction, write_bundle

MANIFEST = """schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
"""


@pytest.fixture
def item(tmp_path: Path) -> InstalledBundle:
    return write_bundle(
        tmp_path / "source", MANIFEST, {"guide.md": instruction("guide"), "skills/review/SKILL.md": "# Review\n"}
    )


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["claude-code"])
    return root


def _seeded_manifest(target: str) -> str:
    return f"""schema = 1
name = "seedy"
version = "0.1.0"
[[assets]]
id = "hook"
kind = "document"
seeded = true
source = "hook.sh"
target = "{target}"
"""


@pytest.mark.parametrize(
    "seed_target", [".GIT/hooks/pre-commit", ".Git/config", ".Claude/settings.json", ".DEVKIT/config.toml", "Agents.md"]
)
def test_reserved_seed_targets_are_case_insensitive(tmp_path: Path, seed_target: str) -> None:
    with pytest.raises(BundleError, match="may not be under"):
        write_bundle(tmp_path / "source", _seeded_manifest(seed_target), {"hook.sh": "#!/bin/sh\n"})


@pytest.mark.parametrize("name", [".GIT/hooks/pre-commit", ".Devkit/Config.toml", ".devkit/OVERRIDES/team/x.md"])
def test_transactions_never_write_reserved_paths_in_any_case(tmp_path: Path, name: str) -> None:
    with pytest.raises(UnsafeWorkspaceError, match="unsafe deployment path"):
        project_path(tmp_path, name)


def test_symlinked_agents_md_is_left_alone_when_the_block_is_off(item: InstalledBundle, target: Path) -> None:
    (target / "CLAUDE.md").write_text("# Project\n")
    (target / AGENTS_FILE).symlink_to("CLAUDE.md")
    with pytest.raises(UnsafeWorkspaceError, match="is a symlink") as raised:
        sync_project(target, [item])
    assert "guidance_block = false" in (raised.value.fix or "")
    (target / CONFIG_PATH).write_text("guidance_block = false\n" + (target / CONFIG_PATH).read_text())
    assert sync_project(target, [item]).to_dict()["actions"]
    assert (target / AGENTS_FILE).is_symlink() and (target / "CLAUDE.md").read_text() == "# Project\n"


def test_crlf_agents_md_keeps_one_block_and_its_line_endings(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_bytes(b"# Project\r\n")
    sync_project(target, [item])
    data = (target / AGENTS_FILE).read_bytes()
    assert data.count(START.encode()) == 1 and b"\n" not in data.replace(b"\r\n", b"")
    # A checkout that converts the file to LF (or back) is not an edit.
    (target / AGENTS_FILE).write_bytes(data.replace(b"\r\n", b"\n"))
    assert sync_project(target, [item]).to_dict()["actions"] == []
    (target / AGENTS_FILE).write_bytes(data)
    assert sync_project(target, [item]).to_dict()["actions"] == []
    assert (target / AGENTS_FILE).read_bytes().count(START.encode()) == 1


def test_marker_not_on_its_own_line_is_malformed(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_text(f"Intro {START} trailing\n")
    with pytest.raises(DistributionError, match="malformed guidance block"):
        sync_project(target, [item])


def test_receipt_paths_cannot_leave_the_project(item: InstalledBundle, target: Path, tmp_path: Path) -> None:
    sync_project(target, [item])
    (target / ".devkit/overrides/team").mkdir(parents=True)
    (tmp_path / "secret.md").write_text(instruction("secret"))
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    for asset in receipt["assets"]:
        if asset["id"] == "guide":
            asset["paths"] = [".devkit/overrides/team/../../../../secret.md"]
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=r"must not contain '\.\.'"):
        GetContext().execute(target, "team")


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda r: r["assets"][0].pop("paths"), "missing keys"),
        (lambda r: r["assets"].append("not an object"), "expected an object"),
        (lambda r: r["assets"][0].update(paths=["outside/file.md"]), "invalid asset path"),
    ],
)
def test_malformed_receipt_entries_are_receipt_errors(item: InstalledBundle, target: Path, mutate, match: str) -> None:
    sync_project(target, [item])
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    mutate(receipt)
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=match) as raised:
        GetContext().execute(target, "team")
    assert raised.value.code == "RECEIPT_INVALID"
    with pytest.raises(ReceiptError, match=match):
        read_receipt(target)


def test_readers_share_the_lock_and_writers_exclude_them(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [item])
    assert (target / LOCK).is_file()
    with transaction.project_lock(target, shared=True):
        assert GetContext().execute(target, "team").to_dict()["bundle"] == "team"
        with pytest.raises(LockHeldError, match="project lock"):
            sync_project(target, [item])
    monkeypatch.setattr(transaction, "READ_LOCK_TIMEOUT", 0.05)
    with transaction.project_lock(target), pytest.raises(LockHeldError, match="project lock"):
        GetContext().execute(target, "team")
    with transaction.project_lock(target), pytest.raises(CoreLockHeldError, match="project lock") as raised:
        GetContext().execute(target, "team")  # the core class catches it too
    assert raised.value.seconds == 0.05


@pytest.mark.parametrize("code", [errno.EROFS, errno.EACCES])
def test_a_reader_on_a_read_only_file_system_reads_without_the_lock(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch, code: int
) -> None:
    sync_project(target, [item])

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise OSError(code, os.strerror(code))

    monkeypatch.setattr(transaction, "file_lock", refuse)
    assert GetContext().execute(target, "team").to_dict()["bundle"] == "team"
    with pytest.raises(OSError) as raised, transaction.project_lock(target):
        pass  # a writer never proceeds without the lock
    assert raised.value.errno == code


def test_reader_waits_for_a_writer(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    held, released = threading.Event(), threading.Event()

    def hold() -> None:
        with transaction.project_lock(target):
            held.set()
            released.wait(5)

    writer = threading.Thread(target=hold)
    writer.start()
    assert held.wait(5)
    try:
        timer = threading.Timer(0.2, released.set)
        timer.start()
        assert GetContext().execute(target, "team").to_dict()["bundle"] == "team"
    finally:
        released.set()
        writer.join()


def test_post_sync_extensions_run_after_the_lock_is_released(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def hook(root: Path, result: dict) -> list[str]:
        return [f"hook read {GetContext().execute(root, 'team').to_dict()['bundle']}"]

    entry = type("Entry", (), {"name": "reader", "value": "x:reader", "load": staticmethod(lambda: hook)})()
    monkeypatch.setattr(
        core_extensions.metadata, "entry_points", lambda group: [entry] if group == extensions.GROUP else []
    )
    assert [notice.message for notice in sync_project(target, [item]).notices] == ["hook read team"]


def test_a_file_where_a_destination_directory_must_be_is_unsafe(item: InstalledBundle, target: Path) -> None:
    blocker = target / ".claude/skills/review"
    blocker.parent.mkdir(parents=True)
    blocker.write_text("a project file\n")
    for dry_run in (True, False):
        with pytest.raises(UnsafeWorkspaceError) as raised:
            sync_project(target, [item], dry_run=dry_run)
        error = raised.value
        assert error.code == "WORKSPACE_UNSAFE"
        assert error.target_files == (".claude/skills/review", ".claude/skills/review/SKILL.md")
        assert error.fix is not None and ".claude/skills/review" in error.fix
    assert blocker.read_text() == "a project file\n"
    assert read_receipt(target) is None and not (target / ".devkit/managed").exists()


def test_a_transaction_refuses_a_file_where_a_directory_must_be(tmp_path: Path) -> None:
    (tmp_path / "docs").write_text("a project file\n")
    with pytest.raises(UnsafeWorkspaceError, match="docs is not a directory"):
        transaction.apply_changes(tmp_path, {"docs/guide.md": Content(b"x", 0o644)})
    assert not (tmp_path / ".devkit").exists()


NOTES = 'schema = 1\nname = "team"\nversion = "0.1.0"\n[[assets]]\nid = "notes"\nkind = "document"\nsource = "notes"\n'
NOTES_FILE = ".devkit/managed/team/notes"


def test_a_managed_file_that_becomes_a_directory_upstream_is_replaced(tmp_path: Path, target: Path) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes": "file\n"})])
    assert (target / NOTES_FILE).is_file()
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes/SKILL.md": "directory\n"})
    planned = sync_project(target, [upgraded], dry_run=True).actions
    assert [(item.path, item.action) for item in planned][:2] == [
        (NOTES_FILE, "remove"),
        (f"{NOTES_FILE}/SKILL.md", "create"),
    ]
    sync_project(target, [upgraded])
    assert (target / NOTES_FILE / "SKILL.md").read_text() == "directory\n"
    assert sync_project(target, [upgraded]).actions == []


def test_a_rolled_back_file_to_directory_transition_restores_the_file(
    tmp_path: Path, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes": "file\n"})])
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes/SKILL.md": "directory\n"})
    write = transaction.atomic_write
    failed: list[str] = []

    def fail_on_receipt(root: Path, name: str, content: Content | None) -> None:
        if name == RECEIPT_PATH and not failed:
            failed.append(name)  # the commit's receipt write fails; the rollback's goes through
            raise OSError("disk full")
        write(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail_on_receipt)
    with pytest.raises(OSError, match="disk full"):
        sync_project(target, [upgraded])
    monkeypatch.undo()
    assert (target / NOTES_FILE).read_text() == "file\n"
    assert not (target / ".devkit/transient/sync-journal.json").exists()


def test_a_managed_directory_that_becomes_a_file_upstream_is_replaced(tmp_path: Path, target: Path) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes/SKILL.md": "directory\n"})])
    assert (target / NOTES_FILE / "SKILL.md").is_file()
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes": "file\n"})
    planned = sync_project(target, [upgraded], dry_run=True).actions  # `--check` plans the same way
    assert [(item.path, item.action) for item in planned][:2] == [
        (NOTES_FILE, "create"),
        (f"{NOTES_FILE}/SKILL.md", "remove"),
    ]
    assert (target / NOTES_FILE / "SKILL.md").read_text() == "directory\n"  # the dry run wrote nothing
    sync_project(target, [upgraded])
    assert (target / NOTES_FILE).read_text() == "file\n"
    assert sync_project(target, [upgraded]).actions == []


def test_a_managed_directory_holding_an_unowned_file_is_never_replaced_by_a_file(tmp_path: Path, target: Path) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes/SKILL.md": "directory\n"})])
    (target / NOTES_FILE / "mine.md").write_text("a project file\n")
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes": "file\n"})
    for dry_run in (True, False):
        with pytest.raises(UnsafeWorkspaceError, match="holds files devkit does not remove") as raised:
            sync_project(target, [upgraded], dry_run=dry_run)
        assert raised.value.code == "WORKSPACE_UNSAFE" and raised.value.target_files == (NOTES_FILE,)
    assert (target / NOTES_FILE / "mine.md").read_text() == "a project file\n"
    assert (target / NOTES_FILE / "SKILL.md").read_text() == "directory\n"
    assert not (target / ".devkit/transient/sync-journal.json").exists()


@pytest.mark.parametrize("stop", ["deleted", "emptied", "written"])
def test_an_interrupted_directory_to_file_transition_is_recovered(
    tmp_path: Path, target: Path, monkeypatch: pytest.MonkeyPatch, stop: str
) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes/SKILL.md": "directory\n"})])
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes": "file\n"})
    write, remove = transaction.atomic_write, transaction._remove_emptied

    def interrupt_write(root: Path, name: str, content: Content | None) -> None:
        write(root, name, content)
        if (stop, name) in {("deleted", f"{NOTES_FILE}/SKILL.md"), ("written", NOTES_FILE)}:
            raise SystemExit("simulated process interruption")

    def interrupt_removal(root: Path, name: str) -> None:
        remove(root, name)
        if stop == "emptied":
            raise SystemExit("simulated process interruption")

    monkeypatch.setattr(transaction, "atomic_write", interrupt_write)
    monkeypatch.setattr(transaction, "_remove_emptied", interrupt_removal)
    with pytest.raises(SystemExit):
        sync_project(target, [upgraded])
    monkeypatch.undo()
    assert RecoverProject().execute(target) > 0
    assert (target / NOTES_FILE / "SKILL.md").read_text() == "directory\n"
    assert not (target / ".devkit/transient/sync-journal.json").exists()
    sync_project(target, [upgraded])
    assert (target / NOTES_FILE).read_text() == "file\n"


def test_a_rolled_back_directory_to_file_transition_restores_the_directory(
    tmp_path: Path, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [write_bundle(tmp_path / "v1", NOTES, {"notes/SKILL.md": "directory\n"})])
    upgraded = write_bundle(tmp_path / "v2", NOTES, {"notes": "file\n"})
    write = transaction.atomic_write
    failed: list[str] = []

    def fail_on_receipt(root: Path, name: str, content: Content | None) -> None:
        if name == RECEIPT_PATH and not failed:
            failed.append(name)  # the commit's receipt write fails; the rollback's goes through
            raise OSError("disk full")
        write(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail_on_receipt)
    with pytest.raises(OSError, match="disk full"):
        sync_project(target, [upgraded])
    monkeypatch.undo()
    assert (target / NOTES_FILE / "SKILL.md").read_text() == "directory\n"
    assert not (target / ".devkit/transient/sync-journal.json").exists()


def test_a_project_file_deleted_in_the_same_change_set_still_blocks_a_directory(tmp_path: Path) -> None:
    (tmp_path / "docs").write_text("a project file\n")
    with pytest.raises(UnsafeWorkspaceError, match="docs is not a directory"):
        transaction.apply_changes(tmp_path, {"docs": None, "docs/guide.md": Content(b"x", 0o644)})
    assert (tmp_path / "docs").read_text() == "a project file\n"


def test_a_journal_from_an_earlier_devkit_is_refused_with_a_manual_rollback(target: Path) -> None:
    journal = target / ".devkit/transient/sync-journal.json"
    journal.parent.mkdir(parents=True, exist_ok=True)
    journal.write_text(json.dumps({"schema": 1, "changes": {}}))
    with pytest.raises(RecoveryError) as raised:
        transaction.recover_locked(target)
    error = raised.value
    assert error.code == "RECOVERY_BLOCKED" and "earlier devkit" in error.message
    assert error.fix == transaction.LEGACY_JOURNAL_FIX and "devkit recover" in transaction.LEGACY_JOURNAL_FIX
    # The manual rollback is what recovery does: every unedited file goes back to its `before`.
    assert "equals its base64 `before` or `after` content, write back the `before`" in transaction.LEGACY_JOURNAL_FIX
    assert journal.exists()


def test_removed_projections_leave_no_empty_directories(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    assert (target / ".claude/skills/review/SKILL.md").is_file()
    update_config(target, agents=[])
    sync_project(target, [item])
    assert not (target / ".claude/skills/review").exists()
    assert (target / ".claude/skills").is_dir()  # the owned prefix stays
    update_config(target, deselect=["team"])
    sync_project(target, [item])
    assert not (target / ".devkit/managed/team").exists()
    assert (target / ".devkit/transient").is_dir()


def test_editing_byproducts_are_not_bundle_content(tmp_path: Path) -> None:
    root = tmp_path / "source"
    item = write_bundle(
        root,
        MANIFEST,
        {
            "guide.md": instruction("guide"),
            "skills/review/SKILL.md": "# Review\n",
            "skills/review/.DS_Store": "finder",
            "skills/review/__pycache__/tool.cpython-312.pyc": "bytecode",
            "skills/review/stale.pyc": "bytecode",
        },
    )
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=["claude-code"])
    sync_project(target, [item])
    names = json.loads((target / RECEIPT_PATH).read_text())["files"]
    assert not any(".DS_Store" in name or "pycache" in name or name.endswith(".pyc") for name in names)


@pytest.mark.parametrize(
    ("files", "match"),
    [
        ({"guide.md": "# No frontmatter\n"}, "requires YAML frontmatter"),
        ({"guide.md": "---\nname: guide\n---\nBody\n"}, "nonempty description"),
        ({"guide.md": "---\nname: guide\nname: twice\ndescription: d\n---\n"}, "duplicate key"),
    ],
)
def test_instruction_headers_are_validated_at_load(tmp_path: Path, files: dict[str, str], match: str) -> None:
    manifest = 'schema = 1\nname = "team"\nversion = "0.1.0"\n[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "guide.md"\n'
    with pytest.raises(BundleError, match=match):
        write_bundle(tmp_path / "source", manifest, files)


def test_every_file_of_an_instruction_directory_needs_a_header(tmp_path: Path) -> None:
    manifest = (
        'schema = 1\nname = "team"\nversion = "0.1.0"\n[[assets]]\nid = "docs"\nkind = "instruction"\nsource = "docs"\n'
    )
    files = {"docs/a.md": instruction("a"), "docs/diagram.txt": "not an instruction\n"}
    with pytest.raises(BundleError, match=r"docs/diagram\.txt"):
        write_bundle(tmp_path / "source", manifest, files)


def test_variant_keys_must_be_supported_agents(tmp_path: Path) -> None:
    manifest = """schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
claude = "reviewer.md"
"""
    with pytest.raises(BundleError, match=r"unknown variants \['claude'\]"):
        write_bundle(tmp_path / "source", manifest, {"reviewer.md": "x\n"})


def test_rendered_description_keeps_line_breaks() -> None:
    contract = read_contract(
        b"---\nrole: r\ntitle: Reviewer\ndescription: |\n  First line.\n  Second line.\nhosts:\n"
        b"  claude-code: native\n  codex: unsupported\n  antigravity: unsupported\n---\nPrompt.\n",
        "test",
    )
    rendered = render_projection("claude-code", contract, ".devkit/managed/b/r.md")
    assert rendered is not None
    assert b'description: "Reviewer. First line.\\nSecond line."' in rendered


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_a_lock_file_that_is_not_a_regular_file_is_unsafe(target: Path, tmp_path: Path, kind: str) -> None:
    lock = target / LOCK
    lock.parent.mkdir(parents=True, exist_ok=True)
    elsewhere = tmp_path / "elsewhere"
    if kind == "symlink":
        lock.symlink_to(elsewhere)
    else:
        lock.mkdir()
    with pytest.raises(UnsafeWorkspaceError) as raised, transaction.project_lock(target):
        pass
    assert raised.value.code == "WORKSPACE_UNSAFE" and raised.value.target_files == (LOCK,)
    assert not elsewhere.exists()
