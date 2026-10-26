"""The development bundle is loadable through the same manifest reader as consumers."""

import tomllib
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle


def test_bundle_loads_with_its_declared_default_preset() -> None:
    package = Path(__file__).resolve().parents[2]
    project = tomllib.loads((package / "pyproject.toml").read_text())["project"]
    bundle = load_bundle(package / "src/devkit_dev/bundle")
    assert bundle.name == "devkit-dev"
    assert bundle.version == project["version"]
    assert bundle.default_preset == "structure"
    assert bundle.default_preset in bundle.presets
    assert {asset.id for asset in bundle.assets} == {
        "project-structure",
        "testing",
        "architecture",
        "usecase-boundaries",
        "handbook",
    }
    assert bundle.presets["handbook"] == ("handbook",)
    assert project["dependencies"] == []


def test_handbook_playbook_names_the_refresh_procedure() -> None:
    package = Path(__file__).resolve().parents[2]
    text = (package / "src/devkit_dev/bundle/playbooks/handbook.md").read_text()
    for step in ("just handbook status", "just handbook stamp", "just handbook generate", "just handbook verify"):
        assert step in text
    assert text.index("just handbook verify") < text.index("Human review")
    assert "before the `just version-sync` metadata commit and the tag" in text
    assert "Record the review in the completion report" in text
