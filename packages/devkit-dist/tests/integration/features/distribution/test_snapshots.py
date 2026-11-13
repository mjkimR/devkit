"""Real source/consumer files prove snapshot ownership, provenance and refresh safety."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from devkit_core.base.errors import ArgumentError
from devkit_dist.features.distribution.models.snapshots import (
    SnapshotConflictError,
    SnapshotInvalidError,
    SnapshotUnsupportedError,
    SnapshotWriteError,
)
from devkit_dist.features.distribution.repositories.snapshots import read_tree, snapshot_lock
from devkit_dist.features.distribution.services.snapshots.operations import validate_package
from devkit_dist.features.distribution.services.snapshots.provenance import load_provenance
from devkit_dist.features.distribution.usecases import snapshots as operations
from devkit_dist.features.distribution.usecases.snapshots import CreateBundleSnapshot, RefreshBundleSnapshot
from distsupport.snapshots import content_source


@pytest.fixture
def checkout(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = content_source(tmp_path / "upstream", rule=True)
    root = tmp_path / "consumer"
    root.mkdir()
    return root, source, root / "tools/team-copy"


def create(checkout: tuple[Path, Path, Path]):
    root, source, destination = checkout
    return CreateBundleSnapshot().execute(root, source, destination, "team-copy")


def refresh(checkout: tuple[Path, Path, Path], *, apply: bool = False):
    root, source, destination = checkout
    preview = RefreshBundleSnapshot().execute(root, destination, source)
    if not apply:
        return preview
    return RefreshBundleSnapshot().execute(
        root, destination, source, expect=preview.current_digest, candidate=preview.candidate_digest
    )


def test_complete_provider_bytes_modes_versions_and_path_free_provenance(checkout) -> None:
    root, source, destination = checkout
    outcome = create(checkout)
    assert outcome.status == "created" and outcome.bundles == {"alpha": "1.2.3", "beta": "1.2.3"}
    record = load_provenance(read_tree(destination))
    assert record["source"]["version"] == "2.3.4" and record["source"]["commit"] is None
    assert "snapshot.json" not in record["files"]
    serialized = (destination / "snapshot.json").read_text()
    for forbidden in (str(source), "private.invalid", "ssh://", "created_at"):
        assert forbidden not in serialized
    for name in ("alpha", "beta"):
        origin = source / f"src/private_content/{name}/bundle"
        copied = destination / f"src/team_copy/{name}/bundle"
        assert read_tree(origin) == read_tree(copied)
        assert (copied / "check.sh").stat().st_mode & 0o111
        assert (copied / "native/reviewer.toml").is_file()
        assert (copied / "guide.md.jinja").is_file()
        assert (copied / "rules/example/helper.py").is_file()
    assert (destination / "notices/LICENSE").read_bytes() == (source / "LICENSE").read_bytes()
    assert 'version = "0.0.0"' in (destination / "pyproject.toml").read_text()
    assert not (root / ".devkit").exists()
    assert [item["code"] for item in outcome.actions][:2] == ["SNAPSHOT_REPLACE_PROVIDER", "SNAPSHOT_INSTALL_LOCAL"]
    removal = next(item for item in outcome.actions if item["code"] == "SNAPSHOT_REPLACE_PROVIDER")
    assert "direct dev-group" in removal["detail"] and "skip when absent" in removal["detail"]
    assert "owning group" in removal["detail"] and "transitive" in removal["detail"]
    validate_package(destination)


def test_preview_apply_mode_deletion_additions_and_bytecode_idempotence(checkout) -> None:
    _, source, destination = checkout
    initial = create(checkout)
    before = read_tree(destination)
    origin = source / "src/private_content/alpha/bundle"
    (origin / "check.sh").chmod(0o644)
    (origin / "extra.txt").write_text("Additional support.\n")
    (origin / "rules/example/helper.py").write_text("VALUE = 'changed'\n")
    (source / "src/private_content/beta/bundle/check.sh").unlink()
    preview = refresh(checkout)
    assert read_tree(destination) == before and preview.status == "preview"
    prefix = "src/team_copy/alpha/bundle"
    assert f"{prefix}/extra.txt" in preview.changes["added"]
    assert f"{prefix}/check.sh" in preview.changes["modified"]
    assert "src/team_copy/beta/bundle/check.sh" in preview.changes["removed"]
    assert preview.current_digest == initial.candidate_digest != preview.candidate_digest
    updated = refresh(checkout, apply=True)
    assert updated.status == "updated" and updated.candidate_digest == preview.candidate_digest
    cached = destination / "src/team_copy/alpha/__pycache__/__init__.cpython-312.pyc"
    cached.parent.mkdir()
    cached.write_bytes(b"runtime bytecode")
    snapshot = read_tree(destination)
    times = {rel: (destination / rel).stat().st_mtime_ns for rel in snapshot}
    assert refresh(checkout, apply=True).status == "unchanged"
    assert times == {rel: (destination / rel).stat().st_mtime_ns for rel in snapshot}


def test_refresh_requires_both_reviewed_digests_and_detects_source_drift(checkout) -> None:
    root, source, destination = checkout
    create(checkout)
    preview = refresh(checkout)
    old = read_tree(destination)
    assert preview.status == "preview" and preview.code == "BUNDLE_SNAPSHOT_PREVIEW"
    for expect, candidate, missing in (
        (preview.current_digest, None, "--candidate"),
        (None, preview.candidate_digest, "--expect"),
    ):
        with pytest.raises(ArgumentError) as refused:
            RefreshBundleSnapshot().execute(root, destination, source, expect=expect, candidate=candidate)
        assert refused.value.code == "ARGUMENT_INVALID" and list(refused.value.target_files) == [missing]
    for expect, candidate in (("0" * 64, preview.candidate_digest), (preview.current_digest, "0" * 64)):
        with pytest.raises(SnapshotConflictError):
            RefreshBundleSnapshot().execute(root, destination, source, expect=expect, candidate=candidate)
    assert read_tree(destination) == old
    (source / "src/private_content/alpha/bundle/check.sh").write_text("changed\n")
    with pytest.raises(SnapshotConflictError):
        RefreshBundleSnapshot().execute(
            root, destination, source, expect=preview.current_digest, candidate=preview.candidate_digest
        )
    assert read_tree(destination) == old


@pytest.mark.parametrize("drift", ["edit", "addition", "mode", "deletion", "symlink"])
def test_authored_local_drift_never_overwrites(checkout, drift: str) -> None:
    _, _, destination = checkout
    create(checkout)
    local = destination / "src/team_copy/alpha/bundle/check.sh"
    if drift == "edit":
        local.write_text("local edit")
    elif drift == "addition":
        (destination / "local.txt").write_text("local file")
    elif drift == "mode":
        local.chmod(0o644)
    elif drift == "deletion":
        local.unlink()
    else:
        (destination / "outside").symlink_to(local)
    with pytest.raises((SnapshotConflictError, SnapshotInvalidError)):
        refresh(checkout, apply=True)
    assert destination.is_dir()
    if drift == "edit":
        assert local.read_text() == "local edit"


def test_invalid_schema_and_aggregate_refuse(checkout) -> None:
    _, _, destination = checkout
    create(checkout)
    path = destination / "snapshot.json"
    record = json.loads(path.read_text())
    record["schema"] = 2
    path.write_text(json.dumps(record))
    with pytest.raises(SnapshotInvalidError, match="schema"):
        refresh(checkout)
    record["schema"] = 1
    record["digest"] = "0" * 64
    path.write_text(json.dumps(record))
    with pytest.raises(SnapshotInvalidError, match="digest"):
        refresh(checkout)


@pytest.mark.parametrize(
    "expression",
    [
        "import missing_private_runtime\n",
        "from private_content import runtime\n",
        "from ... import outside\n",
        "import importlib\nimportlib.import_module('private_runtime')\n",
        "__import__('private_runtime')\n",
    ],
)
def test_unsupported_python_is_rejected_before_destination_writes(checkout, expression: str) -> None:
    root, source, destination = checkout
    (source / "src/private_content/alpha/bundle/rules/example/extra.py").write_text(expression)
    with pytest.raises(SnapshotUnsupportedError):
        create(checkout)
    assert not destination.exists() and not (root / "tools").exists()


@pytest.mark.parametrize("mutation", ["dependency", "command", "initializer", "mapping", "hook", "workflow"])
def test_unsupported_provider_metadata_and_declarative_references(checkout, mutation: str) -> None:
    _, source, destination = checkout
    metadata = source / "pyproject.toml"
    bundle = source / "src/private_content/alpha/bundle"
    if mutation == "dependency":
        metadata.write_text(metadata.read_text().replace("dependencies = []", 'dependencies = ["private-runtime"]'))
    elif mutation == "command":
        metadata.write_text(metadata.read_text() + '\n[project.scripts]\nprivate = "private_content:main"\n')
    elif mutation == "initializer":
        (source / "src/private_content/__init__.py").write_text("raise RuntimeError('must never execute')\n")
    elif mutation == "mapping":
        metadata.write_text(
            metadata.read_text().replace('packages = ["src/private_content"]', 'packages = ["elsewhere"]')
        )
    elif mutation == "hook":
        (bundle / "hook.toml").write_text('host = "codex"\nevent = "SessionStart"\nhandler = "private-handler"\n')
        with (bundle / "bundle.toml").open("a") as stream:
            stream.write('\n[[assets]]\nid = "hook"\nkind = "hook"\nsource = "hook.toml"\n')
    else:
        (bundle / "flow.md").write_text(
            "---\nid: example-flow\nchecks:\n  - {name: external, class: plugin, module: private_runtime}\n"
            "stages:\n  - {id: start}\n---\nFlow.\n"
        )
        with (bundle / "bundle.toml").open("a") as stream:
            stream.write('\n[[assets]]\nid = "flow"\nkind = "workflow"\nsource = "flow.md"\n')
    with pytest.raises(SnapshotUnsupportedError):
        create(checkout)
    assert not destination.exists()


@pytest.mark.parametrize("failure", [OSError, SnapshotInvalidError])
def test_validated_replacement_failure_rolls_back_prior_package(
    checkout, monkeypatch: pytest.MonkeyPatch, failure
) -> None:
    _, source, destination = checkout
    create(checkout)
    before = read_tree(destination)
    (source / "src/private_content/alpha/bundle/extra.txt").write_text("new")
    original = operations.validate_package

    def fail_after_install(path: Path) -> None:
        original(path)
        if path == destination:
            raise failure("injected post-replacement validation failure")

    monkeypatch.setattr(operations, "validate_package", fail_after_install)
    with pytest.raises(SnapshotWriteError):
        refresh(checkout, apply=True)
    assert read_tree(destination) == before
    assert sorted(destination.parent.iterdir()) == [destination]


@pytest.mark.parametrize(
    "target", [".git/copy", ".devkit/copy", ".agents/copy", "nested/.git/copy", "../outside", "AGENTS.md"]
)
def test_protected_or_out_of_root_destinations_refuse(checkout, target: str) -> None:
    root, source, _ = checkout
    with pytest.raises(SnapshotInvalidError):
        CreateBundleSnapshot().execute(root, source, Path(target), "team-copy")


def test_existing_nested_and_source_overlapping_destinations_refuse(checkout) -> None:
    root, source, destination = checkout
    create(checkout)
    with pytest.raises(SnapshotConflictError):
        create(checkout)
    with pytest.raises(SnapshotConflictError):
        CreateBundleSnapshot().execute(root, source, destination / "nested", "nested-copy")
    with pytest.raises(SnapshotInvalidError):
        CreateBundleSnapshot().execute(source, source, source / "copy", "team-copy")
    with snapshot_lock(root), pytest.raises(SnapshotConflictError):
        refresh(checkout)


def test_provider_and_entrypoint_changes_return_reinstall_and_deselection(checkout) -> None:
    root, source, _ = checkout
    create(checkout)
    config = root / ".devkit/config.toml"
    config.parent.mkdir()
    config.write_text('[presets]\nbeta = "core"\n')
    metadata = source / "pyproject.toml"
    metadata.write_text(metadata.read_text().replace('beta = "private_content.beta"', 'gamma = "private_content.beta"'))
    manifest = source / "src/private_content/beta/bundle/bundle.toml"
    manifest.write_text(manifest.read_text().replace('name = "beta"', 'name = "gamma"'))
    before = config.read_bytes()
    preview = refresh(checkout)
    assert preview.bundles == {"alpha": "1.2.3", "gamma": "1.2.3"}
    assert preview.removed_selected == ["beta"] and preview.packaging_changed
    assert {item["code"] for item in preview.actions} >= {"SNAPSHOT_REINSTALL_PACKAGE", "SNAPSHOT_DESELECT_REMOVED"}
    refresh(checkout, apply=True)
    assert config.read_bytes() == before


def test_optional_commit_matches_only_copied_committed_inputs(checkout) -> None:
    _, source, _ = checkout
    for args in (
        ("init", "-q"),
        ("add", "."),
        ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "content"),
    ):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    create(checkout)
    assert refresh(checkout).current_digest
    record = json.loads((checkout[2] / "snapshot.json").read_text())
    assert record["source"]["commit"] == head
    (source / "src/private_content/alpha/bundle/extra.txt").write_text("not committed")
    refresh(checkout, apply=True)
    record = json.loads((checkout[2] / "snapshot.json").read_text())
    assert record["source"]["commit"] is None


@pytest.fixture
def subdirectory_checkout(tmp_path: Path) -> tuple[Path, Path, Path]:
    repository = tmp_path / "repository"
    source = content_source(repository / "tools/content", rule=True)
    root = tmp_path / "consumer"
    root.mkdir()
    for args in (
        ("init", "-q"),
        ("add", "."),
        ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "content"),
    ):
        subprocess.run(["git", "-C", str(repository), *args], check=True, capture_output=True)
    return root, source, root / "tools/team-copy"


def test_subdirectory_commit_and_source_path_spelling(subdirectory_checkout) -> None:
    root, source, destination = subdirectory_checkout
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    initial = create(subdirectory_checkout)
    assert load_provenance(read_tree(destination))["source"]["commit"] == head
    relative_source = Path("../repository/tools/content")
    preview = RefreshBundleSnapshot().execute(root, destination, relative_source)
    assert preview.candidate_digest == initial.candidate_digest
    assert preview.changes == {"added": [], "modified": [], "removed": []}


@pytest.mark.parametrize("change", ["bytes", "mode"])
def test_subdirectory_commit_rejects_dirty_copied_inputs(subdirectory_checkout, change: str) -> None:
    _, source, destination = subdirectory_checkout
    create(subdirectory_checkout)
    assert load_provenance(read_tree(destination))["source"]["commit"] is not None
    if change == "bytes":
        guide = source / "src/private_content/alpha/bundle/guide.md.jinja"
        guide.write_text(guide.read_text().replace("alpha body.", "uncommitted copied bytes."))
    else:
        (source / "src/private_content/alpha/bundle/check.sh").chmod(0o644)
    assert refresh(subdirectory_checkout, apply=True).status == "updated"
    assert load_provenance(read_tree(destination))["source"]["commit"] is None


def test_subdirectory_commit_metadata_only_refresh(subdirectory_checkout, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_dist.features.distribution.services.snapshots import source as source_service

    root, source, destination = subdirectory_checkout
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    with monkeypatch.context() as legacy:
        legacy.setattr(source_service, "source_commit", lambda *_: None)
        initial = create(subdirectory_checkout)
    before = read_tree(destination)
    assert load_provenance(before)["source"]["commit"] is None
    before_times = {rel: (destination / rel).stat().st_mtime_ns for rel in before}
    preview = refresh(subdirectory_checkout)
    assert preview.changes == {"added": [], "modified": ["snapshot.json"], "removed": []}
    assert preview.current_digest == initial.candidate_digest != preview.candidate_digest
    assert preview.packaging_changed is False
    assert read_tree(destination) == before
    assert before_times == {rel: (destination / rel).stat().st_mtime_ns for rel in before}
    updated = RefreshBundleSnapshot().execute(
        root, destination, source, expect=preview.current_digest, candidate=preview.candidate_digest
    )
    assert updated.code == "BUNDLE_SNAPSHOT_UPDATED"
    assert load_provenance(read_tree(destination))["source"]["commit"] == head
    adopted = read_tree(destination)
    adopted_times = {rel: (destination / rel).stat().st_mtime_ns for rel in adopted}
    repeated = refresh(subdirectory_checkout, apply=True)
    assert repeated.code == "BUNDLE_SNAPSHOT_UNCHANGED"
    assert read_tree(destination) == adopted
    assert adopted_times == {rel: (destination / rel).stat().st_mtime_ns for rel in adopted}


def test_edit_during_candidate_preparation_is_preserved(checkout, monkeypatch: pytest.MonkeyPatch) -> None:
    root, source, destination = checkout
    create(checkout)
    (source / "src/private_content/alpha/bundle/extra.txt").write_text("upstream")
    preview = refresh(checkout)
    original = operations.prepare_candidate
    local = destination / "src/team_copy/alpha/bundle/guide.md.jinja"

    def edit_during_prepare(source_path: Path, package: str):
        candidate = original(source_path, package)
        local.write_text("authored during refresh")
        return candidate

    monkeypatch.setattr(operations, "prepare_candidate", edit_during_prepare)
    with pytest.raises(SnapshotConflictError):
        RefreshBundleSnapshot().execute(
            root, destination, source, expect=preview.current_digest, candidate=preview.candidate_digest
        )
    assert local.read_text() == "authored during refresh"
    assert not (destination / "src/team_copy/alpha/bundle/extra.txt").exists()
    assert sorted(destination.parent.iterdir()) == [destination]


def test_source_commit_is_bound_to_the_captured_head(checkout, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_dist.features.distribution.repositories import snapshots as repository

    _, source, destination = checkout
    for args in (
        ("init", "-q"),
        ("add", "."),
        ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "first"),
    ):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    guide = source / "src/private_content/alpha/bundle/guide.md.jinja"
    guide.write_text(guide.read_text().replace("alpha body.", "new copied bytes."))
    real_git = repository.run_git
    advanced = False

    def advance_head(cwd, *args, **kwargs):
        nonlocal advanced
        if "ls-tree" in args and not advanced:
            advanced = True
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(source),
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-qam",
                    "second",
                ],
                check=True,
                capture_output=True,
            )
        return real_git(cwd, *args, **kwargs)

    monkeypatch.setattr(repository, "run_git", advance_head)
    create(checkout)
    assert advanced
    assert json.loads((destination / "snapshot.json").read_text())["source"]["commit"] is None


def test_source_path_spelling_does_not_change_provenance(checkout) -> None:
    root, source, destination = checkout
    for args in (
        ("init", "-q"),
        ("add", "."),
        ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "source"),
    ):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    first = create(checkout)
    alias = root / ".." / source.name
    preview = RefreshBundleSnapshot().execute(root, destination, alias)
    assert preview.candidate_digest == first.candidate_digest
    assert preview.changes == {"added": [], "modified": [], "removed": []}


def test_source_symlink_stays_rejected_before_canonicalization(checkout) -> None:
    root, source, destination = checkout
    link = source.parent / "source-link"
    link.symlink_to(source, target_is_directory=True)
    with pytest.raises(SnapshotInvalidError):
        CreateBundleSnapshot().execute(root, link, destination, "team-copy")
    assert not destination.exists()


def test_source_symlinked_parent_stays_rejected_before_canonicalization(checkout) -> None:
    root, source, destination = checkout
    alias_parent = source.parent / "alias-parent"
    alias_parent.symlink_to(source.parent, target_is_directory=True)
    with pytest.raises(SnapshotInvalidError) as raised:
        CreateBundleSnapshot().execute(root, alias_parent / source.name, destination, "team-copy")
    assert raised.value.code == "BUNDLE_SNAPSHOT_INVALID" and str(alias_parent) in str(raised.value)
    assert raised.value.fix == f"Pass the resolved source path instead: {source.resolve()}"
    assert not destination.exists()


def test_destination_symlinked_parent_refusal_names_the_resolved_path(checkout) -> None:
    root, source, _ = checkout
    alias = root.parent / "consumer-alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(SnapshotInvalidError) as raised:
        CreateBundleSnapshot().execute(alias, source, alias / "tools/team-copy", "team-copy")
    assert raised.value.code == "BUNDLE_SNAPSHOT_INVALID" and str(alias) in str(raised.value)
    assert raised.value.fix == f"Pass the resolved destination path instead: {root.resolve() / 'tools/team-copy'}"
    assert not (root / "tools").exists()


def test_symlink_inside_source_checkout_stays_rejected(checkout) -> None:
    root, source, destination = checkout
    package = source / "src/private_content"
    (package / "linked").symlink_to(package / "alpha", target_is_directory=True)
    (source / "pyproject.toml").write_text(
        (source / "pyproject.toml")
        .read_text()
        .replace('alpha = "private_content.alpha"', 'alpha = "private_content.linked"')
    )
    with pytest.raises(SnapshotInvalidError):
        CreateBundleSnapshot().execute(root, source, destination, "team-copy")
    assert not destination.exists()


def test_finder_metadata_in_snapshot_is_not_authored_drift(checkout) -> None:
    _, _, destination = checkout
    create(checkout)
    (destination / ".DS_Store").write_bytes(b"finder")
    (destination / "src/team_copy/alpha/bundle/.DS_Store").write_bytes(b"finder")
    assert refresh(checkout, apply=True).status == "unchanged"
