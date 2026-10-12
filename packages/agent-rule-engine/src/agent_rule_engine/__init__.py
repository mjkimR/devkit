from __future__ import annotations

from agent_rule_engine.engine.config import ConfigError, RulesConfig, load_rules_config
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
from agent_rule_engine.workspace.cache import MarkdownLink, WorkspaceCache
from agent_rule_engine.workspace.catalog import Document, DocumentCatalog, is_valid_doc_id

__all__ = [
    "Autofixable",
    "ConfigError",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
    "MarkdownLink",
    "Phase",
    "PhaseEntry",
    "Rule",
    "RuleContext",
    "RuleRegistry",
    "RulesConfig",
    "Severity",
    "Violation",
    "WorkspaceCache",
    "default_registry",
    "evaluate",
    "is_valid_doc_id",
    "load_rules_config",
    "resolve_phases",
]
