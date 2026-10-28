"""Restricted checkout-local preferences, independent of distribution and governance."""

from __future__ import annotations

import copy
import math
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.models.development import development_approach
from devkit_dist.features.project.repositories.project import read_toml
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH

LOCAL_CONFIG_PATH = ".devkit/config.local.toml"


class LocalKeyForbiddenError(ConfigError):
    code = "CONFIG_LOCAL_KEY_FORBIDDEN"
    fix = "Remove the forbidden key from .devkit/config.local.toml; shared policy belongs in .devkit/config.toml"


@dataclass(frozen=True)
class EffectiveConfig:
    values: dict[str, Any]
    sources: dict[str, str]


@dataclass(frozen=True)
class ExecutionEnvironment:
    environment: str
    source: str


def _invalid(path: Path | str, message: str) -> ConfigError:
    """``CONFIG_INVALID`` for ``path``: a workspace-relative name (``CONFIG_PATH``, ``LOCAL_CONFIG_PATH``)."""
    return ConfigError(f"{path}: {message}", target_files=[str(path)])


def validate_runtime_tables(data: dict[str, Any], path: Path | str) -> None:
    for table, key, default, expected in (
        ("execution", "environment", "local", str),
        ("mcp", "register", True, bool),
        ("presentation", "language", "auto", str),
        ("shared", "adapter", "local", str),
    ):
        value = data.get(table, {})
        if not isinstance(value, dict) or set(value) - {key}:
            raise _invalid(path, f"{table}: expected only {key}")
        setting = value.get(key, default)
        if type(setting) is not expected or (table == "execution" and setting not in ("local", "cloud")):
            raise _invalid(path, f"{table}.{key}: invalid value {setting!r}")
        if table == "shared" and (not isinstance(setting, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", setting)):
            raise _invalid(path, "shared.adapter: expected a lowercase adapter ID")


def read_local_config(root: Path) -> dict[str, Any]:
    file = root / LOCAL_CONFIG_PATH
    path = LOCAL_CONFIG_PATH
    if file.is_symlink() or (file.exists() and not stat.S_ISREG(file.stat().st_mode)):
        raise _invalid(path, "config must be a regular file, not a symlink")
    data = read_toml(file, path) or {}
    unknown = set(data) - {"schema", "execution", "mcp", "presentation", "playbooks", "bundles", "shared"}
    if unknown:
        raise LocalKeyForbiddenError(f"{path}: forbidden keys: {sorted(unknown)}", target_files=[str(path)])
    if "schema" in data and (type(data["schema"]) is not int or data["schema"] != 1):
        raise _invalid(path, "unsupported config schema")
    validate_runtime_tables(data, path)
    playbooks = data.get("playbooks", {})
    if not isinstance(playbooks, dict):
        raise _invalid(path, "playbooks: expected table")
    if set(playbooks) - {"limit", "max_bytes", "min_score", "min_similarity", "mode"}:
        raise _invalid(path, "playbooks: unknown keys")
    for key, value in playbooks.items():
        valid = False
        if key in ("limit", "max_bytes"):
            low, high = (1, 20) if key == "limit" else (1024, 65536)
            valid = type(value) is int and low <= value <= high
        elif key in ("min_score", "min_similarity"):
            valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
            if key == "min_similarity":
                valid = valid and value <= 1
        elif key == "mode":
            valid = isinstance(value, str) and value.lower() in ("auto", "dense", "hybrid", "lexical")
        if not valid:
            raise _invalid(path, f"playbooks.{key}: invalid value")
    bundles = data.get("bundles", {})
    if not isinstance(bundles, dict):
        raise _invalid(path, "bundles: expected table")
    for name, settings in bundles.items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or not isinstance(settings, dict):
            raise _invalid(path, f"bundles.{name}: invalid bundle table")
        if set(settings) - {"variables"}:
            raise LocalKeyForbiddenError(f"{path}: bundles.{name}: only variables are local", target_files=[str(path)])
        values = settings.get("variables", {})
        if not isinstance(values, dict) or any(
            not re.fullmatch(r"[a-z][a-z0-9_]*", k) or type(v) not in (str, bool, int) for k, v in values.items()
        ):
            raise _invalid(path, f"bundles.{name}.variables: expected scalar template inputs")
    return data


def merge_config(shared: dict[str, Any], local: dict[str, Any], *, path: Path | str) -> dict[str, Any]:
    """Recursive tables; whole scalar/array replacement; no coercion across types."""
    merged = copy.deepcopy(shared)
    for key, value in local.items():
        if key in merged:
            old = merged[key]
            if isinstance(old, dict) and isinstance(value, dict):
                merged[key] = merge_config(old, value, path=path)
                continue
            if type(old) is not type(value):
                raise _invalid(path, f"{key}: overlay type differs from shared value")
        merged[key] = copy.deepcopy(value)
    return merged


def read_effective_config(root: Path, *, local: bool = True) -> EffectiveConfig:
    """Read only the explicit workspace; every present local input is validated.

    ``sources`` name each value's file workspace-relative (``.devkit/config.toml``, ``.devkit/config.local.toml``)
    or ``default``, as errors about these files do.
    """
    shared_file = root / CONFIG_PATH
    if shared_file.is_symlink() or (shared_file.exists() and not shared_file.is_file()):
        raise _invalid(CONFIG_PATH, "config must be a regular file")
    shared = read_toml(shared_file, CONFIG_PATH) or {}
    if "schema" in shared and (type(shared["schema"]) is not int or shared["schema"] != 1):
        raise _invalid(CONFIG_PATH, "unsupported config schema")
    validate_runtime_tables(shared, CONFIG_PATH)
    development = development_approach(shared)
    overlay = read_local_config(root) if local else {}
    values = merge_config(shared, overlay, path=LOCAL_CONFIG_PATH)
    sources: dict[str, str] = {}

    def record(data: dict[str, Any], source: str, prefix: str = "") -> None:
        for key, value in data.items():
            name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                record(value, source, name)
            else:
                sources[name] = source

    record(shared, CONFIG_PATH)
    record(overlay, LOCAL_CONFIG_PATH)
    for table, key, value in (
        ("execution", "environment", "local"),
        ("mcp", "register", True),
        ("presentation", "language", "auto"),
        ("shared", "adapter", "local"),
    ):
        values.setdefault(table, {}).setdefault(key, value)
        sources.setdefault(f"{table}.{key}", "default")
    values.setdefault("development", {})["approach"] = development.approach
    sources["development.approach"] = development.source
    return EffectiveConfig(values, sources)


def resolve_execution_environment(root: Path) -> ExecutionEnvironment:
    """An execution constraint, never approval authority or a host-interactivity guarantee."""
    if not root.is_dir() or not (root / ".devkit").is_dir():
        raise _invalid(root, "execution workspace must be an existing devkit project")
    config = read_effective_config(root)
    return ExecutionEnvironment(config.values["execution"]["environment"], config.sources["execution.environment"])
