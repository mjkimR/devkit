from __future__ import annotations

import inspect
import logging
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field

from devkit.rules.engine.errors import RuleExecutionError, RuleProblem, SettingsError
from devkit.rules.engine.models import Autofixable, Rule, RuleContext, Severity, Violation
from devkit.rules.engine.phases import effective_phase, runs_in_phase
from devkit.rules.engine.policy import effective_severity, validate_policy

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    violations: list[Violation] = field(default_factory=list)
    errors: list[RuleProblem] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors) or any(v.severity is Severity.ERROR and not v.fixed for v in self.violations)


def _finding_key(v: Violation) -> tuple[str, str, str]:
    """Identity of a finding across the fix pass; the line is left out because fixes may move it."""
    return v.rule_id, v.file, v.message


def evaluate(ctx: RuleContext, rules: Sequence[Rule]) -> EvaluationResult:
    """Evaluate rules sequentially using context and cache, applying autofix and convergence rechecks."""
    result = EvaluationResult()

    # 0. Project policy must name known rules, change something, and type-check against settings
    resolvers, policy_errors = validate_policy(
        rules,
        phase_overrides=ctx.phase_overrides,
        severity_overrides=ctx.severity_overrides,
        settings=ctx.rule_settings,
    )
    if policy_errors:
        result.errors.extend(policy_errors)
        return result
    ctx.settings_resolvers = resolvers

    # 1. Phase filtering on the effective (overridden) phase
    phases = {r.id: effective_phase(r, ctx.phase_overrides) for r in rules}
    severities = {r.id: effective_severity(r, ctx.severity_overrides) for r in rules}
    active_rules: list[Rule] = [r for r in rules if runs_in_phase(phases[r.id], ctx.phase)]

    def _check(rule: Rule, stage: str, errors: list[RuleProblem]) -> list[Violation]:
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
            return []
        except Exception as exc:
            errors.append(_execution_error(rule, f"Rule {stage} error ({rule.id}): {exc}"))
            return []
        for v in found:
            v.phase = phases[rule.id]
            v.severity = severities[rule.id]
        return found

    # 2. Initial check
    initial_violations: list[Violation] = []
    for r in active_rules:
        initial_violations.extend(_check(r, "execution", result.errors))

    # If fix is not requested or dry_run, return initial findings
    if not ctx.fix or ctx.dry_run or result.errors:
        result.violations = initial_violations
        return result

    # 3. Autofix execution
    modified_files: set[str] = set()
    for r in active_rules:
        if isinstance(r, Autofixable):
            try:
                changed = r.fix(ctx)
                if changed:
                    modified_files.update(changed)
                    ctx.cache.invalidate_many(changed)
            except Exception as exc:
                result.errors.append(_execution_error(r, f"Rule fix error ({r.id}): {exc}"))
                ctx.cache.invalidate_all()
                break

    if not modified_files and not result.errors:
        result.violations = initial_violations
        return result

    # 4. Re-check for convergence
    recheck_violations: list[Violation] = []
    for r in active_rules:
        recheck_violations.extend(_check(r, "recheck", result.errors))

    # 5. A fixable finding is fixed when the recheck reports fewer findings with its identity
    remaining = Counter(_finding_key(v) for v in recheck_violations)
    final_violations: list[Violation] = []
    for v in initial_violations:
        if result.errors or not v.fixable:
            continue
        key = _finding_key(v)
        if remaining[key] > 0:
            remaining[key] -= 1
            continue
        v.fixed = True
        final_violations.append(v)

    final_violations.extend(recheck_violations)
    result.violations = final_violations
    return result


def _execution_error(rule: Rule, message: str) -> RuleExecutionError:
    """A rule that raised: logged with its traceback, reported with the file defining the rule."""
    logger.exception(message)
    try:
        source = [inspect.getfile(type(rule))]
    except (TypeError, OSError):
        source = []
    return RuleExecutionError(message, rule_id=rule.id, target_files=source)
