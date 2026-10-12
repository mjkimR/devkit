"""Pluggable Git commit gates for devkit workspaces."""

from agent_commit_gate.base import BaseGate
from agent_commit_gate.config import GateEntry, GatesConfig, load_gates_config, resolve_settings
from agent_commit_gate.models import (
    Gate,
    GateConfigError,
    GateContext,
    GateError,
    GateResult,
    Outcome,
    Stage,
)
from agent_commit_gate.registry import GateRegistry, default_registry, deployed_gate_paths, project_registry
from agent_commit_gate.runner import GateRun, StageReport, run_stage

__all__ = [
    "BaseGate",
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
    "default_registry",
    "deployed_gate_paths",
    "load_gates_config",
    "project_registry",
    "resolve_settings",
    "run_stage",
]
