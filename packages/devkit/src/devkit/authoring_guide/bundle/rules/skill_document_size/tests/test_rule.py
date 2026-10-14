"""``RULE-skill-document-size``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

import json
from pathlib import Path

from devkit.rules.testing import check, evaluate, load_rule

RULE = load_rule(__file__)


def _receipt(owned: list[str]) -> str:
    """A minimal installation receipt that owns ``owned`` (agent projections of bundle skills)."""
    files = {name: {"sha256": "0" * 64, "mode": 420} for name in owned}
    return json.dumps(
        {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": files}
    )


def test_checks_project_and_bundle_sources(tmp_path: Path) -> None:
    files = {
        ".agents/skills/demo/SKILL.md": "x" * 8192,
        ".claude/skills/demo/references/guide.md": "x" * 8193,
        "tools/kit/src/kit/bundle/playbooks/ops.md": "x" * 9000,
        "tools/kit/src/kit/bundle/skills/demo/scripts/tool.py": "x" * 9000,
        "docs/large.md": "x" * 9000,
        # A projection the receipt owns is fixed in its bundle, never reported in the project.
        ".claude/skills/devkit-playbook/SKILL.md": "x" * 9000,
        ".devkit/installation.json": _receipt([".claude/skills/devkit-playbook/SKILL.md"]),
    }
    found = check(RULE, tmp_path, files)
    assert [v.file for v in found] == [
        ".claude/skills/demo/references/guide.md",
        "tools/kit/src/kit/bundle/playbooks/ops.md",
    ]
    assert found[0].message == "File has 8193 bytes; effective max_bytes is 8192"
    assert "skill-authoring playbook" in found[0].remediation
    assert {(v.phase.value, v.severity.value) for v in found} == {("hygiene", "warning")}


def test_paths_and_overrides_come_from_settings(tmp_path: Path) -> None:
    files = {".agents/skills/demo/SKILL.md": "x" * 9000, "agents/custom/SKILL.md": "x" * 9000}
    settings = {"paths": ["agents/**"], "overrides": [{"path": "agents/custom/SKILL.md", "max_bytes": 12288}]}
    assert check(RULE, tmp_path, files, settings=settings) == []
    found = check(RULE, tmp_path, settings={"paths": ["agents/**"]})
    assert [v.file for v in found] == ["agents/custom/SKILL.md"]


def test_invalid_settings_are_reported(tmp_path: Path) -> None:
    result = evaluate(RULE, tmp_path, settings={"extensions": ["md"]})
    assert [problem.code for problem in result.errors] == ["RULES_SETTINGS_INVALID"]


def test_follows_changed_file_targets(tmp_path: Path) -> None:
    files = {".agents/skills/a/SKILL.md": "x" * 9000, ".agents/skills/b/SKILL.md": "x" * 9000}
    found = check(RULE, tmp_path, files, targets=[".agents/skills/b"])
    assert [v.file for v in found] == [".agents/skills/b/SKILL.md"]
