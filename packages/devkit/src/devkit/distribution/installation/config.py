"""Project configuration (``.devkit/config.toml``): bundle selection.

A bundle from another distribution is deployed only when ``[presets]`` names it.
A built-in bundle (shipped by the ``devkit`` distribution itself) is deployed
with its default preset unless ``[presets]`` names it, which selects other
presets, or sets it to ``false``, which opts the project out. Native
projections go to every supported agent unless ``agents`` narrows the list;
``agents = []`` turns projection off.
"""

from __future__ import annotations

import math
import os
import re
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import TOMLKitError

from devkit.core.errors import ConfigError

from ..bundles.common import AGENT_NAMES, SLUG
from ..errors import SelectionError
from .discovery import InstalledBundle
from .workspace import CONFIG

SCHEMA = 1
# ``rules`` is owned by ``devkit.rules`` (phase overrides), ``workflow`` by
# ``devkit.workflow`` (layout, approvals) and ``gates`` by ``devkit.gate``
# (gate settings); all are only passed through here. ``[tool.<name>]`` tables belong
# to whichever tool ``<name>`` is and are passed through unread, like ``[tool.*]`` in
# ``pyproject.toml``; every other top-level key is rejected so typos are caught.
FIELDS = frozenset(
    {
        "schema",
        "agents",
        "presets",
        "playbooks",
        "rules",
        "workflow",
        "gates",
        "guidance_block",
        "override_drift",
        "tool",
    }
)
OVERRIDE_DRIFT = ("warn", "block")
TOOL_NAME = re.compile(r"[a-z][a-z0-9_-]*\Z")


def all_agents() -> list[str]:
    return sorted(AGENT_NAMES)


@dataclass(frozen=True)
class ProjectConfig:
    agents: list[str] = field(default_factory=all_agents)
    presets: dict[str, list[str]] = field(default_factory=dict)
    # Bundles set to ``false`` in ``[presets]``: never selected by default.
    opted_out: frozenset[str] = frozenset()
    # ``guidance_block = false`` stops ``devkit sync`` from managing the block in root AGENTS.md.
    guidance_block: bool = True
    # ``override_drift = "block"`` makes upstream drift behind an override abort the sync.
    override_drift: str = "warn"


def _config_path(root: Path) -> Path:
    """``root/.devkit/config.toml``; it is read and written in place, so it must be a regular file."""
    path = root / CONFIG
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ConfigError(f"config must be a regular file: {CONFIG}")
    return path


def _load(root: Path) -> dict[str, Any] | None:
    path = _config_path(root)
    if not path.exists():
        return None
    try:
        data = tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid config: {exc}") from exc
    if "schema" in data and (type(data["schema"]) is not int or data["schema"] != SCHEMA):
        raise ConfigError("unsupported config schema")
    unknown = set(data) - FIELDS
    if unknown:
        raise ConfigError(f"config: unknown fields: {sorted(unknown)}")
    validate_tool_tables(data.get("tool"))
    return data


def validate_tool_tables(tool: object) -> None:
    """``[tool.<name>]`` must be a table of tables; their contents are never inspected."""
    if tool is None:
        return
    if not isinstance(tool, dict):
        raise ConfigError("config tool: expected a table of [tool.<name>] tables")
    for name, value in tool.items():
        if not (isinstance(name, str) and TOOL_NAME.fullmatch(name)):
            raise ConfigError(f"config tool: invalid tool name: {name!r}")
        if not isinstance(value, dict):
            raise ConfigError(f"config tool.{name}: expected a table")


def _agents(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v in AGENT_NAMES for v in value):
        raise ConfigError("config: invalid agents")
    return sorted(set(value))


def parse_presets(value: object, context: str = "config") -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise ConfigError(f"{context}: invalid presets")
    result = {}
    for bundle, presets in value.items():
        if isinstance(presets, str):
            presets = [presets]
        if (
            not (isinstance(bundle, str) and SLUG.fullmatch(bundle))
            or not isinstance(presets, list)
            or not presets
            or not all(isinstance(v, str) and SLUG.fullmatch(v) for v in presets)
            or len(set(presets)) != len(presets)
        ):
            raise ConfigError(f"{context}: invalid presets")
        result[bundle] = list(presets)
    return result


def parse_selection(value: object) -> tuple[dict[str, list[str]], frozenset[str]]:
    """``[presets]`` of the config: preset selections and the bundles set to ``false``."""
    if not isinstance(value, dict):
        raise ConfigError("config: invalid presets")
    opted_out = frozenset(name for name, presets in value.items() if presets is False)
    for name in opted_out:
        if not (isinstance(name, str) and SLUG.fullmatch(name)):
            raise ConfigError("config: invalid presets")
    return parse_presets({k: v for k, v in value.items() if k not in opted_out}), opted_out


def default_selection(installed: list[InstalledBundle], config: ProjectConfig) -> dict[str, list[str]]:
    """Built-in bundles the configuration neither names nor opts out of, with their default preset."""
    return {
        item.bundle.name: [item.bundle.default_preset]
        for item in installed
        if item.builtin
        and item.bundle.default_preset is not None
        and item.bundle.name not in config.presets
        and item.bundle.name not in config.opted_out
    }


def effective_selection(installed: list[InstalledBundle], config: ProjectConfig) -> dict[str, list[str]]:
    """What ``devkit sync`` deploys without command-line selections: defaults, then ``[presets]``."""
    return {**default_selection(installed, config), **config.presets}


def validate_playbooks_config(playbooks: object) -> dict[str, int | float]:
    if playbooks is None:
        return {}
    if not isinstance(playbooks, dict):
        raise ConfigError("config playbooks: expected a table")
    unknown = set(playbooks) - {"min_score", "limit", "max_bytes"}
    if unknown:
        raise ConfigError(f"config playbooks: unknown fields: {sorted(unknown)}")
    result: dict[str, int | float] = {}
    if "limit" in playbooks:
        val = playbooks["limit"]
        if type(val) is not int or not 1 <= val <= 20:
            raise ConfigError("config playbooks: limit must be an integer between 1 and 20")
        result["limit"] = val
    if "min_score" in playbooks:
        val = playbooks["min_score"]
        if not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
            raise ConfigError("config playbooks: min_score must be a finite nonnegative number")
        result["min_score"] = float(val)
    if "max_bytes" in playbooks:
        val = playbooks["max_bytes"]
        if type(val) is not int or not 1024 <= val <= 65536:
            raise ConfigError("config playbooks: max_bytes must be an integer between 1024 and 65536")
        result["max_bytes"] = val
    return result


def read_playbook_config(root: Path) -> dict[str, int | float]:
    data = _load(root)
    return validate_playbooks_config(data.get("playbooks")) if data else {}


def read_config(root: Path) -> ProjectConfig:
    data = _load(root)
    if data is None:
        return ProjectConfig()
    validate_playbooks_config(data.get("playbooks"))
    guidance_block = data.get("guidance_block", True)
    if type(guidance_block) is not bool:
        raise ConfigError("config: guidance_block must be a boolean")
    override_drift = data.get("override_drift", "warn")
    if override_drift not in OVERRIDE_DRIFT:
        raise ConfigError(f"config: override_drift must be one of {list(OVERRIDE_DRIFT)}")
    presets, opted_out = parse_selection(data.get("presets", {}))
    return ProjectConfig(
        agents=_agents(data["agents"]) if "agents" in data else all_agents(),
        presets=presets,
        opted_out=opted_out,
        guidance_block=guidance_block,
        override_drift=override_drift,
    )


def resolve_selection(installed: list[InstalledBundle], requested: dict[str, list[str]]) -> dict[str, list[str]]:
    """Resolve CLI selections; an empty preset list means the bundle's ``default_preset``."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    result = {}
    for name, presets in requested.items():
        bundle = bundles.get(name)
        if bundle is None:
            raise SelectionError(
                f"bundle is not installed: {name}",
                fix="Install the content package that ships it, or run `devkit list`",
            )
        if not presets:
            if bundle.default_preset is None:
                raise SelectionError(
                    f"{name}: no default preset; choose one of: {', '.join(f'{name}:{p}' for p in bundle.preset_names)}"
                )
            presets = [bundle.default_preset]
        bundle.select(presets)
        result[name] = list(dict.fromkeys(presets))
    return result


def _document(root: Path) -> tomlkit.TOMLDocument:
    path = _config_path(root)
    if not path.exists():
        doc = tomlkit.document()
        doc["schema"] = SCHEMA
        return doc
    try:
        return tomlkit.parse(path.read_text("utf-8"))
    except (OSError, UnicodeError, TOMLKitError) as exc:
        raise ConfigError(f"invalid config: {exc}") from exc


def _check_writable(root: Path) -> None:
    """Fail before anything is synchronized when the configuration could not be saved afterwards."""
    path = _config_path(root)
    directory = next((parent for parent in (path.parent, root) if parent.exists()), root)
    if path.exists() and not os.access(path, os.R_OK):
        raise ConfigError(f"config is not readable: {CONFIG}")
    if not os.access(directory, os.W_OK | os.X_OK):
        raise ConfigError(f"cannot write {CONFIG}: {directory} is not writable")


def _write(root: Path, text: str) -> None:
    path = _config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, temp = tempfile.mkstemp(prefix=".devkit-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def _preset_value(presets: list[str]) -> str | list[str]:
    return presets[0] if len(presets) == 1 else presets


@dataclass(frozen=True)
class ConfigUpdate:
    """A selection edit rendered and checked before a sync, saved with ``apply`` after it."""

    root: Path
    text: str | None

    def apply(self) -> None:
        if self.text is not None:
            _write(self.root, self.text)


def prepare_config_update(
    root: Path,
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    opt_out: list[str] | tuple[str, ...] = (),
) -> ConfigUpdate:
    """Render a selection edit and check that it can be saved, without writing.

    ``deselect`` deletes a bundle's entry; ``opt_out`` records ``<bundle> = false``
    so a built-in bundle stays unselected. Selecting a bundle replaces either.
    Unrelated tables, comments and formatting are preserved. Nothing to change
    yields an update whose ``apply`` does nothing.
    """
    read_config(root)
    if agents is None and not (presets or deselect or opt_out):
        return ConfigUpdate(root, None)
    doc = _document(root)
    if agents is not None:
        doc["agents"] = sorted(set(agents))
    if presets or deselect or opt_out:
        table = doc.get("presets")
        if table is None:
            table = tomlkit.table()
            doc["presets"] = table
        for name, values in (presets or {}).items():
            table[name] = _preset_value(values)
        for name in deselect:
            if name in table:
                del table[name]
        for name in opt_out:
            table[name] = False
    _check_writable(root)
    return ConfigUpdate(root, tomlkit.dumps(doc))


def update_config(
    root: Path,
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
    opt_out: list[str] | tuple[str, ...] = (),
) -> None:
    """Edit selection entries in place (``prepare_config_update`` then ``apply``)."""
    prepare_config_update(root, agents=agents, presets=presets, deselect=deselect, opt_out=opt_out).apply()
