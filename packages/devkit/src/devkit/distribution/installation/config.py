"""Project configuration (``.devkit/config.toml``): bundle selection.

A bundle is deployed when ``[presets]`` names it. An installed bundle that
declares ``auto_select``, built in or from any other package, is also deployed
with its default preset unless ``[presets]`` names it, which selects other
presets, or sets it to ``false``, which opts the project out. Native
projections go to every supported agent unless ``agents`` narrows the list;
``agents = []`` turns projection off.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import TOMLKitError

from devkit.core.errors import ConfigError
from devkit.core.project import read_toml
from devkit.core.receipt import CONFIG_PATH, Receipt
from devkit.distribution.bundles.common import AGENT_NAMES, SLUG
from devkit.distribution.content import Content
from devkit.distribution.errors import SelectionError
from devkit.distribution.installation.discovery import InstalledBundle, unusable_bundles
from devkit.distribution.installation.transaction import replace_file
from devkit.search import SearchMode

SCHEMA = 1
# ``rules`` is owned by ``devkit.rules`` (phase overrides), ``workflow`` by
# ``devkit.workflow`` (layout, approvals), ``gates`` by ``devkit.gate`` (gate
# settings) and ``worktree`` by ``devkit.worktree``; all are only passed through here. ``[tool.<name>]`` tables belong
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
        "worktree",
        "guidance_block",
        "override_drift",
        "tool",
    }
)
OVERRIDE_DRIFT = ("warn", "block")
TOOL_NAME = re.compile(r"[a-z][a-z0-9_-]*\Z")

# ``devkit playbook search`` bounds: the ``[playbooks]`` table, the command's options and the library all check these.
PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX = 1, 20
PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX = 1024, 65536
DEFAULT_PLAYBOOK_LIMIT = 5
DEFAULT_PLAYBOOK_MIN_SCORE = 0.1
DEFAULT_PLAYBOOK_MAX_BYTES = 8192
DEFAULT_PLAYBOOK_MODE = SearchMode.AUTO
# Measured on English metadata: keeps most matches while dropping the long tail of weak cosine similarities.
DEFAULT_PLAYBOOK_MIN_SIMILARITY = 0.35
# A requested preset that stands for the bundle's ``default_preset`` (a bare ``bundle`` on the command line).
DEFAULT_PRESET = ""


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
    path = root / CONFIG_PATH
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ConfigError(f"config must be a regular file: {CONFIG_PATH}")
    return path


def _load(root: Path) -> dict[str, Any] | None:
    data = read_toml(_config_path(root), CONFIG_PATH)
    if data is None:
        return None
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
    """Auto-selected bundles the configuration neither names nor opts out of, with their default preset."""
    return {
        item.bundle.name: [item.bundle.default_preset]
        for item in installed
        if item.auto_selected
        and item.bundle.default_preset is not None
        and item.bundle.name not in config.presets
        and item.bundle.name not in config.opted_out
    }


def retained_selection(
    installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None
) -> dict[str, list[str]]:
    """Deployed bundles without a usable package that the configuration neither names nor opts out of.

    A package that cannot be loaded, or is not installed, cannot be read for
    ``auto_select``, so the bundle the receipt records as deployed stays
    selected with its recorded presets: the load error, or the missing package,
    then stops the command instead of a broken upgrade or a partial environment
    removing the bundle's files. Only ``devkit remove`` deselects it.
    """
    if receipt is None:
        return {}
    usable = {item.bundle.name for item in installed}
    return {
        name: list(presets)
        for name, presets in receipt.selection.presets.items()
        if name not in usable and name not in config.presets and name not in config.opted_out
    }


def effective_selection(
    installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None = None
) -> dict[str, list[str]]:
    """What ``devkit sync`` deploys without command-line selections: defaults, then ``[presets]``.

    With the ``receipt``, deployed bundles without a usable package are kept (``retained_selection``).
    """
    return {
        **default_selection(installed, config),
        **retained_selection(installed, config, receipt),
        **config.presets,
    }


def merge_selection(
    installed: list[InstalledBundle], config: ProjectConfig, requested: dict[str, list[str]]
) -> dict[str, list[str]]:
    """``requested`` joined with the presets each bundle already deploys, existing presets first."""
    current = effective_selection(installed, config)
    return {name: list(dict.fromkeys([*current.get(name, []), *presets])) for name, presets in requested.items()}


def validate_playbooks_config(playbooks: object) -> dict[str, int | float | str]:
    if playbooks is None:
        return {}
    if not isinstance(playbooks, dict):
        raise ConfigError("config playbooks: expected a table")
    unknown = set(playbooks) - {"min_score", "limit", "max_bytes", "mode", "min_similarity"}
    if unknown:
        raise ConfigError(f"config playbooks: unknown fields: {sorted(unknown)}")
    result: dict[str, int | float | str] = {}
    if "limit" in playbooks:
        val = playbooks["limit"]
        if type(val) is not int or not PLAYBOOK_LIMIT_MIN <= val <= PLAYBOOK_LIMIT_MAX:
            raise ConfigError(
                f"config playbooks: limit must be an integer between {PLAYBOOK_LIMIT_MIN} and {PLAYBOOK_LIMIT_MAX}"
            )
        result["limit"] = val
    if "min_score" in playbooks:
        val = playbooks["min_score"]
        if not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
            raise ConfigError("config playbooks: min_score must be a finite nonnegative number")
        result["min_score"] = float(val)
    if "max_bytes" in playbooks:
        val = playbooks["max_bytes"]
        if type(val) is not int or not PLAYBOOK_MAX_BYTES_MIN <= val <= PLAYBOOK_MAX_BYTES_MAX:
            raise ConfigError(
                "config playbooks: max_bytes must be an integer between"
                f" {PLAYBOOK_MAX_BYTES_MIN} and {PLAYBOOK_MAX_BYTES_MAX}"
            )
        result["max_bytes"] = val
    if "mode" in playbooks:
        val = playbooks["mode"]
        modes = [mode.value for mode in SearchMode]
        if not isinstance(val, str) or val.lower() not in modes:
            raise ConfigError(f"config playbooks: mode must be one of {', '.join(modes)}")
        result["mode"] = val.lower()
    if "min_similarity" in playbooks:
        val = playbooks["min_similarity"]
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not 0 <= val <= 1:
            raise ConfigError("config playbooks: min_similarity must be a number between 0 and 1")
        result["min_similarity"] = float(val)
    return result


def read_playbook_config(root: Path) -> dict[str, int | float | str]:
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
    """Resolve CLI selections; ``DEFAULT_PRESET``, or an empty preset list, means the bundle's ``default_preset``."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    result = {}
    for name, presets in requested.items():
        bundle = bundles.get(name)
        if bundle is None:
            unusable = unusable_bundles(installed)
            if name in unusable:
                raise unusable[name]
            raise SelectionError(
                f"bundle is not installed: {name}",
                fix="Install the content package that ships it, or run `devkit list`",
            )
        if not presets or DEFAULT_PRESET in presets:
            default = bundle.default_preset
            if default is None:
                raise SelectionError(
                    f"{name}: the bundle declares no default preset",
                    fix=f"Select one of: {', '.join(f'{name}:{p}' for p in bundle.preset_names)}",
                )
            presets = [default if preset == DEFAULT_PRESET else preset for preset in presets] or [default]
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
        raise ConfigError(f"config is not readable: {CONFIG_PATH}")
    if not os.access(directory, os.W_OK | os.X_OK):
        raise ConfigError(f"cannot write {CONFIG_PATH}: {directory} is not writable")


def _write(root: Path, text: str) -> None:
    """Replace the configuration atomically, keeping its permission bits."""
    path = _config_path(root)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    replace_file(path, Content(text.encode("utf-8"), mode))


def _preset_value(presets: list[str]) -> str | list[str]:
    return presets[0] if len(presets) == 1 else presets


@dataclass(frozen=True)
class ConfigUpdate:
    """A rendered and checked selection edit: ``apply`` saves it, ``revert`` puts the file back as it was."""

    root: Path
    text: str | None
    # The file before the edit; ``None`` when it did not exist.
    before: Content | None = None

    def apply(self) -> None:
        if self.text is not None:
            _write(self.root, self.text)

    def revert(self) -> None:
        if self.text is not None:
            replace_file(_config_path(self.root), self.before)


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
    path = _config_path(root)
    before = Content(path.read_bytes(), path.stat().st_mode & 0o777) if path.exists() else None
    return ConfigUpdate(root, tomlkit.dumps(doc), before)


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
