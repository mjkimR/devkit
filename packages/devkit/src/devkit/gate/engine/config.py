"""Layered ``[gates]`` configuration.

Two files contribute, later layers overriding earlier ones:

1. ``.devkit/config.toml`` (Git-tracked, shared by the team). Only ``[gates]`` is
   read; other tables belong to ``devkit`` and the other engines.
2. ``<common-git-dir>/devkit.config`` (untracked, per clone, shared by every
   worktree). It uses the same TOML shape and currently accepts only ``[gates]``.

Layers are deep-merged table by table; a scalar or array in a later layer
replaces the earlier value as a whole. The merged table looks like::

    [gates.settings.message-nonempty]
    enabled = false

    [gates.settings.some-gate]
    enabled = true
    threshold = 3

``enabled`` is reserved in every gate table; the other keys are matched to the
gate's declared settings by ``resolve_settings``, which type-checks them with
the rule engine's settings checker (``int``, ``float``, ``str``, ``bool`` and
``list[str]``, ``null`` only for an ``| None`` field).

A file that cannot be read or parsed raises the core ``ConfigError``
(``CONFIG_INVALID``) unchanged; a malformed ``[gates]`` table or invalid
settings raise ``GateConfigError`` (``GATE_CONFIG_INVALID``).
"""

from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.core import CONFIG_PATH, config_table, read_project_config, read_toml
from devkit.gate.engine.models import Gate
from devkit.gate.errors import GateConfigError, GateDefinitionError
from devkit.rules.engine.settings import check_setting_value, describe_setting_type

LOCAL_CONFIG = "devkit.config"
GATES_TABLE = "gates"
SETTINGS_KEY = "settings"
ENABLED_KEY = "enabled"


@dataclass(frozen=True)
class GateEntry:
    enabled: bool | None = None  # ``None`` keeps the gate's ``enabled_by_default``
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GatesConfig:
    gates: dict[str, GateEntry] = field(default_factory=dict)
    sources: tuple[Path, ...] = ()  # files that contributed, lowest precedence first

    def enabled(self, gate: Gate) -> bool:
        entry = self.gates.get(gate.id)
        return gate.enabled_by_default if entry is None or entry.enabled is None else entry.enabled


def merge(base: dict[str, Any], top: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge ``top`` over ``base``: tables merge, everything else is replaced."""
    merged = dict(base)
    for key, value in top.items():
        current = merged.get(key)
        merged[key] = merge(current, value) if isinstance(current, dict) and isinstance(value, dict) else value
    return merged


def _table(value: object, context: str) -> dict[str, Any]:
    return config_table(value, context, GateConfigError)


def parse_gates(table: dict[str, Any], sources: tuple[Path, ...] = ()) -> GatesConfig:
    unknown = set(table) - {SETTINGS_KEY}
    if unknown:
        raise GateConfigError(f"config {GATES_TABLE}: unknown fields: {sorted(unknown)}")
    gates: dict[str, GateEntry] = {}
    settings = _table(table.get(SETTINGS_KEY, {}), f"{GATES_TABLE}.{SETTINGS_KEY}")
    for gate_id in sorted(settings):
        context = f"{GATES_TABLE}.{SETTINGS_KEY}.{gate_id}"
        values = dict(_table(settings[gate_id], context))
        enabled = values.pop(ENABLED_KEY, None)
        if enabled is not None and not isinstance(enabled, bool):
            raise GateConfigError(f"config {context}.{ENABLED_KEY}: expected true or false, got {enabled!r}")
        gates[gate_id] = GateEntry(enabled, values)
    return GatesConfig(gates, sources)


def load_gates_config(repo_root: Path, common_git_dir: Path) -> GatesConfig:
    """Merge ``[gates]`` from the project config and the clone-local ``<common-git-dir>/devkit.config``."""
    merged: dict[str, Any] = {}
    sources: list[Path] = []
    project_path = repo_root / CONFIG_PATH
    project = read_project_config(repo_root)
    if GATES_TABLE in project:
        merged = merge(merged, _table(project[GATES_TABLE], f"{project_path}: {GATES_TABLE}"))
        sources.append(project_path)
    local_path = common_git_dir / LOCAL_CONFIG
    local = read_toml(local_path)
    if local is not None:
        unknown = set(local) - {GATES_TABLE}
        if unknown:
            raise GateConfigError(f"config {local_path}: unknown fields: {sorted(unknown)}")
        if GATES_TABLE in local:
            merged = merge(merged, _table(local[GATES_TABLE], f"{local_path}: {GATES_TABLE}"))
            sources.append(local_path)
    return parse_gates(merged, tuple(sources))


def resolve_settings(gate: Gate, values: dict[str, Any]) -> Any:
    """Apply configured values over the gate's default settings dataclass.

    Each value is checked against its field's annotation with the rule
    engine's settings checker. A settings declaration it does not support is a
    defect of the gate (``GateDefinitionError``); an unknown key or a value of
    the wrong type is ``GateConfigError``.
    """
    defaults = gate.settings
    context = f"{GATES_TABLE}.{SETTINGS_KEY}.{gate.id}"
    if defaults is None:
        if values:
            raise GateConfigError(f"config {context}: gate has no settings, got {sorted(values)}")
        return None
    if not dataclasses.is_dataclass(defaults) or isinstance(defaults, type):
        raise GateDefinitionError(f"gate {gate.id!r}: settings must be a dataclass instance or None")
    try:
        hints = typing.get_type_hints(type(defaults))
        for item in dataclasses.fields(defaults):
            describe_setting_type(hints[item.name])
    except Exception as exc:
        raise GateDefinitionError(f"gate {gate.id!r}: invalid settings declaration: {exc}") from exc
    names = {f.name for f in dataclasses.fields(defaults)}
    unknown = set(values) - names
    if unknown:
        raise GateConfigError(f"config {context}: unknown settings {sorted(unknown)} (known: {sorted(names)})")
    resolved: dict[str, Any] = {}
    for key, value in values.items():
        try:
            resolved[key] = check_setting_value(hints[key], value)
        except ValueError as exc:
            raise GateConfigError(f"config {context}.{key}: {exc}") from None
    return dataclasses.replace(defaults, **resolved)
