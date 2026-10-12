from __future__ import annotations

import json
from pathlib import Path

from agent_rule_engine import RuleRegistry, managed_rule_paths

RULE = """from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


class ManagedRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-managed-{n}", name="managed", description="from a bundle")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []
"""


def _receipt(root: Path, assets: list[dict[str, object]]) -> None:
    path = root / ".devkit/installation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": 1, "assets": assets}))


def test_managed_rule_paths_reads_rule_assets_only(tmp_path: Path) -> None:
    (tmp_path / ".devkit/managed/team/rules").mkdir(parents=True)
    (tmp_path / ".devkit/managed/team/rules/a.py").write_text(RULE.format(n="a"))
    (tmp_path / ".devkit/managed/team/rules/README.md").write_text("doc\n")
    (tmp_path / ".devkit/overrides/team/rules").mkdir(parents=True)
    (tmp_path / ".devkit/overrides/team/rules/b.py").write_text(RULE.format(n="b"))
    _receipt(
        tmp_path,
        [
            {
                "bundle": "team",
                "id": "rules",
                "kind": "rule",
                "paths": [
                    ".devkit/managed/team/rules/README.md",
                    ".devkit/managed/team/rules/a.py",
                    ".devkit/overrides/team/rules/b.py",
                    ".devkit/managed/team/rules/missing.py",
                ],
            },
            {"bundle": "team", "id": "flow", "kind": "workflow", "paths": [".devkit/managed/team/flow.py"]},
        ],
    )
    assert [p.relative_to(tmp_path).as_posix() for p in managed_rule_paths(tmp_path)] == [
        ".devkit/managed/team/rules/a.py",
        ".devkit/overrides/team/rules/b.py",
    ]
    registry = RuleRegistry()
    discovered = registry.discover_from_files(managed_rule_paths(tmp_path))
    assert sorted(r.id for r in discovered) == ["RULE-managed-a", "RULE-managed-b"]


def test_managed_rule_paths_tolerates_missing_or_invalid_receipt(tmp_path: Path) -> None:
    assert managed_rule_paths(tmp_path) == []
    _receipt(tmp_path, [])
    assert managed_rule_paths(tmp_path) == []
    (tmp_path / ".devkit/installation.json").write_text("{not json")
    assert managed_rule_paths(tmp_path) == []
