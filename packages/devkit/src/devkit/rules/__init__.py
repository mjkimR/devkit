from __future__ import annotations

from devkit.rules.engine.config import RulesConfig, load_rules_config
from devkit.rules.engine.discovery import ManagedRules, resolve_managed_rules
from devkit.rules.engine.errors import (
    PinnedWriteError,
    PolicyError,
    RelatedUnresolvedNotice,
    RuleDefinitionError,
    RuleExecutionError,
    RuleLoadError,
    RuleProblem,
    RulesConfigError,
    RulesDirError,
    RulesError,
    RulesRunError,
    RulesTestUnavailableError,
    SettingsError,
    SnapshotError,
    TargetError,
)
from devkit.rules.engine.evaluator import EvaluationResult, evaluate_rules
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
    ProjectRules,
    ProjectRun,
    build_project_registry,
    expand_targets,
    load_project_rules,
    run_project_rules,
)
from devkit.rules.engine.registry import RuleRegistry, default_rule_registry
from devkit.rules.engine.related import RelatedAsset, resolve_related
from devkit.rules.engine.settings import RawSettings, SettingsResolver, match_path, validate_pattern
from devkit.rules.workspace.cache import WorkspaceCache
from devkit.rules.workspace.catalog import Document, DocumentCatalog
from devkit.rules.workspace.markdown import MarkdownLink, count_tasks, extract_links
from devkit.rules.workspace.snapshot import Snapshot, git_snapshot, materialize_snapshot

__all__ = [
    "Autofixable",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
    "ManagedRules",
    "MarkdownLink",
    "Phase",
    "PhaseEntry",
    "PinnedWriteError",
    "PolicyError",
    "ProjectRules",
    "ProjectRun",
    "RawSettings",
    "RelatedAsset",
    "RelatedUnresolvedNotice",
    "Rule",
    "RuleContext",
    "RuleDefinitionError",
    "RuleExecutionError",
    "RuleLoadError",
    "RuleProblem",
    "RuleRegistry",
    "RulesConfig",
    "RulesConfigError",
    "RulesDirError",
    "RulesError",
    "RulesRunError",
    "RulesTestUnavailableError",
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
    "default_rule_registry",
    "evaluate_rules",
    "expand_targets",
    "extract_links",
    "git_snapshot",
    "load_project_rules",
    "load_rules_config",
    "match_path",
    "materialize_snapshot",
    "resolve_managed_rules",
    "resolve_phases",
    "resolve_related",
    "run_project_rules",
    "validate_pattern",
    "validate_policy",
]
