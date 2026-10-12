"""Built-in bundles (shipped by the ``devkit`` distribution) are selected by default; others need ``devkit add``."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.distribution.bundles import BundleError, load_bundle
from devkit.distribution.cli import cli
from devkit.distribution.installation import discovery
from devkit.distribution.installation.config import read_config, update_config
from devkit.distribution.installation.discovery import InstalledBundle, discover_bundles
from devkit.distribution.installation.sync import sync_project
from devkit.distribution.installation.workspace import CONFIG, RECEIPT

BUILTINS = {"advisory": ["core"], "devkit": ["core"]}


def _bundle(root: Path, name: str, *, default_preset: str | None = "core") -> Path:
    root.mkdir(parents=True)
    (root / "guide.md").write_text("---\nname: guide\ndescription: A guide.\n---\nBody.\n")
    default = f'default_preset = "{default_preset}"\n' if default_preset else ""
    (root / "bundle.toml").write_text(
        f'schema = 1\nname = "{name}"\nversion = "0.1.0"\n{default}'
        '[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "guide.md"\n'
        '[presets.core]\nassets = ["guide"]\n'
    )
    return root


@pytest.fixture
def bundles(tmp_path: Path) -> list[InstalledBundle]:
    return [
        InstalledBundle("devkit", "0.1.0", load_bundle(_bundle(tmp_path / "builtin", "kit")), builtin=True),
        InstalledBundle("other-content", "0.1.0", load_bundle(_bundle(tmp_path / "external", "other"))),
    ]


@pytest.fixture
def target(tmp_path: Path) -> Path:
    path = tmp_path / "consumer"
    path.mkdir()
    return path


def _selection(root: Path) -> dict[str, list[str]]:
    return json.loads((root / RECEIPT).read_text())["selection"]["presets"]


def _config(root: Path) -> dict:
    return tomllib.loads((root / CONFIG).read_text())


def test_empty_project_gets_builtins_but_not_external_bundles(bundles: list[InstalledBundle], target: Path) -> None:
    result = sync_project(target, bundles)
    assert _selection(target) == {"kit": ["core"]}
    assert [item["bundle"] for item in result["unselected"]] == ["other"]  # type: ignore[union-attr]
    assert not (target / CONFIG).exists()


def test_config_false_opts_out_and_a_named_preset_replaces_the_default(
    bundles: list[InstalledBundle], target: Path
) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG).write_text("[presets]\nkit = false\n")
    sync_project(target, bundles)
    assert not (target / RECEIPT).exists() or _selection(target) == {}
    assert read_config(target).opted_out == frozenset({"kit"})

    (target / CONFIG).write_text('[presets]\nkit = "all"\nother = "core"\n')
    sync_project(target, bundles)
    assert _selection(target) == {"kit": ["all"], "other": ["core"]}


def test_one_run_selection_overrides_an_opt_out(bundles: list[InstalledBundle], target: Path) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG).write_text("[presets]\nkit = false\n")
    sync_project(target, bundles, presets={"kit": ["core"]})
    assert _selection(target) == {"kit": ["core"]}


@pytest.mark.parametrize("value", ["true", "[]", '""'])
def test_invalid_preset_values_are_rejected(target: Path, value: str) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG).write_text(f"[presets]\nkit = {value}\n")
    with pytest.raises(BundleError, match="invalid presets"):
        read_config(target)


def test_update_config_opt_out_and_reselect(target: Path) -> None:
    (target / ".devkit").mkdir()
    (target / CONFIG).write_text('# keep\n[presets]\nother = "core"\n')
    update_config(target, deselect=["other"], opt_out=["kit"])
    assert _config(target)["presets"] == {"kit": False}
    assert "# keep" in (target / CONFIG).read_text()
    update_config(target, presets={"kit": ["core"]})
    assert _config(target)["presets"] == {"kit": "core"}


def test_builtin_without_default_preset_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = tmp_path / "module"
    _bundle(module / "bundle", "kit", default_preset=None)
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
    with pytest.raises(BundleError, match="must declare default_preset"), discover_bundles():
        pass
    entry.dist.metadata["Name"] = "kit-content"
    with discover_bundles() as found:
        assert not found[0].builtin


# --- the real installed distribution -------------------------------------------------


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def test_cli_sync_deploys_the_shipped_builtins(target: Path) -> None:
    _run("sync", "--workspace-root", str(target))
    assert _selection(target) == BUILTINS  # devkit-starter, when installed, is not auto-selected
    listed = {item["bundle"]: item for item in json.loads(_run("list", "--workspace-root", str(target)))["installed"]}
    assert listed["devkit"]["builtin"] and listed["devkit"]["selected"] == ["core"]
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

    failed = CliRunner().invoke(cli, ["remove", "nothing-here", "--workspace-root", str(target)])
    assert failed.exit_code != 0 and "bundle is not selected" in failed.output
