"""Real deep-research selection, explicit-only projection, role ownership and retention guidance (SPEC-deep-research-bundle)."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import devkit_adaptive.bundles
import pytest
import yaml
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[3]
REPOSITORY = PACKAGE.parents[1]
BUNDLE = PACKAGE / "src/devkit_catalog/deep_research/bundle"
ADAPTIVE_DEV = Path(devkit_adaptive.bundles.__file__).parent / "adaptive_dev/bundle"
SKILL = BUNDLE / "skills/deep-research/SKILL.md"
MOVED = ("direction-explorer", "discovery-critic", "discovery-planner")
ROLES = {*MOVED, "research-investigator"}
DISCOVERY_ROLES = {"idea-explorer", "evidence-researcher", "idea-challenger"}
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
    assert set(bundle.presets["core"]) == {"deep-research", "discovery"}
    update_config(tmp_path, agents=HOSTS)
    sync_project(tmp_path, _installed())
    assert not (tmp_path / ".devkit/managed/deep-research").exists()
    update_config(tmp_path, presets={"deep-research": ["core"]})
    sync_project(tmp_path, _installed())
    managed = tmp_path / ".devkit/managed/deep-research"
    assert {path.as_posix() for path in _files(managed)} == {
        "bundle.toml",
        "skills/discovery/SKILL.md",
        "skills/discovery/references/orchestration.md",
        "skills/discovery/references/retention.md",
        *(f"skills/discovery/roles/{role}.md" for role in DISCOVERY_ROLES),
        "skills/deep-research/SKILL.md",
        "skills/deep-research/references/orchestration.md",
        "skills/deep-research/references/workspace.md",
        "skills/deep-research/references/synthesis.md",
        "skills/deep-research/references/cloud-handoff.md",
        *(f"skills/deep-research/roles/{role}.md" for role in ROLES),
    }
    for role in ROLES:
        assert (tmp_path / f".agents/skills/deep-research/roles/{role}.md").is_file()
        assert (tmp_path / f".claude/skills/deep-research/roles/{role}.md").is_file()
        for directory, suffix in ((".codex/agents", "toml"), (".claude/agents", "md"), (".agents/agents", "md")):
            assert not (tmp_path / directory / f"{role}.{suffix}").exists()
    for absent in ("docs", "specs", ".devkit/adaptive-dev.md", ".devkit/managed/adaptive-dev", ".devkit/managed/spec"):
        assert not (tmp_path / absent).exists(), absent


@pytest.mark.parametrize("entry", ["deep-research", "discovery"])
def test_entry_projects_explicit_invocation_for_each_host(tmp_path: Path, entry: str) -> None:  # AC-02
    update_config(tmp_path, agents=HOSTS, presets={"deep-research": ["core"]})
    sync_project(tmp_path, _installed())
    relative = f"skills/{entry}"
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
        title, guard = (
            ("# Deep research", GUARD)
            if entry == "deep-research"
            else ("# Idea discovery", "Run only when the user explicitly invokes this entry.")
        )
        assert body[:2] == [title, guard], projected
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
        for word in ("configuration.development.approach", ".devkit/adaptive-dev.md", "adaptive-dev", "incubation"):
            assert word not in content, (path, word)
        assert not re.search(r"\b(ADR|CAP|UC|US|ARCH|SPEC|MS|PROP|FB|RULE|PLAN|TASKS)-[A-Za-z0-9]", content), path
        assert len(path.read_bytes()) <= 12288, path


def test_selection_beside_adaptive_dev_has_one_owner_per_role(tmp_path: Path) -> None:  # AC-04
    update_config(tmp_path, agents=["codex"], presets={"adaptive-dev": ["core"], "deep-research": ["core"]})
    sync_project(tmp_path, _installed(ADAPTIVE_DEV, BUNDLE))
    for role in MOVED:
        assert (tmp_path / f".devkit/managed/deep-research/skills/deep-research/roles/{role}.md").is_file()
        assert not (tmp_path / f".devkit/managed/adaptive-dev/subagents/{role}.md").exists()
        assert not (tmp_path / f".codex/agents/{role}.toml").exists()
    assert not (tmp_path / ".devkit/managed/adaptive-dev/skills/deep-research").exists()
    assert (tmp_path / ".agents/skills/adaptive-dev/SKILL.md").is_file()
    assert (tmp_path / ".agents/skills/deep-research/SKILL.md").is_file()


@pytest.mark.parametrize("role", MOVED)
def test_moved_role_policy_key_follows_the_bundle(tmp_path: Path, role: str) -> None:  # AC-05
    installed = _installed(ADAPTIVE_DEV, BUNDLE)
    update_config(tmp_path, agents=["codex"], presets={"adaptive-dev": ["core"], "deep-research": ["core"]})
    sync_project(tmp_path, installed)
    config = tmp_path / ".devkit/config.toml"
    base = config.read_text()
    config.write_text(base + f'\n[subagents.roles."incubation:{role}"]\nlevel = "deep"\n')
    before = _files(tmp_path)
    with pytest.raises(ConfigError, match=f"subagents.roles.incubation:{role}"):
        sync_project(tmp_path, installed)
    assert _files(tmp_path) == before
    config.write_text(base + f'\n[subagents.roles."deep-research:{role}"]\nlevel = "deep"\n')
    with pytest.raises(ConfigError, match=f"subagents.roles.deep-research:{role}"):
        sync_project(tmp_path, installed)
    config.write_text(base)
    sync_project(tmp_path, installed)


def test_roles_keep_optional_execution_and_coordinator_material_ownership() -> None:  # AC-06
    for role in ROLES:
        body = (SKILL.parent / f"roles/{role}.md").read_text()
        assert not body.startswith("---")
        assert_rule(body, "only", "coordinator", "writes", "retained material")
        assert_rule(body, "index", "HEAD", "unchanged")
        assert_rule(body, "return", "`status`", "source/artifact identity", "failure conditions")
    investigator = (SKILL.parent / "roles/research-investigator.md").read_text()
    assert_rule(investigator, "one question", "team investigation")
    assert_rule(investigator, "payload permits", "experiment", "only", "sandbox/prototype boundary", "assigned scratch")
    orchestration = (SKILL.parent / "references/orchestration.md").read_text()
    # AC-04 of SPEC-lightweight-general-subagent: one static type for every role, no runtime fallback.
    assert_rule(
        orchestration, "`role-worker` subagent for every selected role", "read the assigned role file before acting"
    )
    assert_rule(
        orchestration, "`role-worker` is unavailable", "stop that delegation", "its cause", "never spawn another"
    )
    assert "general subagent" not in orchestration
    assert_rule(SKILL.read_text(), "absolute path to a `role-worker` subagent", "read that file first")
    assert_rule(orchestration, "fresh context", "without parent conversation inheritance")
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


def test_guides_name_the_add_command() -> None:  # AC-11
    install = REPOSITORY / "guides/INSTALL_GUIDE.md"
    existing = REPOSITORY / "guides/install/existing-repository.md"
    recommendations = REPOSITORY / "guides/install/bundle-recommendations.md"
    for path in (install, existing, recommendations, PACKAGE / "README.md"):
        assert "uv run devkit add deep-research" in path.read_text(), path
    row = next(line for line in recommendations.read_text().splitlines() if line.startswith("| `deep-research`"))
    assert "strongly recommend during installation as an optional addition" in row.lower()
    assert "require explicit user invocation" in row.lower()


def test_upgrade_removes_registered_roles(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy-bundle"
    shutil.copytree(BUNDLE, legacy)
    manifest = legacy / "bundle.toml"
    content = manifest.read_text().replace(
        'assets = ["deep-research", "discovery"]',
        'assets = ["deep-research", "discovery", ' + ", ".join(f'"{role}"' for role in sorted(ROLES)) + "]",
    )
    (legacy / "subagents").mkdir()
    for role in sorted(ROLES):
        content += f'\n[[assets]]\nid = "{role}"\nkind = "subagent"\nsource = "subagents/{role}.md"\n'
        (legacy / f"subagents/{role}.md").write_text(
            f"---\nrole: {role}\ntitle: Research role\ndescription: Research role\nhosts:\n"
            "  codex: {status: emulated}\n  claude-code: {status: native}\n  antigravity: {status: unverified}\n---\n\nResearch.\n"
        )
    manifest.write_text(content)
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    update_config(consumer, agents=HOSTS, presets={"deep-research": ["core"]})
    sync_project(consumer, _installed(legacy))
    for role in ROLES:
        assert (consumer / f".codex/agents/{role}.toml").is_file()
    sync_project(consumer, _installed())
    for role in ROLES:
        for directory, suffix in ((".codex/agents", "toml"), (".claude/agents", "md"), (".agents/agents", "md")):
            assert not (consumer / directory / f"{role}.{suffix}").exists()
        assert (consumer / f".agents/skills/deep-research/roles/{role}.md").is_file()


def test_cloud_handoff_keeps_inspectable_requests_and_truthful_returns() -> None:  # SPEC-cloud-research-handoff
    cloud = (SKILL.parent / "references/cloud-handoff.md").read_text()
    assert_rule(cloud, "local-only research", "free of a cloud request", "provider account")
    assert_rule(cloud, "request label and revision", "report to repeat it")
    assert_rule(
        cloud, "self-contained copyable prompt", "intended decision", "bounded questions", "known facts", "constraints"
    )
    assert_rule(cloud, "exact outbound content", "omit secrets", "credentials", "private context")
    assert_rule(cloud, "`awaiting user result`", "neither submission nor execution")
    assert_rule(cloud, "do not poll", "elapsed time", "explicitly partial")
    assert_rule(cloud, "identity is missing", "revision is superseded", "clarify the association", "duplicate")
    assert_rule(cloud, "unreadable format", "inaccessible report link", "request readable content", "do not infer")
    assert_rule(cloud, "`returned`", "actual readable", "provider/model", "receipt date", "inspection limits")
    assert_rule(cloud, "source data", "no action, upload or Git authority")
    assert_rule(
        cloud, "inspected support", "provider assertions", "inference", "contradictions", "inaccessible citations"
    )
    assert_rule(cloud, "`reviewed`", "does not imply every claim", "faithful summaries", "sensitive reports")


def test_cloud_handoff_resume_requires_only_retained_partial_evidence() -> None:  # SPEC-cloud-research-handoff
    cloud = (SKILL.parent / "references/cloud-handoff.md").read_text()
    assert_rule(
        cloud,
        "exact safe prompt",
        "label/revision",
        "disposition",
        "remaining question",
        "next action",
        "transient-only",
    )
    assert_rule(
        cloud, "user names that partial material", "same partial index", "never rewrite a complete", "silently resubmit"
    )
    assert_rule(cloud, "only the coordinator", "retained material", "no extra document kind")
    for name in ("workspace", "synthesis"):
        text = (SKILL.parent / f"references/{name}.md").read_text()
        assert_rule(
            text, "cloud", "exact safe", "partial material", "scratch" if name == "workspace" else "transient-only"
        )


def test_discovery_upgrade_preserves_research_override_and_material(tmp_path: Path) -> None:
    legacy = tmp_path / "research-only"
    shutil.copytree(BUNDLE, legacy)
    manifest = legacy / "bundle.toml"
    manifest.write_text(
        manifest.read_text()
        .replace(
            '\n[[assets]]\nid = "discovery"\nkind = "skill"\nsource = "skills/discovery"\ninvocation = "user"\n', ""
        )
        .replace('assets = ["deep-research", "discovery"]', 'assets = ["deep-research"]')
    )
    shutil.rmtree(legacy / "skills/discovery")
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    update_config(consumer, agents=HOSTS, presets={"deep-research": ["core"]})
    override = consumer / ".devkit/overrides/deep-research/skills/deep-research"
    shutil.copytree(SKILL.parent, override)
    custom = override / "roles/research-investigator.md"
    custom.write_text(custom.read_text() + "\nPreserve this consumer's evidence vocabulary.\n")
    material = consumer / "docs/materials/retained.md"
    material.parent.mkdir(parents=True)
    material.write_text("Retained consumer evidence.\n")
    sync_project(consumer, _installed(legacy))
    research = consumer / ".agents/skills/deep-research"
    before = _files(research)
    sync_project(consumer, _installed())
    assert _files(research) == before
    assert material.read_text() == "Retained consumer evidence.\n"
    discovery = consumer / ".agents/skills/discovery"
    assert (discovery / "SKILL.md").is_file()
    for role in DISCOVERY_ROLES:
        assert (discovery / f"roles/{role}.md").is_file()
        assert not (consumer / f".codex/agents/{role}.toml").exists()
    for entry in ("discovery", "deep-research"):
        projected = consumer / f".agents/skills/{entry}"
        for source in projected.rglob("*.md"):
            for target in re.findall(r"`((?:references|roles)/[a-z-]+\.md)`", source.read_text()):
                if "<" not in target:
                    assert (projected / target).is_file(), (source, target)
    update_config(consumer, opt_out=["deep-research"])
    sync_project(consumer, _installed())
    assert not discovery.exists()
    assert not research.exists()
    assert custom.is_file()
    assert material.read_text() == "Retained consumer evidence.\n"
    update_config(consumer, presets={"deep-research": ["core"]})
    sync_project(consumer, _installed())
    assert (discovery / "SKILL.md").is_file()
    assert _files(research) == before
