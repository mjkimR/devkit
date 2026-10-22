from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from devkit_agt.features.rules.models.errors import TargetError
from devkit_agt.features.rules.models.settings import RawSettings, SettingsResolver, match_path
from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache

if TYPE_CHECKING:
    from devkit_agt.features.rules.models.snapshot import Snapshot


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


@dataclass(init=False)
class RuleContext:
    """What a rule sees during one evaluation: the workspace, the targets, the cache and the project policy.

    Every argument is keyword-friendly and optional except ``workspace_root``.
    ``cache`` defaults to a fresh ``WorkspaceCache`` of the workspace, so
    ``ctx.cache`` is always a ``WorkspaceCache``.
    """

    workspace_root: Path
    changed_files: list[str]
    rules_dir: Path | None
    phase: Phase
    fix: bool
    dry_run: bool
    cache: WorkspaceCache
    # Project policy moving rules out of their declared phase (``[rules.phase_overrides]``).
    phase_overrides: dict[str, Phase]
    # Project policy changing the severity a rule reports (``[rules.severity_overrides]``).
    severity_overrides: dict[str, Severity]
    # Project values for rule settings (``[rules.settings.<id>]``), matched to rules by the evaluator.
    rule_settings: dict[str, RawSettings]
    # Resolved settings per rule; populated by ``evaluate_rules`` before any check runs.
    settings_resolvers: dict[str, SettingsResolver]
    # Project exclusions (``[rules] exclude``): workspace-relative ``**`` patterns no rule targets.
    exclude: tuple[str, ...]
    # Whether the run named explicit targets (before exclusions were applied).
    has_targets: bool
    # The explicit targets, workspace-relative, before ``exclude`` removed any: what the evaluator matches a rule's
    # ``inputs`` against.
    targets: tuple[str, ...]
    # The Git snapshot a ``check --staged`` or ``--ci`` run evaluates (``mode``, ``base``, ``changed``, ``deleted``);
    # ``None`` for a working-tree run. Rules about diff evidence read it.
    snapshot: Snapshot | None

    def __init__(
        self,
        workspace_root: Path,
        changed_files: list[str] | None = None,
        rules_dir: Path | None = None,
        phase: Phase = Phase.LINTER,
        fix: bool = False,
        dry_run: bool = False,
        cache: WorkspaceCache | None = None,
        phase_overrides: dict[str, Phase] | None = None,
        severity_overrides: dict[str, Severity] | None = None,
        rule_settings: dict[str, RawSettings] | None = None,
        settings_resolvers: dict[str, SettingsResolver] | None = None,
        exclude: tuple[str, ...] = (),
        snapshot: Snapshot | None = None,
    ) -> None:
        self.workspace_root = workspace_root.resolve()
        self.snapshot = snapshot
        if cache is None:
            cache = WorkspaceCache(self.workspace_root)
        elif cache.workspace_root != self.workspace_root:
            raise ValueError("Context and cache must use the same workspace root")
        self.cache = cache
        self.rules_dir = rules_dir
        self.phase = phase
        self.fix = fix
        self.dry_run = dry_run
        self.phase_overrides = phase_overrides if phase_overrides is not None else {}
        self.severity_overrides = severity_overrides if severity_overrides is not None else {}
        self.rule_settings = rule_settings if rule_settings is not None else {}
        self.settings_resolvers = settings_resolvers if settings_resolvers is not None else {}
        self.exclude = tuple(exclude)
        targets = changed_files or []
        self.has_targets = bool(targets) or snapshot is not None
        named: list[str] = []
        normalized: list[str] = []
        for name in targets:
            relative = self._relative(name)
            if relative is None:
                raise TargetError(f"Target file is outside the workspace: {name}", target_files=[str(name)])
            named.append(relative)
            if not self._excluded(relative):
                normalized.append(relative)
        self.targets = tuple(named)
        self.changed_files = normalized
        if snapshot is None:
            # Targets named on the command line are listed by ``find_files`` even where discovery skips files
            # (Git-ignored, dependency and cache directories); a snapshot's changed files are not such
            # exceptions, so a scan of the snapshot lists what a whole-workspace scan would.
            self.cache.add_explicit(normalized)

    def _relative(self, path: str | Path) -> str | None:
        """Workspace-relative POSIX form of ``path``, or ``None`` when it lies outside the workspace.

        The path is normalized lexically, so a symlink inside the workspace keeps
        its own name (as ``WorkspaceCache.find_files`` lists it). Only a path
        that is outside lexically is retried after resolving symlinks, for roots
        reached through a symlinked prefix.
        """
        candidate = Path(path)
        absolute = candidate if candidate.is_absolute() else self.workspace_root / candidate
        option = Path(os.path.normpath(absolute))
        if not option.is_relative_to(self.workspace_root):
            # Resolve only when the lexical form is outside: a path inside never touches the file system.
            option = absolute.resolve()
            if not option.is_relative_to(self.workspace_root):
                return None
        relative = option.relative_to(self.workspace_root).as_posix()
        return relative if relative != "." else None

    def relative_path(self, path: str | Path) -> str | None:
        """Workspace-relative POSIX form of ``path`` (relative to the workspace or absolute), or ``None`` outside it."""
        return self._relative(path)

    def _excluded(self, relative: str) -> bool:
        return any(match_path(p, relative) for p in self.exclude)

    def is_file_targeted(self, path: str) -> bool:
        relative = self._relative(path)
        if relative is None or self._excluded(relative):
            return False
        if not self.has_targets:
            return True
        return relative in self.changed_files

    def settings(self, rule: Rule, path: str | Path | None = None) -> Any:
        """Effective settings of ``rule`` for a workspace-relative ``path``.

        Without a resolver (library callers that skip ``evaluate_rules``) the rule's
        declared defaults are returned.
        """
        resolver = self.settings_resolvers.get(rule.id)
        if resolver is None:
            return getattr(rule, "settings", None)
        if path is None:
            return resolver.resolve()
        relative = self._relative(path)
        if relative is None:
            raise TargetError(f"{path} is outside the workspace {self.workspace_root}", target_files=[str(path)])
        return resolver.for_file(relative)


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
