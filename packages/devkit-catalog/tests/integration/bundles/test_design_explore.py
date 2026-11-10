"""Opt-in general solution exploration skill deployment and its instruction boundaries (SPEC-design-solution-exploration)."""

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
BUNDLE = PACKAGE / "src/devkit_catalog/design_explore/bundle"
SKILL = BUNDLE / "skills/design-explore"
ROLES = {"solution-explorer", "reference-researcher", "design-critic"}
HOSTS = ["codex", "claude-code", "antigravity"]


def _installed() -> list[InstalledBundle]:
    bundle = load_bundle(BUNDLE)
    return [InstalledBundle("devkit-catalog", bundle.version, bundle)]


def test_explicit_selection_projects_local_roles_and_user_only_entry(tmp_path: Path) -> None:  # AC-01
    update_config(tmp_path, agents=HOSTS)
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/design-explore").exists()
    update_config(tmp_path, presets={"design-explore": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/design-explore"
    assert {p.relative_to(managed).as_posix() for p in managed.rglob("*") if p.is_file()} == {
        "bundle.toml",
        "skills/design-explore/SKILL.md",
        "skills/design-explore/references/orchestration.md",
        "skills/design-explore/references/exploration-methods.md",
        *(f"skills/design-explore/roles/{role}.md" for role in ROLES),
    }
    shared = tmp_path / ".agents/skills/design-explore"
    claude = tmp_path / ".claude/skills/design-explore"
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
    assert all("design-explore" not in line or "Installed bundles:" in line for line in guidance.splitlines())
    assert all(role not in guidance for role in ROLES)


def test_removal_preserves_user_artifacts_and_other_selected_assets(tmp_path: Path) -> None:  # AC-06
    other = load_bundle(PACKAGE / "src/devkit_catalog/command_design/bundle")
    installed = [*_installed(), InstalledBundle("devkit-catalog", other.version, other)]
    update_config(tmp_path, agents=HOSTS, presets={"design-explore": ["core"], "command-design": ["core"]})
    sync_project(tmp_path, installed)
    artifact = tmp_path / "design/flow.md"
    artifact.parent.mkdir()
    artifact.write_text("A user-owned flow sketch.\n")
    update_config(tmp_path, opt_out=["design-explore"])
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".agents/skills/design-explore").exists()
    assert (tmp_path / ".devkit/managed/command-design").is_dir()
    assert artifact.read_text() == "A user-owned flow sketch.\n"
    update_config(tmp_path, presets={"design-explore": ["core"]})
    sync_project(tmp_path, installed)
    assert (tmp_path / ".agents/skills/design-explore/SKILL.md").is_file()
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


def test_general_design_and_output_authority_contracts() -> None:  # AC-02, AC-04
    text = (SKILL / "SKILL.md").read_text()
    assert_rule(text, "actual goal and hard constraints")
    assert_rule(text, "implementation starts only", "separate request", "existing project workflow")
    assert_rule(text, "conversation by default", "only the coordinator", "explicitly requested destination")
    assert_rule(text, "no commit", "delivery approval", "publication permission")
    assert_rule(text, "no fixed cast", "option count", "numeric score", "comparative-effectiveness experiment")
    assert_rule(text, "unconventional plausible mechanism", "benefit", "averaging candidates")
    assert_rule(text, "distinguishing mechanism", "benefit", "main tradeoff", "decision-changing")
    methods = (SKILL / "references/exploration-methods.md").read_text()
    for domain in ("data model", "module boundary", "workflow", "architectures"):
        assert domain in methods
    assert_rule(methods, "Three database brands", "not three architectures")
    assert_rule(methods, "hard-constraint conflict", "infeasible sketch", "user changes that constraint")


def test_optional_local_assignments_and_evidence_boundaries() -> None:  # AC-03, AC-04, AC-05
    text = (SKILL / "references/orchestration.md").read_text()
    assert_rule(text, "directory containing the invoked `SKILL.md`", "not the working directory")
    assert_rule(text, "fresh context without parent conversation inheritance", "peer conclusions out")
    assert_rule(text, "fresh children are unavailable", "inline", "not independent")
    assert_rule(text, "failed or missing role", "missing coverage", "not agreement")
    assert_rule(text, "self-contained assignment", "hard constraints", "absolute read/write boundaries", "stop")
    assert_rule(text, "wait for actual returns")
    # AC-06 of SPEC-lightweight-general-subagent: role-worker per role, running-UI exception, no runtime fallback.
    assert_rule(text, "absolute installed path to a `role-worker` subagent", "running UI", "`general-purpose`")
    assert_rule(text, "`role-worker` is unavailable", "stop that delegation", "its cause", "never spawn another")
    assert "general child" not in text
    researcher = (SKILL / "roles/reference-researcher.md").read_text()
    assert_rule(researcher, "precise source links", "separate inference from evidence")
    assert_rule(researcher, "access is refused", "stop", "without another access route")
    critic = (SKILL / "roles/design-critic.md").read_text()
    assert_rule(critic, "zero findings", "none are supported")
    assert_rule(critic, "plausible unconventional mechanisms", "uncertainty alone")
    assert_rule(critic, "unwanted work or prerequisites")
    for role in ROLES:
        content = (SKILL / f"roles/{role}.md").read_text()
        assert_rule(content, "product source", "retained files", "index and HEAD unchanged")
        assert_rule(content, "no native sandbox or permission boundary")


# SPEC-design-explore-counterarguments AC-01..05
def test_optional_author_response_has_evidence_disposition_and_stop_contracts() -> None:
    orchestration = (SKILL / "references/orchestration.md").read_text()
    assert_rule(
        orchestration,
        "supported objections",
        "goal or hard constraints",
        "zero supported findings",
        "no author response",
    )
    assert_rule(
        orchestration,
        "after independent first passes",
        "actual candidate",
        "evidence",
        "failure conditions",
        "preserved constraints",
    )
    assert_rule(orchestration, "one critic pass", "at most one author response per affected candidate")
    assert_rule(
        orchestration, "cannot return", "missing author coverage", "coordinator's own", "invent no author reply"
    )
    assert_rule(orchestration, "accept and revise", "rebut", "bounded unknown", "uninspected claims", "does not prove")
    assert_rule(
        orchestration,
        "each selected objection",
        "actual response or revision",
        "reasoned disposition",
        "no serialized schema",
    )
    assert_rule(
        orchestration,
        "no automatic further reply",
        "before another pass",
        "finite pass/time bound",
        "stop without starting implementation",
    )
    explorer = (SKILL / "roles/solution-explorer.md").read_text()
    assert_rule(explorer, "response after initial exploration", "otherwise use initial exploration")
    assert_rule(explorer, "without reading peer conclusions", "first pass")
    assert_rule(
        explorer, "each selected objection", "accept and revise", "rebut", "labeled inference", "bounded unknown"
    )
    assert_rule(explorer, "inaccessible evidence", "uninspected claims", "does not prove")
    assert_rule(explorer, "stop after the assigned response", "no further critique", "implementation")
    critic = (SKILL / "roles/design-critic.md").read_text()
    assert_rule(critic, "no automatic further critic reply", "decision-changing", "finite pass/time bound")
