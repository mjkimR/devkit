from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from agent_rule_engine.cache import WorkspaceCache


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
    options: dict[str, Any] = field(default_factory=dict)

    def is_file_targeted(self, path: str) -> bool:
        if not self.changed_files:
            return True
        norm = Path(path).as_posix()
        return any(norm == Path(cf).as_posix() or norm.endswith(Path(cf).as_posix()) for cf in self.changed_files)


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
