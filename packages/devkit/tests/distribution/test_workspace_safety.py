"""Path safety, the project lock, the root guidance block, pruning and bundle source hygiene."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest
from devkit.core.errors import ReceiptError
from devkit.distribution.bundles import build_bundle, load_bundle
from devkit.distribution.bundles.subagents import read_contract, render
from devkit.distribution.errors import BundleError, DistributionError, LockHeldError, UnsafeWorkspaceError
from devkit.distribution.installation import hooks, transaction
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.guidance_block import START
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.sync import sync_project
from devkit.distribution.installation.workspace import AGENTS_FILE, CONFIG, LOCK, RECEIPT, project_path
from testsupport.distribution import instruction, write_bundle

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
    with pytest.raises(UnsafeWorkspaceError, match="guidance_block = false"):
        sync_project(target, [item])
    (target / CONFIG).write_text("guidance_block = false\n" + (target / CONFIG).read_text())
    assert sync_project(target, [item])["actions"]
    assert (target / AGENTS_FILE).is_symlink() and (target / "CLAUDE.md").read_text() == "# Project\n"


def test_crlf_agents_md_keeps_one_block_and_its_line_endings(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_bytes(b"# Project\r\n")
    sync_project(target, [item])
    data = (target / AGENTS_FILE).read_bytes()
    assert data.count(START.encode()) == 1 and b"\n" not in data.replace(b"\r\n", b"")
    # A checkout that converts the file to LF (or back) is not an edit.
    (target / AGENTS_FILE).write_bytes(data.replace(b"\r\n", b"\n"))
    assert sync_project(target, [item])["actions"] == []
    (target / AGENTS_FILE).write_bytes(data)
    assert sync_project(target, [item])["actions"] == []
    assert (target / AGENTS_FILE).read_bytes().count(START.encode()) == 1


def test_marker_not_on_its_own_line_is_malformed(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_text(f"Intro {START} trailing\n")
    with pytest.raises(DistributionError, match="malformed guidance block"):
        sync_project(target, [item])


def test_receipt_paths_cannot_leave_the_project(item: InstalledBundle, target: Path, tmp_path: Path) -> None:
    sync_project(target, [item])
    (target / ".devkit/overrides/team").mkdir(parents=True)
    (tmp_path / "secret.md").write_text(instruction("secret"))
    receipt = json.loads((target / RECEIPT).read_text())
    for asset in receipt["assets"]:
        if asset["id"] == "guide":
            asset["paths"] = [".devkit/overrides/team/../../../../secret.md"]
    (target / RECEIPT).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=r"must not contain '\.\.'"):
        get_context(target, "team")


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
    receipt = json.loads((target / RECEIPT).read_text())
    mutate(receipt)
    (target / RECEIPT).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=match) as raised:
        get_context(target, "team")
    assert raised.value.code == "RECEIPT_INVALID"
    with pytest.raises(ReceiptError, match=match):
        read_receipt(target)


def test_readers_share_the_lock_and_writers_exclude_them(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [item])
    assert (target / LOCK).is_file()
    with transaction.project_lock(target, shared=True):
        assert get_context(target, "team")["bundle"] == "team"
        with pytest.raises(LockHeldError, match="project lock"):
            sync_project(target, [item])
    monkeypatch.setattr(transaction, "READ_LOCK_TIMEOUT", 0.05)
    with transaction.project_lock(target), pytest.raises(LockHeldError, match="project lock"):
        get_context(target, "team")


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
        assert get_context(target, "team")["bundle"] == "team"
    finally:
        released.set()
        writer.join()


def test_post_sync_hooks_run_after_the_lock_is_released(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def hook(root: Path, result: dict) -> list[str]:
        return [f"hook read {get_context(root, 'team')['bundle']}"]

    entry = type("Entry", (), {"name": "reader", "value": "x:reader", "load": staticmethod(lambda: hook)})()
    monkeypatch.setattr(hooks.metadata, "entry_points", lambda group: [entry] if group == hooks.GROUP else [])
    assert sync_project(target, [item])["notices"] == ["hook read team"]


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
    names = json.loads((target / RECEIPT).read_text())["files"]
    assert not any(".DS_Store" in name or "pycache" in name or name.endswith(".pyc") for name in names)
    result = build_bundle(load_bundle(root), tmp_path / "out.zip")
    assert result["files"] == 4  # bundle.toml, guide.md, SKILL.md, inventory.json


def test_failed_build_leaves_no_partial_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    item = write_bundle(
        tmp_path / "source", MANIFEST, {"guide.md": instruction("guide"), "skills/review/SKILL.md": "x"}
    )
    output = tmp_path / "out.zip"

    def explode(*args: object, **kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("zipfile.ZipFile.writestr", explode)
    with pytest.raises(OSError, match="disk full"):
        build_bundle(item.bundle, output)
    assert not output.exists()


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
        b"  claude-code: native\n---\nPrompt.\n",
        "test",
    )
    rendered = render("claude-code", contract, ".devkit/managed/b/r.md")
    assert rendered is not None
    assert b'description: "Reviewer. First line.\\nSecond line."' in rendered
