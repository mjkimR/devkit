from pathlib import Path

from agent_rule_engine import RuleRegistry


def test_discovery_loads_dataclass_and_ignores_imported_rules(tmp_path: Path) -> None:
    (tmp_path / "check.py").write_text("""from dataclasses import dataclass
from agent_rule_engine.rules import BaseRule, SpecFormatRule

@dataclass
class CustomRule(BaseRule):
    id: str = "RULE-custom"
    name: str = "custom"
    description: str = "Custom check"

    def check(self, ctx):
        return []
""")
    registry = RuleRegistry()
    discovered = registry.discover_from_dir(tmp_path)
    assert [rule.id for rule in discovered] == ["RULE-custom"]
    assert not registry.errors
