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
    assert "→ **Core sentence.** Explanation" in guidance
    assert "# Reply style" in text
    assert "→ **Core sentence.** Supporting explanation." in text
    assert "Required user and workflow formats take precedence" in text
    assert "return the artifact without conversational framing" in text
    assert "State what is finished and what remains" in text
    assert "Follow repository and task language requirements" in text
    assert (
        "unless the user explicitly requests another language" in text
        if language == "ko"
        else ("unless they explicitly request another language" in text)
    )
    for directory in (".agents/skills", ".claude/skills"):
        projected = tmp_path / directory / "response-style/SKILL.md"
        assert projected.is_file()
        assert projected.read_text() == text
    assert not (tmp_path / ".devkit/managed/response-style/instructions/response-style.md").exists()


def test_response_style_has_one_bounded_guidance_pointer() -> None:
    root = _bundle_root(ENTRY_POINTS["response-style"])
    pointers = list((root / "guidance").glob("*.md"))
    assert len(pointers) == 1
    pointer = pointers[0].read_bytes()
    assert pointer.endswith(b"\n")
    assert len(pointer) <= 300


@pytest.mark.parametrize("preset", ["all", "upkeep", "reporting"])
def test_maintenance_selection_and_independent_lookup(tmp_path: Path, preset: str) -> None:
    from devkit.distribution.installation.config import update_config
    from devkit.distribution.installation.discovery import InstalledBundle
    from devkit.distribution.installation.playbook_search import search_playbooks
    from devkit.distribution.installation.sync import sync_project

    bundle = load_bundle(_bundle_root(ENTRY_POINTS["maintenance"]))
    installed = [InstalledBundle("devkit-catalog", PROJECT["version"], bundle)]
    update_config(tmp_path, agents=["codex"], presets={})
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".devkit/managed/maintenance").exists()
    update_config(tmp_path, agents=["codex"], presets={"maintenance": [preset]})
    sync_project(tmp_path, installed)
    root = tmp_path / ".devkit/managed/maintenance"
    from devkit.distribution.installation.playbook_get import get_playbook

    selected = {
        "all": {"drift-reconciliation", "weekly-report"},
        "upkeep": {"drift-reconciliation"},
        "reporting": {"weekly-report"},
    }[preset]
    assert {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} == {
        "bundle.toml",
        *(f"playbooks/{name}.md" for name in selected),
    }
    for name in selected:
        result = search_playbooks(tmp_path, name.replace("-", " "), mode="lexical")
        assert any(item.id == name and item.bundle == "maintenance" for item in result.results)
        exact = get_playbook(tmp_path, f"maintenance/{name}")
        assert exact.name == name
        assert exact.body.strip()
    assert not (tmp_path / "materials").exists()
    assert not (root / "skills").exists()


def test_maintenance_uses_default_all_and_valid_upkeep() -> None:
    bundle = load_bundle(_bundle_root(ENTRY_POINTS["maintenance"]))
    assert bundle.default_preset == "all"
    assert set(bundle.presets) == {"upkeep", "reporting"}
    assert {asset.id for asset in bundle.assets} == {"drift-reconciliation", "weekly-report"}
