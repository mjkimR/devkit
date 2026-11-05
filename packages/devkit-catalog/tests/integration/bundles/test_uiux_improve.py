"""Opt-in UI/UX skill deployment and its instruction boundaries (SPEC-ux-design-exploration)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
BUNDLE = PACKAGE / "src/devkit_catalog/uiux_improve/bundle"
SKILL = BUNDLE / "skills/uiux-improve"
ROLES = {"designer", "unconventional-designer", "reference-researcher", "critic"}
HOSTS = ["codex", "claude-code", "antigravity"]


def _installed() -> list[InstalledBundle]:
    bundle = load_bundle(BUNDLE)
    return [InstalledBundle("devkit-catalog", bundle.version, bundle)]


def test_explicit_selection_projects_local_roles_and_user_only_entry(tmp_path: Path) -> None:  # AC-01
    update_config(tmp_path, agents=HOSTS)
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/uiux-improve").exists()
    update_config(tmp_path, presets={"uiux-improve": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/uiux-improve"
    assert {p.relative_to(managed).as_posix() for p in managed.rglob("*") if p.is_file()} == {
        "bundle.toml",
        "skills/uiux-improve/SKILL.md",
        "skills/uiux-improve/references/orchestration.md",
        "skills/uiux-improve/references/design-guidance.md",
        *(f"skills/uiux-improve/roles/{role}.md" for role in ROLES),
    }
    shared = tmp_path / ".agents/skills/uiux-improve"
    claude = tmp_path / ".claude/skills/uiux-improve"
    assert (shared / "SKILL.md").read_bytes() == (SKILL / "SKILL.md").read_bytes()
    assert yaml.safe_load((shared / "agents/openai.yaml").read_text())["policy"]["allow_implicit_invocation"] is False
    assert yaml.safe_load((claude / "SKILL.md").read_text().split("---", 2)[1])["disable-model-invocation"] is True
    for role in ROLES:
        assert (shared / f"roles/{role}.md").is_file()
        assert (claude / f"roles/{role}.md").is_file()
        for directory, suffix in ((".codex/agents", "toml"), (".claude/agents", "md"), (".agents/agents", "md")):
            assert not (tmp_path / directory / f"{role}.{suffix}").exists()
    for absent in (
        "docs",
        "specs",
        ".devkit/managed/spec",
        ".devkit/managed/deep-research",
        ".devkit/managed/adaptive-dev",
    ):
        assert not (tmp_path / absent).exists()
    # The distribution-owned bundle inventory may name the selection; no design guidance is added.
    guidance = (tmp_path / "AGENTS.md").read_text()
    assert all("uiux-improve" not in line or "Installed bundles:" in line for line in guidance.splitlines())
    assert all(role not in guidance for role in ROLES)


def test_removal_preserves_user_artifacts_and_other_selected_assets(tmp_path: Path) -> None:  # AC-06
    other = load_bundle(PACKAGE / "src/devkit_catalog/command_design/bundle")
    installed = [*_installed(), InstalledBundle("devkit-catalog", other.version, other)]
    update_config(tmp_path, agents=HOSTS, presets={"uiux-improve": ["core"], "command-design": ["core"]})
    sync_project(tmp_path, installed)
    artifact = tmp_path / "design/flow.md"
    artifact.parent.mkdir()
    artifact.write_text("A user-owned flow sketch.\n")
    update_config(tmp_path, opt_out=["uiux-improve"])
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".agents/skills/uiux-improve").exists()
    assert (tmp_path / ".devkit/managed/command-design").is_dir()
    assert artifact.read_text() == "A user-owned flow sketch.\n"
    update_config(tmp_path, presets={"uiux-improve": ["core"]})
    sync_project(tmp_path, installed)
    assert (tmp_path / ".agents/skills/uiux-improve/SKILL.md").is_file()
    assert artifact.read_text() == "A user-owned flow sketch.\n"


def test_installed_text_is_self_contained_and_links_only_conditional_references() -> None:  # AC-05
    text = (SKILL / "SKILL.md").read_text()
    linked = set(re.findall(r"`(references/[a-z-]+\.md)`", text))
    assert linked == {p.relative_to(SKILL).as_posix() for p in (SKILL / "references").glob("*.md")}
    for name in linked:
        assert any(name in line and ("when" in line.lower() or "before" in line.lower()) for line in text.splitlines())
    orchestration = (SKILL / "references/orchestration.md").read_text()
    assert set(re.findall(r"`roles/([a-z-]+)\.md`", orchestration)) == ROLES
    for path in SKILL.rglob("*.md"):
        content = path.read_text()
        assert not re.search(r"\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MAT|FB)-[A-Za-z0-9]", content), path
        assert len(path.read_bytes()) <= 12288, path
    for role in ROLES:
        assert not (SKILL / f"roles/{role}.md").read_text().startswith("---")


def test_entry_preserves_improvement_scope_and_consumer_authority() -> None:  # AC-02, AC-03, AC-04
    skill = (SKILL / "SKILL.md").read_text()
    assert_rule(skill, "review-only", "findings", "no product edits")
    assert_rule(skill, "existing development workflow", "implementation", "approvals")
    assert_rule(skill, "normal improvement request", "changed interface or flow", "verification status")
    assert_rule(skill, "actually checked", "material limits")
    assert_rule(skill, "no commit", "integration", "publication permission")
    assert_rule(skill, "do not require", "fixed cast", "alternative count", "comparative-effectiveness experiment")
    orchestration = (SKILL / "references/orchestration.md").read_text()
    assert_rule(orchestration, "directory containing the invoked `SKILL.md`", "not the working")
    assert_rule(orchestration, "fresh context without parent conversation inheritance")
    assert_rule(orchestration, "fresh children are unavailable", "inline", "not independent contexts")
    assert_rule(orchestration, "keep peer conclusions out", "first-pass payloads")
    assert_rule(orchestration, "failed or missing role", "no findings")
    critic = (SKILL / "roles/critic.md").read_text()
    assert_rule(critic, "zero findings", "none are supported")
    assert_rule(critic, "requested improvement", "unwanted work or prerequisites")
    for role in ROLES:
        text = (SKILL / f"roles/{role}.md").read_text()
        assert_rule(text, "index", "HEAD unchanged")
        assert "retained files" in text
