from __future__ import annotations

from agent_rule_engine.engine.config import ConfigError, RulesConfig, load_rules_config
from agent_rule_engine.engine.discovery import ManagedRules, resolve_managed_rules
from agent_rule_engine.engine.evaluator import EvaluationResult, evaluate
from agent_rule_engine.engine.models import (
    Autofixable,
    Phase,
    Rule,
    RuleContext,
    Severity,
    Violation,
)
from agent_rule_engine.engine.phases import PhaseEntry, resolve_phases
from agent_rule_engine.engine.registry import RuleRegistry, default_registry
from agent_rule_engine.engine.settings import RawSettings, SettingsError, SettingsResolver, match_path
from agent_rule_engine.workspace.cache import MarkdownLink, WorkspaceCache
from agent_rule_engine.workspace.catalog import Document, DocumentCatalog
from agent_rule_engine.workspace.markdown import count_tasks
from agent_rule_engine.workspace.snapshot import Snapshot, SnapshotError, git_snapshot, materialize

__all__ = [
    "Autofixable",
    "ConfigError",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
    "ManagedRules",
    "MarkdownLink",
    "Phase",
    "PhaseEntry",
    "RawSettings",
    "Rule",
    "RuleContext",
    "RuleRegistry",
    "RulesConfig",
    "SettingsError",
    "SettingsResolver",
    "Severity",
    "Snapshot",
    "SnapshotError",
    "Violation",
    "WorkspaceCache",
    "count_tasks",
    "default_registry",
    "evaluate",
    "git_snapshot",
    "load_rules_config",
    "match_path",
    "materialize",
    "resolve_managed_rules",
    "resolve_phases",
]
