"""Query rule policy, source guides and resolved display metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.rules.models.config import RulesConfig
from devkit_agt.features.rules.models.contracts import Rule
from devkit_agt.features.rules.models.phases import declared_promotion, effective_phase
from devkit_agt.features.rules.models.policy import effective_severity
from devkit_agt.features.rules.models.settings import SettingsResolver
from devkit_agt.features.rules.services.builtins.base import guide_path


class ResolveRuleGuideUseCase(BaseUseCase):
    """Query guide display."""

    def execute(self, rule: Rule | None, workspace_root: Path) -> str | None:
        return _display_path(guide_path(rule) if rule is not None else None, workspace_root)


def _display_path(path: Path | None, workspace_root: Path) -> str | None:
    """``path`` relative to the workspace when it lies inside it, else absolute."""
    if path is None:
        return None
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return str(path)


class ExplainRuleUseCase(BaseUseCase):
    """Query explain entry."""

    def execute(
        self, rule: Rule, config: RulesConfig, resolver: SettingsResolver | None, workspace_root: Path
    ) -> dict[str, Any]:
        promote_to = declared_promotion(rule)
        inputs = getattr(rule, "inputs", None)
        return {
            "rule_id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "default_phase": rule.phase.value,
            "effective_phase": effective_phase(rule, config.phase_overrides).value,
            "default_severity": rule.severity.value,
            "effective_severity": effective_severity(rule, config.severity_overrides).value,
            "promote_to": promote_to.value if promote_to else None,
            "settings": resolver.to_dict() if resolver else None,
            "guide": ResolveRuleGuideUseCase().execute(rule, workspace_root),
            "inputs": list(inputs) if inputs is not None else None,
        }


class ReadRuleGuideUseCase(BaseUseCase):
    """Query read guide."""

    def execute(self, rule: Rule) -> str | None:
        """Read the effective guide beside a rule, including its managed fallback."""
        path = guide_path(rule)
        return path.read_text("utf-8") if path is not None else None
