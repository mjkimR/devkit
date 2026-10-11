from __future__ import annotations

from agent_rule_engine.cache import MarkdownLink, WorkspaceCache
from agent_rule_engine.evaluator import EvaluationResult, evaluate
from agent_rule_engine.index import Document, DocumentCatalog, is_valid_doc_id
from agent_rule_engine.models import (
    Autofixable,
    Phase,
    Rule,
    RuleContext,
    Severity,
    Violation,
)
from agent_rule_engine.registry import RuleRegistry, default_registry

__all__ = [
    "Autofixable",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
    "MarkdownLink",
    "Phase",
    "Rule",
    "RuleContext",
    "RuleRegistry",
    "Severity",
    "Violation",
    "WorkspaceCache",
    "default_registry",
    "evaluate",
    "is_valid_doc_id",
]
