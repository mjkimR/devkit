"""Built-in ``pre-commit`` gate: the rule engine's staged check.

The gate evaluates ``agent-rule-engine``'s linter phase over the exact Git
index, as ``agent-rules check --staged`` does: the staged tree is materialized
into a temporary directory and becomes the workspace root, so unstaged edits,
untracked files and local-only configuration cannot change the result.
``.devkit/config.toml``, the installation receipt and synchronized rules are
all read from the snapshot (Git-ignored managed rule copies come from the
working tree only when they match the receipt's hash).
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterable
from pathlib import Path

from agent_advisory import Actor, Retry

from agent_commit_gate.base import BaseGate
from agent_commit_gate.models import GateConfigError, GateContext, GateError, GateResult, Stage

RULE_ENGINE_PACKAGE = "agent-rule-engine"
MAX_DETAIL_LINES = 40


class StagedRulesGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="rules-staged",
            description="Refuse a commit whose staged tree fails agent-rule-engine's linter phase (agent-rules check --staged).",
            stage=Stage.PRE_COMMIT,
            order=100,
        )

    def run(self, ctx: GateContext) -> GateResult:
        try:
            from agent_rule_engine import (
                ConfigError,
                EvaluationResult,
                Phase,
                RuleContext,
                WorkspaceCache,
                default_registry,
                evaluate,
                load_rules_config,
                resolve_managed_rules,
            )
            from agent_rule_engine.workspace.snapshot import SnapshotError, git_snapshot, materialize
        except ImportError as exc:
            raise GateError(
                f"{RULE_ENGINE_PACKAGE} is not importable: {exc}",
                code="GATE_RULES_UNAVAILABLE",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
                fix=f"uv sync  (the {RULE_ENGINE_PACKAGE} package must be installed in the hook's interpreter)",
            ) from exc

        try:
            snapshot = git_snapshot(ctx.repo_root, staged=True)
        except SnapshotError as exc:
            raise GateError(
                f"cannot read the staged tree: {exc}",
                code="GATE_RULES_SNAPSHOT_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
            ) from exc
        if not snapshot.changed:
            return GateResult.skipped("no changed files in the index")

        with tempfile.TemporaryDirectory(prefix="commit-gate-rules-") as directory:
            root = Path(directory)
            try:
                materialize(snapshot, root)
            except SnapshotError as exc:
                raise GateError(
                    f"cannot materialize the staged tree: {exc}",
                    code="GATE_RULES_SNAPSHOT_FAILED",
                    actor=Actor.DEVELOPER,
                    retry=Retry.AFTER_FIX,
                ) from exc

            try:
                config = load_rules_config(root)
            except ConfigError as exc:
                raise GateConfigError(
                    f"invalid [rules] policy in the staged tree: {exc}",
                    code="GATE_RULES_CONFIG_INVALID",
                    target_files=[".devkit/config.toml"],
                    fix="Correct [rules] in .devkit/config.toml and stage the file",
                ) from exc

            registry = default_registry()
            managed = resolve_managed_rules(root, source_root=ctx.repo_root)
            registry.errors.extend(managed.errors)
            registry.discover_from_files(managed.paths)
            if registry.errors:
                raise GateError(
                    "synchronized rules could not be loaded",
                    *_cap(registry.errors),
                    code="GATE_RULES_LOAD_FAILED",
                    actor=Actor.DEVELOPER,
                    retry=Retry.AFTER_FIX,
                    fix="devkit sync  (restores managed rule files recorded in the receipt), then stage the receipt",
                )

            rule_ctx = RuleContext(
                workspace_root=root,
                changed_files=list(snapshot.changed),
                phase=Phase.LINTER,
                cache=WorkspaceCache(root),
                phase_overrides=dict(config.phase_overrides),
                severity_overrides=dict(config.severity_overrides),
                rule_settings=dict(config.settings),
            )
            result: EvaluationResult = evaluate(rule_ctx, registry.get_all())

        if result.errors:
            raise GateError(
                "rule evaluation failed on the staged tree",
                *_cap(result.errors),
                code="GATE_RULES_FAILED",
                actor=Actor.DEVELOPER,
                retry=Retry.AFTER_FIX,
                fix="Fix the rule execution or policy error reported by agent-rule-engine (`agent-rules check --staged`)",
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
                    "uv run agent-rules fix  (repairs fixable findings; stage the result), "
                    f"uv run agent-rules explain {rule_ids[0]}  (rule guide and effective settings)"
                ),
                target_files=sorted({v.file for v in errors}),
            )
        note = f"{len(snapshot.changed)} changed file(s) checked"
        if warnings:
            note += f", {warnings} warning(s)"
        return GateResult.passed(note)


def _cap(lines: Iterable[object]) -> list[str]:
    items = [str(line) for line in lines]
    if len(items) <= MAX_DETAIL_LINES:
        return items
    return [*items[:MAX_DETAIL_LINES], f"... and {len(items) - MAX_DETAIL_LINES} more"]
