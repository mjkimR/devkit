from pathlib import Path

from devkit.rules import RuleRegistry


def test_discovery_loads_dataclass_and_ignores_imported_rules(tmp_path: Path) -> None:
    (tmp_path / "check.py").write_text("""from dataclasses import dataclass
from devkit.rules.rules import BaseRule, MarkdownLinkRule

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


def test_loading_is_atomic_per_file_and_in_definition_order(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("""from devkit.rules.rules import BaseRule

class Zeta(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-zeta", name="z", description="z")
    def check(self, ctx):
        return []

class Alpha(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-alpha", name="a", description="a")
    def check(self, ctx):
        return []
""")
    (tmp_path / "b.py").write_text("""from devkit.rules.rules import BaseRule

class Fine(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-fine", name="f", description="f")
    def check(self, ctx):
        return []

class NeedsArgs(BaseRule):
    def __init__(self, limit):
        super().__init__(id="RULE-args", name="n", description="n")
""")
    (tmp_path / "_helper.py").write_text("raise RuntimeError('never imported')\n")
    registry = RuleRegistry()
    discovered = registry.discover_from_dir(tmp_path)
    assert [rule.id for rule in discovered] == ["RULE-zeta", "RULE-alpha"]
    assert len(registry.errors) == 1 and "b.py" in str(registry.errors[0]) and "limit" in str(registry.errors[0])
    assert registry.errors[0].code == "RULES_LOAD_FAILED" and registry.errors[0].target_files[0].endswith("b.py")
    assert registry.get("RULE-fine") is None


def test_same_id_replaces_a_builtin(tmp_path: Path) -> None:
    from devkit.rules import default_rule_registry

    (tmp_path / "links.py").write_text("""from devkit.rules.rules import BaseRule

class Links(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-markdown-link", name="custom links", description="replacement")
    def check(self, ctx):
        return []
""")
    registry = default_rule_registry()
    registry.discover_from_dir(tmp_path)
    rule = registry.get("RULE-markdown-link")
    assert rule is not None and rule.name == "custom links"
