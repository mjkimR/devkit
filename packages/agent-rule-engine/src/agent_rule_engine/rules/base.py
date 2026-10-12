from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_rule_engine.engine.models import Phase, Rule, Severity


@dataclass
class BaseRule(Rule):
    id: str
    name: str
    description: str
    phase: Phase = Phase.LINTER
    severity: Severity = Severity.ERROR
    # Declared on a ``hygiene`` rule that is meant to become a ``linter`` rule once
    # the codebase is clean. The CLI reports remaining violations for such rules.
    promote_to: Phase | None = None

    def __post_init__(self) -> None:
        if self.promote_to is None:
            return
        if self.phase != Phase.HYGIENE or self.promote_to != Phase.LINTER:
            raise ValueError(
                f"{self.id}: promote_to is only valid as 'linter' on a 'hygiene' rule "
                f"(got phase={self.phase.value}, promote_to={self.promote_to.value})"
            )

    def normalize_rel_path(self, workspace_root: Path, path: str | Path) -> str:
        p = Path(path)
        if p.is_absolute():
            try:
                return p.relative_to(workspace_root).as_posix()
            except ValueError:
                return p.as_posix()
        return p.as_posix()
