from __future__ import annotations

from agent_rule_engine.engine.config import ConfigError, RulesConfig, load_rules_config
from agent_rule_engine.engine.discovery import managed_rule_paths
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
from agent_rule_engine.workspace.catalog import Document, DocumentCatalog, is_valid_doc_id
from agent_rule_engine.workspace.snapshot import Snapshot, SnapshotError, git_snapshot, materialize

__all__ = [
    "Autofixable",
    "ConfigError",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
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
    "default_registry",
    "evaluate",
    "git_snapshot",
    "is_valid_doc_id",
    "load_rules_config",
    "managed_rule_paths",
    "match_path",
    "materialize",
    "resolve_phases",
]
