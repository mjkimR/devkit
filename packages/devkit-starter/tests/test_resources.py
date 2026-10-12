import tomllib
from pathlib import Path

import pytest
from devkit.distribution.bundles import load_bundle

PACKAGE = Path(__file__).parents[1]
BUNDLE = PACKAGE / "src/devkit_starter/bundle"
EXAMPLES = Path(__file__).parents[3] / "examples/bundles"


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def test_resource_manifest_and_skill_are_in_package() -> None:
    assert (BUNDLE / "bundle.toml").is_file()
    assert (BUNDLE / "skills/review/SKILL.md").is_file()
    assert (BUNDLE / "instructions/development.md").is_file()
    assert (BUNDLE / "playbooks/review.md").is_file()


def test_the_example_mirror_is_identical_in_both_directions() -> None:
    assert _files(BUNDLE) == _files(EXAMPLES / "starter")


def test_bundle_version_matches_the_package_version() -> None:
    pyproject = tomllib.loads((PACKAGE / "pyproject.toml").read_text())
    assert load_bundle(BUNDLE).version == pyproject["project"]["version"]


@pytest.mark.parametrize("example", sorted(path.name for path in EXAMPLES.iterdir() if path.is_dir()))
def test_example_bundles_load(example: str) -> None:
    bundle = load_bundle(EXAMPLES / example)
    assert bundle.name == example and bundle.default_preset in bundle.presets
