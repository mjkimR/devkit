"""Project policy for loaded rules: one validation shared by evaluation, ``phases`` and ``explain``.

``[rules]`` in ``.devkit/config.toml`` may move rules between phases, change
their severity and configure their typed settings. Every entry must name a
loaded rule and change something; settings must type-check against the rule's
declared dataclass. ``validate_policy`` collects every problem as a
``PolicyError`` carrying the rule ID, so a caller can tell which rule is
affected, together with the ``RuleDefinitionError`` of every loaded rule whose
``inputs`` declaration is malformed.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from devkit_agt.features.rules.models.contracts import Phase, Rule, Severity, rule_file
from devkit_agt.features.rules.models.errors import PolicyError, RuleDefinitionError, RuleProblem
from devkit_agt.features.rules.models.phases import validate_phase_overrides
from devkit_agt.features.rules.models.settings import RawSettings, SettingsResolver, build_resolvers, validate_pattern


def check_inputs(rule_id: str, value: object) -> None:
    """Accept a rule's ``inputs`` declaration: ``None`` or a non-empty tuple of ``validate_pattern`` patterns.

    Raises ``RuleDefinitionError`` (``RULES_DEFINITION_INVALID``) for anything else: a list, a string, an empty tuple
    (a rule that could never run in a targeted run) or a pattern ``validate_pattern`` rejects.
    """
    if value is None:
        return
    if not isinstance(value, tuple) or not value:
        raise RuleDefinitionError(
            f"{rule_id}: inputs must be None or a non-empty tuple of workspace path patterns, got {value!r}",
            rule_id=rule_id,
        )
    for pattern in value:
        try:
            validate_pattern(pattern)
        except ValueError as exc:
            raise RuleDefinitionError(f"{rule_id}: invalid inputs pattern: {exc}", rule_id=rule_id) from None


def validate_inputs(rules: Sequence[Rule]) -> list[RuleDefinitionError]:
    """One problem per rule whose ``inputs`` attribute (read with ``getattr``, absent means ``None``) is malformed.

    ``BaseRule`` checks its own declaration when constructed; this covers rules that satisfy the ``Rule`` protocol
    without subclassing it. Each problem names the file defining the rule when it has one.
    """
    errors: list[RuleDefinitionError] = []
    for rule in rules:
        try:
            check_inputs(rule.id, getattr(rule, "inputs", None))
        except RuleDefinitionError as exc:
            source = rule_file(rule)
            errors.append(RuleDefinitionError(str(exc), rule_id=rule.id, target_files=[str(source)] if source else []))
    return errors


def validate_severity_overrides(rules: Sequence[Rule], overrides: Mapping[str, Severity]) -> list[PolicyError]:
    """Problems for severity overrides that cannot apply to ``rules``."""
    by_id = {r.id: r for r in rules}
    errors: list[PolicyError] = []
    for rule_id in sorted(overrides):
        rule = by_id.get(rule_id)
        if rule is None:
            errors.append(PolicyError(f"severity override for unknown rule: {rule_id}", rule_id=rule_id))
        elif rule.severity == overrides[rule_id]:
            errors.append(
                PolicyError(
                    f"severity override for {rule_id} is redundant: the rule already reports "
                    f"{rule.severity.value}; remove the entry",
                    rule_id=rule_id,
                )
            )
    return errors


def effective_severity(rule: Rule, overrides: Mapping[str, Severity] | None = None) -> Severity:
    """Severity a rule reports once project overrides are applied."""
    if overrides and rule.id in overrides:
        return overrides[rule.id]
    return rule.severity


def validate_policy(
    rules: Sequence[Rule],
    *,
    phase_overrides: Mapping[str, Phase],
    severity_overrides: Mapping[str, Severity],
    settings: Mapping[str, RawSettings],
) -> tuple[dict[str, SettingsResolver], list[RuleProblem]]:
    """Settings resolvers for ``rules`` and every policy problem (inputs declarations, phase, severity, settings)."""
    resolvers, settings_errors = build_resolvers(rules, settings)
    errors: list[RuleProblem] = [
        *validate_inputs(rules),
        *validate_phase_overrides(rules, phase_overrides),
        *validate_severity_overrides(rules, severity_overrides),
        *settings_errors,
    ]
    for rule in rules:
        scoped = getattr(rule, "change_scope", False)
        if not isinstance(scoped, bool):
            errors.append(RuleDefinitionError(f"{rule.id}: change_scope must be bool", rule_id=rule.id))
        elif scoped and (
            rule.phase is not Phase.LINTER
            or getattr(rule, "promote_to", None) is not None
            or phase_overrides.get(rule.id, Phase.LINTER) is not Phase.LINTER
        ):
            errors.append(
                PolicyError(
                    f"{rule.id}: change-scoped rules must remain linter rules without promotion", rule_id=rule.id
                )
            )
    return resolvers, errors
