from __future__ import annotations

from devkit_agt.features.rules import (
    Violation,
)


def _finding(line: int, message: str = "bad", *, fixable: bool = True) -> Violation:
    return Violation("RULE-x", "doc.md", line, message, fixable=fixable)


def test_mark_fixed_counts_findings_by_identity_and_leaves_inputs_alone() -> None:
    from devkit_agt.features.rules.services.evaluator import _mark_fixed

    initial = [_finding(1), _finding(2), _finding(3, "other"), _finding(4, "manual", fixable=False)]
    recheck = [_finding(5), _finding(4, "manual", fixable=False)]
    marked = _mark_fixed(initial, recheck)
    # One of two "bad" findings remains (on a moved line), "other" is gone, the unfixable one stays as rechecked.
    assert [(v.line, v.message, v.fixed) for v in marked] == [
        (2, "bad", True),
        (3, "other", True),
        (5, "bad", False),
        (4, "manual", False),
    ]
    assert not any(v.fixed for v in initial) and marked[2] is recheck[0]


def test_mark_fixed_without_recheck_findings_marks_every_fixable_finding() -> None:
    from devkit_agt.features.rules.services.evaluator import _mark_fixed

    assert [v.fixed for v in _mark_fixed([_finding(1), _finding(2, fixable=False)], [])] == [True]
    assert _mark_fixed([], []) == []


def test_blocking_violations_are_unfixed_errors() -> None:
    from devkit_agt.features.rules import EvaluationResult, RuleExecutionError, Severity

    error = _finding(1)
    fixed = Violation("RULE-x", "a.md", 1, "fixed", fixed=True)
    warning = Violation("RULE-x", "a.md", 2, "warn", severity=Severity.WARNING)
    result = EvaluationResult(violations=[error, fixed, warning])
    assert result.blocking_violations == [error] and not result.ok
    assert EvaluationResult(violations=[fixed, warning]).ok
    assert not EvaluationResult(errors=[RuleExecutionError("boom")]).ok
