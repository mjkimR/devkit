from pathlib import Path

from devkit.rules import RuleRegistry


def test_discovery_loads_dataclass_and_ignores_imported_rules(tmp_path: Path) -> None:
    (tmp_path / "custom").mkdir()
    (tmp_path / "custom/check.py").write_text("""from dataclasses import dataclass
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


def test_loading_is_atomic_per_package_and_in_definition_order(tmp_path: Path) -> None:
    for name in ("a", "b", "_helper"):
        (tmp_path / name).mkdir()
    (tmp_path / "a/a.py").write_text("""from devkit.rules.rules import BaseRule

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
    (tmp_path / "b/fine.py").write_text("""from devkit.rules.rules import BaseRule

class Fine(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-fine", name="f", description="f")
    def check(self, ctx):
        return []
""")
    (tmp_path / "b/needs_args.py").write_text("""from devkit.rules.rules import BaseRule

class NeedsArgs(BaseRule):
    def __init__(self, limit):
        super().__init__(id="RULE-args", name="n", description="n")
""")
    (tmp_path / "_helper/x.py").write_text("raise RuntimeError('never imported')\n")
    registry = RuleRegistry()
    discovered = registry.discover_from_dir(tmp_path)
    assert [rule.id for rule in discovered] == ["RULE-zeta", "RULE-alpha"]
    assert len(registry.errors) == 1 and "limit" in str(registry.errors[0])
    assert str(registry.errors[0]).startswith(f"Failed to load rule package {tmp_path / 'b'}: ")
    assert registry.errors[0].code == "RULES_LOAD_FAILED" and registry.errors[0].target_files == (str(tmp_path / "b"),)
    assert registry.get("RULE-fine") is None


def test_same_id_replaces_a_builtin(tmp_path: Path) -> None:
    from devkit.rules import default_rule_registry

    (tmp_path / "links").mkdir()
    (tmp_path / "links/links.py").write_text("""from devkit.rules.rules import BaseRule

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


def test_a_rule_file_directly_in_the_rules_dir_is_a_load_error(tmp_path: Path) -> None:
    (tmp_path / "loose.py").write_text("raise RuntimeError('never imported')\n")
    registry = RuleRegistry()
    assert registry.discover_from_dir(tmp_path) == []
    (error,) = registry.errors
    assert error.code == "RULES_LOAD_FAILED" and error.target_files == (str(tmp_path / "loose.py"),)
    assert error.fix == f"Move {(tmp_path / 'loose.py').as_posix()} into {tmp_path.as_posix()}/loose/"


def test_a_rule_package_with_helpers_guide_and_tests(tmp_path: Path) -> None:
    from devkit.rules.rules import guide_path

    package = tmp_path / "rules/limits"
    (package / "tests").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "helpers.py").write_text("def limit():\n    return 3\n")
    (package / "limits.md").write_text("# Limits\n")
    (package / "tests/test_limits.py").write_text("raise RuntimeError('never imported')\n")
    (package / "limits.py").write_text("""from devkit.rules.rules import BaseRule
from .helpers import limit

class Limits(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-limits", name="limits", description=f"at most {limit()}", guide="limits.md")
    def check(self, ctx):
        from .helpers import limit as lazy
        return [] if lazy() == 3 else ["unexpected"]
""")
    registry = RuleRegistry()
    (rule,) = registry.discover_from_dir(tmp_path / "rules")
    assert registry.errors == [] and rule.description == "at most 3"
    assert rule.check(None) == []  # type: ignore[arg-type]
    assert guide_path(rule) == (package / "limits.md").resolve()
