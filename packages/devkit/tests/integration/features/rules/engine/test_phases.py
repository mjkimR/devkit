from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import (
    Phase,
    RuleContext,
    RulesConfigError,
    Violation,
    default_rule_registry,
    evaluate_rules,
    load_rules_config,
)
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_dist.base import errors as core_errors


def _write_config(root: Path, body: str) -> Path:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


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
        ('[rules]\nexclude = "docs/**"\n', "expected an array of path patterns"),
        ('[rules]\nexclude = ["/abs/**"]\n', r"exclude\[0\].*workspace-relative"),
        ('[rules]\nexclude = ["a/**", "a/**"]\n', "duplicate pattern"),
        ('[rules]\nexclude = ["../up"]\n', "parent segment"),
    ],
)
def test_invalid_rules_config(tmp_path: Path, body: str, match: str) -> None:
    _write_config(tmp_path, body)
    with pytest.raises(RulesConfigError, match=match) as caught:
        load_rules_config(tmp_path)
    assert caught.value.code == "RULES_CONFIG_INVALID" and isinstance(caught.value, core_errors.ConfigError)


def test_unreadable_config_is_the_core_config_error(tmp_path: Path) -> None:
    _write_config(tmp_path, "invalid toml [[\n")
    with pytest.raises(core_errors.ConfigError, match="invalid config") as caught:
        load_rules_config(tmp_path)
    assert type(caught.value) is core_errors.ConfigError and caught.value.code == "CONFIG_INVALID"


def test_config_reads_exclude_patterns(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules]\nexclude = ["docs/research/**", "CHANGELOG.md"]\n')
    assert load_rules_config(tmp_path).exclude == ("docs/research/**", "CHANGELOG.md")
    assert load_rules_config(tmp_path / "nowhere").exclude == ()


def _rule(rule_id: str, phase: Phase, promote_to: Phase | None = None) -> BaseRule:
    class Stub(BaseRule):
        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "doc.md", 1, "stub", phase=self.phase)]

    return Stub(id=rule_id, name=rule_id, description="stub", phase=phase, promote_to=promote_to)


def test_override_moves_linter_rule_out_of_linter_run(tmp_path: Path) -> None:
    rules = [_rule("RULE-a", Phase.LINTER)]
    overrides = {"RULE-a": Phase.HYGIENE}

    linter = evaluate_rules(RuleContext(workspace_root=tmp_path, phase=Phase.LINTER, phase_overrides=overrides), rules)
    assert linter.violations == [] and linter.ok

    hygiene = evaluate_rules(
        RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE, phase_overrides=overrides), rules
    )
    assert [v.rule_id for v in hygiene.violations] == ["RULE-a"]
    # The violation reports the phase it ran in, not the rule's declared default.
    assert hygiene.violations[0].phase == Phase.HYGIENE


def test_override_for_unknown_rule_is_an_evaluation_error(tmp_path: Path) -> None:
    result = evaluate_rules(RuleContext(workspace_root=tmp_path, phase_overrides={"RULE-nope": Phase.HYGIENE}), [])
    assert not result.ok
    assert result.violations == []
    assert "unknown rule: RULE-nope" in str(result.errors[0])


def test_builtin_override_end_to_end(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("[broken](missing.md)\n", encoding="utf-8")
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    config = load_rules_config(tmp_path)
    rules = default_rule_registry().get_all()

    linter = evaluate_rules(RuleContext(workspace_root=tmp_path, phase_overrides=dict(config.phase_overrides)), rules)
    assert not any(v.rule_id == "RULE-markdown-link" for v in linter.violations)

    hygiene = evaluate_rules(
        RuleContext(workspace_root=tmp_path, phase=Phase.HYGIENE, phase_overrides=dict(config.phase_overrides)),
        rules,
    )
    assert any(v.rule_id == "RULE-markdown-link" for v in hygiene.violations)
