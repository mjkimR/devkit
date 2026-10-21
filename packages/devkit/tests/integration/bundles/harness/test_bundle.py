"""The built-in ``harness`` bundle of devkit-agt: the harness and ``devkit run`` guidance that left ``devkit``.

It is auto-selected and built in wherever devkit-agt is installed (``ADR-dist-bundles-compatibility``).
"""

from __future__ import annotations

import json
import re
import shutil
import tomllib
from importlib import resources
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.cli import cli
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle, discover_bundles
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.override_commands import create_override
from devkit_dist.features.distribution.usecases.sync import sync_project

PACKAGE = Path(__file__).parents[4]
BUNDLE = PACKAGE / "src/devkit_agt/bundles/harness/bundle"
INSTRUCTIONS = ["devkit-run", "harness-assets", "harness-consumption"]


def _devkit_root() -> Path:
    path = resources.files("devkit_dist.bundles.devkit").joinpath("bundle")
    assert isinstance(path, Path)
    return path


def test_the_bundle_is_auto_selected_with_its_core_preset() -> None:
    bundle = load_bundle(BUNDLE)
    assert (bundle.name, bundle.default_preset, bundle.auto_select) == ("harness", "core", True)
    assert bundle.preset_names == ["all", "core", "run"]
    assert bundle.select(["core"]) == set(INSTRUCTIONS)
    assert bundle.select(["run"]) == {"devkit-run", "run-pointer"}
    kinds = {asset.id: asset.kind for asset in bundle.assets}
    assert {kinds[asset] for asset in bundle.select(["core"])} == {"instruction"}  # nothing in AGENTS.md by default
    assert kinds["run-pointer"] == "guidance"
    assert bundle.version == tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]["version"]


def test_the_constitution_holds_the_harness_contracts() -> None:
    constitution = (BUNDLE / "AGENTS.md").read_text("utf-8")
    contracts = re.findall(r"^\d+\. \*\*(.+?)\*\*", constitution, re.MULTILINE)
    assert contracts == ["Rules and gates run as code.", "Snapshot gates trust the committed receipt."]
    assert "`[rules]` and `[gates]`" in constitution
    assert "`devkit rules check --staged`, `--ci`" in constitution
    assert len(constitution.splitlines()) <= 100


def test_discovery_reports_both_wheels_bundles_as_built_in() -> None:
    with discover_bundles() as installed:
        builtin = {item.bundle.name: item.package for item in installed if item.builtin}
        harness = next(item for item in installed if item.bundle.name == "harness")
    assert builtin == {
        "advisory": "devkit-dist",
        "authoring": "devkit-agt",
        "devkit": "devkit-dist",
        "git-commits": "devkit-dist",
        "harness": "devkit-agt",
    }
    assert harness.auto_selected and harness.bundle.default_preset == "core"


def test_a_fresh_sync_deploys_harness_without_an_auto_selected_notice(tmp_path: Path) -> None:
    result = CliRunner().invoke(cli, ["sync", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    receipt = json.loads((tmp_path / ".devkit/installation.json").read_text())
    assert receipt["selection"]["presets"]["harness"] == ["core"]
    assert receipt["tool"]["package"] == "devkit-dist"
    packages = {record["bundle"]: record["package"] for record in receipt["packages"]}
    assert packages["harness"] == "devkit-agt" and packages["devkit"] == "devkit-dist"
    notices = [notice for notice in payload["notices"] if notice["code"] == "BUNDLE_AUTO_SELECTED"]
    assert not any("harness" in notice["message"] for notice in notices)
    assert all(notice["code"] != "HARNESS_ENGINE_MISSING" for notice in payload["notices"])
    listed = json.loads(CliRunner().invoke(cli, ["list", "-w", str(tmp_path)]).stdout)["installed"]
    entry = next(item for item in listed if item["bundle"] == "harness")
    assert (entry["package"], entry["builtin"], entry["auto_select"], entry["default_preset"]) == (
        "devkit-agt",
        True,
        True,
        "core",
    )


def test_the_run_preset_adds_one_agents_md_line_pointing_at_devkit_run(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"harness": ["run"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit-agt", "0.1.0", load_bundle(BUNDLE))])
    assert (target / ".devkit/managed/harness/instructions/devkit-run.md").is_file()
    block = (target / "AGENTS.md").read_text()
    [line] = [line for line in block.splitlines() if "devkit run" in line]
    assert line.startswith("- Run tests, linters and type checks as `uv run devkit run -- <command>`")
    assert "`.devkit/managed/harness/instructions/devkit-run.md`" in line


def test_the_context_delivers_the_moved_guidance(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"harness": ["core"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit-agt", "0.1.0", load_bundle(BUNDLE))])
    context = GetContext().execute(target, "harness").to_dict()
    assert "Rules and gates run as code" in context["constitution"]
    headers = {entry["header"].split("\n", 1)[0] for entry in context["instructions"]}
    assert headers == {f"name: {name}" for name in INSTRUCTIONS}
    bodies = "\n".join(Path(entry["path"]).read_text() for entry in context["instructions"])
    for moved in ("devkit workflow next", "devkit rules check --staged", ".git/devkit.config", "--rules-dir"):
        assert moved in bodies
    for entry in context["instructions"]:
        assert "description: Read before" in entry["header"] and entry["header"].isascii()


def test_an_override_of_a_moved_asset_stops_applying_and_is_recreated_in_harness(tmp_path: Path) -> None:
    # The devkit bundle as it was before the split: devkit-run lived in it.
    old = tmp_path / "old-devkit"
    shutil.copytree(_devkit_root(), old)
    shutil.copy(BUNDLE / "instructions/devkit-run.md", old / "instructions/devkit-run.md")
    manifest = old / "bundle.toml"
    manifest.write_text(
        manifest.read_text().replace(
            'assets = ["consumption", "resource-kinds", "in-repo-bundle"]',
            'assets = ["consumption", "resource-kinds", "in-repo-bundle", "devkit-run"]',
        )
        + '\n[[assets]]\nid = "devkit-run"\nkind = "instruction"\nsource = "instructions/devkit-run.md"\n'
    )
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=[])
    before = [InstalledBundle("devkit-agt", "0.1.1", load_bundle(old))]
    sync_project(target, before)
    create_override(target, before, "devkit:devkit-run")
    override = target / ".devkit/overrides/devkit/instructions/devkit-run.md"
    override.write_text(override.read_text() + "\nProject note.\n")
    sync_project(target, before)

    after = [
        InstalledBundle("devkit-dist", "0.1.1", load_bundle(_devkit_root())),
        InstalledBundle("devkit-agt", "0.1.1", load_bundle(BUNDLE)),
    ]
    update_config(target, presets={"devkit": ["core"], "harness": ["core"]})
    sync_project(target, after)
    managed = target / ".devkit/managed/harness/instructions/devkit-run.md"
    assert managed.read_bytes() == (BUNDLE / "instructions/devkit-run.md").read_bytes()  # upstream, not the override
    assert "Project note." in override.read_text()  # the project's file is left in place
    assert not (target / ".devkit/managed/devkit/instructions/devkit-run.md").exists()
    create_override(target, after, "harness:devkit-run")
    assert (target / ".devkit/overrides/harness/instructions/devkit-run.md").is_file()
