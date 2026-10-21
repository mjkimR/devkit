"""The development bundle is loadable through the same manifest reader as consumers."""

import tomllib
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle


def test_bundle_loads_with_its_declared_default_preset() -> None:
    package = Path(__file__).resolve().parents[1]
    project = tomllib.loads((package / "pyproject.toml").read_text())["project"]
    bundle = load_bundle(package / "src/devkit_dev/bundle")
    assert bundle.name == "devkit-dev"
    assert bundle.version == project["version"]
    assert bundle.default_preset == "structure"
    assert bundle.default_preset in bundle.presets
    assert {asset.id for asset in bundle.assets} == {"project-structure", "architecture"}
    assert project["dependencies"] == []
