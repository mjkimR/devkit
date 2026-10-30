"""Real deep-research selection, explicit-only projection, role ownership and retention guidance (SPEC-deep-research-bundle)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest
import yaml
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.subagents import read_contract
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
REPOSITORY = PACKAGE.parents[1]
BUNDLE = PACKAGE / "src/devkit_catalog/deep_research/bundle"
INCUBATION = PACKAGE / "src/devkit_catalog/incubation/bundle"
SKILL = BUNDLE / "skills/deep-research/SKILL.md"
MOVED = ("direction-explorer", "discovery-critic", "discovery-planner")
ROLES = {*MOVED, "research-investigator"}
GUARD = "Run only when the user explicitly invokes this entry; never suggest or start it otherwise."
HOSTS = ["codex", "claude-code", "antigravity"]


def _installed(*roots: Path) -> list[InstalledBundle]:
    bundles = [load_bundle(root) for root in roots or (BUNDLE,)]
    return [InstalledBundle("devkit-catalog", bundle.version, bundle) for bundle in bundles]


def _files(root: Path) -> dict[Path, bytes]:
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_requires_explicit_selection_and_deploys_exactly_its_preset(tmp_path: Path) -> None:  # AC-01
    bundle = load_bundle(BUNDLE)
    assert not bundle.auto_select
    assert bundle.default_preset == "core"
    assert set(bundle.presets["core"]) == {"deep-research", *ROLES}
    update_config(tmp_path, agents=HOSTS)
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/deep-research").exists()
    update_config(tmp_path, presets={"deep-research": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/deep-research"
    assert {path.as_posix() for path in _files(managed)} == {
        "bundle.toml",
        "skills/deep-research/SKILL.md",
        "skills/deep-research/references/orchestration.md",
        "skills/deep-research/references/workspace.md",
        "skills/deep-research/references/synthesis.md",
        *(f"subagents/{role}.md" for role in ROLES),
    }
    for role in ROLES:
        projected = tomllib.loads((tmp_path / f".codex/agents/{role}.toml").read_text())
        assert projected["sandbox_mode"] == "workspace-write"
        assert (tmp_path / f".claude/agents/{role}.md").is_file()
        assert (tmp_path / f".agents/agents/{role}.md").is_file()
    for absent in ("docs", "specs", ".devkit/incubation.md", ".devkit/managed/incubation", ".devkit/managed/spec"):
        assert not (tmp_path / absent).exists(), absent


def test_entry_projects_explicit_invocation_for_each_host(tmp_path: Path) -> None:  # AC-02
    update_config(tmp_path, agents=HOSTS, presets={"deep-research": ["core"]})
    sync_project(tmp_path, _installed())
    relative = "skills/deep-research"
    managed = tmp_path / ".devkit/managed/deep-research" / relative
    shared = tmp_path / ".agents" / relative
    claude = tmp_path / ".claude" / relative
    # Codex and Antigravity share the source skill; policy belongs to native projection metadata.
    assert (shared / "SKILL.md").read_bytes() == (managed / "SKILL.md").read_bytes()
    assert yaml.safe_load((shared / "agents/openai.yaml").read_text())["policy"]["allow_implicit_invocation"] is False
    frontmatter = (claude / "SKILL.md").read_text().split("---", 2)[1]
    assert yaml.safe_load(frontmatter)["disable-model-invocation"] is True
    assert not (managed / "agents/openai.yaml").exists()
    for projected in (shared / "SKILL.md", claude / "SKILL.md"):
        body = [line for line in projected.read_text().split("---", 2)[2].splitlines() if line.strip()]
        assert body[:2] == ["# Deep research", GUARD], projected
    description = yaml.safe_load(SKILL.read_text().split("---", 2)[1])["description"]
    assert not re.search(r"\b(use|when|suggest|trigger)\b", description, re.IGNORECASE), description


def test_bundle_text_is_approach_neutral_and_self_contained() -> None:  # AC-03
    text = SKILL.read_text()
    references = set(re.findall(r"`(references/[a-z-]+\.md)`", text))
    assert references == {path.relative_to(SKILL.parent).as_posix() for path in (SKILL.parent / "references").glob("*")}
    for reference in references:
        assert any(reference in line and ("before" in line or "when" in line) for line in text.splitlines())
    for path in BUNDLE.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_text()
        for word in ("configuration.development.approach", ".devkit/incubation.md", "incubation"):
            assert word not in content, (path, word)
        assert not re.search(r"\b(ADR|CAP|UC|US|ARCH|SPEC|MS|PROP|FB)-[a-z]", content), path
        assert len(path.read_bytes()) <= 12288, path


def test_selection_beside_incubation_has_one_owner_per_role(tmp_path: Path) -> None:  # AC-04
    update_config(tmp_path, agents=["codex"], presets={"incubation": ["core"], "deep-research": ["core"]})
    sync_project(tmp_path, _installed(INCUBATION, BUNDLE))
    for role in MOVED:
        assert (tmp_path / f".devkit/managed/deep-research/subagents/{role}.md").is_file()
        assert not (tmp_path / f".devkit/managed/incubation/subagents/{role}.md").exists()
        assert (tmp_path / f".codex/agents/{role}.toml").is_file()
    assert not (tmp_path / ".devkit/managed/incubation/skills/incubate-research").exists()
    assert (tmp_path / ".agents/skills/incubate/SKILL.md").is_file()
    assert (tmp_path / ".agents/skills/deep-research/SKILL.md").is_file()


@pytest.mark.parametrize("role", MOVED)
def test_moved_role_policy_key_follows_the_bundle(tmp_path: Path, role: str) -> None:  # AC-05
    installed = _installed(INCUBATION, BUNDLE)
    update_config(tmp_path, agents=["codex"], presets={"incubation": ["core"], "deep-research": ["core"]})
    sync_project(tmp_path, installed)
    config = tmp_path / ".devkit/config.toml"
    base = config.read_text()
    config.write_text(base + f'\n[subagents.roles."incubation:{role}"]\nlevel = "deep"\n')
    before = _files(tmp_path)
    with pytest.raises(ConfigError, match=f"subagents.roles.incubation:{role}"):
        sync_project(tmp_path, installed)
    assert _files(tmp_path) == before
    config.write_text(base + f'\n[subagents.roles."deep-research:{role}"]\nlevel = "deep"\n')
    sync_project(tmp_path, installed)


def test_roles_keep_optional_execution_and_coordinator_material_ownership() -> None:  # AC-06
    for role in ROLES:
        contract = read_contract((BUNDLE / f"subagents/{role}.md").read_bytes(), "deep-research", role)
        assert contract.hosts["codex"].status == "emulated"
        assert_rule(contract.body, "only", "coordinator", "writes", "retained material")
        assert_rule(contract.body, "index", "HEAD", "unchanged")
        assert_rule(contract.body, "return", "`status`", "source/artifact identity", "failure conditions")
    investigator = (BUNDLE / "subagents/research-investigator.md").read_text()
    assert_rule(investigator, "one question", "team investigation")
    assert_rule(investigator, "payload permits", "experiment", "only", "sandbox/prototype boundary", "assigned scratch")
    orchestration = (SKILL.parent / "references/orchestration.md").read_text()
    assert_rule(orchestration, "effective contract", "`.devkit/managed/deep-research/subagents/`")
    assert_rule(orchestration, "research-investigator", "one question per instance")


def test_retention_contract_and_no_commit_are_stated() -> None:  # AC-07
    skill = SKILL.read_text()
    synthesis = (SKILL.parent / "references/synthesis.md").read_text()
    workspace = (SKILL.parent / "references/workspace.md").read_text()
    assert_rule(
        synthesis, "`uv run devkit docs resolve MAT-<slug>`", "`docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`", "absent"
    )
    assert_rule(synthesis, "`<YYYYMMDD>-<slug>.md`", "`id: MAT-<slug>`", "`created_at`")
    assert_rule(synthesis, "`Status:`", "`complete`", "`partial`", "open questions", "next investigation")
    assert_rule(synthesis, "names a `partial` material", "update that index in place", "never rewrite a `complete`")
    assert_rule(synthesis, "code span", "`MAT-<slug>`", "never copy")
    assert_rule(synthesis, "uncommitted", "git policy")
    assert_rule(workspace, "`.devkit/transient/deep-research/`", "collision-free")
    assert_rule(workspace, "verify", "ignored", "stop allocation")
    assert_rule(skill, "never stage, commit or push", "git policy")
    assert_rule(skill, "committed to the base", "commit it through the project's git policy")


def test_reselection_preserves_retained_material(tmp_path: Path) -> None:
    update_config(tmp_path, agents=["codex"], presets={"deep-research": ["core"]})
    material = tmp_path / "docs/materials/2026-10/20261030-reading/20261030-reading.md"
    material.parent.mkdir(parents=True)
    material.write_text("---\nid: MAT-reading\n---\n\n# [MAT-reading] Reading\n\nStatus: partial\n")
    expected = material.read_bytes()
    sync_project(tmp_path, _installed())
    update_config(tmp_path, opt_out=["deep-research"])
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".agents/skills/deep-research").exists()
    assert not (tmp_path / ".codex/agents/research-investigator.toml").exists()
    update_config(tmp_path, presets={"deep-research": ["core"]})
    sync_project(tmp_path, _installed())
    assert material.read_bytes() == expected


def test_spec_intake_exempts_the_entry_and_proposals_cite_materials() -> None:  # AC-10
    spec = REPOSITORY / "packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec"
    intake = (spec / "SKILL.md.jinja").read_text()
    assert_rule(intake, "explicit `/deep-research` invocation", "not intake", "playbook discovery", "classification")
    assert_rule(intake, "explicit `/deep-research` invocation", "unit", "ordinary intake")
    assert_rule((spec / "references/proposals-catalog.md").read_text(), "`MAT-<slug>`", "code span", "never copied")


def _guidance() -> list[Path]:
    return [*sorted((REPOSITORY / "guides").rglob("*.md")), PACKAGE / "README.md"]


def test_guides_name_the_bundle_only_as_a_selection() -> None:  # AC-09
    allowed = (
        "devkit add deep-research",
        "deep-research:<role>",
        ".devkit/overrides/deep-research/",
        "`CAP-DLV-deep-research`",
    )
    for path in _guidance():
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if "deep-research" in line:
                assert line.startswith("| `deep-research`") or any(token in line for token in allowed), (
                    f"{path.relative_to(REPOSITORY)}:{number}"
                )
            assert "incubate-research" not in line, f"{path.relative_to(REPOSITORY)}:{number}"


def test_guides_name_the_add_command_and_migration_steps() -> None:  # AC-11
    install = REPOSITORY / "guides/INSTALL_GUIDE.md"
    existing = REPOSITORY / "guides/install/existing-repository.md"
    recommendations = REPOSITORY / "guides/install/bundle-recommendations.md"
    for path in (install, existing, recommendations, PACKAGE / "README.md"):
        assert "uv run devkit add deep-research" in path.read_text(), path
    for path in (install, existing, PACKAGE / "README.md"):
        text = path.read_text()
        assert_rule(text, "`incubation:<role>`", "`deep-research:<role>`")
        assert_rule(
            text, "`.devkit/overrides/incubation/subagents/<role>.md`", "`.devkit/overrides/deep-research/subagents/`"
        )
        assert_rule(text, "`ORPHAN_LEFT`", "devkit add deep-research")
    row = next(line for line in recommendations.read_text().splitlines() if line.startswith("| `deep-research`"))
    assert "the user asks for an explicit research entry" in row.lower()
