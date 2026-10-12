from __future__ import annotations

from pathlib import Path

import pytest
from agent_rule_engine import (
    ConfigError,
    Phase,
    RuleContext,
    Violation,
    default_registry,
    evaluate,
    load_rules_config,
    resolve_phases,
)
from agent_rule_engine.engine.config import parse_rules_config
from agent_rule_engine.engine.phases import remaining_by_rule, transition_entries, validate_phase_overrides
from agent_rule_engine.rules import BaseRule


def _write_config(root: Path, body: str) -> Path:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# --- config -----------------------------------------------------------------


def test_missing_config_yields_defaults(tmp_path: Path) -> None:
    config = load_rules_config(tmp_path)
    assert config.phase_overrides == {}
    assert config.source is None


def test_config_without_rules_table_is_ignored(tmp_path: Path) -> None:
    _write_config(tmp_path, 'schema = 1\nagents = ["codex"]\n')
    assert load_rules_config(tmp_path).phase_overrides == {}


def test_config_reads_phase_overrides(tmp_path: Path) -> None:
    path = _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    config = load_rules_config(tmp_path)
    assert config.phase_overrides == {"RULE-markdown-link": Phase.HYGIENE}
    assert config.source == path


@pytest.mark.parametrize(
    ("body", "match"),
    [
        ("[rules]\nunknown = 1\n", "unknown fields"),
        ("rules = 1\n", "expected a table"),
        ("[rules]\nphase_overrides = 1\n", "expected a table of rule ID"),
        ('[rules.phase_overrides]\nRULE-x = "linter"\n', "is not 'hygiene'"),
        ("[rules.phase_overrides]\nRULE-x = 1\n", "is not 'hygiene'"),
        ("invalid toml [[\n", "invalid config"),
    ],
)
def test_invalid_rules_config(tmp_path: Path, body: str, match: str) -> None:
    _write_config(tmp_path, body)
    with pytest.raises(ConfigError, match=match):
        load_rules_config(tmp_path)


def test_parse_rules_config_rejects_non_table() -> None:
    with pytest.raises(ConfigError, match="expected a table"):
        parse_rules_config([])


# --- rule metadata ----------------------------------------------------------


def _rule(rule_id: str, phase: Phase, promote_to: Phase | None = None) -> BaseRule:
    class Stub(BaseRule):
        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "doc.md", 1, "stub", phase=self.phase)]

    return Stub(id=rule_id, name=rule_id, description="stub", phase=phase, promote_to=promote_to)


def test_promote_to_requires_hygiene_rule_targeting_linter() -> None:
    assert _rule("RULE-ok", Phase.HYGIENE, Phase.LINTER).promote_to == Phase.LINTER
    with pytest.raises(ValueError, match="promote_to is only valid"):
        _rule("RULE-bad", Phase.LINTER, Phase.LINTER)
    with pytest.raises(ValueError, match="promote_to is only valid"):
        _rule("RULE-bad", Phase.HYGIENE, Phase.HYGIENE)


# --- phase resolution --------------------------------------------------------


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
    assert any("redundant" in e and "RULE-h" in e for e in errors)
    assert any("unknown rule: RULE-zzz" in e for e in errors)
    assert validate_phase_overrides(rules, {"RULE-a": Phase.HYGIENE}) == []


def test_remaining_by_rule_skips_fixed() -> None:
    violations = [
        Violation("RULE-a", "x.md", 1, "m"),
        Violation("RULE-a", "y.md", 1, "m", fixed=True),
        Violation("RULE-b", "x.md", 1, "m"),
    ]
    assert remaining_by_rule(violations) == {"RULE-a": 1, "RULE-b": 1}


# --- evaluator ---------------------------------------------------------------


def test_override_moves_linter_rule_out_of_linter_run(tmp_path: Path) -> None:
    rules = [_rule("RULE-a", Phase.LINTER)]
    overrides = {"RULE-a": Phase.HYGIENE}

    linter = evaluate(RuleContext(workspace_root=tmp_path, phase=Phase.LINTER, phase_overrides=overrides), rules)
    assert linter.violations == [] and not linter.has_errors

    hygiene = evaluate(RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE, phase_overrides=overrides), rules)
    assert [v.rule_id for v in hygiene.violations] == ["RULE-a"]
    # The violation reports the phase it ran in, not the rule's declared default.
    assert hygiene.violations[0].phase == Phase.HYGIENE


def test_override_for_unknown_rule_is_an_evaluation_error(tmp_path: Path) -> None:
    result = evaluate(RuleContext(workspace_root=tmp_path, phase_overrides={"RULE-nope": Phase.HYGIENE}), [])
    assert result.has_errors
    assert result.violations == []
    assert "unknown rule: RULE-nope" in result.errors[0]


def test_builtin_override_end_to_end(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("[broken](missing.md)\n", encoding="utf-8")
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    config = load_rules_config(tmp_path)
    rules = default_registry().get_all()

    linter = evaluate(RuleContext(workspace_root=tmp_path, phase_overrides=dict(config.phase_overrides)), rules)
    assert not any(v.rule_id == "RULE-markdown-link" for v in linter.violations)

    hygiene = evaluate(
        RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE, phase_overrides=dict(config.phase_overrides)),
        rules,
    )
    assert any(v.rule_id == "RULE-markdown-link" for v in hygiene.violations)
