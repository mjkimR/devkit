"""Pluggable Git commit gates for devkit workspaces.

Library entry points: ``load_gate_project`` (a repository's gates and their
validated configuration) and ``RunHookUseCase.execute`` (run one stage as the hook wrapper
does). ``devkit gate`` is a thin command line over them.
"""

from devkit_agt.features.gate.models.base import BaseGate
from devkit_agt.features.gate.models.contracts import Gate, GateContext, GateResult, Outcome, Stage
from devkit_agt.features.gate.models.errors import (
    ForeignHookError,
    GateConfigError,
    GateDefinitionError,
    GateError,
    GateInterpreterError,
    GateLoadError,
    GatePythonError,
    GateRefusedError,
    GateResultError,
    GateTemplateNotice,
    HookBackupExistsError,
    HookInstallSkippedNotice,
    HookLayoutError,
    HookPreservedNotice,
    HooksPathSetError,
)
from devkit_agt.features.gate.repositories.config import GateEntry, GatesConfig, load_gates_config, resolve_settings
from devkit_agt.features.gate.usecases.registry import (
    DeployedGates,
    GateRegistry,
    default_gate_registry,
    deployed_gate_packages,
    project_registry,
)
from devkit_agt.features.gate.usecases.runner import (
    GateProject,
    GateRun,
    RunHookUseCase,
    StageReport,
    Validation,
    load_gate_project,
    run_stage,
    validate_gates,
)

__all__ = [
    "BaseGate",
    "DeployedGates",
    "ForeignHookError",
    "Gate",
    "GateConfigError",
    "GateContext",
    "GateDefinitionError",
    "GateEntry",
    "GateError",
    "GateInterpreterError",
    "GateLoadError",
    "GateProject",
    "GatePythonError",
    "GateRefusedError",
    "GateRegistry",
    "GateResult",
    "GateResultError",
    "GateRun",
    "GateTemplateNotice",
    "GatesConfig",
    "HookBackupExistsError",
    "HookInstallSkippedNotice",
    "HookLayoutError",
    "HookPreservedNotice",
    "HooksPathSetError",
    "Outcome",
    "RunHookUseCase",
    "Stage",
    "StageReport",
    "Validation",
    "default_gate_registry",
    "deployed_gate_packages",
    "load_gate_project",
    "load_gates_config",
    "project_registry",
    "resolve_settings",
    "run_stage",
    "validate_gates",
]
