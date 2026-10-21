from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from devkit_core.core import PluginFailure, PluginPackage, iter_plugin_packages, load_subclasses

from devkit_agt.features.rules.models.contracts import Rule
from devkit_agt.features.rules.models.errors import RuleLoadError, RuleProblem
from devkit_agt.features.rules.services.builtins import (
    BaseRule,
    CleanArtifactsRule,
    CliContractRule,
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

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def get_all(self) -> list[Rule]:
        return list(self._rules.values())

    def discover_from_dir(self, rules_dir: Path) -> list[Rule]:
        """Load rules from every plugin package under a directory, in sorted order.

        Each immediate subdirectory not starting with ``_`` or ``.`` is one
        package; a ``.py`` file directly in ``rules_dir`` is a ``RuleLoadError``
        telling to move it into a package directory
        (``devkit_core.core.plugins.iter_plugin_packages``).
        """
        packages, failures = iter_plugin_packages(rules_dir)
        self._record(failures)
        return self.discover_from_packages(packages)

    def discover_from_packages(self, packages: Iterable[PluginPackage]) -> list[Rule]:
        """Load the ``BaseRule`` subclasses defined in each plugin package, in order.

        Loading is atomic per package (``devkit_core.core.plugins``): a package
        that fails to import or whose classes cannot be instantiated
        contributes no rule, and the failure is recorded in ``errors`` as a
        ``RuleLoadError`` (``RULES_LOAD_FAILED``) naming the package.
        """
        loaded = load_subclasses(packages, BaseRule, namespace=PLUGIN_NAMESPACE)
        discovered: list[Rule] = []
        for instance in loaded.instances:
            self.register(instance)
            discovered.append(instance)
        self._record(loaded.errors)
        return discovered

    def _record(self, failures: Iterable[PluginFailure]) -> None:
        self.errors.extend(
            RuleLoadError(
                f"Failed to load rule package {failure.path}: {failure.message}",
                target_files=[str(failure.path)],
                fix=failure.fix,
            )
            for failure in failures
        )


def default_rule_registry() -> RuleRegistry:
    """Return a registry populated with default built-in rules."""
    registry = RuleRegistry()
    registry.register(MarkdownLinkRule())
    registry.register(FileLengthRule())
    registry.register(SecretLeakRule())
    registry.register(CleanArtifactsRule())
    registry.register(CliContractRule())
    return registry
