"""Offline validation and pure resolution of neutral subagent levels."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from devkit_dist.base.errors import ConfigError
from devkit_dist.features.distribution.models.errors import PackageError
from devkit_dist.features.distribution.models.settings import AGENT_NAMES
from devkit_dist.features.distribution.models.subagents import LEVELS, ModelSettings, SubagentPolicy

if TYPE_CHECKING:
    from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle

# Empty Antigravity settings inherit the entire unavailable native combination.
DEFAULTS = {
    "minimal": {
        "claude-code": ModelSettings("haiku", "low"),
        "codex": ModelSettings("gpt-6-luna", "low"),
        "antigravity": ModelSettings(),
    },
    "compact": {
        "claude-code": ModelSettings("haiku"),
        "codex": ModelSettings("gpt-6-luna"),
        "antigravity": ModelSettings("flash"),
    },
    "lean": {
        "claude-code": ModelSettings("sonnet", "medium"),
        "codex": ModelSettings("gpt-6.1-terra", "medium"),
        "antigravity": ModelSettings("flash"),
    },
    "standard": {
        "claude-code": ModelSettings("sonnet"),
        "codex": ModelSettings("gpt-6.1-sol"),
        "antigravity": ModelSettings(),
    },
    "deep": {
        "claude-code": ModelSettings("opus"),
        "codex": ModelSettings("gpt-6-astra"),
        "antigravity": ModelSettings(),
    },
    "maximal": {
        "claude-code": ModelSettings("opus", "high"),
        "codex": ModelSettings("gpt-6-astra", "high"),
        "antigravity": ModelSettings(),
    },
}
EFFORTS = {
    "claude-code": {"low", "medium", "high", "xhigh", "max", "inherit"},
    "codex": {"none", "low", "medium", "high", "xhigh", "max", "inherit"},
    "antigravity": {"inherit"},
}
IDENTITY = re.compile(r"[a-z][a-z0-9-]*:[a-z][a-z0-9-]*\Z")


def _invalid(context: str, message: str) -> ConfigError:
    return ConfigError(
        f"{context}: {message}",
        fix=f"Correct {context} in .devkit/config.toml using the documented subagent levels and host mappings",
    )


def _table(value: object, context: str, keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _invalid(context, "expected a table")
    if unknown := set(value) - set(keys):
        raise _invalid(context, f"unknown keys {sorted(unknown)}")
    return value


def _level(value: object, context: str) -> str:
    if not isinstance(value, str) or value not in LEVELS:
        raise _invalid(context, f"expected one of {list(LEVELS)}")
    return value


def _mapping(level: str, host: str, value: object) -> ModelSettings:
    context = f"subagents.levels.{level}.{host}"
    fields = _table(value, context, ("model", "effort"))
    current = DEFAULTS[level][host]
    model, effort = current.model, current.effort
    if "model" in fields:
        model = fields["model"]
        if not isinstance(model, str) or not model.strip() or any(ord(char) < 32 or ord(char) == 127 for char in model):
            raise _invalid(f"{context}.model", "expected a nonempty native model identifier or inherit")
        if host == "antigravity" and model not in {"flash", "pro", "inherit"}:
            raise _invalid(f"{context}.model", "expected flash, pro or inherit")
        model = None if model == "inherit" else model
    if "effort" in fields:
        effort = fields["effort"]
        if not isinstance(effort, str) or effort not in EFFORTS[host]:
            raise _invalid(f"{context}.effort", f"expected one of {sorted(EFFORTS[host])}")
        effort = None if effort == "inherit" else effort
    if host == "codex" and model in {"gpt-6.1-sol", "gpt-6-astra"} and effort == "none":
        raise _invalid(context, f"model {model} does not support effort none; select a supported effort or inherit")
    return ModelSettings(model, effort)


def parse_subagents(value: object) -> SubagentPolicy:
    """Validate all supplied mappings, including unused levels and hosts."""
    table = _table(value, "subagents", ("default_level", "levels", "roles"))
    default = _level(table["default_level"], "subagents.default_level") if "default_level" in table else None
    levels = _table(table.get("levels", {}), "subagents.levels", LEVELS[1:])
    mappings = []
    for level, hosts in levels.items():
        for host, fields in _table(hosts, f"subagents.levels.{level}", AGENT_NAMES).items():
            mappings.append((level, host, _mapping(level, host, fields)))
    roles = table.get("roles", {})
    if not isinstance(roles, dict):
        raise _invalid("subagents.roles", "expected a table")
    selected = []
    for identity, fields in roles.items():
        if not isinstance(identity, str) or not IDENTITY.fullmatch(identity):
            raise _invalid("subagents.roles", "expected bundle:asset keys using lowercase slugs")
        entry = _table(fields, f"subagents.roles.{identity}", ("level",))
        if "level" not in entry:
            raise _invalid(f"subagents.roles.{identity}", "level is required")
        selected.append((identity, _level(entry["level"], f"subagents.roles.{identity}.level")))
    return SubagentPolicy(default, tuple(mappings), tuple(selected))


def resolve_settings(
    policy: SubagentPolicy, identity: str, source_level: str | None, host: str
) -> ModelSettings | None:
    """None preserves authored native fields; empty ModelSettings explicitly resets them."""
    level = dict(policy.roles).get(identity, policy.default_level if policy.default_level is not None else source_level)
    if level is None:
        return None
    if level == "inherit":
        return ModelSettings()
    for mapped_level, mapped_host, settings in policy.mappings:
        if (level, host) == (mapped_level, mapped_host):
            return settings
    return DEFAULTS[level][host]


def validate_role_overrides(
    policy: SubagentPolicy,
    installed: list[InstalledBundle],
    selected: set[str],
    *,
    unusable: Mapping[str, PackageError] | None = None,
) -> None:
    """Unknown bundles fail; entries in installed unselected bundles stay dormant."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    for identity, _ in policy.roles:
        name, asset_id = identity.split(":")
        context = f"subagents.roles.{identity}"
        if unusable is not None and name in unusable:
            if name in selected:
                raise unusable[name]
            continue
        if name not in bundles:
            raise _invalid(context, "bundle is not installed; install it or remove its role override")
        if name not in selected:
            continue
        asset = next((asset for asset in bundles[name].assets if asset.id == asset_id), None)
        if asset is None or asset.kind != "subagent" or "common" not in dict(asset.sources):
            raise _invalid(context, "expected a common subagent contract in the selected bundle")
