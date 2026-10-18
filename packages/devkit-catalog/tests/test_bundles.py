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


@pytest.mark.parametrize("language", ["auto", "ko"])
def test_response_style_deploys_configured_language(tmp_path: Path, language: str) -> None:
    from devkit.distribution.installation.config import update_config
    from devkit.distribution.installation.discovery import InstalledBundle
    from devkit.distribution.installation.sync import sync_project

    bundle = load_bundle(_bundle_root(ENTRY_POINTS["response-style"]))
    update_config(tmp_path, agents=["codex", "claude-code", "antigravity"], presets={"response-style": ["all"]})
    path = tmp_path / ".devkit/config.toml"
    path.write_text(path.read_text() + f'\n[bundles.response-style.variables]\nlanguage = "{language}"\n')
    sync_project(tmp_path, [InstalledBundle("devkit-catalog", PROJECT["version"], bundle)])
    target = tmp_path / ".devkit/managed/response-style/skills/response-style/SKILL.md"
    text = target.read_text()
    assert "{{" not in text and "{%" not in text
    guidance = (tmp_path / "AGENTS.md").read_text()
    assert "read and apply the `response-style` skill" in guidance
    assert ".devkit/managed/response-style/instructions/" not in guidance
    assert ("Use ko as the default" if language == "ko" else "Use the language of the user's current request") in text
    assert "default conversation language" not in guidance
    for directory in (".agents/skills", ".claude/skills"):
        projected = tmp_path / directory / "response-style/SKILL.md"
        assert projected.is_file()
        assert "# Communication" in projected.read_text()
    assert not (tmp_path / ".devkit/managed/response-style/instructions/response-style.md").exists()
