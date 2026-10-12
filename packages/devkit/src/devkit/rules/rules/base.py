from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.rules.engine.models import Phase, Rule, Severity


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
    # Default settings as a dataclass instance; ``[rules.settings.<id>]`` may change
    # its fields per project and per path. ``None`` means the rule has no settings.
    settings: Any = None
    # Markdown guide for this rule, relative to the module defining the rule class.
    guide: str | None = None

    def __post_init__(self) -> None:
        if self.promote_to is None:
            return
        if self.phase != Phase.HYGIENE or self.promote_to != Phase.LINTER:
            raise ValueError(
                f"{self.id}: promote_to is only valid as 'linter' on a 'hygiene' rule "
                f"(got phase={self.phase.value}, promote_to={self.promote_to.value})"
            )

    def validate_settings(self, settings: Any) -> None:
        """Reject settings values the field types alone cannot express; raise ``ValueError``."""


def guide_path(rule: Rule) -> Path | None:
    """Absolute path of the rule's guide document, if it declares one and the file exists."""
    name = getattr(rule, "guide", None)
    if not isinstance(name, str) or not name:
        return None
    try:
        module_file = Path(inspect.getfile(type(rule)))
    except (TypeError, OSError):
        return None
    path = (module_file.parent / name).resolve()
    return path if path.is_file() else None
