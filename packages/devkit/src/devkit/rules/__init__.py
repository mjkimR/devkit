from __future__ import annotations

from devkit.rules.engine.config import ConfigError, RulesConfig, load_rules_config
from devkit.rules.engine.discovery import ManagedRules, resolve_managed_rules
from devkit.rules.engine.errors import PolicyError
from devkit.rules.engine.evaluator import EvaluationResult, evaluate
from devkit.rules.engine.models import (
    Autofixable,
    Phase,
    Rule,
    RuleContext,
    Severity,
    Violation,
)
from devkit.rules.engine.phases import PhaseEntry, resolve_phases
from devkit.rules.engine.policy import validate_policy
from devkit.rules.engine.project import (
    ProjectRun,
    RulesDirError,
    TargetError,
    build_project_registry,
    expand_targets,
    run_project_rules,
)
from devkit.rules.engine.registry import RuleRegistry, default_registry
from devkit.rules.engine.settings import RawSettings, SettingsError, SettingsResolver, match_path
from devkit.rules.workspace.cache import WorkspaceCache
from devkit.rules.workspace.catalog import Document, DocumentCatalog
from devkit.rules.workspace.markdown import MarkdownLink, count_tasks, extract_links
from devkit.rules.workspace.snapshot import Snapshot, SnapshotError, git_snapshot, materialize

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
    "PolicyError",
    "ProjectRun",
    "RawSettings",
    "Rule",
    "RuleContext",
    "RuleRegistry",
    "RulesConfig",
    "RulesDirError",
    "SettingsError",
    "SettingsResolver",
    "Severity",
    "Snapshot",
    "SnapshotError",
    "TargetError",
    "Violation",
    "WorkspaceCache",
    "build_project_registry",
    "count_tasks",
    "default_registry",
    "evaluate",
    "expand_targets",
    "extract_links",
    "git_snapshot",
    "load_rules_config",
    "match_path",
    "materialize",
    "resolve_managed_rules",
    "resolve_phases",
    "run_project_rules",
    "validate_policy",
]
