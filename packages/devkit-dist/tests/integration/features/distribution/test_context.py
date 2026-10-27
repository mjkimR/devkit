import hashlib
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_core.base.errors import ArgumentError
from devkit_dist.features.distribution.models.errors import BundleError, NotSynchronizedError, SelectionError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.plan import plan_bundle
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import cli


@pytest.fixture
def project(tmp_path: Path) -> tuple[Path, Path, list[InstalledBundle]]:
    source = tmp_path / "source"
    source.mkdir()
    (source / "AGENTS.md").write_text("# Constitution\nApply the shared contracts.\n")
    (source / "guide.md").write_text(
        "---\nname: testing\ndescription: |\n  Use when writing tests.\n---\nBODY_ONLY_SENTINEL\n"
    )
    for name in ["review", "test"]:
        (source / name).mkdir()
        (source / name / "SKILL.md").write_bytes(b"---\r\nname: example\r\n---\r\n\r\nSkill body.\r\n")
    (source / "bundle.toml").write_text("""schema = 1
name = "team"
version = "0.1.0"
[[assets]]
id = "review"
kind = "skill"
source = "review"
[[assets]]
id = "test"
kind = "skill"
source = "test"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[presets.skills]
assets = ["review", "test"]
""")
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]})
    installed = [InstalledBundle("team-content", "0.1.0", load_bundle(source))]
    return source, target, installed


def test_progressive_disclosure_and_stateless_repeated_reads(project) -> None:
    source, target, installed = project
    sync_project(target, installed)
    nested = target / "nested"
    nested.mkdir()
    result = GetContext().execute(nested, "team").to_dict()
    assert result["constitution"] == (source / "AGENTS.md").read_text()
    assert "BODY_ONLY_SENTINEL" not in str(result)
    assert "Use when writing tests" in str(result)
    instruction = result["instructions"][0]
    assert "BODY_ONLY_SENTINEL" in Path(instruction["path"]).read_text()
    assert GetContext().execute(target, "team").to_dict() == result
    cli_result = CliRunner().invoke(cli, ["get-context", "team", "--workspace-root", str(nested)])
    assert cli_result.exit_code == 0, cli_result.output
    assert "BODY_ONLY_SENTINEL" not in cli_result.output
    sync_project(target, installed, presets={"team": ["skills"]})
    assert GetContext().execute(target, "team").to_dict()["instructions"] == []
    assert GetContext().execute(target, "team").to_dict()["constitution"] == result["constitution"]


def test_deployed_prerequisite_preserves_frontmatter_and_source(project) -> None:
    source, target, installed = project
    original = (source / "review/SKILL.md").read_bytes()
    update_config(target, agents=["codex", "claude-code"])
    sync_project(target, installed)
    for directory in [".devkit/managed/team", ".agents/skills", ".claude/skills"]:
        for skill in ["review", "test"]:
            output = (target / directory / skill / "SKILL.md").read_bytes()
            assert output.startswith(b"---\r\nname: example\r\n---\r\n")
            assert output.count(b"uv run devkit get-context team") == 1
            assert b"once per bundle per agent context" in output
            assert output.endswith(b"Skill body.\r\n")
    assert (source / "review/SKILL.md").read_bytes() == original
    assert sync_project(target, installed).to_dict()["actions"] == []


def test_instruction_only_bundle_still_gets_discovery(project) -> None:
    source, target, installed = project
    (source / "AGENTS.md").unlink()
    sync_project(target, installed)
    assert GetContext().execute(target, "team").to_dict()["constitution"] is None
    assert b"get-context team" in (target / ".devkit/managed/team/review/SKILL.md").read_bytes()
    sync_project(target, installed, presets={"team": ["skills"]})
    assert (target / ".devkit/managed/team/review/SKILL.md").read_bytes() == (source / "review/SKILL.md").read_bytes()


def test_context_errors_do_not_expose_instruction_bodies(project) -> None:
    source, target, installed = project
    (source / "guide.md").write_text("BODY_ONLY_SENTINEL\n")
    sync_project(target, installed)
    result = CliRunner().invoke(cli, ["get-context", "team", "--workspace-root", str(target)])
    assert result.exit_code == 2
    assert "frontmatter" in result.output
    assert "BODY_ONLY_SENTINEL" not in result.output
    with pytest.raises(SelectionError, match="not synchronized"):
        GetContext().execute(target, "missing")
    with pytest.raises(ArgumentError, match="lowercase slug"):
        GetContext().execute(target, "../team")
    (target / ".devkit/managed/team/AGENTS.md").write_text("changed")
    with pytest.raises(NotSynchronizedError, match="modified context"):
        GetContext().execute(target, "team")


def test_constitution_symlink_rejected(project, tmp_path: Path) -> None:
    source, _, _ = project
    (source / "AGENTS.md").unlink()
    (source / "AGENTS.md").symlink_to(tmp_path / "absent")
    with pytest.raises(BundleError, match="symlink"):
        load_bundle(source)


def test_plan_matches_deployment(project) -> None:
    _, target, installed = project
    bundle = installed[0].bundle
    sync_project(target, installed)
    for item in plan_bundle(bundle).to_dict()["files"]:
        assert item["sha256"] == hashlib.sha256((target / item["destination"]).read_bytes()).hexdigest()


def test_unclosed_skill_frontmatter_fails_before_deployment(project) -> None:
    source, target, installed = project
    (source / "review/SKILL.md").write_text("---\nname: review\n")
    with pytest.raises(BundleError, match=r"SKILL\.md: frontmatter opened with .* is never closed"):
        sync_project(target, installed)
    assert not (target / ".devkit/managed").exists()
