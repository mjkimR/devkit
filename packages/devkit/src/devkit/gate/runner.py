"""Validate the gate setup and run every enabled gate of one stage."""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from devkit.advisory import AdvisoryError, as_advisory_error
from devkit.gate.config import GatesConfig, resolve_settings
from devkit.gate.models import RESULT_INVALID, GateConfigError, GateContext, GateResult, Outcome, Stage
from devkit.gate.registry import GateRegistry

INVALID_SETTINGS_NOTE = "invalid settings"


@dataclass(frozen=True)
class GateRun:
    gate_id: str
    outcome: Outcome
    note: str = ""
    error: AdvisoryError | None = None  # set exactly when ``outcome`` is ``FAILED``


@dataclass(frozen=True)
class Validation:
    """Every problem that fails the blocking stages, and the resolved settings of each validly configured gate."""

    settings: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    errors: tuple[AdvisoryError, ...] = ()


@dataclass(frozen=True)
class StageReport:
    stage: Stage
    runs: tuple[GateRun, ...]
    errors: tuple[AdvisoryError, ...] = ()  # registry and configuration problems

    @property
    def failed(self) -> bool:
        return bool(self.errors) or any(run.outcome is Outcome.FAILED for run in self.runs)


def validate(registry: GateRegistry, config: GatesConfig) -> Validation:
    """Check the registry and the configuration of every gate, whatever its stage or enablement.

    Registry errors, configured gates that are not installed, and invalid
    settings of any gate (enabled or not) are all reported, so ``status`` and
    every stage see the same problems.
    """
    errors: list[AdvisoryError] = list(registry.errors)
    gates = registry.get_all()
    unknown = sorted(set(config.gates) - {gate.id for gate in gates})
    if unknown:
        errors.append(
            GateConfigError(
                f"configured gates are not installed: {unknown}",
                "Select the bundle that ships them and run `devkit sync`, or remove their [gates.settings] entries.",
                target_files=[str(path) for path in config.sources],
            )
        )
    settings: dict[str, Any] = {}
    for gate in gates:
        entry = config.gates.get(gate.id)
        try:
            settings[gate.id] = resolve_settings(gate, entry.values if entry else {})
        except Exception as exc:
            errors.append(as_advisory_error(exc))
    return Validation(MappingProxyType(settings), tuple(errors))


def _invalid_result(gate_id: str, result: object) -> GateConfigError:
    return GateConfigError(
        f"gate {gate_id!r} returned {type(result).__name__}; run() returns a GateResult or None",
        code=RESULT_INVALID,
        input_error=False,
    )


def run_stage(
    ctx: GateContext, registry: GateRegistry, config: GatesConfig, validation: Validation | None = None
) -> StageReport:
    """Run the stage's gates in order. A failing gate does not stop the others, so one run reports every refusal.

    ``validation`` defaults to ``validate(registry, config)``; its errors fail
    the stage, and a gate whose settings are invalid is skipped.
    """
    checked = validation if validation is not None else validate(registry, config)
    runs: list[GateRun] = []
    for gate in registry.for_stage(ctx.stage):
        if not config.enabled(gate):
            runs.append(GateRun(gate.id, Outcome.SKIPPED, "disabled"))
            continue
        if gate.id not in checked.settings:
            runs.append(GateRun(gate.id, Outcome.SKIPPED, INVALID_SETTINGS_NOTE))
            continue
        try:
            result = gate.run(dataclasses.replace(ctx, settings=checked.settings[gate.id]))
        except Exception as exc:
            runs.append(GateRun(gate.id, Outcome.FAILED, error=as_advisory_error(exc)))
            continue
        if result is None:
            result = GateResult.passed()
        if not isinstance(result, GateResult):
            runs.append(GateRun(gate.id, Outcome.FAILED, error=_invalid_result(gate.id, result)))
            continue
        runs.append(GateRun(gate.id, result.outcome, result.note))
    return StageReport(ctx.stage, tuple(runs), checked.errors)
