"""Real incubation asset selection, projection and project-context ownership."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.subagents import read_contract
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
BUNDLE = PACKAGE / "src/devkit_catalog/incubation/bundle"
ROLES = {"product-clarifier", "incubation-researcher", "usage-reviewer"}


def _installed() -> list[InstalledBundle]:
    bundle = load_bundle(BUNDLE)
    return [InstalledBundle("devkit-catalog", bundle.version, bundle)]


def test_incubation_requires_explicit_selection(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex"])
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/incubation").exists()
    assert not (tmp_path / ".agents/skills/incubate/SKILL.md").exists()
    assert not (tmp_path / ".devkit/incubation.md").exists()
    assert not load_bundle(BUNDLE).auto_select


def test_incubation_projects_roles_and_entry_without_seeding_product_state(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex", "claude-code", "antigravity"], presets={"incubation": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/incubation"
    assert (managed / "templates/current-context.md").is_file()
    assert (tmp_path / ".agents/skills/incubate/SKILL.md").read_bytes() == (
        managed / "skills/incubate/SKILL.md"
    ).read_bytes()
    for role in ROLES:
        assert (tmp_path / f".codex/agents/{role}.toml").is_file()
        assert (tmp_path / f".claude/agents/{role}.md").is_file()
        assert (tmp_path / f".agents/agents/{role}.md").is_file()
        projected = tomllib.loads((tmp_path / f".codex/agents/{role}.toml").read_text())
        assert projected["sandbox_mode"] == (
            "read-only" if role in {"product-clarifier", "usage-reviewer"} else "workspace-write"
        )
    assert not (tmp_path / ".devkit/incubation.md").exists()
    assert not (tmp_path / "docs").exists()
    assert not (tmp_path / "specs").exists()
    assert not (tmp_path / ".devkit/managed/spec").exists()


def test_reselection_preserves_project_owned_context_and_settings(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex"], presets={"incubation": ["core"]})
    config = tmp_path / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[presentation]\nlanguage = "ko"\n')
    context = tmp_path / ".devkit/incubation.md"
    context.write_bytes(b"# Household list\nCurrent decision: keep offline use.\nUnverified: two-user merge.\n")
    expected = context.read_bytes()
    roadmap = tmp_path / "docs/materials/initial-roadmap.md"
    roadmap.parent.mkdir(parents=True)
    roadmap.write_text("# Proposed roadmap\nUnknown: shared edit frequency.\n")
    expected_roadmap = roadmap.read_bytes()
    sync_project(tmp_path, _installed())
    update_config(tmp_path, opt_out=["incubation"])
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".agents/skills/incubate/SKILL.md").exists()
    assert not (tmp_path / ".codex/agents/usage-reviewer.toml").exists()
    update_config(tmp_path, presets={"incubation": ["core"]})
    sync_project(tmp_path, _installed())
    assert context.read_bytes() == expected
    assert roadmap.read_bytes() == expected_roadmap
    assert tomllib.loads(config.read_text())["presentation"]["language"] == "ko"


def test_roles_keep_optional_execution_and_coordinator_context_ownership() -> None:
    for role in ROLES:
        content = (BUNDLE / f"subagents/{role}.md").read_bytes()
        contract = read_contract(content, "incubation", role)
        assert contract.hosts["codex"].status == "emulated"
        assert_rule(contract.body, "only", "coordinator", "writes", "`.devkit/incubation.md`")
        assert_rule(contract.body, "index", "HEAD", "unchanged")
        assert_rule(contract.body, "return", "`status`", "source/artifact identity", "failure conditions")
    researcher = (BUNDLE / "subagents/incubation-researcher.md").read_text()
    assert_rule(researcher, "payload permits", "experiment", "only", "sandbox/prototype boundary")


def test_preset_keeps_product_iteration_without_the_research_entry() -> None:  # SPEC-deep-research-bundle AC-04
    bundle = load_bundle(BUNDLE)
    assert set(bundle.presets["core"]) == {"incubate", "incubation-pointer", "current-context-template", *ROLES}
    assert {asset.id for asset in bundle.assets} == set(bundle.presets["core"])


def test_no_file_names_or_suggests_the_research_entry() -> None:  # SPEC-deep-research-bundle AC-09
    for path in BUNDLE.rglob("*"):
        if path.is_file():
            content = path.read_text()
            assert "incubate-research" not in content, path
            assert "deep-research" not in content, path
    for path in (BUNDLE / "skills/incubate/SKILL.md", BUNDLE / "skills/incubate/references/discovery.md"):
        assert "suggest" not in path.read_text().lower(), path
    assert_rule(
        (BUNDLE / "skills/incubate/references/current-context.md").read_text(), "research material", "`MAT-<slug>`"
    )


def test_guidance_is_self_contained_and_references_are_conditional() -> None:
    skill = BUNDLE / "skills/incubate/SKILL.md"
    text = skill.read_text()
    references = set(re.findall(r"`(references/[a-z-]+\.md)`", text))
    assert references == {
        path.relative_to(skill.parent).as_posix() for path in (skill.parent / "references").glob("*.md")
    }
    for reference in references:
        assert any(reference in line and ("before" in line or "when" in line) for line in text.splitlines())
    for path in BUNDLE.rglob("*.md"):
        content = path.read_text()
        assert not re.search(r"\b(ADR|CAP|UC|US|ARCH|SPEC|MS|PROP|FB)-[a-z]", content), path
        assert len(path.read_bytes()) <= 12288, path
    assert "configuration.development.approach" in text
    assert_rule((BUNDLE / "skills/incubate/references/delegation.md").read_text(), "no SDD envelope")
