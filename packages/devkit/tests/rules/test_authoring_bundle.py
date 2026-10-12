"""The opt-in ``authoring`` bundle: its manifest, and its two rules run from a synchronized consumer."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.cli import cli
from devkit.core import GUIDANCE_END, GUIDANCE_START
from devkit.distribution.bundles import load_bundle
from testsupport.rules import write

PACKAGE = Path(__file__).parents[2]
BUNDLE = PACKAGE / "src/devkit/rules/authoring/bundle"


def test_presets_pair_each_playbook_with_its_rule() -> None:
    bundle = load_bundle(BUNDLE)
    assert (bundle.name, bundle.default_preset, bundle.auto_select) == ("authoring", "all", False)
    assert bundle.select(["skill-authoring"]) == {"skill-authoring", "skill-document-size"}
    assert bundle.select(["agent-guide-authoring"]) == {"agent-guide-authoring", "agent-guide-size"}
    pyproject = tomllib.loads((PACKAGE / "pyproject.toml").read_text())
    assert bundle.version == pyproject["project"]["version"]


def test_content_is_english_and_skill_documents_fit_their_own_budget() -> None:
    hangul = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
    for path in sorted(BUNDLE.rglob("*.md")):
        assert not hangul.search(path.read_text()), path.name
        assert path.stat().st_size <= 8192, path.name


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def _violations(root: Path, *extra: str) -> dict[str, list[dict[str, object]]]:
    result = CliRunner().invoke(
        cli, ["rules", "check", "-w", str(root), "--phase", "hygiene", "--format", "json", *extra]
    )
    assert result.exit_code == 0, result.output
    found: dict[str, list[dict[str, object]]] = {}
    for item in json.loads(result.stdout)["violations"]:
        found.setdefault(str(item["rule_id"]), []).append(item)
    return found


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    _run("add", "authoring", "--workspace-root", str(root))
    return root


def test_add_deploys_both_presets_and_the_playbooks_are_searchable(consumer: Path) -> None:
    config = tomllib.loads((consumer / ".devkit/config.toml").read_text())
    assert config["presets"]["authoring"] == "all"
    for query, name in [
        ("restructure a large skill", "skill-authoring"),
        ("curate agent guide", "agent-guide-authoring"),
    ]:
        found = json.loads(_run("playbook", "search", query, "--workspace-root", str(consumer)))
        assert found["results"][0]["name"] == name


def test_skill_document_size_checks_project_and_bundle_sources(consumer: Path) -> None:
    write(consumer, ".agents/skills/demo/SKILL.md", "x" * 8192)
    write(consumer, ".claude/skills/demo/references/guide.md", "x" * 8193)
    write(consumer, "tools/kit/src/kit/bundle/playbooks/ops.md", "x" * 9000)
    write(consumer, "tools/kit/src/kit/bundle/skills/demo/scripts/tool.py", "x" * 9000)
    write(consumer, "docs/large.md", "x" * 9000)
    # A projection the receipt owns is fixed in its bundle, never reported in the project.
    write(consumer, ".claude/skills/devkit-playbook/SKILL.md", "x" * 9000)
    found = _violations(consumer)["RULE-skill-document-size"]
    assert [item["file"] for item in found] == [
        ".claude/skills/demo/references/guide.md",
        "tools/kit/src/kit/bundle/playbooks/ops.md",
    ]
    assert found[0]["message"] == "File has 8193 bytes; effective max_bytes is 8192"
    assert "skill-authoring playbook" in str(found[0]["remediation"])


def test_skill_document_size_settings_and_exceptions(consumer: Path) -> None:
    write(consumer, ".agents/skills/demo/SKILL.md", "x" * 9000)
    write(consumer, "agents/custom/SKILL.md", "x" * 9000)
    (consumer / ".devkit/config.toml").write_text(
        (consumer / ".devkit/config.toml").read_text()
        + '\n[rules.settings.RULE-skill-document-size]\npaths = ["agents/**"]\n'
        + "\n# Read as one procedure.\n[[rules.settings.RULE-skill-document-size.overrides]]\n"
        + 'path = "agents/custom/SKILL.md"\nmax_bytes = 12288\n'
    )
    assert "RULE-skill-document-size" not in _violations(consumer)
    (consumer / ".devkit/config.toml").write_text(
        (consumer / ".devkit/config.toml").read_text() + "\n[rules.settings.RULE-agent-guide-size]\nmax_bytes = 0\n"
    )
    result = CliRunner().invoke(cli, ["rules", "check", "-w", str(consumer), "--phase", "hygiene"])
    assert result.exit_code == 2 and "max_bytes must be a positive integer" in result.output


def test_agent_guide_size_reports_the_devkit_block_share(consumer: Path) -> None:
    guide = consumer / "AGENTS.md"
    text = guide.read_text()
    block = text[text.index(GUIDANCE_START) : text.index(GUIDANCE_END) + len(GUIDANCE_END)]
    guide.write_text("# Project\n\n" + "x" * 8192 + "\n\n" + text)
    write(consumer, "packages/app/AGENTS.md", "x" * 9000)
    write(consumer, "tools/kit/src/kit/bundle/AGENTS.md", "x" * 9000)  # a bundle constitution
    write(consumer, "docs/AGENTS-notes.md", "x" * 9000)
    (consumer / "CLAUDE.md").symlink_to("AGENTS.md")
    found = _violations(consumer)["RULE-agent-guide-size"]
    assert [item["file"] for item in found] == ["AGENTS.md", "packages/app/AGENTS.md"]
    size = guide.stat().st_size
    share = len(block.encode())
    assert found[0]["message"] == (
        f"Guide has {size} bytes, including {share} bytes of the devkit guidance block; effective max_bytes is 8192"
    )
    assert found[1]["message"] == "Guide has 9000 bytes; effective max_bytes is 8192"


def test_rules_follow_changed_file_targets(consumer: Path) -> None:
    write(consumer, ".agents/skills/demo/SKILL.md", "x" * 9000)
    write(consumer, "packages/app/AGENTS.md", "x" * 9000)
    found = _violations(consumer, "packages/app/AGENTS.md")
    assert "RULE-skill-document-size" not in found
    assert [item["file"] for item in found["RULE-agent-guide-size"]] == ["packages/app/AGENTS.md"]
