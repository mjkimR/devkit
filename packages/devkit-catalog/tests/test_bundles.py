import tomllib
from pathlib import Path

import pytest
from devkit.distribution.bundles import load_bundle

PACKAGE = Path(__file__).parents[1]
SOURCE = PACKAGE / "src"
PROJECT = tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]
ENTRY_POINTS: dict[str, str] = PROJECT["entry-points"]["devkit.bundles"]
DEVKIT_PROJECT = tomllib.loads((PACKAGE.parent / "devkit/pyproject.toml").read_text())["project"]


def _bundle_root(module: str) -> Path:
    return SOURCE.joinpath(*module.split(".")) / "bundle"


@pytest.mark.parametrize("name", sorted(ENTRY_POINTS))
def test_registered_bundle_loads_under_its_entry_point_name(name: str) -> None:
    bundle = load_bundle(_bundle_root(ENTRY_POINTS[name]))
    assert bundle.name == name
    assert bundle.version == PROJECT["version"]


@pytest.mark.parametrize("name", sorted(ENTRY_POINTS))
def test_catalog_bundle_is_opt_in_with_a_default_preset(name: str) -> None:
    bundle = load_bundle(_bundle_root(ENTRY_POINTS[name]))
    assert not bundle.auto_select, "catalog bundles are deployed only once a project selects them"
    assert bundle.default_preset is not None, "`devkit add <bundle>` must work without naming a preset"


def test_every_bundle_directory_is_registered() -> None:
    found = {path.parent for path in SOURCE.rglob("bundle/bundle.toml")}
    assert found == {_bundle_root(module) for module in ENTRY_POINTS.values()}


def test_catalog_names_do_not_collide_with_devkit_builtins() -> None:
    assert not set(ENTRY_POINTS) & set(DEVKIT_PROJECT["entry-points"]["devkit.bundles"])
