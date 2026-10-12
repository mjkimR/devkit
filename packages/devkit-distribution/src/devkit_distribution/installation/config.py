"""Project configuration (``.devkit/config.toml``): explicit bundle selection.

A bundle is deployed only when ``[presets]`` names it.
"""

from __future__ import annotations

import math
import os
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import TOMLKitError

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG

from .discovery import InstalledBundle
from .inventory import AGENTS
from .transaction import CONFIG

SCHEMA = 1
# ``rules`` is owned by ``agent-rule-engine`` (phase overrides) and is only passed through here.
FIELDS = frozenset({"schema", "agents", "presets", "playbooks", "rules"})


@dataclass(frozen=True)
class ProjectConfig:
    agents: list[str] = field(default_factory=list)
    presets: dict[str, list[str]] = field(default_factory=dict)


def _load(root: Path) -> dict[str, Any] | None:
    path = root / CONFIG
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BundleError(f"invalid config: {exc}") from exc
    if "schema" in data and (type(data["schema"]) is not int or data["schema"] != SCHEMA):
        raise BundleError("unsupported config schema")
    unknown = set(data) - FIELDS
    if unknown:
        raise BundleError(f"config: unknown fields: {sorted(unknown)}")
    return data


def _agents(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v in AGENTS for v in value):
        raise BundleError("config: invalid agents")
    return sorted(set(value))


def parse_presets(value: object, context: str = "config") -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise BundleError(f"{context}: invalid presets")
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
            raise BundleError(f"{context}: invalid presets")
        result[bundle] = list(presets)
    return result


def validate_playbooks_config(playbooks: object) -> dict[str, int | float]:
    if playbooks is None:
        return {}
    if not isinstance(playbooks, dict):
        raise BundleError("config playbooks: expected a table")
    unknown = set(playbooks) - {"min_score", "limit", "max_bytes"}
    if unknown:
        raise BundleError(f"config playbooks: unknown fields: {sorted(unknown)}")
    result: dict[str, int | float] = {}
    if "limit" in playbooks:
        val = playbooks["limit"]
        if type(val) is not int or not 1 <= val <= 20:
            raise BundleError("config playbooks: limit must be an integer between 1 and 20")
        result["limit"] = val
    if "min_score" in playbooks:
        val = playbooks["min_score"]
        if not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
            raise BundleError("config playbooks: min_score must be a finite nonnegative number")
        result["min_score"] = float(val)
    if "max_bytes" in playbooks:
        val = playbooks["max_bytes"]
        if type(val) is not int or not 1024 <= val <= 65536:
            raise BundleError("config playbooks: max_bytes must be an integer between 1024 and 65536")
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
    return ProjectConfig(
        agents=_agents(data["agents"]) if "agents" in data else [],
        presets=parse_presets(data.get("presets", {})),
    )


def resolve_selection(installed: list[InstalledBundle], requested: dict[str, list[str]]) -> dict[str, list[str]]:
    """Resolve CLI selections; an empty preset list means the bundle's ``default_preset``."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    result = {}
    for name, presets in requested.items():
        bundle = bundles.get(name)
        if bundle is None:
            raise BundleError(f"bundle is not installed: {name}")
        if not presets:
            if bundle.default_preset is None:
                raise BundleError(
                    f"{name}: no default preset; choose one of: {', '.join(f'{name}:{p}' for p in bundle.preset_names)}"
                )
            presets = [bundle.default_preset]
        bundle.select(presets)
        result[name] = list(dict.fromkeys(presets))
    return result


def _document(root: Path) -> tomlkit.TOMLDocument:
    path = root / CONFIG
    if not path.is_file():
        doc = tomlkit.document()
        doc["schema"] = SCHEMA
        return doc
    try:
        return tomlkit.parse(path.read_text("utf-8"))
    except (OSError, UnicodeError, TOMLKitError) as exc:
        raise BundleError(f"invalid config: {exc}") from exc


def _write(root: Path, doc: tomlkit.TOMLDocument) -> None:
    path = root / CONFIG
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise BundleError(f"config must be a regular file: {CONFIG}")
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, temp = tempfile.mkstemp(prefix=".devkit-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(tomlkit.dumps(doc))
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def _preset_value(presets: list[str]) -> str | list[str]:
    return presets[0] if len(presets) == 1 else presets


def update_config(
    root: Path,
    *,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: list[str] | tuple[str, ...] = (),
) -> None:
    """Edit selection entries in place, preserving unrelated tables, comments, and formatting."""
    read_config(root)
    doc = _document(root)
    if agents is not None:
        doc["agents"] = sorted(set(agents))
    if presets or deselect:
        table = doc.get("presets")
        if table is None:
            table = tomlkit.table()
            doc["presets"] = table
        for name, values in (presets or {}).items():
            table[name] = _preset_value(values)
        for name in deselect:
            if name in table:
                del table[name]
    _write(root, doc)
