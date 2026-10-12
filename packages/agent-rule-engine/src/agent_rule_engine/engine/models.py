from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from agent_rule_engine.engine.settings import RawSettings, SettingsResolver
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

    def __post_init__(self) -> None:
        self.workspace_root = self.workspace_root.resolve()
        if self.cache is None:
            self.cache = WorkspaceCache(self.workspace_root)
        elif self.cache.workspace_root != self.workspace_root:
            raise ValueError("Context and cache must use the same workspace root")
        normalized: list[str] = []
        for name in self.changed_files:
            path = Path(name)
            resolved = (path if path.is_absolute() else self.workspace_root / path).resolve()
            try:
                normalized.append(resolved.relative_to(self.workspace_root).as_posix())
            except ValueError as exc:
                raise ValueError(f"Target file is outside the workspace: {name}") from exc
        self.changed_files = normalized

    def is_file_targeted(self, path: str) -> bool:
        if not self.changed_files:
            return True
        candidate = Path(path)
        resolved = (candidate if candidate.is_absolute() else self.workspace_root / candidate).resolve()
        try:
            relative = resolved.relative_to(self.workspace_root).as_posix()
        except ValueError:
            return False
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
