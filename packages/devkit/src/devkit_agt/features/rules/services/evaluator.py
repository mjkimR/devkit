"""One evaluation of a rule set: policy validation, phase filtering, target scoping, checks, autofix and the
convergence recheck."""

from __future__ import annotations

import inspect
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace

from devkit.advisory import AdvisoryError, Level
from devkit_core.core.logs import get_logger
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH

from devkit_agt.features.rules.models.contracts import Autofixable, Rule, RuleContext, Severity, Violation
from devkit_agt.features.rules.models.errors import RuleExecutionError, RuleProblem, SettingsError
from devkit_agt.features.rules.models.phases import effective_phase, runs_in_phase
from devkit_agt.features.rules.models.policy import effective_severity, validate_policy
from devkit_agt.features.rules.models.settings import match_path

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    violations: list[Violation] = field(default_factory=list)
    errors: list[RuleProblem] = field(default_factory=list)
    # IDs of the active rules the final check pass did not evaluate, because no explicit target matched their
    # declared ``inputs`` (``scope_rules``).
    skipped: list[str] = field(default_factory=list)

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


def scope_rules(ctx: RuleContext, rules: Sequence[Rule], modified: Iterable[str] = ()) -> tuple[list[Rule], list[str]]:
    """The rules of ``rules`` a run must evaluate, and the IDs of those it can skip.

    A rule with declared ``inputs`` (read with ``getattr``) is skipped only in a working-tree run with explicit
    targets (``ctx.has_targets`` and no ``ctx.snapshot``) when no target, before ``[rules] exclude``, and no file in
    ``modified`` (the files fixes wrote) matches one of its patterns. A target that is the project configuration
    ``.devkit/config.toml`` keeps every rule, since ``[rules]`` policy can change any rule's findings. Undeclared rules
    always run, and so does every rule of a whole-workspace or snapshot run.
    """
    if not ctx.has_targets or ctx.snapshot is not None:
        return list(rules), []
    names = list(ctx.targets)
    names.extend(relative for path in modified if (relative := ctx.relative_path(path)) is not None)
    if CONFIG_PATH in names:
        return list(rules), []
    selected: list[Rule] = []
    skipped: list[str] = []
    for rule in rules:
        inputs: tuple[str, ...] | None = getattr(rule, "inputs", None)
        if inputs is None or any(match_path(pattern, name) for pattern in inputs for name in names):
            selected.append(rule)
        else:
            skipped.append(rule.id)
    return selected, skipped


def evaluate_rules(ctx: RuleContext, rules: Sequence[Rule]) -> EvaluationResult:
    """Evaluate ``rules`` in order against ``ctx``, applying autofix and one convergence recheck when asked.

    The project policy in ``ctx`` is validated first, together with every
    rule's ``inputs`` declaration; any problem is returned without running a
    rule. Only rules active in ``ctx.phase`` (after phase overrides) run, minus
    those ``scope_rules`` skips for the explicit targets; their IDs are returned
    in ``skipped``. With ``ctx.fix`` (and not ``ctx.dry_run``) every selected
    autofixable rule fixes, then the rules ``scope_rules`` selects for the
    targets plus the modified files check again (every active rule when a fix
    failed, since its writes are unknown): a fixable initial finding the
    recheck no longer reports is returned with ``fixed`` set, followed by the
    recheck's findings.
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
    selected, skipped = scope_rules(ctx, active)
    result = EvaluationResult(skipped=skipped)
    _log_skipped(skipped)
    initial = _check_rules(ctx, selected, "execution", result.errors)
    if not ctx.fix or ctx.dry_run or result.errors:
        result.violations = initial
        return result

    modified = _apply_fixes(ctx, selected, result.errors)
    if not modified and not result.errors:
        result.violations = initial
        return result

    if result.errors:
        rechecked, skipped = active, []
    else:
        rechecked, skipped = scope_rules(ctx, active, modified)
    result.skipped = skipped
    recheck = _check_rules(ctx, rechecked, "recheck", result.errors)
    result.violations = recheck if result.errors else _mark_fixed(initial, recheck)
    return result


def _log_skipped(skipped: Sequence[str]) -> None:
    if skipped:
        logger.info("Skipped rules no explicit target can affect (declared inputs): %s", ", ".join(skipped))


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
