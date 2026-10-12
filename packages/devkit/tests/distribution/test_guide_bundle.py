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


def test_guide_bundle_is_valid_and_instruction_only() -> None:
    bundle = load_bundle(_root())
    assert bundle.name == "devkit"
    assert bundle.default_preset == "core"
    assert bundle.select(["core"]) == set(INSTRUCTIONS)
    assert {asset.kind for asset in bundle.assets} == {"instruction"}
    assert bundle.constitution is not None
    assert len(bundle.constitution.read_text("utf-8").splitlines()) <= 100


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
