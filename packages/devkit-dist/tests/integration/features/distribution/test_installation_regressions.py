"""Regressions of the installation layer: override safety and baselines, adoption, conflicts, locks, status."""

from __future__ import annotations

import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode, Level
from devkit_core.core import extensions as core_extensions
from devkit_dist.features.distribution.models.errors import (
    BundleConflictError,
    BundleError,
    ConflictError,
    LockHeldError,
    PackageError,
    SelectionError,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.models.settings import DEFAULT_PRESET
from devkit_dist.features.distribution.services.installation import discovery, extensions, guidance_block
from devkit_dist.features.distribution.services.installation.config import (
    prepare_config_update,
    resolve_selection,
    update_config,
)
from devkit_dist.features.distribution.services.installation.discovery import (
    Discovered,
    InstalledBundle,
    discover_bundles,
)
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.distribution.services.installation.workspace import AGENTS_FILE, DEPLOYED
from devkit_dist.features.distribution.usecases import sync as sync_module
from devkit_dist.features.distribution.usecases.override_commands import create_override, diff_override, list_overrides
from devkit_dist.features.distribution.usecases.status import get_project_listing, get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, OVERRIDES_PATH, RECEIPT_PATH, ToolRecord
from distsupport.distribution import cli, instruction, reload, write_bundle

MANIFEST = """schema = 1
name = "team"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[presets.small]
assets = ["review"]
"""

FILES = {
    "skills/review/SKILL.md": "# Review\n",
    "guide.md": instruction("guide", "Upstream v1.\n"),
}


@pytest.fixture
def item(tmp_path: Path) -> InstalledBundle:
    return write_bundle(tmp_path / "source", MANIFEST, FILES)


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=["claude-code"])
    return root


def _upgrade(item: InstalledBundle, body: str = "Upstream v2.\n") -> InstalledBundle:
    (item.bundle.root / "guide.md").write_text(instruction("guide", body))
    return reload(item)


def _skill_bundle(root: Path, name: str, extra: str, skill: str = "review") -> InstalledBundle:
    manifest = f'schema = 1\nname = "{name}"\nversion = "0.1.0"\n'
    manifest += f'[[assets]]\nid = "{skill}"\nkind = "skill"\nsource = "skills/{skill}"\n'
    return write_bundle(
        root / name,
        manifest,
        {f"skills/{skill}/SKILL.md": "# Skill\n", f"skills/{skill}/{extra}": f"{name}\n"},
        package=f"{name}-content",
    )


# --- overrides ---------------------------------------------------------------


@pytest.mark.parametrize("link", [OVERRIDES_PATH, f"{OVERRIDES_PATH}/team"])
def test_symlinked_override_directory_is_refused_before_any_write(
    item: InstalledBundle, target: Path, tmp_path: Path, link: str
) -> None:
    sync_project(target, [item])
    outside = tmp_path / "outside"
    (outside / "team/skills/review").mkdir(parents=True)
    (outside / "team/skills/review/SKILL.md").write_text("# OUTSIDE\n")
    shutil.copytree(outside / "team", outside / "plain")
    (target / link).parent.mkdir(parents=True, exist_ok=True)
    (target / link).symlink_to(outside if link == OVERRIDES_PATH else outside / "plain")
    receipt = (target / RECEIPT_PATH).read_bytes()
    with pytest.raises(UnsafeWorkspaceError, match="deployment symlink"):
        sync_project(target, [item])
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    assert (target / ".claude/skills/review/SKILL.md").read_text().endswith("# Review\n")


def test_forced_create_takes_the_current_upstream_as_baseline(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    newer = _upgrade(item)
    assert [entry.asset for entry in sync_project(target, [newer]).drift] == ["guide"]
    (target / CONFIG_PATH).write_text('override_drift = "block"\n' + (target / CONFIG_PATH).read_text())
    change = create_override(target, [newer], "team:guide", force=True)
    assert [notice.code for notice in change.notices] == []
    diff = diff_override(target, [newer], "team:guide")
    assert diff.drift_detected is False
    assert diff.baseline_upstream_sha256 == diff.current_upstream_sha256
    assert (target / OVERRIDES_PATH / "team/guide.md").read_text().endswith("Upstream v2.\n")


def test_narrowed_preset_keeps_the_override_baseline(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    update_config(target, presets={"team": ["small"]})
    sync_project(target, [item])
    receipt = read_receipt(target)
    assert receipt is not None and list(receipt.overrides["team"]) == ["guide"]
    newer = _upgrade(item)
    assert sync_project(target, [newer]).drift == []
    # Drift behind an asset that is not deployed is not a status problem, as it is not a sync warning.
    assert get_project_status(target, [newer]).override_drift == []
    update_config(target, presets={"team": ["all"]})
    assert [entry.asset for entry in sync_project(target, [newer]).drift] == ["guide"]
    assert get_project_status(target, [newer]).override_drift == [("team", "guide")]


def test_removed_override_files_drop_the_record_of_an_undeployed_asset(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    create_override(target, [item], "team:guide")
    update_config(target, presets={"team": ["small"]})
    shutil.rmtree(target / OVERRIDES_PATH / "team")
    sync_project(target, [item])
    receipt = read_receipt(target)
    assert receipt is not None and dict(receipt.overrides) == {}


def test_failure_after_the_commit_keeps_the_override_files(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [item])

    def fail(*args: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(sync_module, "_record_seen_bundles", fail)
    with pytest.raises(OSError, match="disk full"):
        create_override(target, [item], "team:guide")
    assert (target / OVERRIDES_PATH / "team/guide.md").is_file()
    receipt = read_receipt(target)
    assert receipt is not None and list(receipt.overrides["team"]) == ["guide"]
    monkeypatch.undo()
    assert sync_project(target, [item]).actions == []


# --- adoption and conflicts --------------------------------------------------


def test_identical_unowned_files_and_block_are_adopted_without_a_write(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    owned = json.loads((target / RECEIPT_PATH).read_text())
    agents = (target / AGENTS_FILE).read_bytes()
    (target / RECEIPT_PATH).unlink()  # a branch whose receipt predates the selection; projections stay on disk
    result = sync_project(target, [item])
    assert [action.path for action in result.actions] == [RECEIPT_PATH]
    adopted = json.loads((target / RECEIPT_PATH).read_text())
    assert adopted["files"] == owned["files"] and adopted["guidance_block"] == owned["guidance_block"]
    assert (target / AGENTS_FILE).read_bytes() == agents


def test_every_conflicting_path_is_reported_at_once(item: InstalledBundle, target: Path) -> None:
    sync_project(target, [item])
    edited = [".claude/skills/review/SKILL.md", ".devkit/managed/team/guide.md"]
    for name in edited:
        (target / name).write_text("edited\n")
    (target / RECEIPT_PATH).write_text(
        json.dumps(
            {
                **(receipt := json.loads((target / RECEIPT_PATH).read_text())),
                "files": {k: v for k, v in receipt["files"].items() if k != ".devkit/managed/team/bundle.toml"},
            }
        )
    )
    (target / ".devkit/managed/team/bundle.toml").write_text("foreign\n")
    (target / DEPLOYED).unlink()  # a clone whose own syncs never wrote bundle.toml
    agents = target / AGENTS_FILE
    agents.write_text(agents.read_text().replace("## devkit", "## devkit (edited)"))
    with pytest.raises(ConflictError) as raised:
        sync_project(target, [item])
    error = raised.value
    assert error.code == "SYNC_CONFLICT"
    assert error.target_files == (*edited, ".devkit/managed/team/bundle.toml", AGENTS_FILE)
    assert "managed files were edited" in error.message and "unowned destinations" in error.message
    assert error.fix is not None and "devkit override create" in error.fix and "Move each unowned file" in error.fix


def test_unowned_block_that_differs_is_still_a_conflict(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_text(f"{guidance_block.START}\nmine\n{guidance_block.END}\n")
    with pytest.raises(ConflictError, match="unowned guidance block") as raised:
        sync_project(target, [item])
    assert raised.value.fix is not None and "markers" in raised.value.fix


def test_two_bundles_never_share_a_skill_directory(tmp_path: Path, target: Path) -> None:
    alpha, beta = _skill_bundle(tmp_path, "alpha", "a.py"), _skill_bundle(tmp_path, "beta", "b.py")
    update_config(target, presets={"alpha": ["all"], "beta": ["all"]}, deselect=["team"])
    with pytest.raises(BundleConflictError, match=r"\.claude/skills/review \(alpha:review and beta:review\)"):
        sync_project(target, [alpha, beta])
    assert not (target / RECEIPT_PATH).exists()
    with pytest.raises(BundleConflictError, match=r"\.agents/skills/review"):
        sync_project(target, [alpha, beta], agents=["codex", "antigravity"])
    # One asset projected for Codex and Antigravity shares its directory with itself.
    update_config(target, deselect=["beta"])
    sync_project(target, [alpha, beta], agents=["codex", "antigravity"])
    assert sorted(p.name for p in (target / ".agents/skills/review").iterdir()) == ["SKILL.md", "a.py"]


# --- guidance block text -----------------------------------------------------


def test_disabling_the_block_keeps_paragraphs_apart(item: InstalledBundle, target: Path) -> None:
    (target / AGENTS_FILE).write_text("Intro paragraph.\n")
    sync_project(target, [item])
    agents = target / AGENTS_FILE
    agents.write_text(agents.read_text() + "\nClosing paragraph.\n")
    (target / CONFIG_PATH).write_text("guidance_block = false\n" + (target / CONFIG_PATH).read_text())
    sync_project(target, [item])
    assert agents.read_text() == "Intro paragraph.\n\nClosing paragraph.\n"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a\n\nB\n\nb\n", "a\n\nb\n"),
        ("a\nB\n\nb\n", "a\n\nb\n"),
        ("a\r\n\r\nB\r\nb\r\n", "a\r\n\r\nb\r\n"),
        ("B\n\nb\n", "b\n"),
    ],
)
def test_strip_keeps_a_blank_line_that_stood_next_to_the_block(text: str, expected: str) -> None:
    block = f"{guidance_block.START}\nbody\n{guidance_block.END}"
    newline = "\r\n" if "\r\n" in text else "\n"
    assert guidance_block.strip(text.replace("B", block.replace("\n", newline))) == expected


# --- receipt tool ------------------------------------------------------------


def test_a_writing_sync_records_the_running_version(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [item])
    monkeypatch.setattr(sync_module, "tool_identity", lambda: ToolRecord("devkit-agt", "9.9.9"))
    (target / ".claude/skills/review/SKILL.md").unlink()
    result = sync_project(target, [item])
    assert [action.path for action in result.actions] == [".claude/skills/review/SKILL.md", RECEIPT_PATH]
    assert [notice.code for notice in result.notices] == ["TOOL_VERSION_CHANGED"]
    assert json.loads((target / RECEIPT_PATH).read_text())["tool"]["version"] == "9.9.9"
    assert sync_project(target, [item]).actions == []


# --- locks and readers -------------------------------------------------------


def test_readers_of_a_project_without_devkit_create_nothing(item: InstalledBundle, tmp_path: Path) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    status = get_project_status(bare, [item])
    assert status.receipt is False and status.ok
    get_project_listing(bare, [item])
    assert list_overrides(bare, [item]) == []
    assert list(bare.iterdir()) == []


def test_status_reports_unsafe_paths_instead_of_failing(item: InstalledBundle, target: Path, tmp_path: Path) -> None:
    sync_project(target, [item])
    skill = target / ".claude/skills/review/SKILL.md"
    skill.unlink()
    skill.symlink_to(tmp_path / "elsewhere.md")
    (target / AGENTS_FILE).write_text(f"{guidance_block.START}\n{guidance_block.START}\n{guidance_block.END}\n")
    status = get_project_status(target, [item])
    assert status.files.unsafe == [".claude/skills/review/SKILL.md"]
    assert status.guidance_block == "invalid"
    assert [(error.code, error.exit_code) for error in status.errors] == [
        ("WORKSPACE_UNSAFE", ExitCode.FINDINGS),
        ("GUIDANCE_BLOCK_INVALID", ExitCode.FINDINGS),
    ]
    (target / AGENTS_FILE).unlink()
    (target / AGENTS_FILE).symlink_to(tmp_path / "AGENTS.md")
    status = get_project_status(target, [item])
    assert status.guidance_block == "invalid" and status.errors[-1].code == "WORKSPACE_UNSAFE"


# --- saving the selection ----------------------------------------------------


def test_saved_selection_is_rendered_under_the_lock_and_put_back_on_failure(
    item: InstalledBundle, target: Path
) -> None:
    before = (target / CONFIG_PATH).read_bytes()

    def save():
        with pytest.raises(LockHeldError), project_lock(target):
            pass
        return prepare_config_update(target, presets={"team": ["small"]})

    sync_project(target, [item], save=save)
    assert 'team = "small"' in (target / CONFIG_PATH).read_text()
    assert not (target / ".devkit/managed/team/guide.md").exists()

    (target / CONFIG_PATH).write_bytes(before)
    (target / ".claude/skills/review/SKILL.md").write_text("edited\n")
    with pytest.raises(ConflictError):
        sync_project(target, [item], save=lambda: prepare_config_update(target, presets={"team": ["all"]}))
    assert (target / CONFIG_PATH).read_bytes() == before


def test_post_sync_extensions_see_the_saved_selection(
    item: InstalledBundle, target: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = _skill_bundle(tmp_path, "other", "o.py", skill="lint")
    seen: list[str] = []

    def hook(root: Path, result: dict) -> None:
        seen.append((root / CONFIG_PATH).read_text())

    entry = SimpleNamespace(name="probe", value="fake:probe", load=lambda: hook)
    monkeypatch.setattr(
        core_extensions.metadata, "entry_points", lambda group: [entry] if group == extensions.GROUP else []
    )

    @contextmanager
    def found():
        yield [item, other]

    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", found)
    result = CliRunner().invoke(cli, ["add", "other:all", "--workspace-root", str(target)])
    assert result.exit_code == 0, result.output
    assert len(seen) == 1 and 'other = "all"' in seen[0]


# --- discovery and unusable packages ----------------------------------------


def _entry(name: str, module: str = "content_module") -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        value=module,
        module=module,
        attr=None,
        extras=[],
        dist=SimpleNamespace(metadata={"Name": f"{name}-content"}, version="0.1.0"),
    )


@pytest.mark.parametrize("failure", [RuntimeError("init failed"), SyntaxError("bad"), RecursionError("deep")])
def test_a_content_package_that_fails_to_load_is_recorded_as_unusable(
    monkeypatch: pytest.MonkeyPatch, failure: BaseException
) -> None:
    def files(name: str) -> Path:
        raise failure

    monkeypatch.setattr(discovery.resources, "files", files)
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [_entry("broken")])
    with discover_bundles() as found:
        assert list(found) == []
        error = found.unusable["broken"]
    assert error.code == "BUNDLE_PACKAGE_INVALID" and "broken: cannot read content resources" in error.message
    assert error.fix is not None and "broken-content" in error.fix


def test_entry_point_name_must_be_the_bundle_name(
    item: InstalledBundle, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "module"
    shutil.copytree(item.bundle.root, module / "bundle")
    monkeypatch.setattr(discovery.resources, "files", lambda name: module)
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [_entry("other")])
    with discover_bundles() as found:
        assert list(found) == []
        assert "registers bundle team" in found.unusable["other"].message


def test_deeply_nested_manifest_is_a_bundle_error(tmp_path: Path) -> None:
    depth = 100_000
    (tmp_path / "deep").mkdir()
    with pytest.raises(BundleError, match=r"cannot read bundle\.toml: maximum recursion depth"):
        write_bundle(tmp_path / "deep", f"schema = 1\nx = {'[' * depth}{']' * depth}\n", {})


def _broken(item: InstalledBundle) -> Discovered:
    return Discovered([item], {"broken": PackageError("broken: cannot read content resources", fix="Upgrade it")})


def test_unusable_unselected_package_is_a_warning_and_a_selected_one_an_error(
    item: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    installed = _broken(item)
    result = sync_project(target, installed)
    (warning,) = [notice for notice in result.notices if notice.code == "BUNDLE_PACKAGE_INVALID"]
    assert warning.level is Level.WARNING and warning.exit_code == ExitCode.OK
    listing = get_project_listing(target, installed)
    assert [notice.code for notice in listing.notices] == ["BUNDLE_PACKAGE_INVALID"]
    status = get_project_status(target, installed)
    assert status.errors == [] and [notice.code for notice in status.notices] == ["BUNDLE_PACKAGE_INVALID"]

    update_config(target, presets={"broken": ["all"]})
    with pytest.raises(PackageError, match="broken: cannot read content resources"):
        sync_project(target, installed)
    with pytest.raises(PackageError):
        get_project_listing(target, installed)
    status = get_project_status(target, installed)
    assert [(error.code, error.exit_code) for error in status.errors] == [("BUNDLE_PACKAGE_INVALID", ExitCode.FINDINGS)]
    assert status.notices == []

    # The project can still deselect it.
    @contextmanager
    def found():
        yield installed

    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", found)
    removed = CliRunner().invoke(cli, ["remove", "broken", "--workspace-root", str(target)])
    assert removed.exit_code == 0, removed.output
    assert "broken" not in (target / CONFIG_PATH).read_text()
    assert "[WARN]   (BUNDLE_PACKAGE_INVALID)" in removed.stderr
    added = CliRunner().invoke(cli, ["add", "broken", "--workspace-root", str(target), "--format", "json"])
    assert added.exit_code == 2 and json.loads(added.stdout)["error"]["code"] == "BUNDLE_PACKAGE_INVALID"


# --- bare and named presets --------------------------------------------------


def test_bare_bundle_keeps_its_default_preset_next_to_named_ones(
    tmp_path: Path, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = MANIFEST + '[presets.extra]\nassets = ["guide"]\n'
    bundle = write_bundle(
        tmp_path / "presets", manifest.replace('default_preset = "all"', 'default_preset = "small"'), FILES
    )
    assert resolve_selection([bundle], {"team": [DEFAULT_PRESET, "extra"]}) == {"team": ["small", "extra"]}
    assert resolve_selection([bundle], {"team": ["extra", DEFAULT_PRESET]}) == {"team": ["extra", "small"]}

    @contextmanager
    def found():
        yield [bundle]

    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", found)
    result = CliRunner().invoke(cli, ["sync", "--preset", "team", "--preset", "team:extra", "-w", str(target)])
    assert result.exit_code == 0, result.output
    assert 'team = ["small", "extra"]' in (target / CONFIG_PATH).read_text()

    no_default = write_bundle(tmp_path / "nodefault", MANIFEST.replace('default_preset = "all"\n', ""), FILES)
    with pytest.raises(SelectionError, match="declares no default preset"):
        resolve_selection([no_default], {"team": [DEFAULT_PRESET, "small"]})
