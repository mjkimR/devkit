from __future__ import annotations

from devkit_agt.features.rules.models.contracts import (
    Autofixable,
    Phase,
    Rule,
    RuleContext,
    Severity,
    Violation,
)
from devkit_agt.features.rules.models.errors import (
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
from devkit_agt.features.rules.models.file_facts import FactsDependency, FileFactsDescriptor, FileFactsSource, JsonValue
from devkit_agt.features.rules.models.markdown import (
    ChecklistItem,
    LineKind,
    MarkdownLink,
    ScannedLine,
    count_tasks,
    extract_links,
    parse_checklist_item,
    scan,
)
from devkit_agt.features.rules.models.phases import PhaseEntry, resolve_phases
from devkit_agt.features.rules.models.policy import validate_policy
from devkit_agt.features.rules.models.settings import RawSettings, SettingsResolver, match_path, validate_pattern
from devkit_agt.features.rules.models.snapshot import Snapshot
from devkit_agt.features.rules.repositories.config import RulesConfig, load_rules_config
from devkit_agt.features.rules.repositories.discovery import ManagedRules, resolve_managed_rules
from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache
from devkit_agt.features.rules.repositories.workspace.catalog import Document, DocumentCatalog
from devkit_agt.features.rules.repositories.workspace.facts import capture_facts_dependency
from devkit_agt.features.rules.repositories.workspace.relocation import (
    LinkRelocation,
    LinkRelocationReport,
    RelocatedLink,
    UnresolvedLink,
    UnresolvedReason,
    relocate_links,
)
from devkit_agt.features.rules.repositories.workspace.snapshot import git_snapshot, materialize_snapshot
from devkit_agt.features.rules.services.evaluator import EvaluationResult, evaluate_rules
from devkit_agt.features.rules.services.registry import RuleRegistry, default_rule_registry
from devkit_agt.features.rules.usecases.project import (
    ProjectRules,
    ProjectRun,
    build_project_registry,
    expand_targets,
    load_project_rules,
    run_project_rules,
)
from devkit_agt.features.rules.usecases.related import RelatedAsset, ResolveRelatedUseCase

__all__ = [
    "Autofixable",
    "ChecklistItem",
    "Document",
    "DocumentCatalog",
    "EvaluationResult",
    "FactsDependency",
    "FileFactsDescriptor",
    "FileFactsSource",
    "JsonValue",
    "LineKind",
    "LinkRelocation",
    "LinkRelocationReport",
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
    "RelocatedLink",
    "ResolveRelatedUseCase",
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
    "ScannedLine",
    "SettingsError",
    "SettingsResolver",
    "Severity",
    "Snapshot",
    "SnapshotError",
    "TargetError",
    "UnresolvedLink",
    "UnresolvedReason",
    "Violation",
    "WorkspaceCache",
    "build_project_registry",
    "capture_facts_dependency",
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
    "parse_checklist_item",
    "relocate_links",
    "resolve_managed_rules",
    "resolve_phases",
    "run_project_rules",
    "scan",
    "validate_pattern",
    "validate_policy",
]
