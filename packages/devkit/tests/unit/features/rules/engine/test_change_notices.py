from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules import ChangeSpan, Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.models.phases import remaining_by_rule
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_agt.features.rules.services.changes import excerpts, file_change
from devkit_agt.features.rules.services.evaluator import evaluate_rules


def test_exact_spans_and_deletion_anchors() -> None:
    change = file_change(
        "a.py", b"def f():\n    old()\n", b"def f():\n    new()\n", mode="working", base="tree", status="modified"
    )
    assert change.affects(change.span("after", 1, 3))
    assert not change.affects(change.span("after", 1, 2))
    assert not change.affects(ChangeSpan("a.py", "after", 1, 3, "stale"))
    deleted = file_change("a.py", b"old\n", b"", mode="ci", base="tree", status="deleted")
    assert deleted.affects(deleted.span("before", 1, 2))
    assert deleted.hunks[0].after.start == deleted.hunks[0].after.end == 1


def test_notice_metadata_is_nonrepairable_and_info_distinct() -> None:
    class Notice(BaseRule):
        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "a.py", 1, "consider", fixable=True)]

    notice = Notice("RULE-fixture", "fixture", "fixture", severity=Severity.NOTICE)
    run = evaluate_rules(RuleContext(Path("/virtual")), [notice])
    assert [e.code for e in run.errors] == ["RULES_EXECUTION_FAILED"]
    assert Severity.INFO.value == "info" and Severity.NOTICE.value == "notice"
    assert remaining_by_rule([Violation("RULE-fixture", "a.py", 1, "consider", severity=Severity.NOTICE)]) == {}


def test_change_rules_are_omitted_in_hygiene_and_reject_bad_policy() -> None:
    class Notice(BaseRule):
        def check(self, ctx: RuleContext) -> list[Violation]:
            raise AssertionError("hygiene must not call change-scoped rules")

    rule = Notice("RULE-fixture", "fixture", "fixture", severity=Severity.NOTICE, change_scope=True)
    run = evaluate_rules(RuleContext(Path("/virtual"), phase=Phase.HYGIENE), [rule])
    assert run.ok and not run.errors
    bad = evaluate_rules(RuleContext(Path("/virtual"), phase_overrides={rule.id: Phase.HYGIENE}), [rule])
    assert any(e.code == "RULES_POLICY_INVALID" for e in bad.errors)


def test_excerpt_limits_are_utf8_byte_bounded() -> None:
    change = file_change("a.py", b"", ("가" * 500 + "\n").encode() * 30, mode="working", base="tree", status="added")
    hunks, omitted = excerpts(change)
    assert len(hunks) == 1
    shown = sum(len(h[key].encode()) for h in hunks for key in ("before_text", "after_text"))
    assert shown <= 8192 and omitted["bytes"] + shown == len(change.after.encode())
    assert omitted["lines"] > 0
