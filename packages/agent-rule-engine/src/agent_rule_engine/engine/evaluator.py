from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agent_rule_engine.engine.models import Autofixable, Phase, Rule, RuleContext, Violation

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    violations: list[Violation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors) or any(v.severity.value == "error" and not v.fixed for v in self.violations)


def evaluate(ctx: RuleContext, rules: list[Rule]) -> EvaluationResult:
    """Evaluate rules sequentially using context and cache, applying autofix and convergence rechecks."""
    result = EvaluationResult()

    # 1. Phase filtering
    active_rules: list[Rule] = []
    for r in rules:
        if ctx.phase == Phase.LINTER and r.phase != Phase.LINTER:
            continue
        active_rules.append(r)

    # 2. Prerequisite ordering: format rules run before relationship checks
    active_rules.sort(key=lambda r: 0 if r.id == "RULE-spec-format" else 1)

    # 3. Initial check
    initial_violations: list[Violation] = []
    for r in active_rules:
        try:
            violations = r.check(ctx)
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
            violations = r.check(ctx)
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
