"""Pluggable Git commit gates for devkit workspaces.

Library entry points: ``load_gate_project`` (a repository's gates and their
validated configuration) and ``run_hook`` (run one stage as the hook wrapper
does). ``devkit gate`` is a thin command line over them.
"""

from devkit.gate.engine.base import BaseGate
from devkit.gate.engine.config import GateEntry, GatesConfig, load_gates_config, resolve_settings
from devkit.gate.engine.models import Gate, GateContext, GateResult, Outcome, Stage
from devkit.gate.engine.registry import (
    DeployedGates,
    GateRegistry,
    default_gate_registry,
    deployed_gate_packages,
    project_registry,
)
from devkit.gate.engine.runner import (
    GateProject,
    GateRun,
    StageReport,
    Validation,
    load_gate_project,
    run_hook,
    run_stage,
    validate_gates,
)
from devkit.gate.errors import (
    ForeignHookError,
    GateConfigError,
    GateDefinitionError,
    GateError,
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
    "Stage",
    "StageReport",
    "Validation",
    "default_gate_registry",
    "deployed_gate_packages",
    "load_gate_project",
    "load_gates_config",
    "project_registry",
    "resolve_settings",
    "run_hook",
    "run_stage",
    "validate_gates",
]
