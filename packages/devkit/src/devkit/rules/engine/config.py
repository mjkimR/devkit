"""Project-level rule engine configuration read from ``.devkit/config.toml``.

Only the ``[rules]`` table is interpreted here; other tables belong to
``devkit`` and ``devkit.workflow`` and are ignored. A missing
file yields an empty config. Entries that need the loaded rules to validate
(unknown rule IDs, settings keys) are checked by the evaluator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.core.project import config_table, read_project_config
from devkit.core.receipt import CONFIG_PATH
from devkit.rules.engine.errors import RulesConfigError
from devkit.rules.engine.models import Phase, Severity
from devkit.rules.engine.settings import Override, RawSettings, validate_pattern

__all__ = ["RulesConfig", "load_rules_config", "parse_rules_config"]

RULES_TABLE = "rules"
PHASE_OVERRIDES_KEY = "phase_overrides"
SEVERITY_OVERRIDES_KEY = "severity_overrides"
SETTINGS_KEY = "settings"
EXCLUDE_KEY = "exclude"
OVERRIDES_KEY = "overrides"
PATH_KEY = "path"
KNOWN_KEYS = {PHASE_OVERRIDES_KEY, SEVERITY_OVERRIDES_KEY, SETTINGS_KEY, EXCLUDE_KEY}


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


def _table(value: object, context: str) -> dict[str, Any]:
    return config_table(value, context, RulesConfigError)


def _phase_overrides(raw: object) -> dict[str, Phase]:
    if not isinstance(raw, dict):
        raise RulesConfigError(f"config {RULES_TABLE}.{PHASE_OVERRIDES_KEY}: expected a table of rule ID to phase")
    overrides: dict[str, Phase] = {}
    for rule_id in sorted(raw):
        value = raw[rule_id]
        if not isinstance(value, str) or value.lower() != Phase.HYGIENE.value:
            raise RulesConfigError(
                f"config {RULES_TABLE}.{PHASE_OVERRIDES_KEY}.{rule_id}: {value!r} is not 'hygiene'; "
                "set it to 'hygiene' or remove the entry to keep the rule's default phase"
            )
        overrides[rule_id] = Phase.HYGIENE
    return overrides


def _severity_overrides(raw: object) -> dict[str, Severity]:
    overrides: dict[str, Severity] = {}
    table = _table(raw, f"{RULES_TABLE}.{SEVERITY_OVERRIDES_KEY}")
    allowed = [s.value for s in Severity]
    for rule_id in sorted(table):
        value = table[rule_id]
        if not isinstance(value, str) or value.lower() not in allowed:
            raise RulesConfigError(
                f"config {RULES_TABLE}.{SEVERITY_OVERRIDES_KEY}.{rule_id}: {value!r} is not one of {allowed}"
            )
        overrides[rule_id] = Severity(value.lower())
    return overrides


def _settings(raw: object) -> dict[str, RawSettings]:
    result: dict[str, RawSettings] = {}
    table = _table(raw, f"{RULES_TABLE}.{SETTINGS_KEY}")
    for rule_id in sorted(table):
        context = f"{RULES_TABLE}.{SETTINGS_KEY}.{rule_id}"
        entry = dict(_table(table[rule_id], context))
        overrides: list[Override] = []
        raw_overrides = entry.pop(OVERRIDES_KEY, [])
        if not isinstance(raw_overrides, list):
            raise RulesConfigError(f"config {context}.{OVERRIDES_KEY}: expected an array of tables")
        for index, item in enumerate(raw_overrides):
            values = dict(_table(item, f"{context}.{OVERRIDES_KEY}[{index}]"))
            pattern = values.pop(PATH_KEY, None)
            try:
                validate_pattern(pattern)  # type: ignore[arg-type]
            except ValueError as exc:
                raise RulesConfigError(f"config {context}.{OVERRIDES_KEY}[{index}].{PATH_KEY}: {exc}") from None
            if not values:
                raise RulesConfigError(f"config {context}.{OVERRIDES_KEY}[{index}]: no settings besides path")
            overrides.append(Override(str(pattern), values))
        result[rule_id] = RawSettings(entry, tuple(overrides))
    return result


def _exclude(raw: object) -> tuple[str, ...]:
    context = f"{RULES_TABLE}.{EXCLUDE_KEY}"
    if not isinstance(raw, list):
        raise RulesConfigError(f"config {context}: expected an array of path patterns")
    patterns: list[str] = []
    for index, pattern in enumerate(raw):
        try:
            validate_pattern(pattern)  # type: ignore[arg-type]
        except ValueError as exc:
            raise RulesConfigError(f"config {context}[{index}]: {exc}") from None
        if pattern in patterns:
            raise RulesConfigError(f"config {context}[{index}]: duplicate pattern {pattern!r}")
        patterns.append(pattern)
    return tuple(patterns)


def parse_rules_config(data: object, source: Path | None = None) -> RulesConfig:
    """Validate the ``[rules]`` table from an already parsed TOML document."""
    if not isinstance(data, dict):
        raise RulesConfigError("config: expected a table")
    rules = data.get(RULES_TABLE)
    if rules is None:
        return RulesConfig(source=source)
    rules = _table(rules, RULES_TABLE)
    unknown = set(rules) - KNOWN_KEYS
    if unknown:
        raise RulesConfigError(f"config {RULES_TABLE}: unknown fields: {sorted(unknown)}")
    return RulesConfig(
        phase_overrides=_phase_overrides(rules[PHASE_OVERRIDES_KEY]) if PHASE_OVERRIDES_KEY in rules else {},
        severity_overrides=_severity_overrides(rules[SEVERITY_OVERRIDES_KEY])
        if SEVERITY_OVERRIDES_KEY in rules
        else {},
        settings=_settings(rules[SETTINGS_KEY]) if SETTINGS_KEY in rules else {},
        exclude=_exclude(rules[EXCLUDE_KEY]) if EXCLUDE_KEY in rules else (),
        source=source,
    )


def load_rules_config(workspace_root: Path) -> RulesConfig:
    """Read ``.devkit/config.toml`` under ``workspace_root``; missing file means defaults.

    An unreadable file raises the core ``ConfigError`` (``CONFIG_INVALID``)
    unchanged; a malformed ``[rules]`` table raises ``RulesConfigError``
    (``RULES_CONFIG_INVALID``).
    """
    data = read_project_config(workspace_root)
    path = workspace_root / CONFIG_PATH
    return parse_rules_config(data, source=path if path.is_file() else None)
