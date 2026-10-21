"""Built-in ``pre-commit`` gate: check the staged tree against the project's rules.

It runs what ``devkit rules check --staged`` runs, in the hook's own process:
``git_snapshot(staged=True)`` captures the index of the commit being made (Git's
``GIT_INDEX_FILE``, so ``git commit -a`` and ``git commit <paths>`` are checked as
committed) and ``run_project_rules`` evaluates the linter phase on the snapshot's
changed files, reading the policy, the receipt and the tracked rules from the
snapshot. The rules themselves are policy and ship in bundles; this gate is the
rule engine's commit-time integration, so it is on by default and a project turns
it off with ``enabled = false``.

While the rules run, the hook's ``GIT_DIR``, ``GIT_INDEX_FILE``, ``GIT_WORK_TREE`` and
``GIT_PREFIX`` are removed from the environment and the index is passed as
``DEVKIT_GIT_INDEX_FILE``, as ``verify-commands`` does for its commands, so a rule that
runs Git in the materialized snapshot is not pointed at this repository; the
environment is restored afterwards.

A commit with nothing staged is skipped. Unfixed error-severity violations refuse
the commit (``GATE_RULES_FAILED``); warning-severity ones are returned as one
``GATE_RULES_WARNINGS`` notice. A run that could not complete (rules that cannot
load, an invalid ``[rules]`` table, a rule that raised) is ``RULES_RUN_FAILED``,
not a refusal: ``AUTO`` with the shared fix when every problem is ``AUTO`` with the
same one (managed rule files missing: ``devkit sync``), else ``MAINTENANCE``.

The rule engine is imported when the gate runs, so other stages do not load it.
"""

from __future__ import annotations

import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from devkit.advisory import Actor
from devkit_core.core.git import COMMIT_INDEX_VARIABLE

from devkit_agt.features.gate.models.base import BaseGate
from devkit_agt.features.gate.models.contracts import GateContext, GateResult, Stage
from devkit_agt.features.gate.models.errors import GateRefusedError, RulesWarningsNotice
from devkit_agt.features.gate.usecases.gates.commands import HOOK_GIT_VARIABLES

if TYPE_CHECKING:
    from devkit_agt.features.rules import RuleProblem, RulesRunError, Violation

# Violations listed in a refusal or notice; the rest are counted.
MAX_LISTED = 20


@contextmanager
def _rules_environment(root: Path) -> Iterator[None]:
    """The hook's Git variables removed and its index passed as ``DEVKIT_GIT_INDEX_FILE`` until the block ends."""
    saved = {name: os.environ.pop(name) for name in (*HOOK_GIT_VARIABLES, COMMIT_INDEX_VARIABLE) if name in os.environ}
    if index := saved.get("GIT_INDEX_FILE"):
        os.environ[COMMIT_INDEX_VARIABLE] = str(root / index)  # Git may pass it relative to the top level
    try:
        yield
    finally:
        for name in (*HOOK_GIT_VARIABLES, COMMIT_INDEX_VARIABLE):
            os.environ.pop(name, None)
        os.environ.update(saved)


def _listed(violations: Sequence[Violation]) -> list[str]:
    lines: list[str] = []
    for violation in violations[:MAX_LISTED]:
        lines.append(f"{violation.rule_id} {violation.file}:{violation.line}: {violation.message}")
        if violation.remediation:
            lines.append(f"  fix: {violation.remediation}")
    if len(violations) > MAX_LISTED:
        lines.append(f"... and {len(violations) - MAX_LISTED} more")
    return lines


def _not_run(problems: Sequence[RuleProblem]) -> RulesRunError:
    from devkit_agt.features.rules import RulesRunError

    fixes = {problem.fix for problem in problems}
    if all(problem.actor is Actor.TOOL for problem in problems) and len(fixes) == 1 and all(fixes):
        return RulesRunError(problems, actor=Actor.TOOL, fix=next(iter(fixes)))
    return RulesRunError(problems)


class RulesCheckGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="rules-check",
            description="Check the staged tree against the project's rules (devkit rules check --staged).",
            stage=Stage.PRE_COMMIT,
        )

    def run(self, ctx: GateContext) -> GateResult:
        from devkit_agt.features.rules import Severity, git_snapshot, run_project_rules

        with _rules_environment(ctx.repo_root):
            snapshot = git_snapshot(ctx.repo_root, staged=True)
            if not snapshot.changed and not snapshot.deleted:
                return GateResult.skipped("nothing staged")
            run = run_project_rules(snapshot.root, snapshot=snapshot)
        if run.errors:
            raise _not_run(run.errors)
        blocking = run.blocking_violations
        if blocking:
            raise GateRefusedError(
                f"{len(blocking)} rule violation(s) in the staged tree",
                *_listed(blocking),
                code="GATE_RULES_FAILED",
                fix=(
                    "Fix the violations (devkit rules fix repairs the fixable ones), stage the fixes and commit again; "
                    "devkit rules check --staged reproduces this check"
                ),
            )
        warnings = [v for v in run.result.violations if v.severity is Severity.WARNING and not v.fixed]
        notices = (
            [RulesWarningsNotice(f"{len(warnings)} rule warning(s) in the staged tree", *_listed(warnings))]
            if warnings
            else []
        )
        return GateResult.passed(f"{len(snapshot.changed)} staged file(s) checked", notices=notices)
