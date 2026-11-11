"""Opt-in app-uiux-improve deployment and its instruction boundaries (SPEC-uiux-improve-ooux-impeccable)."""

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
BUNDLE = PACKAGE / "src/devkit_catalog/app_uiux_improve/bundle"
SKILL = BUNDLE / "skills/app-uiux-improve"
ROLES = {"designer", "unconventional-designer", "reference-researcher", "critic"}
HOSTS = ["codex", "claude-code", "antigravity"]


def _installed() -> list[InstalledBundle]:
    bundle = load_bundle(BUNDLE)
    return [InstalledBundle("devkit-catalog", bundle.version, bundle)]


def test_explicit_selection_projects_local_roles_and_user_only_entry(tmp_path: Path) -> None:  # AC-07, AC-08
    update_config(tmp_path, agents=HOSTS)
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/app-uiux-improve").exists()
    update_config(tmp_path, presets={"app-uiux-improve": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/app-uiux-improve"
    assert {p.relative_to(managed).as_posix() for p in managed.rglob("*") if p.is_file()} == {
        "bundle.toml",
        "skills/app-uiux-improve/SKILL.md",
        "skills/app-uiux-improve/references/orchestration.md",
        "skills/app-uiux-improve/references/design-guidance.md",
        *(f"skills/app-uiux-improve/roles/{role}.md" for role in ROLES),
    }
    shared = tmp_path / ".agents/skills/app-uiux-improve"
    claude = tmp_path / ".claude/skills/app-uiux-improve"
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
    assert all("app-uiux-improve" not in line or "Installed:" in line for line in guidance.splitlines())
    assert all(role not in guidance for role in ROLES)


def test_removal_preserves_user_artifacts_and_other_selected_assets(tmp_path: Path) -> None:  # AC-08
    other = load_bundle(PACKAGE / "src/devkit_catalog/command_design/bundle")
    installed = [*_installed(), InstalledBundle("devkit-catalog", other.version, other)]
    update_config(tmp_path, agents=HOSTS, presets={"app-uiux-improve": ["core"], "command-design": ["core"]})
    sync_project(tmp_path, installed)
    artifact = tmp_path / "design/flow.md"
    artifact.parent.mkdir()
    artifact.write_text("A user-owned flow sketch.\n")
    update_config(tmp_path, opt_out=["app-uiux-improve"])
    sync_project(tmp_path, installed)
    assert not (tmp_path / ".agents/skills/app-uiux-improve").exists()
    assert (tmp_path / ".devkit/managed/command-design").is_dir()
    assert artifact.read_text() == "A user-owned flow sketch.\n"
    update_config(tmp_path, presets={"app-uiux-improve": ["core"]})
    sync_project(tmp_path, installed)
    assert (tmp_path / ".agents/skills/app-uiux-improve/SKILL.md").is_file()
    assert artifact.read_text() == "A user-owned flow sketch.\n"


def test_installed_text_is_self_contained_and_links_only_conditional_references() -> None:  # AC-08
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


def test_entry_preserves_improvement_scope_and_consumer_authority() -> None:  # AC-01, AC-09
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
    # AC-05 of SPEC-lightweight-general-subagent: subagent type per assignment, no runtime fallback.
    assert_rule(orchestration, "interacts with a running UI", "`general-purpose`", "outside `role-worker`")
    assert_rule(orchestration, "`role-worker` subagent for every other assignment")
    assert_rule(
        orchestration, "`role-worker` is unavailable", "stop that delegation", "its cause", "never spawn another"
    )
    assert "general subagent with" not in orchestration
    assert_rule(orchestration, "failed or missing role", "no findings")
    critic = (SKILL / "roles/critic.md").read_text()
    assert_rule(critic, "zero findings", "none are supported")
    assert_rule(critic, "requested improvement", "unwanted work or prerequisites")
    for role in ROLES:
        text = (SKILL / f"roles/{role}.md").read_text()
        assert_rule(text, "index", "HEAD unchanged")
        assert "retained files" in text


def test_framing_is_proportionate_and_reads_ooux_documents_only_where_present() -> None:  # AC-01, AC-10
    skill = (SKILL / "SKILL.md").read_text()
    assert_rule(skill, "local change", "without an ORCA pass")
    assert_rule(skill, "adds, merges or reorders views or flows", "objects", "relationships", "CTAs", "attributes")
    assert_rule(skill, "review-only", "lens", "no product edits")
    assert_rule(skill, "OOUX documents", "only where they exist", "edit none", "stale")
    guidance = (SKILL / "references/design-guidance.md").read_text()
    assert_rule(guidance, "skip it for a local change")
    assert_rule(guidance, "domain nouns", "not widgets")
    assert_rule(guidance, "`docs/steering/glossary.md`")
    assert_rule(guidance, "`docs/steering/ux-objects.md`")
    assert_rule(guidance, "`docs/ux/<area>/`")
    assert_rule(guidance, "optional project convention", "if none exist, frame in conversation")
    assert_rule(guidance, "never write these files", "report each one the change made stale")
    assert_rule(guidance, "example", "customer", "invoice", "relationship", "ctas", "attributes", "states")
    assert_rule(guidance, "readable contrast")
    assert_rule(guidance, "consistent scale")
    assert_rule(guidance, "decorative gradient", "nested container", "purpose")
    assert_rule(guidance, "empty, loading and error states")
    assert_rule(guidance, "copies none of its text")
    for path in SKILL.rglob("*.md"):
        text = path.read_text().lower()
        assert "namespace" not in text, path
        assert not re.search(r"spec-sync|living spec|sdd\b", text), path


def test_impeccable_delegation_is_selected_briefed_routed_and_accepted() -> None:  # AC-02, AC-03, AC-04, AC-06, AC-09
    skill = (SKILL / "SKILL.md").read_text()
    assert_rule(skill, "impeccable only after the user selects it", "without that selection, work inline")
    assert_rule(skill, "before product edits or delegation", "steps that precede implementation")
    assert_rule(skill, "make no product edits until the session returns", "recorded base")
    assert_rule(skill, "delegated impeccable session", "no commit, integration or publication permission")
    orchestration = (SKILL / "references/orchestration.md").read_text()
    # Selection and availability (AC-04).
    assert_rule(orchestration, "not selected impeccable", "neither start a session nor load or invoke", "work inline")
    assert_rule(orchestration, "installed impeccable permits an offer", "hook", "consumer check evidence")
    assert_rule(
        orchestration,
        "`npx impeccable install`",
        "`/plugin marketplace add pbakaus/impeccable`",
        "manual copy",
        "`skills/impeccable`",
        "install only on the user's request",
        "needs no prompt answers",
        "hand the user the exact command",
        "continue inline",
    )
    # Workflow first and the brief (AC-02).
    assert_rule(orchestration, "steps that precede implementation before delegating")
    assert_rule(orchestration, "framing result", "ooux documents by path", "read-only", "conversation framing")
    assert_rule(orchestration, "drafts or specifications", "by path, read-only")
    assert_rule(orchestration, "absolute working directory", "recorded base", "head", "content hashes")
    assert_rule(orchestration, "edit list", "product files the session may edit")
    assert_rule(orchestration, "data schema", "business logic", "dependencies", "the ooux documents", "uncommitted")
    assert_rule(orchestration, "`product.md` or `design.md` only on the user's explicit direction")
    assert_rule(orchestration, "stop condition", "expected return", "detector", "degraded coverage", "blockers")
    # Routing (AC-03).
    assert_rule(orchestration, "fresh child", "refine existing surfaces without user answers", "`polish`", "`audit`")
    assert_rule(orchestration, "cannot load impeccable", "upstream question", "blocker", "never answers")
    assert_rule(orchestration, "move the command to a session the user operates")
    assert_rule(orchestration, "new work", "`init`", "`shape`", "`critique`", "their own impeccable session")
    assert_rule(orchestration, "exclude `live`", "sandbox or approvals")
    assert_rule(orchestration, "make no product edits until the session returns")
    # Acceptance (AC-06, AC-10).
    assert_rule(orchestration, "compare the working directory with the recorded base")
    assert_rule(orchestration, "outside the edit list", "without reverting or deleting", "accepted work")
    assert_rule(orchestration, "head moved", "base is missing", "unverifiable", "limited")
    assert_rule(orchestration, "ooux document", "made stale", "edit none", "consumer workflow's own step")


def test_project_files_setup_and_cleanup_follow_the_users_request() -> None:  # AC-05
    orchestration = (SKILL / "references/orchestration.md").read_text()
    assert_rule(orchestration, "`product.md`, `design.md`", "consumer-owned", "report", "project files and git")
    assert_rule(orchestration, "ooux reference section", "by path", "copy none of their content")
    assert_rule(orchestration, "on the user's request", "not on your own initiative")
    assert_rule(orchestration, "ignore entries", "confined to `.impeccable/` paths", "after showing the user the exact")
    assert_rule(orchestration, "remove impeccable runtime or session output the user names")
    assert_rule(orchestration, "out of any cleanup", "only on the user's explicit direction")
    assert_rule(orchestration, "user-requested change", "consumer workflow", "host's approvals")
    skill = (SKILL / "SKILL.md").read_text()
    assert_rule(skill, "install impeccable", "ignore entries", "`product.md` or `design.md`", "user's request")
    assert_rule(
        skill,
        "user asks you to install impeccable",
        "ignore entries",
        "remove impeccable output",
        "`product.md` reference section",
        "read `references/orchestration.md` before acting",
    )


GUIDE_SECTIONS = (
    "What it is for",
    "One-time setup",
    "Per-task flow",
    "Launch routes",
    "What the coordinator does and does not do",
    "OOUX document linkage",
    "Opt-in setup and cleanup",
    "Troubleshooting",
)


def test_usage_guide_stays_a_human_document_outside_agent_assets(tmp_path: Path) -> None:  # AC-11
    guide = BUNDLE / "README.md"
    text = guide.read_text()
    headings = re.findall(r"^## \d+\. (.+)$", text, flags=re.MULTILINE)
    assert headings == list(GUIDE_SECTIONS)
    assert not re.search(r"\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9]", text)
    for route in ("`npx impeccable install`", "`/plugin marketplace add pbakaus/impeccable`", "`skills/impeccable`"):
        assert route in text
    catalog = (PACKAGE / "README.md").read_text()
    assert "(src/devkit_catalog/app_uiux_improve/bundle/README.md)" in catalog
    # No agent-read bundle file points at the bundle's own guide; a pointer to Impeccable's README stays allowed.
    own_guide = re.compile(r"\.\./README\.md|bundle/README\.md|\(README\.md\)|`README\.md`")
    for path in [BUNDLE / "bundle.toml", *SKILL.rglob("*")]:
        if path.is_file():
            assert not own_guide.search(path.read_text()), path
    update_config(tmp_path, agents=HOSTS, presets={"app-uiux-improve": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/app-uiux-improve"
    assert not list(managed.rglob("README.md"))
    for projected in (".agents/skills/app-uiux-improve", ".claude/skills/app-uiux-improve"):
        assert (tmp_path / projected / "SKILL.md").is_file()
        assert not list((tmp_path / projected).rglob("README.md"))
