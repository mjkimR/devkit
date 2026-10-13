"""Validate the gate setup and run every enabled gate of one stage.

The library entry points behind ``devkit gate``: ``load_gate_project`` reads a
repository's gates and their validated configuration (what ``gate status``
reports), ``run_hook`` runs one stage the way the hook wrappers do.
``validate_gates`` and ``run_stage`` are the steps underneath.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

from devkit.advisory import AdvisoryError, ExitCode, Level, as_advisory_error
from devkit.compact import CommandInterrupted
from devkit.core import ConfigError, require_git_toplevel
from devkit.core.logs import get_logger
from devkit.gate.engine.config import GatesConfig, load_gates_config, resolve_settings
from devkit.gate.engine.models import Gate, GateContext, GateResult, Outcome, Stage
from devkit.gate.engine.registry import GateRegistry, project_registry
from devkit.gate.errors import GateConfigError, GateResultError
from devkit.gate.hooks import git

INVALID_SETTINGS_NOTE = "invalid settings"
NOT_INSTALLED_FIX = "Select the bundle that ships them and run `devkit sync`, or remove their [gates.settings] entries"

_log = get_logger(__name__)


def _highest_exit_code(problems: Sequence[AdvisoryError]) -> ExitCode:
    return max((problem.exit_code for problem in problems), default=ExitCode.OK)


@dataclass(frozen=True)
class GateRun:
    gate_id: str
    outcome: Outcome
    note: str = ""
    error: AdvisoryError | None = None  # set exactly when ``outcome`` is ``FAILED``
    notices: tuple[AdvisoryError, ...] = ()  # warnings and notices of a gate that passed or was skipped


@dataclass(frozen=True)
class Validation:
    """Every problem that fails the blocking stages, and the resolved settings of each validly configured gate."""

    settings: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    errors: tuple[AdvisoryError, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def exit_code(self) -> ExitCode:
        """The highest ``exit_code`` among ``errors``; ``OK`` when there are none."""
        return _highest_exit_code(self.errors)


@dataclass(frozen=True)
class StageReport:
    stage: Stage
    runs: tuple[GateRun, ...]
    errors: tuple[AdvisoryError, ...] = ()  # registry and configuration problems

    @property
    def problems(self) -> tuple[AdvisoryError, ...]:
        """The setup problems, then the error of every failed gate, in run order."""
        return (*self.errors, *(run.error for run in self.runs if run.error is not None))

    @property
    def notices(self) -> tuple[AdvisoryError, ...]:
        """The warnings and notices of every gate, in run order; they never fail the stage."""
        return tuple(notice for run in self.runs for notice in run.notices)

    @property
    def ok(self) -> bool:
        """Whether every gate passed or was skipped and the setup has no problem."""
        return not self.problems

    @property
    def exit_code(self) -> ExitCode:
        """The highest ``exit_code`` among ``problems``: ``1`` for refusals, ``2`` for setup or load problems.

        ``OK`` when there are none. ``devkit gate run`` exits with it on a
        blocking stage; post-commit never blocks.
        """
        return _highest_exit_code(self.problems)


def validate_gates(registry: GateRegistry, config: GatesConfig) -> Validation:
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
                fix=NOT_INSTALLED_FIX,
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


def run_stage(
    ctx: GateContext, registry: GateRegistry, config: GatesConfig, validation: Validation | None = None
) -> StageReport:
    """Run the stage's gates in order. A failing gate does not stop the others, so one run reports every refusal.

    ``validation`` defaults to ``validate_gates(registry, config)``; its errors
    fail the stage, and a gate whose settings are invalid is skipped. Each
    outcome is logged (``devkit gate run -v`` prints it as an ``[INFO]`` line).
    """
    checked = validation if validation is not None else validate_gates(registry, config)
    runs: list[GateRun] = []
    for gate in registry.for_stage(ctx.stage):
        run = _run_gate(gate, ctx, config, checked)
        note = f" note={run.note}" if run.note else ""
        _log.info("gate %s stage=%s outcome=%s%s", run.gate_id, ctx.stage, run.outcome, note)
        runs.append(run)
    return StageReport(ctx.stage, tuple(runs), checked.errors)


def _run_gate(gate: Gate, ctx: GateContext, config: GatesConfig, checked: Validation) -> GateRun:
    if not config.enabled(gate):
        return GateRun(gate.id, Outcome.SKIPPED, "disabled")
    if gate.id not in checked.settings:
        return GateRun(gate.id, Outcome.SKIPPED, INVALID_SETTINGS_NOTE)
    try:
        result = gate.run(dataclasses.replace(ctx, settings=checked.settings[gate.id]))
    except CommandInterrupted:  # a signal stopped a gate's `run_command`: abort like Ctrl-C, exiting 128 + N
        raise
    except (Exception, SystemExit) as exc:  # a gate calling sys.exit() must not end the stage; Ctrl-C still aborts it
        return GateRun(gate.id, Outcome.FAILED, error=as_advisory_error(exc))
    if result is None:
        result = GateResult.passed()
    if not isinstance(result, GateResult):
        error = GateResultError(
            f"gate {gate.id!r} returned {type(result).__name__}; run() returns a GateResult or None"
        )
        return GateRun(gate.id, Outcome.FAILED, error=error)
    notices = tuple(n.with_level(Level.WARNING) if n.level is Level.ERROR else n for n in result.notices)
    return GateRun(gate.id, result.outcome, result.note, notices=notices)


@dataclass(frozen=True)
class GateProject:
    """A repository's gates and their validated configuration: everything ``gate status`` and a stage run read."""

    root: Path  # top level of the Git work tree
    git_dir: Path
    common_git_dir: Path
    registry: GateRegistry
    config: GatesConfig
    validation: Validation  # includes a configuration file that cannot be read or parsed

    def context(self, stage: Stage, args: Sequence[str] = ()) -> GateContext:
        """The context a gate of ``stage`` runs in, with the arguments Git passed to the hook."""
        return GateContext(
            repo_root=self.root,
            git_dir=self.git_dir,
            common_git_dir=self.common_git_dir,
            stage=stage,
            args=tuple(args),
        )


def load_gate_project(root: Path) -> GateProject:
    """Load the gates and the validated ``[gates]`` configuration of the Git work tree containing ``root``.

    ``root`` may be any directory inside the work tree; the project is its top
    level. Registry, configuration and settings problems (including a
    configuration file that cannot be read, the core ``ConfigError``) are
    collected in ``validation.errors`` rather than raised; only a failed Git
    query raises (``GitError``, ``GIT_FAILED``).
    """
    top = require_git_toplevel(root)
    common = git.common_git_dir(top)
    registry = project_registry(top)
    load_errors: list[AdvisoryError] = []
    try:
        config = load_gates_config(top, common)
    except ConfigError as exc:
        config = GatesConfig()
        load_errors.append(exc)
    checked = validate_gates(registry, config)
    validation = Validation(checked.settings, (*load_errors, *checked.errors))
    return GateProject(top, git.git_dir(top), common, registry, config, validation)


def run_hook(root: Path, stage: Stage, args: Sequence[str] = ()) -> StageReport:
    """Run one stage's gates for the work tree containing ``root``, as the hook wrapper does.

    ``args`` are the arguments Git passed to the hook (the message file of
    ``commit-msg``). The report's ``exit_code`` is what a blocking stage exits
    with; raises only what ``load_gate_project`` raises.
    """
    project = load_gate_project(root)
    return run_stage(project.context(stage, args), project.registry, project.config, project.validation)
