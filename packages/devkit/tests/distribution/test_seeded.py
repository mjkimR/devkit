from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.core.errors import ReceiptError
from devkit.core.receipt import RECEIPT_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.content import Content
from devkit.distribution.errors import BundleError, ConflictError, UnsafeWorkspaceError
from devkit.distribution.installation import transaction
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.plan import plan_bundle
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.sync import recover_project, sync_project
from devkit.distribution.installation.workspace import JOURNAL
from testsupport.distribution import cli

MANIFEST = """schema = 1
name = "sdd"
version = "0.1.0"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[[assets]]
id = "docs-readme"
kind = "document"
seeded = true
source = "seed/README.md"
target = "docs/README.md"
[[assets]]
id = "docs-tree"
kind = "document"
seeded = true
source = "seed/tree"
target = "docs/spec"
[[assets]]
id = "reference"
kind = "document"
source = "reference.md"
[presets.guide-only]
assets = ["guide"]
"""


def write_source(root: Path, manifest: str = MANIFEST) -> Path:
    (root / "seed/tree/stories").mkdir(parents=True)
    (root / "guide.md").write_text("---\nname: guide\ndescription: Guide.\n---\n# Guide\n")
    (root / "reference.md").write_text("# Reference\n")
    (root / "seed/README.md").write_text("# Docs\n")
    (root / "seed/tree/glossary.md").write_text("# Glossary\n")
    (root / "seed/tree/stories/README.md").write_text("# Stories\n")
    script = root / "seed/tree/check.sh"
    script.write_text("#!/bin/sh\n")
    script.chmod(0o755)
    (root / "bundle.toml").write_text(manifest)
    return root


@pytest.fixture
def installed(tmp_path: Path) -> list[InstalledBundle]:
    return [InstalledBundle("sdd-content", "0.1.0", load_bundle(write_source(tmp_path / "source")))]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"sdd": ["all"]}, agents=["codex"])
    return root


def manifest_with(asset: str) -> str:
    return f"""schema = 1
name = "sdd"
version = "0.1.0"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
{asset}
"""


@pytest.mark.parametrize(
    ("asset", "message"),
    [
        (
            '[[assets]]\nid = "x"\nkind = "instruction"\nseeded = true\nsource = "guide.md"\ntarget = "a.md"',
            "only document",
        ),
        ('[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"', "target is required"),
        ('[[assets]]\nid = "x"\nkind = "document"\nsource = "reference.md"\ntarget = "a.md"', "target is required"),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = "yes"\nsource = "reference.md"\ntarget = "a.md"',
            "boolean",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\ntarget = "a.md"\n[assets.variants]\ncodex = "reference.md"',
            "single source",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = "../a.md"',
            "unsafe",
        ),
        ('[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = "/a.md"', "unsafe"),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = "docs//a.md"',
            "unsafe",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = ".devkit/a.md"',
            "may not",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = ".git/hooks/x"',
            "may not",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = ".claude/a.md"',
            "may not",
        ),
        (
            '[[assets]]\nid = "x"\nkind = "document"\nseeded = true\nsource = "reference.md"\ntarget = "AGENTS.md"',
            "may not",
        ),
    ],
)
def test_manifest_rejects_invalid_seeded_assets(tmp_path: Path, asset: str, message: str) -> None:
    root = write_source(tmp_path / "source", manifest_with(asset))
    with pytest.raises(BundleError, match=message):
        load_bundle(root)


def test_manifest_accepts_seeded_document(installed: list[InstalledBundle]) -> None:
    by_id = {asset.id: asset for asset in installed[0].bundle.assets}
    assert (by_id["docs-readme"].seeded, by_id["docs-readme"].target) == (True, "docs/README.md")
    assert (by_id["reference"].seeded, by_id["reference"].target) == (False, None)
    plan = plan_bundle(installed[0].bundle).to_dict()
    assert [item["destination"] for item in plan["seeded"]] == [
        "docs/README.md",
        "docs/spec/check.sh",
        "docs/spec/glossary.md",
        "docs/spec/stories/README.md",
    ]
    assert all(not item["destination"].startswith("docs/") for item in plan["files"])
    assert any(item["destination"] == ".devkit/managed/sdd/reference.md" for item in plan["files"])


def test_seeded_files_are_written_once_and_then_project_owned(installed: list[InstalledBundle], target: Path) -> None:
    first = sync_project(target, installed).to_dict()
    seeds = {a["path"] for a in first["actions"] if a["action"] == "seed"}
    assert seeds == {"docs/README.md", "docs/spec/check.sh", "docs/spec/glossary.md", "docs/spec/stories/README.md"}
    assert (target / "docs/README.md").read_text() == "# Docs\n"
    assert (target / "docs/spec/check.sh").stat().st_mode & 0o777 == 0o755
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    assert not any(name.startswith("docs/") for name in receipt["files"])
    assert ".devkit/managed/sdd/reference.md" in receipt["files"]
    assert receipt["seeded"] == [
        {"bundle": "sdd", "id": "docs-readme", "path": "docs/README.md"},
        {"bundle": "sdd", "id": "docs-tree", "path": "docs/spec/check.sh"},
        {"bundle": "sdd", "id": "docs-tree", "path": "docs/spec/glossary.md"},
        {"bundle": "sdd", "id": "docs-tree", "path": "docs/spec/stories/README.md"},
    ]
    seeded_asset = next(a for a in receipt["assets"] if a["id"] == "docs-tree")
    assert seeded_asset["paths"] == [] and len(seeded_asset["seeded"]) == 3
    receipt_bytes = (target / RECEIPT_PATH).read_bytes()

    # Second sync: nothing to do, receipt bytes preserved.
    assert sync_project(target, installed).to_dict()["actions"] == []
    assert (target / RECEIPT_PATH).read_bytes() == receipt_bytes

    # A hand edit survives; an upstream change does nothing.
    (target / "docs/README.md").write_text("# My docs\n")
    (installed[0].bundle.root / "seed/README.md").write_text("# Upstream v2\n")
    newer = [InstalledBundle("sdd-content", "0.2.0", load_bundle(installed[0].bundle.root))]
    result = sync_project(target, newer).to_dict()
    assert not any(a["path"].startswith("docs/") for a in result["actions"])
    assert (target / "docs/README.md").read_text() == "# My docs\n"

    # A deleted seeded file is seeded again (the asset is still selected).
    (target / "docs/spec/glossary.md").unlink()
    assert sync_project(target, newer).to_dict()["actions"] == [{"path": "docs/spec/glossary.md", "action": "seed"}]

    # Deselecting leaves every seeded file in place and drops the record.
    sync_project(target, [], deselect=["sdd"])
    assert (target / "docs/README.md").read_text() == "# My docs\n"
    assert (target / "docs/spec/stories/README.md").exists()
    assert "seeded" not in json.loads((target / RECEIPT_PATH).read_text())
    assert not (target / ".devkit/managed/sdd/reference.md").exists()


def test_existing_target_is_not_a_collision(installed: list[InstalledBundle], target: Path) -> None:
    (target / "docs").mkdir()
    (target / "docs/README.md").write_text("# Existing\n")
    result = sync_project(target, installed).to_dict()
    assert "docs/README.md" not in {a["path"] for a in result["actions"]}
    assert (target / "docs/README.md").read_text() == "# Existing\n"
    assert any(entry["path"] == "docs/README.md" for entry in json.loads((target / RECEIPT_PATH).read_text())["seeded"])


def test_dry_run_and_check_list_pending_seeds_without_writing(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    planned = sync_project(target, installed, dry_run=True).to_dict()
    assert {"path": "docs/README.md", "action": "seed"} in planned["actions"]
    assert not (target / "docs").exists()
    assert not (target / RECEIPT_PATH).exists()

    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    runner = CliRunner()
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"]).exit_code == 1
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target)]).exit_code == 0
    (target / "docs/README.md").write_text("edited\n")
    assert runner.invoke(cli, ["sync", "--workspace-root", str(target), "--check"]).exit_code == 0
    listed = json.loads(runner.invoke(cli, ["list", "--workspace-root", str(target)]).output)
    assert {"bundle": "sdd", "id": "docs-readme", "path": "docs/README.md"} in listed["seeded"]


def test_seeded_target_collision_between_bundles(tmp_path: Path, target: Path) -> None:
    first = write_source(tmp_path / "a")
    second = write_source(
        tmp_path / "b",
        """schema = 1
name = "other"
version = "0.1.0"
[[assets]]
id = "readme"
kind = "document"
seeded = true
source = "seed/README.md"
target = "docs/README.md"
""",
    )
    installed = [
        InstalledBundle("other-content", "0.1.0", load_bundle(second)),
        InstalledBundle("sdd-content", "0.1.0", load_bundle(first)),
    ]
    update_config(target, presets={"sdd": ["all"], "other": ["all"]})
    with pytest.raises(ConflictError, match=r"seeded target collision: docs/README\.md"):
        sync_project(target, installed)
    assert not (target / "docs").exists()


def test_seeded_target_blocked_by_directory_or_symlink(installed: list[InstalledBundle], target: Path) -> None:
    (target / "docs/README.md").mkdir(parents=True)
    with pytest.raises(UnsafeWorkspaceError, match=r"nonregular deployment path: docs/README\.md"):
        sync_project(target, installed)
    (target / "docs/README.md").rmdir()
    (target / "elsewhere.md").write_text("x\n")
    (target / "docs/README.md").symlink_to(target / "elsewhere.md")
    with pytest.raises(UnsafeWorkspaceError, match=r"deployment symlink: docs/README\.md"):
        sync_project(target, installed)
    assert not (target / RECEIPT_PATH).exists()


def test_seed_writes_are_journaled_and_rolled_back(
    installed: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    assert not (target / "docs/README.md").exists()
    assert not (target / "docs/spec/glossary.md").exists()
    assert not (target / JOURNAL).exists()
    monkeypatch.setattr(transaction, "atomic_write", original)
    assert recover_project(target) == 0
    sync_project(target, installed)
    assert (target / "docs/README.md").exists()


def test_seeded_document_is_not_bundle_context(installed: list[InstalledBundle], target: Path) -> None:
    from devkit.distribution.installation.context import get_context

    sync_project(target, installed)
    context = get_context(target, "sdd").to_dict()
    assert [item["path"].rsplit("/", 1)[-1] for item in context["instructions"]] == ["guide.md"]


@pytest.mark.parametrize(
    "entry",
    [
        "x",
        {"bundle": "sdd", "id": "docs-readme"},
        {"bundle": "Bad", "id": "docs-readme", "path": "docs/README.md"},
        {"bundle": "sdd", "id": "docs-readme", "path": "../README.md"},
        {"bundle": "sdd", "id": "docs-readme", "path": ".devkit/managed/x"},
    ],
)
def test_receipt_rejects_invalid_seeded_records(installed: list[InstalledBundle], target: Path, entry: object) -> None:
    sync_project(target, installed)
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    receipt["seeded"] = [entry]
    (target / RECEIPT_PATH).write_text(json.dumps(receipt))
    with pytest.raises(ReceiptError, match=r"seeded|may not"):
        read_receipt(target)
