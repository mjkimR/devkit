from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_rule_engine.models import Phase, Rule, Severity


@dataclass
class BaseRule(Rule):
    id: str
    name: str
    description: str
    phase: Phase = Phase.LINTER
    severity: Severity = Severity.ERROR

    def normalize_rel_path(self, workspace_root: Path, path: str | Path) -> str:
        p = Path(path)
        if p.is_absolute():
            try:
                return p.relative_to(workspace_root).as_posix()
            except ValueError:
                return p.as_posix()
        return p.as_posix()
