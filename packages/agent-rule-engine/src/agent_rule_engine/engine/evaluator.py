from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agent_rule_engine.engine.models import Autofixable, Rule, RuleContext, Severity, Violation
from agent_rule_engine.engine.phases import effective_phase, runs_in_phase, validate_phase_overrides
from agent_rule_engine.engine.settings import build_resolvers

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    violations: list[Violation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors) or any(v.severity.value == "error" and not v.fixed for v in self.violations)


def validate_severity_overrides(rules: list[Rule], overrides: dict[str, Severity]) -> list[str]:
    """Return human-readable problems for severity overrides that cannot apply to ``rules``."""
    by_id = {r.id: r for r in rules}
    errors: list[str] = []
    for rule_id in sorted(overrides):
        rule = by_id.get(rule_id)
        if rule is None:
            errors.append(f"severity override for unknown rule: {rule_id}")
        elif rule.severity == overrides[rule_id]:
            errors.append(
                f"severity override for {rule_id} is redundant: the rule already reports "
                f"{rule.severity.value}; remove the entry"
            )
    return errors


def effective_severity(rule: Rule, overrides: dict[str, Severity] | None = None) -> Severity:
    """Severity a rule reports once project overrides are applied."""
    if overrides and rule.id in overrides:
        return overrides[rule.id]
    return rule.severity


def evaluate(ctx: RuleContext, rules: list[Rule]) -> EvaluationResult:
    """Evaluate rules sequentially using context and cache, applying autofix and convergence rechecks."""
    result = EvaluationResult()

    # 0. Project policy must name known rules, change something, and type-check against settings
    resolvers, settings_errors = build_resolvers(rules, ctx.rule_settings)
    policy_errors = [
        *validate_phase_overrides(rules, ctx.phase_overrides),
        *validate_severity_overrides(rules, ctx.severity_overrides),
        *settings_errors,
    ]
    if policy_errors:
        result.errors.extend(policy_errors)
        return result
    ctx.settings_resolvers = resolvers

    # 1. Phase filtering on the effective (overridden) phase
    phases = {r.id: effective_phase(r, ctx.phase_overrides) for r in rules}
    severities = {r.id: effective_severity(r, ctx.severity_overrides) for r in rules}
    active_rules: list[Rule] = [r for r in rules if runs_in_phase(phases[r.id], ctx.phase)]

    # 2. Prerequisite ordering: format rules run before relationship checks
    active_rules.sort(key=lambda r: 0 if r.id == "RULE-spec-format" else 1)

    def _check(rule: Rule) -> list[Violation]:
        found = rule.check(ctx)
        for v in found:
            v.phase = phases[rule.id]
            v.severity = severities[rule.id]
        return found

    # 3. Initial check
    initial_violations: list[Violation] = []
    for r in active_rules:
        try:
            violations = _check(r)
            initial_violations.extend(violations)
        except Exception as exc:
            msg = f"Rule execution error ({r.id}): {exc}"
            logger.exception(msg)
            result.errors.append(msg)

    # If fix is not requested or dry_run, return initial findings
    if not ctx.fix or ctx.dry_run or result.errors:
        result.violations = initial_violations
        return result

    # 4. Autofix execution
    modified_files: set[str] = set()
    for r in active_rules:
        if isinstance(r, Autofixable):
            try:
                changed = r.fix(ctx)
                if changed:
                    modified_files.update(changed)
                    ctx.cache.invalidate_many(changed)
            except Exception as exc:
                msg = f"Rule fix error ({r.id}): {exc}"
                logger.exception(msg)
                result.errors.append(msg)
                ctx.cache.invalidate_all()
                break

    if not modified_files and not result.errors:
        result.violations = initial_violations
        return result

    # 5. Cache invalidation
    ctx.cache.invalidate_many(list(modified_files))

    # 6. Re-check for convergence
    recheck_violations: list[Violation] = []
    for r in active_rules:
        try:
            violations = _check(r)
            recheck_violations.extend(violations)
        except Exception as exc:
            msg = f"Rule recheck error ({r.id}): {exc}"
            logger.exception(msg)
            result.errors.append(msg)

    # 7. Calculate fixed status
    def _violation_key(v: Violation) -> str:
        return f"{v.rule_id}:{v.file}:{v.line}:{v.message}"

    remaining_keys = {_violation_key(v) for v in recheck_violations}

    final_violations: list[Violation] = []
    for v in initial_violations:
        if not result.errors and v.fixable and _violation_key(v) not in remaining_keys:
            v.fixed = True
            final_violations.append(v)

    final_violations.extend(recheck_violations)
    result.violations = final_violations
    return result
