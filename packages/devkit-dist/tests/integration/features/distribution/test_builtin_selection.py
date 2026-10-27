"""Bundles declaring ``auto_select`` are deployed by default, from any package; every other bundle needs ``devkit add``."""

from __future__ import annotations

import importlib.util
import json
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.models.errors import BundleError, PackageError, SelectionError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation import discovery
from devkit_dist.features.distribution.services.installation.config import merge_selection, read_config, update_config
from devkit_dist.features.distribution.services.installation.discovery import (
    Discovered,
    InstalledBundle,
    discover_bundles,
)
from devkit_dist.features.distribution.usecases.commands import AddSelection, SyncSelection
from devkit_dist.features.distribution.usecases.status import get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, RECEIPT_PATH
from distsupport.distribution import cli


def _bundle(root: Path, name: str, *, default_preset: str | None = "core", auto_select: bool = False) -> Path:
    root.mkdir(parents=True)
    (root / "guide.md").write_text("---\nname: guide\ndescription: A guide.\n---\nBody.\n")
    (root / "extra.md").write_text("---\nname: extra\ndescription: More.\n---\nBody.\n")
    default = f'default_preset = "{default_preset}"\n' if default_preset else ""
    auto = "auto_select = true\n" if auto_select else ""
    (root / "bundle.toml").write_text(
        f'schema = 1\nname = "{name}"\nversion = "0.1.0"\n{default}{auto}'
        '[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "guide.md"\n'
        '[[assets]]\nid = "extra"\nkind = "instruction"\nsource = "extra.md"\n'
        '[presets.core]\nassets = ["guide"]\n'
        '[presets.more]\nassets = ["extra"]\n'
    )
    return root


@pytest.fixture
def bundles(tmp_path: Path) -> list[InstalledBundle]:
    return [
        InstalledBundle(
            "devkit", "0.1.0", load_bundle(_bundle(tmp_path / "builtin", "kit", auto_select=True)), builtin=True
        ),
        InstalledBundle("devkit", "0.1.0", load_bundle(_bundle(tmp_path / "optional", "opt")), builtin=True),
        InstalledBundle("other-content", "0.1.0", load_bundle(_bundle(tmp_path / "external", "other"))),
    ]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    path = tmp_path / "consumer"
    path.mkdir()
    return path


def _selection(root: Path) -> dict[str, list[str]]:
    return json.loads((root / RECEIPT_PATH).read_text())["selection"]["presets"]


def _config(root: Path) -> dict:
    return tomllib.loads((root / CONFIG_PATH).read_text())


def test_empty_project_gets_auto_selected_builtins_only(bundles: list[InstalledBundle], target: Path) -> None:
    result = sync_project(target, bundles).to_dict()
    assert _selection(target) == {"kit": ["core"]}
    assert [item["bundle"] for item in result["unselected"]] == ["opt", "other"]  # type: ignore[union-attr]
    assert not (target / CONFIG_PATH).exists()


def test_config_false_opts_out_and_a_named_preset_replaces_the_default(
    bundles: list[InstalledBundle], target: Path
) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text("[presets]\nkit = false\n")
    sync_project(target, bundles)
    assert not (target / RECEIPT_PATH).exists() or _selection(target) == {}
    assert read_config(target).opted_out == frozenset({"kit"})

    (target / CONFIG_PATH).write_text('[presets]\nkit = "all"\nother = "core"\n')
    sync_project(target, bundles)
    assert _selection(target) == {"kit": ["all"], "other": ["core"]}


def test_one_run_selection_overrides_an_opt_out(bundles: list[InstalledBundle], target: Path) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text("[presets]\nkit = false\n")
    sync_project(target, bundles, presets={"kit": ["core"]})
    assert _selection(target) == {"kit": ["core"]}


@pytest.mark.parametrize("value", ["true", "[]", '""'])
def test_invalid_preset_values_are_rejected(target: Path, value: str) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text(f"[presets]\nkit = {value}\n")
    with pytest.raises(ConfigError, match="invalid presets"):
        read_config(target)


def test_update_config_opt_out_and_reselect(target: Path) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text('# keep\n[presets]\nother = "core"\n')
    update_config(target, deselect=["other"], opt_out=["kit"])
    assert _config(target)["presets"] == {"kit": False}
    assert "# keep" in (target / CONFIG_PATH).read_text()
    update_config(target, presets={"kit": ["core"]})
    assert _config(target)["presets"] == {"kit": "core"}


def test_merge_selection_joins_existing_presets(bundles: list[InstalledBundle], target: Path) -> None:
    config = read_config(target)
    assert merge_selection(bundles, config, {"kit": ["more"], "opt": ["more"]}) == {
        "kit": ["core", "more"],
        "opt": ["more"],
    }
    assert merge_selection(bundles, config, {"kit": ["core"]}) == {"kit": ["core"]}
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text('[presets]\nkit = false\nopt = "core"\n')
    config = read_config(target)
    assert merge_selection(bundles, config, {"kit": ["more"], "opt": ["core"]}) == {"kit": ["more"], "opt": ["core"]}


def test_auto_select_requires_a_boolean_and_a_default_preset(tmp_path: Path) -> None:
    root = _bundle(tmp_path / "bad", "kit", default_preset=None, auto_select=True)
    with pytest.raises(BundleError, match="auto_select requires default_preset"):
        load_bundle(root)
    manifest = root / "bundle.toml"
    manifest.write_text(manifest.read_text().replace("auto_select = true", 'auto_select = "yes"'))
    with pytest.raises(BundleError, match="auto_select must be a boolean"):
        load_bundle(root)


def test_auto_select_is_allowed_in_any_distribution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = tmp_path / "module"
    _bundle(module / "bundle", "kit", auto_select=True)
    entry = SimpleNamespace(
        name="kit",
        value="kit_module",
        module="kit_module",
        attr=None,
        extras=[],
        dist=SimpleNamespace(metadata={"Name": "devkit-dist"}, version="0.1.0"),
    )
    monkeypatch.setattr(discovery.resources, "files", lambda name: module)
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [entry])
    for package in ("devkit-dist", "devkit-agt"):  # both first-party wheels ship built-in bundles
        entry.dist.metadata["Name"] = package
        with discover_bundles() as found:
            assert found[0].builtin and found[0].auto_selected and found[0].package == package
    entry.dist.metadata["Name"] = "kit-content"
    with discover_bundles() as found:
        assert not found[0].builtin and found[0].auto_selected
        assert found.unusable == {}


# --- auto-selected bundles of other packages ------------------------------------------


@pytest.fixture
def external(tmp_path: Path) -> InstalledBundle:
    return InstalledBundle("ext-content", "0.1.0", load_bundle(_bundle(tmp_path / "ext", "ext", auto_select=True)))


def _codes(result: dict) -> list[str]:
    return [notice["code"] for notice in result["notices"]]


def test_external_auto_selected_bundle_is_deployed_and_announced_once(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    result = sync_project(target, [*bundles, external]).to_dict()
    assert _selection(target) == {"ext": ["core"], "kit": ["core"]}
    notice = next(item for item in result["notices"] if item["code"] == "BUNDLE_AUTO_SELECTED")
    assert notice["message"] == "installed bundles deployed with their default preset: ext"  # not the built-in kit
    assert notice["advisory"]["fix"] == "uv run devkit remove ext"
    assert not (target / CONFIG_PATH).exists()

    assert "BUNDLE_AUTO_SELECTED" not in _codes(sync_project(target, [*bundles, external]).to_dict())


def test_auto_selected_bundle_already_in_the_receipt_is_not_announced(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text('[presets]\next = "more"\n')
    sync_project(target, [*bundles, external])
    (target / CONFIG_PATH).write_text("")
    result = sync_project(target, [*bundles, external]).to_dict()
    assert _selection(target)["ext"] == ["core"]
    assert "BUNDLE_AUTO_SELECTED" not in _codes(result)


def test_external_auto_selected_bundle_opt_out_and_one_run_selection(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG_PATH).write_text("[presets]\next = false\n")
    result = sync_project(target, [*bundles, external]).to_dict()
    assert "ext" not in _selection(target)
    assert "BUNDLE_AUTO_SELECTED" not in _codes(result)
    unselected = next(item for item in result["notices"] if item["code"] == "BUNDLE_UNSELECTED")
    assert unselected["message"] == "installed bundles not selected yet: opt, other"  # an opted-out bundle is not

    (target / CONFIG_PATH).write_text("")
    result = sync_project(target, [*bundles, external], presets={"ext": ["more"]}).to_dict()
    assert _selection(target)["ext"] == ["more"]
    assert "BUNDLE_AUTO_SELECTED" not in _codes(result)


def test_deployed_auto_selected_bundle_whose_package_breaks_is_kept_selected(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    sync_project(target, [*bundles, external])
    deployed = sorted(path for path in (target / ".devkit/managed/ext").rglob("*") if path.is_file())
    broken = Discovered(list(bundles), {"ext": PackageError("ext: cannot read content resources")})

    with pytest.raises(PackageError, match="ext: cannot read content resources"):
        sync_project(target, broken)
    assert _selection(target)["ext"] == ["core"]
    assert deployed and all(path.is_file() for path in deployed)
    status = get_project_status(target, broken)
    assert [error.code for error in status.errors] == ["BUNDLE_PACKAGE_INVALID"]

    update_config(target, opt_out=["ext"])
    sync_project(target, broken)
    assert "ext" not in _selection(target)
    assert not any(path.exists() for path in deployed)


def test_uninstalled_deployed_bundle_is_kept_until_devkit_remove(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sync_project(target, [*bundles, external])
    receipt = (target / RECEIPT_PATH).read_bytes()
    deployed = sorted(path for path in (target / ".devkit/managed/ext").rglob("*") if path.is_file())

    # A partial environment (the package is not installed) never deletes the committed state.
    with pytest.raises(SelectionError, match=r"not installed: ext \(deployed per \.devkit/installation\.json\)"):
        sync_project(target, bundles)
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    assert deployed and all(path.is_file() for path in deployed)

    # `devkit remove` drops it from the receipt without an opt-out entry, so a later install selects it again.
    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", lambda: _found(bundles))
    removed = CliRunner().invoke(cli, ["remove", "ext", "--workspace-root", str(target)])
    assert removed.exit_code == 0, removed.output
    assert "ext" not in _selection(target) and not (target / CONFIG_PATH).exists()
    assert not any(path.exists() for path in deployed)
    sync_project(target, bundles)
    result = sync_project(target, [*bundles, external]).to_dict()
    assert _selection(target)["ext"] == ["core"] and "BUNDLE_AUTO_SELECTED" in _codes(result)


def test_status_reports_a_selected_bundle_whose_package_is_not_installed(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    sync_project(target, [*bundles, external])
    status = get_project_status(target, bundles)  # the package left the environment: sync would refuse
    [error] = status.errors
    assert (error.code, error.exit_code) == ("SELECTION_INVALID", ExitCode.FINDINGS)
    assert error.message == "selected bundle is not installed: ext (deployed per .devkit/installation.json)"
    assert error.fix == "uv run devkit remove ext"
    assert error.target_files == (".devkit/installation.json",)

    update_config(target, presets={"ext": ["core"]})  # selected by an entry: no receipt note
    [error] = get_project_status(target, bundles).errors
    assert error.message == "selected bundle is not installed: ext"
    assert get_project_status(target, [*bundles, external]).errors == []


def test_false_entry_for_an_uninstalled_bundle_is_tolerated(
    bundles: list[InstalledBundle], external: InstalledBundle, target: Path
) -> None:
    sync_project(target, [*bundles, external])
    update_config(target, opt_out=["ext"])
    sync_project(target, bundles)
    assert "ext" not in _selection(target)
    assert not (target / ".devkit/managed/ext").exists()
    result = sync_project(target, [*bundles, external]).to_dict()
    assert "ext" not in _selection(target) and "BUNDLE_AUTO_SELECTED" not in _codes(result)


@contextmanager
def _found(installed: list[InstalledBundle]) -> Iterator[list[InstalledBundle]]:
    yield installed


# --- the real installed distribution -------------------------------------------------


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def _default_selection() -> dict[str, list[str]]:
    with discover_bundles() as installed:
        return {
            bundle.bundle.name: [bundle.bundle.default_preset]
            for bundle in installed
            if bundle.auto_selected and bundle.bundle.default_preset
        }


def test_cli_sync_deploys_the_shipped_builtins(target: Path) -> None:
    _run("sync", "--workspace-root", str(target))
    expected = _default_selection()
    assert _selection(target) == expected  # devkit-starter, when installed, is not auto-selected
    listed = {item["bundle"]: item for item in json.loads(_run("list", "--workspace-root", str(target)))["installed"]}
    assert listed["devkit"]["builtin"] and listed["devkit"]["auto_select"] and listed["devkit"]["selected"] == ["core"]
    assert listed["advisory"]["builtin"] and not listed["advisory"]["opted_out"]
    if "starter" in listed:
        assert not listed["starter"]["builtin"] and listed["starter"]["selected"] is None
    if "spec" in listed:
        assert (
            not listed["spec"]["builtin"] and listed["spec"]["auto_select"] and listed["spec"]["selected"] == ["core"]
        )


def test_cli_remove_persists_false_and_add_clears_it(target: Path) -> None:
    expected = _default_selection()
    without_advisory = {k: v for k, v in expected.items() if k != "advisory"}
    _run("sync", "--workspace-root", str(target))
    _run("remove", "advisory", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": False}
    assert _selection(target) == without_advisory
    listed = {item["bundle"]: item for item in json.loads(_run("list", "--workspace-root", str(target)))["installed"]}
    assert listed["advisory"]["opted_out"] and listed["advisory"]["selected"] is None
    assert json.loads(_run("status", "--workspace-root", str(target)))["opted_out"] == ["advisory"]
    _run("sync", "--workspace-root", str(target))
    assert _selection(target) == without_advisory

    _run("add", "advisory", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": "core"}
    assert _selection(target) == expected

    _run("add", "advisory:python", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": ["core", "python"]}
    assert _selection(target)["advisory"] == ["core", "python"]

    failed = CliRunner().invoke(cli, ["remove", "nothing-here", "--workspace-root", str(target)])
    assert failed.exit_code != 0 and "bundle is not selected" in failed.output


@pytest.mark.skipif(
    importlib.util.find_spec("devkit_agt") is not None,
    reason="devkit-agt is installed: its bundles are built in too",
)
def test_a_standalone_installation_ships_three_built_in_bundles() -> None:
    with discover_bundles() as installed:
        builtin = {item.bundle.name: item.package for item in installed if item.builtin}
    assert builtin == {"advisory": "devkit-dist", "devkit": "devkit-dist", "git-commits": "devkit-dist"}
    assert _default_selection().keys() >= {"advisory", "devkit"} and "harness" not in _default_selection()


@pytest.mark.parametrize("dry_run", [False, True])
def test_public_add_unions_and_sync_replaces_without_transport(
    bundles: list[InstalledBundle], target: Path, monkeypatch: pytest.MonkeyPatch, dry_run: bool
) -> None:
    monkeypatch.setattr("devkit_dist.features.distribution.usecases.commands.discover_bundles", lambda: _found(bundles))
    SyncSelection().execute(target, agents=[], presets={"opt": ["core"]})
    before = (target / CONFIG_PATH).read_bytes()
    added = AddSelection().execute(target, {"opt": ["more"]}, dry_run=dry_run)
    assert list(added.selection.presets["opt"]) == ["core", "more"]
    if dry_run:
        assert (target / CONFIG_PATH).read_bytes() == before
        assert _selection(target)["opt"] == ["core"]
    else:
        assert _config(target)["presets"]["opt"] == ["core", "more"]
        assert _selection(target)["opt"] == ["core", "more"]
    replaced = SyncSelection().execute(target, presets={"opt": ["more"]}, dry_run=dry_run)
    assert list(replaced.selection.presets["opt"]) == ["more"]
    if dry_run:
        assert (target / CONFIG_PATH).read_bytes() == before
    else:
        assert _config(target)["presets"]["opt"] == "more"
        assert _selection(target)["opt"] == ["more"]
