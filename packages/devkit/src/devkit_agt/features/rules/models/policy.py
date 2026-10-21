"""Project policy for loaded rules: one validation shared by evaluation, ``phases`` and ``explain``.

``[rules]`` in ``.devkit/config.toml`` may move rules between phases, change
their severity and configure their typed settings. Every entry must name a
loaded rule and change something; settings must type-check against the rule's
declared dataclass. ``validate_policy`` collects every problem as a
``PolicyError`` carrying the rule ID, so a caller can tell which rule is
affected.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from devkit_agt.features.rules.models.contracts import Phase, Rule, Severity
from devkit_agt.features.rules.models.errors import PolicyError
from devkit_agt.features.rules.models.phases import validate_phase_overrides
from devkit_agt.features.rules.models.settings import RawSettings, SettingsResolver, build_resolvers


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
) -> tuple[dict[str, SettingsResolver], list[PolicyError]]:
    """Settings resolvers for ``rules`` and every policy problem (phase, severity, settings)."""
    resolvers, settings_errors = build_resolvers(rules, settings)
    errors = [
        *validate_phase_overrides(rules, phase_overrides),
        *validate_severity_overrides(rules, severity_overrides),
        *settings_errors,
    ]
    return resolvers, errors
