from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from devkit.core import iter_plugin_files, load_subclasses
from devkit.rules.engine.errors import RuleLoadError, RuleProblem
from devkit.rules.engine.models import Rule
from devkit.rules.rules import (
    BaseRule,
    CleanArtifactsRule,
    FileLengthRule,
    MarkdownLinkRule,
    SecretLeakRule,
)

PLUGIN_NAMESPACE = "devkit_rule"


class RuleRegistry:
    """Registry managing available governance rules, supporting built-ins and dynamic plugins.

    A rule registered with the ID of an earlier one replaces it.
    """

    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}
        self.errors: list[RuleProblem] = []

    def register(self, rule: Rule) -> None:
        self._rules[rule.id] = rule

    def unregister(self, rule_id: str) -> None:
        self._rules.pop(rule_id, None)

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def get_all(self) -> list[Rule]:
        return list(self._rules.values())

    def discover_from_dir(self, rules_dir: Path) -> list[Rule]:
        """Load rules from every Python file under a directory, in sorted path order.

        Files and directories whose name starts with ``_`` or ``.`` are skipped.
        """
        return self.discover_from_files(iter_plugin_files(rules_dir))

    def discover_from_files(self, files: Iterable[Path]) -> list[Rule]:
        """Load the ``BaseRule`` subclasses defined in the given Python files, in definition order.

        Files whose name starts with ``_`` or ``.`` or that are not ``.py``
        files are skipped. Loading is atomic per file (``devkit.core.plugins``):
        a file that fails to import or whose classes cannot be instantiated
        contributes no rule, and the failure is recorded in ``errors`` as a
        ``RuleLoadError`` (``RULES_LOAD_FAILED``) naming the file.
        """
        selected = [path for path in files if path.suffix == ".py" and not path.name.startswith(("_", "."))]
        loaded = load_subclasses(selected, BaseRule, namespace=PLUGIN_NAMESPACE)
        discovered: list[Rule] = []
        for instance in loaded.instances:
            self.register(instance)
            discovered.append(instance)
        self.errors.extend(
            RuleLoadError(
                f"Failed to load rule from {failure.path}: {failure.message}", target_files=[str(failure.path)]
            )
            for failure in loaded.errors
        )
        return discovered


def default_registry() -> RuleRegistry:
    """Return a registry populated with default built-in rules."""
    registry = RuleRegistry()
    registry.register(MarkdownLinkRule())
    registry.register(FileLengthRule())
    registry.register(SecretLeakRule())
    registry.register(CleanArtifactsRule())
    return registry
