"""Real adaptive-dev asset selection, projection and project-context ownership."""

from __future__ import annotations

import re
import shutil
import tomllib
from pathlib import Path

import pytest
import yaml
from devkit.advisory import AdvisoryError
from devkit_dist.features.distribution.models.errors import SelectionError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.subagents import read_contract
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
BUNDLE = PACKAGE / "src/devkit_adaptive/bundles/adaptive_dev/bundle"
SWARM = {"swarm-planner", "swarm-worker", "swarm-verifier"}
ROLES = {"product-clarifier", "product-researcher", "usage-reviewer"}
IMPORT = {"adaptive-import", "agent-asset-conversion"}


def _installed() -> list[InstalledBundle]:
    bundle = load_bundle(BUNDLE)
    return [InstalledBundle("devkit-adaptive", bundle.version, bundle)]


def test_adaptive_dev_requires_explicit_selection(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex"])
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/adaptive-dev").exists()
    assert not (tmp_path / ".agents/skills/adaptive-dev/SKILL.md").exists()
    assert not (tmp_path / ".devkit/adaptive-dev.md").exists()
    assert not load_bundle(BUNDLE).auto_select


def test_adaptive_dev_projects_roles_and_entry_without_seeding_product_state(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex", "claude-code", "antigravity"], presets={"adaptive-dev": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/adaptive-dev"
    assert (managed / "templates/current-context.md").is_file()
    assert (tmp_path / ".agents/skills/adaptive-dev/SKILL.md").read_bytes() == (
        managed / "skills/adaptive-dev/SKILL.md"
    ).read_bytes()
    for relative in (
        "references/delegation.md",
        "references/orchestration.md",
        "roles/architect.md",
        "roles/builder.md",
        "roles/qa-tester.md",
        "roles/reviewer.md",
    ):
        source = BUNDLE / "skills/adaptive-dev" / relative
        assert (managed / "skills/adaptive-dev" / relative).read_bytes() == source.read_bytes()
        for projection in (".agents/skills/adaptive-dev", ".claude/skills/adaptive-dev"):
            assert (tmp_path / projection / relative).read_bytes() == source.read_bytes()
    planner = read_contract((BUNDLE / "subagents/swarm-planner.md").read_bytes(), "adaptive-dev", "swarm-planner")
    assert (
        planner.body
        in tomllib.loads((tmp_path / ".codex/agents/swarm-planner.toml").read_text())["developer_instructions"]
    )
    for projection in (".claude/agents/swarm-planner.md", ".agents/agents/swarm-planner.md"):
        assert planner.body.rstrip() in (tmp_path / projection).read_text()
    # The read-only planner disables Antigravity command execution; an unquoted `off` would project as a boolean.
    antigravity = (tmp_path / ".agents/agents/swarm-planner.md").read_text().split("---", 2)[1]
    assert yaml.safe_load(antigravity)["commandExecutionPolicy"] == "off"
    for role in ROLES | SWARM:
        assert (tmp_path / f".codex/agents/{role}.toml").is_file()
        assert (tmp_path / f".claude/agents/{role}.md").is_file()
        assert (tmp_path / f".agents/agents/{role}.md").is_file()
        projected = tomllib.loads((tmp_path / f".codex/agents/{role}.toml").read_text())
        assert projected["sandbox_mode"] == (
            "read-only" if role in {"product-clarifier", "usage-reviewer", "swarm-planner"} else "workspace-write"
        )
    assert (managed / "playbooks/agent-asset-conversion/SKILL.md").is_file()
    for projection in (".agents/skills/adaptive-import", ".claude/skills/adaptive-import"):
        assert (tmp_path / projection / "SKILL.md").is_file()
    assert not (tmp_path / ".devkit/adaptive-dev.md").exists()
    assert not (tmp_path / "docs").exists()
    assert not (tmp_path / "specs").exists()
    assert not (tmp_path / ".devkit/managed/spec").exists()


def test_coordinator_delegates_without_fixed_child_depth_or_budget() -> None:
    skill = BUNDLE / "skills/adaptive-dev"
    assert_rule(
        (BUNDLE / "AGENTS.md").read_text(),
        "main agent",
        "decomposition",
        "delegation",
        "integration",
        "final validation",
        "actively delegate",
        "useful separable work",
    )
    assert_rule(
        (skill / "SKILL.md").read_text(),
        "actively delegate",
        "planning",
        "research",
        "implementation",
        "verification",
        "`references/delegation.md`",
        "before assigning",
        "main agent",
    )
    paths = [skill / "references/delegation.md", skill / "references/orchestration.md"]
    for role in SWARM:
        path = BUNDLE / f"subagents/{role}.md"
        assert_rule(
            path.read_text(), "delegate useful separable work", "narrower authority", "ownership", "return fields"
        )
        paths.append(path)
    for path in paths:
        text = path.read_text()
        for removed_clause in (
            "at most two child levels",
            "remaining depth",
            "Host-wide allowance",
            "leaf delegates no further",
            "depth, allowance",
        ):
            assert removed_clause not in text, path


def test_reselection_preserves_project_owned_context_and_settings(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex"], presets={"adaptive-dev": ["core"]})
    config = tmp_path / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[presentation]\nlanguage = "ko"\n')
    context = tmp_path / ".devkit/adaptive-dev.md"
    context.write_bytes(b"# Household list\nCurrent decision: keep offline use.\nUnverified: two-user merge.\n")
    expected = context.read_bytes()
    roadmap = tmp_path / "docs/materials/initial-roadmap.md"
    roadmap.parent.mkdir(parents=True)
    roadmap.write_text("# Proposed roadmap\nUnknown: shared edit frequency.\n")
    expected_roadmap = roadmap.read_bytes()
    sync_project(tmp_path, _installed())
    update_config(tmp_path, opt_out=["adaptive-dev"])
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".agents/skills/adaptive-dev/SKILL.md").exists()
    assert not (tmp_path / ".codex/agents/usage-reviewer.toml").exists()
    update_config(tmp_path, presets={"adaptive-dev": ["core"]})
    sync_project(tmp_path, _installed())
    assert context.read_bytes() == expected
    assert roadmap.read_bytes() == expected_roadmap
    assert tomllib.loads(config.read_text())["presentation"]["language"] == "ko"


def test_roles_keep_optional_execution_and_coordinator_context_ownership() -> None:
    for role in ROLES:
        content = (BUNDLE / f"subagents/{role}.md").read_bytes()
        contract = read_contract(content, "adaptive-dev", role)
        assert contract.hosts["codex"].status == "emulated"
        assert_rule(contract.body, "only", "Host", "writes", "`.devkit/adaptive-dev.md`")
        assert_rule(contract.body, "index", "HEAD", "unchanged")
        assert_rule(contract.body, "return", "`status`", "source/artifact identity", "failure conditions")
    researcher = (BUNDLE / "subagents/product-researcher.md").read_text()
    assert_rule(researcher, "payload permits", "experiment", "only", "sandbox/prototype boundary")


def test_preset_keeps_product_iteration_without_the_research_entry() -> None:  # SPEC-deep-research-bundle AC-04
    bundle = load_bundle(BUNDLE)
    assert set(bundle.presets["core"]) == {
        "adaptive-dev",
        "adaptive-dev-pointer",
        "current-context-template",
        *ROLES,
        *SWARM,
        *IMPORT,
    }
    assert {asset.id for asset in bundle.assets} == set(bundle.presets["core"])
    assert set(bundle.presets) == {"core", "agents", "import"}
    assert set(bundle.presets["agents"]) == SWARM
    assert set(bundle.presets["import"]) == IMPORT


def test_no_file_names_or_suggests_the_research_entry() -> None:  # SPEC-deep-research-bundle AC-09
    for path in BUNDLE.rglob("*"):
        if path.is_file():
            content = path.read_text()
            assert "incubate-research" not in content, path
            assert "deep-research" not in content, path
    for path in (BUNDLE / "skills/adaptive-dev/SKILL.md", BUNDLE / "skills/adaptive-dev/references/discovery.md"):
        assert "suggest" not in path.read_text().lower(), path
    assert_rule(
        (BUNDLE / "skills/adaptive-dev/references/current-context.md").read_text(), "research material", "`MAT-<slug>`"
    )


def test_guidance_is_self_contained_and_references_are_conditional() -> None:
    skill = BUNDLE / "skills/adaptive-dev/SKILL.md"
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
    assert_rule((BUNDLE / "skills/adaptive-dev/references/delegation.md").read_text(), "no SDD envelope")


def test_bundle_names_only_adaptive_dev() -> None:  # SPEC-rename-incubation-to-adaptive-dev AC-04
    assert load_bundle(BUNDLE).name == "adaptive-dev"
    for path in BUNDLE.rglob("*"):
        if path.is_file():
            assert "incubat" not in path.read_text().lower(), path
    skill = (BUNDLE / "skills/adaptive-dev/SKILL.md").read_text()
    assert "name: adaptive-dev\n" in skill
    assert_rule(skill, "`uv run devkit get-context adaptive-dev`", "`.devkit/adaptive-dev.md`")
    assert '`[development] approach = "adaptive-dev"`' in skill
    pointer = (BUNDLE / "guidance/adaptive-dev-pointer.md").read_text()
    assert_rule(pointer, "`approach=adaptive-dev`", "`/adaptive-dev`")
    entry_points = tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]["entry-points"]["devkit.bundles"]
    assert entry_points["adaptive-dev"] == "devkit_adaptive.bundles.adaptive_dev"
    assert "incubation" not in entry_points


def test_former_incubation_selection_is_refused(tmp_path: Path) -> None:  # SPEC-rename-incubation-to-adaptive-dev AC-04
    update_config(tmp_path, agents=["codex"], presets={"incubation": ["core"]})
    with pytest.raises(SelectionError) as raised:
        sync_project(tmp_path, _installed())
    assert raised.value.code == "SELECTION_INVALID"
    assert not (tmp_path / ".devkit/managed/adaptive-dev").exists()


def test_agents_only_preserves_sdd_and_projects_no_entry(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex", "claude-code", "antigravity"], presets={"adaptive-dev": ["agents"]})
    config = tmp_path / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[development]\napproach = "sdd"\n')
    before_config = config.read_bytes()
    sync_project(tmp_path, _installed())
    assert {p.stem for p in (tmp_path / ".codex/agents").glob("*.toml")} == SWARM
    for role in SWARM:
        projected = tomllib.loads((tmp_path / f".codex/agents/{role}.toml").read_text())
        assert "model" not in projected
        assert "model_reasoning_effort" not in projected
        assert (tmp_path / f".claude/agents/{role}.md").is_file()
        assert (tmp_path / f".agents/agents/{role}.md").is_file()
        contract = read_contract((BUNDLE / f"subagents/{role}.md").read_bytes(), "adaptive-dev", role)
        assert contract.skill is None
        assert contract.hosts["codex"].status == "emulated"
        assert contract.hosts["claude-code"].status == "emulated"
        assert contract.hosts["antigravity"].status == "unverified"
    assert config.read_bytes() == before_config
    assert not (tmp_path / ".agents/skills/adaptive-dev").exists()
    assert not (tmp_path / ".agents/skills/adaptive-import").exists()
    assert not (tmp_path / ".devkit/managed/adaptive-dev/playbooks").exists()
    assert not (tmp_path / ".devkit/managed/adaptive-dev/templates").exists()
    assert not (tmp_path / ".devkit/adaptive-dev.md").exists()
    assert "`/adaptive-dev`" not in (tmp_path / "AGENTS.md").read_text()


def test_extension_model_policy_and_collision_are_transactional(tmp_path: Path) -> None:
    extension = tmp_path / "project-bundle"
    (extension / "subagents").mkdir(parents=True)
    role = "acme-security-reviewer"
    (extension / f"subagents/{role}.md").write_text(
        (BUNDLE / "subagents/swarm-planner.md").read_text().replace("swarm-planner", role)
    )
    (extension / "bundle.toml").write_text(f'''schema = 1
name = "acme-team"
version = "0.1.0"
default_preset = "core"
[[assets]]
id = "{role}"
kind = "subagent"
source = "subagents/{role}.md"
[presets.core]
assets = ["{role}"]
''')
    bundle = load_bundle(extension)
    installed = [*_installed(), InstalledBundle("acme-team", bundle.version, bundle)]
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    update_config(consumer, agents=["codex"], presets={"adaptive-dev": ["agents"], "acme-team": ["core"]})
    config = consumer / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[subagents.roles."adaptive-dev:swarm-worker"]\nlevel = "lean"\n')
    sync_project(consumer, installed)
    worker = tomllib.loads((consumer / ".codex/agents/swarm-worker.toml").read_text())
    assert worker["model"] == "gpt-6.1-terra"
    assert worker["model_reasoning_effort"] == "medium"
    assert (consumer / f".codex/agents/{role}.toml").is_file()
    assert not (consumer / ".agents/skills/adaptive-dev").exists()
    before = {p.name: p.read_bytes() for p in (consumer / ".codex/agents").glob("*")}
    collision = tmp_path / "collision"
    shutil.copytree(extension, collision)
    (collision / "subagents/swarm-worker.md").write_text(
        (collision / f"subagents/{role}.md").read_text().replace(role, "swarm-worker")
    )
    manifest = collision / "bundle.toml"
    manifest.write_text(manifest.read_text().replace("acme-team", "collision-team").replace(role, "swarm-worker"))
    duplicate = load_bundle(collision)
    update_config(consumer, presets={"collision-team": ["core"]})
    with pytest.raises(AdvisoryError) as raised:
        sync_project(consumer, [*installed, InstalledBundle("collision-team", duplicate.version, duplicate)])
    assert raised.value.code == "BUNDLE_CONFLICT"
    assert before == {p.name: p.read_bytes() for p in (consumer / ".codex/agents").glob("*")}


def test_local_role_paths_resolve_from_installed_skill_not_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    update_config(tmp_path, agents=["codex"], presets={"adaptive-dev": ["core"]})
    sync_project(tmp_path, _installed())
    skill = (tmp_path / ".agents/skills/adaptive-dev/SKILL.md").resolve()
    unrelated = tmp_path / "other-working-directory"
    unrelated.mkdir()
    monkeypatch.chdir(unrelated)
    for role in ("architect", "builder", "qa-tester", "reviewer"):
        overlay = (skill.parent / "roles" / f"{role}.md").resolve(strict=True)
        assert overlay.is_absolute()
        assert "caller" in overlay.read_text()
    # Resolving from a loaded reference is a different path and must not be used.
    assert not (skill.parent / "references/roles/builder.md").exists()


def test_distribution_declares_runtime_and_command_entrypoint() -> None:
    metadata = tomllib.loads((PACKAGE / "pyproject.toml").read_text())
    project = metadata["project"]
    sibling = tomllib.loads((PACKAGE.parent / "devkit-docs/pyproject.toml").read_text())["project"]["version"]
    core = tomllib.loads((PACKAGE.parent / "devkit-core/pyproject.toml").read_text())["project"]["version"]
    assert project["name"] == "devkit-adaptive"
    assert set(project["dependencies"]) == {f"devkit-docs=={sibling}", f"devkit-core=={core}", "click>=8.1.7"}
    assert not any("devkit-spec" in requirement for requirement in project["dependencies"])
    assert project["entry-points"] == {
        "devkit.bundles": {"adaptive-dev": "devkit_adaptive.bundles.adaptive_dev"},
        "devkit.commands": {"adaptive": "devkit_adaptive.cli:cli"},
    }
