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
"""

from __future__ import annotations

from collections.abc import Iterable

from devkit.advisory import Actor, Retry
from devkit.gate.base import BaseGate
from devkit.gate.models import GateConfigError, GateContext, GateError, GateResult, Stage
from devkit.rules import ConfigError, SnapshotError, git_snapshot, run_project_rules

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
        try:
            snapshot = git_snapshot(ctx.repo_root, staged=True)
        except SnapshotError as exc:
            raise GateError(
                f"cannot read the staged tree: {exc}",
                code="GATE_RULES_SNAPSHOT_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
            ) from exc
        if not snapshot.changed and not snapshot.deleted:
            return GateResult.skipped("no changed files in the index")

        try:
            run = run_project_rules(snapshot.root, snapshot=snapshot)
        except SnapshotError as exc:
            raise GateError(
                f"cannot materialize the staged tree: {exc}",
                code="GATE_RULES_SNAPSHOT_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
            ) from exc
        except ConfigError as exc:
            raise GateConfigError(
                f"invalid [rules] policy in the staged tree: {exc}",
                code="GATE_RULES_CONFIG_INVALID",
                target_files=[".devkit/config.toml"],
                fix="Correct [rules] in .devkit/config.toml and stage the file",
            ) from exc

        if run.load_errors:
            raise GateError(
                "synchronized rules could not be loaded",
                *_cap(run.load_errors),
                code="GATE_RULES_LOAD_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
                fix="devkit sync  (restores managed rule files recorded in the receipt), then stage the receipt",
            )

        result = run.result
        if result.errors:
            raise GateError(
                "rule evaluation failed on the staged tree",
                *_cap(result.errors),
                code="GATE_RULES_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
                fix="Fix the rule execution or policy error reported by devkit.rules (`devkit rules check --staged`)",
            )

        errors = [v for v in result.violations if v.severity.value == "error" and not v.fixed]
        warnings = sum(1 for v in result.violations if v.severity.value == "warning")
        if errors:
            rule_ids = sorted({v.rule_id for v in errors})
            raise GateError.blocked(
                f"{len(errors)} rule violation(s) in the staged tree ({snapshot.describe()})",
                *_cap(f"{v.rule_id} {v.file}:{v.line} {v.message}" for v in errors),
                code="GATE_RULES_VIOLATION",
                fix=(
                    "uv run devkit rules fix  (repairs fixable findings; stage the result), "
                    f"uv run devkit rules explain {rule_ids[0]}  (rule guide and effective settings)"
                ),
                target_files=sorted({v.file for v in errors}),
            )
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
