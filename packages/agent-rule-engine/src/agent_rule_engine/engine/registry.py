from __future__ import annotations

import hashlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from agent_rule_engine.engine.models import Rule
from agent_rule_engine.rules import (
    BaseRule,
    DocumentReferenceRule,
    FileLengthRule,
    IdConventionRule,
    MarkdownLinkRule,
    SpecFormatRule,
)


class RuleRegistry:
    """Registry managing available governance rules, supporting built-ins and dynamic plugins."""

    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}
        self.errors: list[str] = []

    def register(self, rule: Rule) -> None:
        self._rules[rule.id] = rule

    def unregister(self, rule_id: str) -> None:
        self._rules.pop(rule_id, None)

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def get_all(self) -> list[Rule]:
        return list(self._rules.values())

    def discover_from_dir(self, rules_dir: Path) -> list[Rule]:
        """Dynamically load rules from a directory containing python files."""
        discovered: list[Rule] = []
        if not rules_dir.exists() or not rules_dir.is_dir():
            return discovered

        for py_file in sorted(rules_dir.rglob("*.py")):
            if py_file.name.startswith(("_", ".")):
                continue

            digest = hashlib.sha256(str(py_file.resolve()).encode()).hexdigest()[:16]
            module_name = f"custom_rule_{digest}"
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            obj.__module__ == module_name
                            and issubclass(obj, BaseRule)
                            and obj is not BaseRule
                            and not inspect.isabstract(obj)
                        ):
                            rule_cls: type[Any] = obj
                            instance = rule_cls()
                            if isinstance(instance, Rule):
                                self.register(instance)
                                discovered.append(instance)
                except Exception as exc:
                    sys.modules.pop(module_name, None)
                    self.errors.append(f"Failed to load rule from {py_file}: {exc}")

        return discovered


def default_registry() -> RuleRegistry:
    """Return a registry populated with default built-in rules."""
    registry = RuleRegistry()
    registry.register(SpecFormatRule())
    registry.register(IdConventionRule())
    registry.register(DocumentReferenceRule())
    registry.register(MarkdownLinkRule())
    registry.register(FileLengthRule())
    return registry
