"""Project-level rule engine configuration read from ``.devkit/config.toml``.

Only the ``[rules]`` table is interpreted here; other tables belong to
``devkit-distribution`` and are ignored. A missing file yields an empty config.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from agent_rule_engine.engine.models import Phase

CONFIG_PATH = ".devkit/config.toml"
RULES_TABLE = "rules"
PHASE_OVERRIDES_KEY = "phase_overrides"


class ConfigError(ValueError):
    """Raised when the ``[rules]`` configuration is malformed."""


@dataclass(frozen=True)
class RulesConfig:
    """Validated ``[rules]`` section.

    ``phase_overrides`` maps a rule ID to the phase a project temporarily moves it
    to. Only ``hygiene`` is accepted: an override parks a linter rule while its
    existing violations are cleared, and is removed once ``check --phase hygiene``
    reports ``remaining=0`` for that rule.
    """

    phase_overrides: dict[str, Phase] = field(default_factory=dict)
    source: Path | None = None


def parse_rules_config(data: object, source: Path | None = None) -> RulesConfig:
    """Validate the ``[rules]`` table from an already parsed TOML document."""
    if not isinstance(data, dict):
        raise ConfigError("config: expected a table")
    rules = data.get(RULES_TABLE)
    if rules is None:
        return RulesConfig(source=source)
    if not isinstance(rules, dict):
        raise ConfigError(f"config {RULES_TABLE}: expected a table")
    unknown = set(rules) - {PHASE_OVERRIDES_KEY}
    if unknown:
        raise ConfigError(f"config {RULES_TABLE}: unknown fields: {sorted(unknown)}")

    overrides: dict[str, Phase] = {}
    raw = rules.get(PHASE_OVERRIDES_KEY)
    if raw is not None:
        if not isinstance(raw, dict):
            raise ConfigError(f"config {RULES_TABLE}.{PHASE_OVERRIDES_KEY}: expected a table of rule ID to phase")
        for rule_id in sorted(raw):
            value = raw[rule_id]
            if not isinstance(value, str) or value.lower() != Phase.HYGIENE.value:
                raise ConfigError(
                    f"config {RULES_TABLE}.{PHASE_OVERRIDES_KEY}.{rule_id}: {value!r} is not 'hygiene'; "
                    "set it to 'hygiene' or remove the entry to keep the rule's default phase"
                )
            overrides[rule_id] = Phase.HYGIENE
    return RulesConfig(phase_overrides=overrides, source=source)


def load_rules_config(workspace_root: Path) -> RulesConfig:
    """Read ``.devkit/config.toml`` under ``workspace_root``; missing file means defaults."""
    path = workspace_root / CONFIG_PATH
    if not path.is_file():
        return RulesConfig()
    try:
        data = tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid config {CONFIG_PATH}: {exc}") from exc
    return parse_rules_config(data, source=path)
