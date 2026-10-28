import re
import tomllib
from pathlib import Path

import pytest
from devkit_dist.features.distribution.services.bundles import load_bundle

PACKAGE = Path(__file__).parents[3]
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
    from devkit_dist.features.distribution.services.installation.config import update_config
    from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
    from devkit_dist.features.distribution.usecases.sync import sync_project

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
    assert "return it without framing" in text
    assert "state what is finished and what remains" in text
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


MAINTENANCE_PRESETS = {
    "all": {"drift-reconciliation", "weekly-report", "review-refactor", "performance-pass"},
    "upkeep": {"drift-reconciliation", "review-refactor"},
    "reporting": {"weekly-report"},
    "refactoring": {"review-refactor"},
    "performance": {"performance-pass", "review-refactor"},
}
REVIEW_REFACTOR = ("SKILL.md", "references/applying.md", "references/criteria.md")
PERFORMANCE_PASS = (
    "SKILL.md",
    "references/measurement.md",
    "references/profiling.md",
    "references/candidates.md",
    "references/changes.md",
)
DIRECTORY_PLAYBOOKS = {"review-refactor": REVIEW_REFACTOR, "performance-pass": PERFORMANCE_PASS}


def _maintenance_files(name: str) -> set[str]:
    if name in DIRECTORY_PLAYBOOKS:
        return {f"playbooks/{name}/{part}" for part in DIRECTORY_PLAYBOOKS[name]}
    return {f"playbooks/{name}.md"}


@pytest.mark.parametrize("preset", sorted(MAINTENANCE_PRESETS))
def test_maintenance_selection_and_independent_lookup(
    tmp_path: Path, preset: str
) -> None:  # SPEC-review-refactor AC-02
    from devkit_dist.features.distribution.services.installation.config import update_config
    from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
    from devkit_dist.features.distribution.usecases.playbook_get import GetPlaybook
    from devkit_dist.features.distribution.usecases.playbook_search import SearchPlaybooks
    from devkit_dist.features.distribution.usecases.sync import sync_project

    bundle = load_bundle(_bundle_root(ENTRY_POINTS["maintenance"]))
    installed = [InstalledBundle("devkit-catalog", PROJECT["version"], bundle)]
    update_config(tmp_path, agents=["codex"], presets={})
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".devkit/managed/maintenance").exists()
    update_config(tmp_path, agents=["codex"], presets={"maintenance": [preset]})
    sync_project(tmp_path, installed)
    root = tmp_path / ".devkit/managed/maintenance"
    selected = MAINTENANCE_PRESETS[preset]
    assert {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} == {
        "bundle.toml",
        *(file for name in selected for file in _maintenance_files(name)),
    }
    for name in selected:
        result = SearchPlaybooks().execute(tmp_path, name.replace("-", " "), mode="lexical")
        assert any(item.id == name and item.bundle == "maintenance" for item in result.results)
        exact = GetPlaybook().execute(tmp_path, f"maintenance/{name}")
        assert exact.name == name
        assert exact.body.strip()
    assert not (tmp_path / "materials").exists()
    assert not (root / "skills").exists()


def test_maintenance_uses_default_all_and_valid_presets() -> None:  # SPEC-review-refactor AC-01
    bundle = load_bundle(_bundle_root(ENTRY_POINTS["maintenance"]))
    assert bundle.default_preset == "all"
    assert {name: set(assets) for name, assets in bundle.presets.items()} == {
        name: assets for name, assets in MAINTENANCE_PRESETS.items() if name != "all"
    }
    assert {asset.id for asset in bundle.assets} == MAINTENANCE_PRESETS["all"]
    asset = next(asset for asset in bundle.assets if asset.id == "review-refactor")
    assert (asset.kind, asset.sources) == ("playbook", (("common", "playbooks/review-refactor"),))
    # SPEC-performance-pass AC-01
    asset = next(asset for asset in bundle.assets if asset.id == "performance-pass")
    assert (asset.kind, asset.sources) == ("playbook", (("common", "playbooks/performance-pass"),))


def _playbook_root(name: str) -> Path:
    return _bundle_root(ENTRY_POINTS["maintenance"]) / "playbooks" / name


def _review_refactor_root() -> Path:
    return _playbook_root("review-refactor")


def _collapsed(text: str) -> str:
    return " ".join(text.split())


def _description_and_body(root: Path) -> tuple[str, str]:
    header, body = (root / "SKILL.md").read_text().split("\n---\n", 1)
    return _collapsed(header.split("description:", 1)[1]), _collapsed(body)


def _assert_self_contained_within_budget(root: Path, expected: tuple[str, ...]) -> dict[str, Path]:
    files = {path.relative_to(root).as_posix(): path for path in root.rglob("*.md")}
    assert set(files) == set(expected)
    for name, path in files.items():
        data = path.read_bytes()
        assert len(data) <= 12288, name
        assert not re.search(rb"\b(ADR|CAP|UC|US|ARCH|SPEC|MS|PROP|FB)-[a-z]", data), name
    linked = set(re.findall(r"`(references/[a-z-]+\.md)`", files["SKILL.md"].read_text()))
    assert linked == {name for name in files if name.startswith("references/")}
    return files


def test_review_refactor_entry_condition_and_description() -> None:  # SPEC-review-refactor AC-03
    description, body = _description_and_body(_review_refactor_root())
    assert "review and refactoring pass over user-selected code, agent guidance or CLI command roots" in description
    assert "consolidates duplicated logic and removes unneeded code" in description
    assert "Run only when the user invoked or confirmed this playbook" in body
    assert "`devkit playbook get maintenance/review-refactor`" in body
    assert "authorize no change" in body
    assert "an unattended run stops at the decision round with nothing applied" in body


def test_review_refactor_is_self_contained_and_within_budget() -> None:  # SPEC-review-refactor AC-04
    _assert_self_contained_within_budget(_review_refactor_root(), REVIEW_REFACTOR)


def _maintenance_preset_assets() -> dict[str, set[str]]:
    bundle = load_bundle(_bundle_root(ENTRY_POINTS["maintenance"]))
    presets = {name: set(assets) for name, assets in bundle.presets.items()}
    return {**presets, "all": {asset.id for asset in bundle.assets}}


def test_performance_pass_is_always_deployed_with_review_refactor() -> None:  # SPEC-performance-pass AC-02
    presets = _maintenance_preset_assets()
    assert any("performance-pass" in assets for assets in presets.values())
    for name, assets in presets.items():
        if "performance-pass" in assets:
            assert "review-refactor" in assets, name


REQUIRED_REVIEW_REFACTOR_CITATIONS = {
    ("references/applying.md", heading)
    for heading in (
        "Work items and route",
        "Branch and edit tasks",
        "Subagent edits",
        "Commits and verification",
        "Review",
        "Report",
        "Integration",
        "Contract removals",
    )
} | {("references/criteria.md", "Preservation evidence")}


def _headings(path: Path) -> set[str]:
    return {
        re.sub(r"^\d+(\.\d+)*\.? ", "", line.lstrip("#").strip())
        for line in path.read_text().splitlines()
        if re.match(r"^#+ ", line)
    }


def test_performance_pass_cites_existing_review_refactor_headings() -> None:  # SPEC-performance-pass AC-03
    citations = {
        match
        for path in _playbook_root("performance-pass").rglob("*.md")
        for match in re.findall(r'review-refactor (references/[a-z-]+\.md) "([^"]+)"', _collapsed(path.read_text()))
    }
    assert not REQUIRED_REVIEW_REFACTOR_CITATIONS - citations, REQUIRED_REVIEW_REFACTOR_CITATIONS - citations
    for file, heading in citations:
        assert heading in _headings(_review_refactor_root() / file), (file, heading)


def test_performance_pass_entry_condition_and_description() -> None:  # SPEC-performance-pass AC-04
    description, body = _description_and_body(_playbook_root("performance-pass"))
    assert "performance pass over user-selected slow commands or operations" in description
    assert "behavior-preserving speedups" in description
    assert "Run only when the user invoked or confirmed this playbook" in body
    assert "`devkit playbook get maintenance/performance-pass`" in body
    assert "authorize no change" in body
    assert "an unattended run stops at the decision round with nothing applied" in body


def test_performance_pass_is_self_contained_and_within_budget() -> None:  # SPEC-performance-pass AC-05
    root = _playbook_root("performance-pass")
    files = _assert_self_contained_within_budget(root, PERFORMANCE_PASS)
    assert {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} == set(PERFORMANCE_PASS)
    references = [name for name in PERFORMANCE_PASS if name.startswith("references/")]
    for name in references:
        text = files[name].read_text()
        assert not [other for other in references if other != name and other in text], name


def test_cli_tool_deploys_its_guide_and_rules_only_when_selected(tmp_path: Path) -> None:  # SPEC-cli-toolkit AC-12
    from devkit_agt.features.rules import RuleRegistry, resolve_managed_rules
    from devkit_dist.features.distribution.services.installation.config import update_config
    from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
    from devkit_dist.features.distribution.usecases.sync import sync_project

    installed = [
        InstalledBundle("devkit-catalog", PROJECT["version"], load_bundle(_bundle_root(ENTRY_POINTS["cli-tool"])))
    ]
    update_config(tmp_path, agents=["codex"])
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".devkit/managed/cli-tool").exists()

    update_config(tmp_path, agents=["codex"], presets={"cli-tool": ["all"]})
    sync_project(tmp_path, installed)
    managed = tmp_path / ".devkit/managed/cli-tool"
    assert (managed / "instructions/cli-tool-structure.md").is_file()
    rules = resolve_managed_rules(tmp_path)
    registry = RuleRegistry()
    registry.discover_from_packages(rules.packages)
    assert not rules.errors and not registry.errors
    assert {rule.id for rule in registry.get_all()} == {
        "RULE-cli-tool-layout",
        "RULE-cli-tool-layers",
        "RULE-cli-tool-command-boundary",
        "RULE-cli-tool-library-output",
        "RULE-cli-tool-heavy-imports",
    }


def test_cli_tool_guide_preset_has_no_rules() -> None:
    bundle = load_bundle(_bundle_root(ENTRY_POINTS["cli-tool"]))
    assert bundle.default_preset == "all"
    assert tuple(bundle.presets["guide"]) == ("cli-tool-structure",)
