"""Auto-selected built-in bundles are deployed by default; every other bundle needs ``devkit add``."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.core.errors import ConfigError
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.errors import BundleError, PackageError
from devkit.distribution.installation import discovery
from devkit.distribution.installation.config import merge_selection, read_config, update_config
from devkit.distribution.installation.discovery import InstalledBundle, discover_bundles
from devkit.distribution.installation.sync import sync_project
from testsupport.distribution import cli

BUILTINS = {"advisory": ["core"], "devkit": ["core"]}


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


def test_auto_select_is_reserved_for_the_devkit_distribution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = tmp_path / "module"
    _bundle(module / "bundle", "kit", auto_select=True)
    entry = SimpleNamespace(
        name="kit",
        value="kit_module",
        module="kit_module",
        attr=None,
        extras=[],
        dist=SimpleNamespace(metadata={"Name": discovery.BUILTIN_DISTRIBUTION}, version="0.1.0"),
    )
    monkeypatch.setattr(discovery.resources, "files", lambda name: module)
    monkeypatch.setattr(discovery.metadata, "entry_points", lambda **kwargs: [entry])
    with discover_bundles() as found:
        assert found[0].builtin and found[0].auto_selected
    entry.dist.metadata["Name"] = "kit-content"
    with pytest.raises(PackageError, match="auto_select is reserved"), discover_bundles():
        pass


# --- the real installed distribution -------------------------------------------------


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def test_cli_sync_deploys_the_shipped_builtins(target: Path) -> None:
    _run("sync", "--workspace-root", str(target))
    assert _selection(target) == BUILTINS  # devkit-starter, when installed, is not auto-selected
    listed = {item["bundle"]: item for item in json.loads(_run("list", "--workspace-root", str(target)))["installed"]}
    assert listed["devkit"]["builtin"] and listed["devkit"]["auto_select"] and listed["devkit"]["selected"] == ["core"]
    assert listed["advisory"]["builtin"] and not listed["advisory"]["opted_out"]
    if "starter" in listed:
        assert not listed["starter"]["builtin"] and listed["starter"]["selected"] is None


def test_cli_remove_persists_false_and_add_clears_it(target: Path) -> None:
    _run("sync", "--workspace-root", str(target))
    _run("remove", "advisory", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": False}
    assert _selection(target) == {"devkit": ["core"]}
    listed = {item["bundle"]: item for item in json.loads(_run("list", "--workspace-root", str(target)))["installed"]}
    assert listed["advisory"]["opted_out"] and listed["advisory"]["selected"] is None
    assert json.loads(_run("status", "--workspace-root", str(target)))["opted_out"] == ["advisory"]
    _run("sync", "--workspace-root", str(target))
    assert _selection(target) == {"devkit": ["core"]}

    _run("add", "advisory", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": "core"}
    assert _selection(target) == BUILTINS

    _run("add", "advisory:python", "--workspace-root", str(target))
    assert _config(target)["presets"] == {"advisory": ["core", "python"]}
    assert _selection(target)["advisory"] == ["core", "python"]

    failed = CliRunner().invoke(cli, ["remove", "nothing-here", "--workspace-root", str(target)])
    assert failed.exit_code != 0 and "bundle is not selected" in failed.output
