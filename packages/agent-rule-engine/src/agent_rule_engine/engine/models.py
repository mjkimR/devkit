from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from agent_rule_engine.engine.settings import RawSettings, SettingsResolver, match_path
from agent_rule_engine.workspace.cache import WorkspaceCache


class Phase(StrEnum):
    LINTER = "linter"
    HYGIENE = "hygiene"


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(slots=True)
class Violation:
    rule_id: str
    file: str
    line: int
    message: str
    column: int = 0
    remediation: str = ""
    fixable: bool = False
    fixed: bool = False
    severity: Severity = Severity.ERROR
    phase: Phase = Phase.LINTER

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "remediation": self.remediation,
            "fixable": self.fixable,
            "fixed": self.fixed,
            "severity": self.severity.value,
            "phase": self.phase.value,
        }


@dataclass
class RuleContext:
    workspace_root: Path
    changed_files: list[str] = field(default_factory=list)
    workflow_files: list[str] = field(default_factory=list)
    rules_dir: Path | None = None
    phase: Phase = Phase.LINTER
    fix: bool = False
    dry_run: bool = False
    cache: WorkspaceCache = field(default=None)  # type: ignore[assignment]
    # Project policy moving rules out of their declared phase (``[rules.phase_overrides]``).
    phase_overrides: dict[str, Phase] = field(default_factory=dict)
    # Project policy changing the severity a rule reports (``[rules.severity_overrides]``).
    severity_overrides: dict[str, Severity] = field(default_factory=dict)
    # Project values for rule settings (``[rules.settings.<id>]``), matched to rules by the evaluator.
    rule_settings: dict[str, RawSettings] = field(default_factory=dict)
    # Resolved settings per rule; populated by ``evaluate`` before any check runs.
    settings_resolvers: dict[str, SettingsResolver] = field(default_factory=dict)
    # Project exclusions (``[rules] exclude``): workspace-relative ``**`` patterns no rule targets.
    exclude: tuple[str, ...] = ()
    # Whether the run named explicit targets (before exclusions were applied).
    has_targets: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.workspace_root = self.workspace_root.resolve()
        if self.cache is None:
            self.cache = WorkspaceCache(self.workspace_root)
        elif self.cache.workspace_root != self.workspace_root:
            raise ValueError("Context and cache must use the same workspace root")
        self.has_targets = bool(self.changed_files)
        normalized: list[str] = []
        for name in self.changed_files:
            relative = self._relative(name)
            if relative is None:
                raise ValueError(f"Target file is outside the workspace: {name}")
            if not self.is_excluded(relative):
                normalized.append(relative)
        self.changed_files = normalized

    def _relative(self, path: str | Path) -> str | None:
        candidate = Path(path)
        resolved = (candidate if candidate.is_absolute() else self.workspace_root / candidate).resolve()
        try:
            return resolved.relative_to(self.workspace_root).as_posix()
        except ValueError:
            return None

    def is_excluded(self, path: str | Path) -> bool:
        """Whether a workspace-relative (or absolute, inside the workspace) path is excluded by policy."""
        if not self.exclude:
            return False
        relative = self._relative(path)
        return relative is not None and any(match_path(p, relative) for p in self.exclude)

    def is_file_targeted(self, path: str) -> bool:
        relative = self._relative(path)
        if relative is None or self.is_excluded(relative):
            return False
        if not self.has_targets:
            return True
        return relative in self.changed_files

    def settings(self, rule: Rule, path: str | Path | None = None) -> Any:
        """Effective settings of ``rule`` for a workspace-relative ``path``.

        Without a resolver (library callers that skip ``evaluate``) the rule's
        declared defaults are returned.
        """
        resolver = self.settings_resolvers.get(rule.id)
        if resolver is None:
            return getattr(rule, "settings", None)
        if path is None:
            return resolver.resolve()
        rel = Path(path)
        if rel.is_absolute():
            rel = rel.resolve().relative_to(self.workspace_root)
        return resolver.for_file(rel.as_posix())


@runtime_checkable
class Rule(Protocol):
    id: str
    name: str
    description: str
    phase: Phase
    severity: Severity

    def check(self, ctx: RuleContext) -> list[Violation]: ...


@runtime_checkable
class Autofixable(Rule, Protocol):
    def fix(self, ctx: RuleContext) -> list[str]:
        """Apply safe deterministic fixes and return list of modified file paths."""
        ...
