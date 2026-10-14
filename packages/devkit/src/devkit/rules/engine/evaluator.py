"""One evaluation of a rule set: policy validation, phase filtering, checks, autofix and the convergence recheck."""

from __future__ import annotations

import inspect
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from devkit.advisory import AdvisoryError, Level
from devkit.core.logs import get_logger
from devkit.rules.engine.errors import RuleExecutionError, RuleProblem, SettingsError
from devkit.rules.engine.models import Autofixable, Rule, RuleContext, Severity, Violation
from devkit.rules.engine.phases import effective_phase, runs_in_phase
from devkit.rules.engine.policy import effective_severity, validate_policy

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    violations: list[Violation] = field(default_factory=list)
    errors: list[RuleProblem] = field(default_factory=list)

    @property
    def blocking_violations(self) -> list[Violation]:
        """Unfixed error-severity violations: the findings that fail a run."""
        return [v for v in self.violations if v.severity is Severity.ERROR and not v.fixed]

    @property
    def ok(self) -> bool:
        """Whether the evaluation completed without problems and no blocking violation remains."""
        return not self.errors and not self.blocking_violations


def _finding_key(v: Violation) -> tuple[str, str, str]:
    """Identity of a finding across the fix pass; the line is left out because fixes may move it."""
    return v.rule_id, v.file, v.message


def evaluate_rules(ctx: RuleContext, rules: Sequence[Rule]) -> EvaluationResult:
    """Evaluate ``rules`` in order against ``ctx``, applying autofix and one convergence recheck when asked.

    The project policy in ``ctx`` is validated first; any policy problem is
    returned without running a rule. Only rules active in ``ctx.phase`` (after
    phase overrides) run. With ``ctx.fix`` (and not ``ctx.dry_run``) every
    autofixable rule fixes, then every active rule checks again: a fixable
    initial finding the recheck no longer reports is returned with ``fixed``
    set, followed by the recheck's findings.
    """
    resolvers, policy_errors = validate_policy(
        rules,
        phase_overrides=ctx.phase_overrides,
        severity_overrides=ctx.severity_overrides,
        settings=ctx.rule_settings,
    )
    if policy_errors:
        return EvaluationResult(errors=list(policy_errors))
    ctx.settings_resolvers = resolvers

    active = [r for r in rules if runs_in_phase(effective_phase(r, ctx.phase_overrides), ctx.phase)]
    result = EvaluationResult()
    initial = _check_rules(ctx, active, "execution", result.errors)
    if not ctx.fix or ctx.dry_run or result.errors:
        result.violations = initial
        return result

    modified = _apply_fixes(ctx, active, result.errors)
    if not modified and not result.errors:
        result.violations = initial
        return result

    recheck = _check_rules(ctx, active, "recheck", result.errors)
    result.violations = recheck if result.errors else _mark_fixed(initial, recheck)
    return result


def _check_rules(ctx: RuleContext, rules: Sequence[Rule], stage: str, errors: list[RuleProblem]) -> list[Violation]:
    """Every rule's findings, with the effective phase and severity; a rule that raises adds to ``errors``."""
    violations: list[Violation] = []
    for rule in rules:
        try:
            found = rule.check(ctx)
        except SettingsError as exc:
            errors.append(
                SettingsError(
                    f"Invalid settings ({rule.id}): {exc}",
                    rule_id=rule.id,
                    input_error=exc.input_error,
                    target_files=exc.target_files,
                )
            )
            continue
        except Exception as exc:
            errors.append(_execution_error(rule, f"Rule {stage} error ({rule.id}): {exc}", exc))
            continue
        phase = effective_phase(rule, ctx.phase_overrides)
        severity = effective_severity(rule, ctx.severity_overrides)
        for v in found:
            v.phase = phase
            v.severity = severity
        violations.extend(found)
    return violations


def _apply_fixes(ctx: RuleContext, rules: Sequence[Rule], errors: list[RuleProblem]) -> set[str]:
    """Run every autofixable rule's ``fix`` and return the modified files.

    Returned paths are invalidated in the cache after each fix, so the next
    fixer reads fresh contents. A fixer that raises adds to ``errors``, clears
    the whole cache (its partial writes are unknown) and stops the pass.
    """
    modified: set[str] = set()
    for rule in rules:
        if not isinstance(rule, Autofixable):
            continue
        try:
            changed = rule.fix(ctx)
        except Exception as exc:
            errors.append(_execution_error(rule, f"Rule fix error ({rule.id}): {exc}", exc))
            ctx.cache.invalidate_all()
            break
        if changed:
            modified.update(changed)
            ctx.cache.invalidate_many(changed)
    return modified


def _mark_fixed(initial: Sequence[Violation], recheck: Sequence[Violation]) -> list[Violation]:
    """Fixed copies of the initial fixable findings the recheck no longer reports, then the recheck's findings.

    A finding counts as fixed when the recheck reports fewer findings with its
    identity (rule, file, message) than the initial check did; the line is not
    compared, because a fix may move it. The inputs are not modified.
    """
    remaining = Counter(_finding_key(v) for v in recheck)
    fixed: list[Violation] = []
    for v in initial:
        if not v.fixable:
            continue
        key = _finding_key(v)
        if remaining[key] > 0:
            remaining[key] -= 1
            continue
        fixed.append(replace(v, fixed=True))
    return [*fixed, *recheck]


def _execution_error(rule: Rule, message: str, exc: Exception) -> RuleExecutionError:
    """A rule that raised, attributed to the rule.

    An ``ERROR`` advisory the rule raised (a pinned write, a malformed configuration the rule reads) keeps its own
    code, mode, fix and targets, so the caller can act on it. Anything else is logged with its traceback and reported
    with the file defining the rule.
    """
    if isinstance(exc, AdvisoryError) and exc.level is Level.ERROR:
        logger.info(message)
        return RuleExecutionError(
            message,
            *exc.details,
            rule_id=rule.id,
            code=exc.code,
            actor=exc.actor,
            retry=exc.retry,
            guardrail=exc.guardrail,
            input_error=exc.input_error,
            retry_after=exc.retry_after,
            fix=exc.fix,
            what_to_report=exc.what_to_report,
            target_files=exc.target_files,
            exit_code=exc.exit_code,
        )
    logger.exception(message)
    try:
        source = [inspect.getfile(type(rule))]
    except (TypeError, OSError):
        source = []
    return RuleExecutionError(message, rule_id=rule.id, target_files=source)
