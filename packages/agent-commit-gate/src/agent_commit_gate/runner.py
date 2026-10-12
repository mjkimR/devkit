"""Run every enabled gate of one stage and collect the outcome."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from agent_advisory import AdvisoryError, as_advisory_error

from agent_commit_gate.config import GatesConfig, resolve_settings
from agent_commit_gate.models import GateConfigError, GateContext, GateResult, Outcome, Stage
from agent_commit_gate.registry import GateRegistry


@dataclass(frozen=True)
class GateRun:
    gate_id: str
    outcome: Outcome
    note: str = ""
    error: AdvisoryError | None = None


@dataclass(frozen=True)
class StageReport:
    stage: Stage
    runs: tuple[GateRun, ...]
    errors: tuple[AdvisoryError, ...] = ()  # registry and configuration problems

    @property
    def failed(self) -> bool:
        return bool(self.errors) or any(run.outcome is Outcome.FAILED for run in self.runs)


def run_stage(ctx: GateContext, registry: GateRegistry, config: GatesConfig) -> StageReport:
    """Run the stage's gates in order. A failing gate does not stop the others, so one run reports every refusal."""
    errors: list[AdvisoryError] = list(registry.errors)
    unknown = sorted(set(config.gates) - {gate.id for gate in registry.get_all()})
    if unknown:
        errors.append(
            GateConfigError(
                f"configured gates are not installed: {unknown}",
                "Select the bundle that ships them and run `devkit sync`, or remove their [gates.settings] entries.",
                target_files=[str(path) for path in config.sources],
            )
        )
    runs: list[GateRun] = []
    for gate in registry.for_stage(ctx.stage):
        if not config.enabled(gate):
            runs.append(GateRun(gate.id, Outcome.SKIPPED, "disabled"))
            continue
        try:
            entry = config.gates.get(gate.id)
            settings = resolve_settings(gate, entry.values if entry else {})
            result = gate.run(dataclasses.replace(ctx, settings=settings)) or GateResult.passed()
        except Exception as exc:
            runs.append(GateRun(gate.id, Outcome.FAILED, error=as_advisory_error(exc)))
            continue
        runs.append(GateRun(gate.id, result.outcome, result.note))
    return StageReport(ctx.stage, tuple(runs), tuple(errors))
