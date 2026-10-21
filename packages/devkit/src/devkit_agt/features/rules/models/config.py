"""Project rule policy values."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from devkit_agt.features.rules.models.contracts import Phase, Severity
from devkit_agt.features.rules.models.settings import RawSettings


@dataclass(frozen=True)
class RulesConfig:
    """Validated ``[rules]`` section.

    ``phase_overrides`` maps a rule ID to the phase a project temporarily moves it
    to. Only ``hygiene`` is accepted: an override parks a linter rule while its
    existing violations are cleared, and is removed once ``check --phase hygiene``
    reports ``remaining=0`` for that rule.

    ``severity_overrides`` maps a rule ID to the severity its violations report
    in this project. ``settings`` holds each configured rule's values and path
    overrides; they are matched to the rule's declared settings at evaluation.

    ``exclude`` lists workspace-relative path patterns (``**`` grammar of the
    settings overrides) that no rule targets: they are dropped from explicit and
    snapshot targets and ``is_file_targeted`` is false for them. They stay in the
    document catalog so link repair can still point at them.
    """

    phase_overrides: dict[str, Phase] = field(default_factory=dict)
    severity_overrides: dict[str, Severity] = field(default_factory=dict)
    settings: dict[str, RawSettings] = field(default_factory=dict)
    exclude: tuple[str, ...] = ()
    source: Path | None = None
