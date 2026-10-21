from __future__ import annotations

import pytest
from devkit_agt.features.rules import (
    Phase,
    RuleContext,
    RulesConfigError,
    Violation,
    resolve_phases,
)
from devkit_agt.features.rules.models.errors import RuleDefinitionError
from devkit_agt.features.rules.models.phases import remaining_by_rule, transition_entries, validate_phase_overrides
from devkit_agt.features.rules.repositories.config import parse_rules_config
from devkit_agt.features.rules.services.builtins import BaseRule


def _rule(rule_id: str, phase: Phase, promote_to: Phase | None = None) -> BaseRule:
    class Stub(BaseRule):
        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "doc.md", 1, "stub", phase=self.phase)]

    return Stub(id=rule_id, name=rule_id, description="stub", phase=phase, promote_to=promote_to)


def test_parse_rules_config_rejects_non_table() -> None:
    with pytest.raises(RulesConfigError, match="expected a table"):
        parse_rules_config([])


def test_promote_to_requires_hygiene_rule_targeting_linter() -> None:
    assert _rule("RULE-ok", Phase.HYGIENE, Phase.LINTER).promote_to == Phase.LINTER
    with pytest.raises(RuleDefinitionError, match="promote_to is only valid"):
        _rule("RULE-bad", Phase.LINTER, Phase.LINTER)
    with pytest.raises(RuleDefinitionError, match="promote_to is only valid"):
        _rule("RULE-bad", Phase.HYGIENE, Phase.HYGIENE)


def test_resolve_phases_reports_overrides_and_promotions() -> None:
    rules = [_rule("RULE-a", Phase.LINTER), _rule("RULE-b", Phase.HYGIENE, Phase.LINTER)]
    entries = {e.rule_id: e for e in resolve_phases(rules, {"RULE-a": Phase.HYGIENE})}

    a = entries["RULE-a"]
    assert (a.default_phase, a.effective_phase, a.overridden, a.transition) == (
        Phase.LINTER,
        Phase.HYGIENE,
        True,
        Phase.LINTER,
    )
    b = entries["RULE-b"]
    assert (b.effective_phase, b.overridden, b.promote_to, b.transition) == (
        Phase.HYGIENE,
        False,
        Phase.LINTER,
        Phase.LINTER,
    )
    assert a.to_dict()["promote_to"] is None and b.to_dict()["promote_to"] == "linter"


def test_transition_entries_only_for_rules_active_in_phase() -> None:
    rules = [_rule("RULE-a", Phase.LINTER), _rule("RULE-b", Phase.HYGIENE, Phase.LINTER)]
    entries = resolve_phases(rules, {"RULE-a": Phase.HYGIENE})
    assert [e.rule_id for e in transition_entries(entries, Phase.HYGIENE)] == ["RULE-a", "RULE-b"]
    assert transition_entries(entries, Phase.LINTER) == []


def test_validate_phase_overrides_rejects_unknown_and_redundant() -> None:
    rules = [_rule("RULE-a", Phase.LINTER), _rule("RULE-h", Phase.HYGIENE)]
    errors = validate_phase_overrides(rules, {"RULE-h": Phase.HYGIENE, "RULE-zzz": Phase.HYGIENE})
    assert any("redundant" in str(e) and e.rule_id == "RULE-h" for e in errors)
    assert any("unknown rule: RULE-zzz" in str(e) and e.rule_id == "RULE-zzz" for e in errors)
    assert {e.code for e in errors} == {"RULES_POLICY_INVALID"}
    assert validate_phase_overrides(rules, {"RULE-a": Phase.HYGIENE}) == []


def test_remaining_by_rule_skips_fixed() -> None:
    violations = [
        Violation("RULE-a", "x.md", 1, "m"),
        Violation("RULE-a", "y.md", 1, "m", fixed=True),
        Violation("RULE-b", "x.md", 1, "m"),
    ]
    assert remaining_by_rule(violations) == {"RULE-a": 1, "RULE-b": 1}
