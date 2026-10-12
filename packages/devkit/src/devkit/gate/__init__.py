"""Pluggable Git commit gates for devkit workspaces."""

from devkit.gate.base import BaseGate
from devkit.gate.config import GateEntry, GatesConfig, load_gates_config, resolve_settings
from devkit.gate.models import (
    Gate,
    GateConfigError,
    GateContext,
    GateError,
    GateResult,
    Outcome,
    Stage,
)
from devkit.gate.registry import DeployedGates, GateRegistry, default_registry, deployed_gate_paths, project_registry
from devkit.gate.runner import GateRun, StageReport, Validation, run_stage, validate

__all__ = [
    "BaseGate",
    "DeployedGates",
    "Gate",
    "GateConfigError",
    "GateContext",
    "GateEntry",
    "GateError",
    "GateRegistry",
    "GateResult",
    "GateRun",
    "GatesConfig",
    "Outcome",
    "Stage",
    "StageReport",
    "Validation",
    "default_registry",
    "deployed_gate_paths",
    "load_gates_config",
    "project_registry",
    "resolve_settings",
    "run_stage",
    "validate",
]
