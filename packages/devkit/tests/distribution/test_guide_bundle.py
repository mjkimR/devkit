"""The ``devkit`` guide bundle shipped inside devkit."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from devkit.distribution.bundles import load_bundle
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.sync import sync_project

INSTRUCTIONS = ["consumption", "devkit-run", "in-repo-bundle", "resource-kinds"]


def _root() -> Path:
    path = resources.files("devkit.distribution.guide").joinpath("bundle")
    assert isinstance(path, Path)
    return path


def test_guide_bundle_is_valid_and_its_default_is_instruction_only() -> None:
    bundle = load_bundle(_root())
    assert bundle.name == "devkit"
    assert bundle.default_preset == "core"
    assert bundle.select(["core"]) == set(INSTRUCTIONS)
    kinds = {asset.id: asset.kind for asset in bundle.assets}
    assert {kinds[asset] for asset in bundle.select(["core"])} == {"instruction"}  # nothing in AGENTS.md by default
    assert bundle.select(["run"]) == {"devkit-run", "run-pointer"} and kinds["run-pointer"] == "guidance"
    assert bundle.constitution is not None
    constitution = bundle.constitution.read_text("utf-8")
    assert len(constitution.splitlines()) <= 100
    # get-context returns the instruction catalog next to the constitution; the constitution does not repeat it.
    assert not any(f"`{name}`:" in constitution for name in INSTRUCTIONS)


def test_run_preset_adds_one_agents_md_line_pointing_at_devkit_run(tmp_path: Path) -> None:
    bundle = load_bundle(_root())
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core", "run"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit", "0.1.0", bundle)])
    block = (target / "AGENTS.md").read_text()
    [line] = [line for line in block.splitlines() if "devkit run" in line]
    assert line.startswith("- Run tests, linters and type checks as `uv run devkit run -- <command>`")
    assert "`.devkit/managed/devkit/instructions/devkit-run.md`" in line


def test_guide_bundle_context_delivers_constitution_and_headers(tmp_path: Path) -> None:
    bundle = load_bundle(_root())
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit", "0.1.0", bundle)])
    context = get_context(target, "devkit").to_dict()
    assert context["constitution"] and "devkit get-context <bundle>" in context["constitution"]
    headers = {entry["header"].split("\n", 1)[0] for entry in context["instructions"]}
    assert headers == {f"name: {name}" for name in INSTRUCTIONS}
    for entry in context["instructions"]:
        header = entry["header"]
        assert "description: Read before" in header
        assert header.isascii(), header
        assert Path(entry["path"]).is_file()


def test_an_unsynchronized_bundle_names_a_runnable_fix_and_the_synchronized_bundles(tmp_path: Path) -> None:
    import pytest
    from devkit.distribution.errors import SelectionError

    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit", "0.1.0", load_bundle(_root()))])
    with pytest.raises(SelectionError) as raised:
        get_context(target, "nope")
    # One exact command, never a guess such as `devkit add nope` for a name that may not exist.
    assert raised.value.fix == "devkit list"
    assert raised.value.details == ("synchronized bundles: devkit",)
