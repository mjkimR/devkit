"""Built-in ``pre-commit`` gate: the rule engine's staged check.

The gate evaluates ``devkit.rules``'s linter phase over the exact Git
index through ``run_project_rules``, the same entry point ``devkit rules check
--staged`` uses: the staged tree is materialized into a temporary directory and
becomes the workspace root, so unstaged edits, untracked files and local-only
configuration cannot change the result. A commit that only deletes files still
runs the evaluation (the policy and the rules are loaded and checked); it is
skipped only when the index changes nothing. ``.devkit/config.toml`` (including
``[rules] exclude``), the installation receipt and synchronized rules are all
read from the snapshot (Git-ignored managed rule copies come from the working
tree only when they match the receipt's hash).

The rule engine's own errors pass through unchanged and fail the stage: a
snapshot that cannot be read (``RULES_SNAPSHOT_FAILED``), an invalid
``[rules]`` table (``RULES_CONFIG_INVALID``, or the core ``CONFIG_INVALID``),
and a run that could not complete (``RULES_RUN_FAILED``, carrying every load,
policy and execution problem). Only unfixed error violations are this gate's
refusal (``GATE_RULES_VIOLATION``).
"""

from __future__ import annotations

from collections.abc import Iterable

from devkit.gate.engine.base import BaseGate
from devkit.gate.engine.models import GateContext, GateResult, Stage
from devkit.gate.errors import GateRefusedError
from devkit.rules import git_snapshot, run_project_rules

MAX_DETAIL_LINES = 40


class StagedRulesGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="rules-staged",
            description="Refuse a commit whose staged tree fails devkit.rules's linter phase (devkit rules check --staged).",
            stage=Stage.PRE_COMMIT,
            order=100,
        )

    def run(self, ctx: GateContext) -> GateResult:
        snapshot = git_snapshot(ctx.repo_root, staged=True)
        if not snapshot.changed and not snapshot.deleted:
            return GateResult.skipped("no changed files in the index")

        run = run_project_rules(snapshot.root, snapshot=snapshot)
        run.raise_for_problems()

        errors = run.blocking_violations
        if errors:
            rule_ids = sorted({v.rule_id for v in errors})
            raise GateRefusedError(
                f"{len(errors)} rule violation(s) in the staged tree ({snapshot.describe()})",
                *_cap(f"{v.rule_id} {v.file}:{v.line} {v.message}" for v in errors),
                code="GATE_RULES_VIOLATION",
                fix=(
                    "Run `devkit rules fix` to repair fixable findings and stage the result; "
                    f"`devkit rules explain {rule_ids[0]}` shows the rule guide and effective settings"
                ),
                target_files=sorted({v.file for v in errors}),
            )
        warnings = sum(1 for v in run.result.violations if v.severity.value == "warning")
        note = f"{len(snapshot.changed)} changed file(s) checked"
        if snapshot.deleted:
            note += f", {len(snapshot.deleted)} deleted"
        if warnings:
            note += f", {warnings} warning(s)"
        return GateResult.passed(note)


def _cap(lines: Iterable[object]) -> list[str]:
    items = [str(line) for line in lines]
    if len(items) <= MAX_DETAIL_LINES:
        return items
    return [*items[:MAX_DETAIL_LINES], f"... and {len(items) - MAX_DETAIL_LINES} more"]
