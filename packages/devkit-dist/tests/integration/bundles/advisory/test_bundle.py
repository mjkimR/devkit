from __future__ import annotations

import re
from pathlib import Path

from devkit.advisory import ACTION_TEXT
from devkit_dist.features.distribution.services.bundles import load_bundle

BUNDLE = Path(__file__).parents[4] / "src/devkit_dist/bundles/advisory/bundle"


def test_bundle_presets_split_core_and_python() -> None:
    bundle = load_bundle(BUNDLE)
    assert bundle.name == "advisory"
    assert bundle.default_preset == "core"
    assert bundle.select(["core"]) == {"agent-advisory"}
    assert bundle.select(["python"]) == {"agent-advisory", "agent-advisory-python", "unique-code"}


def test_guide_names_every_mode_and_defers_texts_to_the_runtime() -> None:
    guide = (BUNDLE / "instructions/agent-advisory.md").read_text()
    assert "`devkit.advisory.ACTION_TEXT`" in guide
    for mode in ACTION_TEXT:
        assert f"`{mode.value}`" in guide, mode.value


def test_bundle_version_matches_the_package_version() -> None:
    import tomllib

    pyproject = tomllib.loads((Path(__file__).parents[4] / "pyproject.toml").read_text())
    assert load_bundle(BUNDLE).version == pyproject["project"]["version"]


def test_guides_are_english_only() -> None:
    hangul = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]")
    for guide in sorted((BUNDLE / "instructions").glob("*.md")):
        assert not hangul.search(guide.read_text()), guide.name
