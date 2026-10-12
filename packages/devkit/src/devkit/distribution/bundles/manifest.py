"""``bundle.toml`` schema 1: load and validate a bundle source directory."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from devkit.core.errors import UnsafePathError
from devkit.core.paths import normalize_relpath

from ..errors import BundleError, SelectionError
from .common import AGENT_NAMES, ALL, SLUG, VERSION
from .instructions import read_instruction_header
from .playbooks import playbook_entry, read_playbook_header
from .subagents import read_contract, subagent_entry
from .workflows import read_workflow_header, workflow_entry

KINDS = frozenset(
    {"skill", "subagent", "instruction", "playbook", "rule", "workflow", "workflow-check", "gate", "document"}
)
# Workspace roots a seeded target may never enter: devkit's own state, Git, agent projections
# and the root guidance file are owned by devkit, the host or the project in other ways.
# Compared case-insensitively: on a case-insensitive file system ``.GIT`` is ``.git``.
SEED_FORBIDDEN_ROOTS = frozenset({".devkit", ".git", ".agents", ".claude", ".codex"})
SEED_FORBIDDEN_FILES = frozenset({"agents.md"})
# By-products of editing a source in place (Finder metadata, bytecode caches); never bundle content.
IGNORED_NAMES = frozenset({".DS_Store", "__pycache__"})
IGNORED_SUFFIXES = (".pyc",)

__all__ = ["ALL", "SLUG", "Asset", "Bundle", "load_bundle", "safe_source", "seed_target", "source_files"]


@dataclass(frozen=True)
class Asset:
    id: str
    kind: str
    sources: tuple[tuple[str, str], ...]
    # ``seeded`` assets are written once to ``target`` (workspace-relative) and then project-owned.
    seeded: bool = False
    target: str | None = None


@dataclass(frozen=True)
class Bundle:
    root: Path
    name: str
    version: str
    assets: tuple[Asset, ...]
    presets: dict[str, tuple[str, ...]]
    default_preset: str | None = None

    @property
    def preset_names(self) -> list[str]:
        return [ALL, *sorted(self.presets)]

    def asset(self, asset_id: str) -> Asset | None:
        return next((asset for asset in self.assets if asset.id == asset_id), None)

    def select(self, presets: list[str] | tuple[str, ...]) -> set[str]:
        """Return the union of asset IDs selected by ``presets``."""
        if not presets:
            raise SelectionError(f"{self.name}: at least one preset is required")
        selected: set[str] = set()
        for preset in presets:
            if preset == ALL:
                selected.update(asset.id for asset in self.assets)
            elif preset in self.presets:
                selected.update(self.presets[preset])
            else:
                raise SelectionError(
                    f"{self.name}: unknown preset {preset}; available: {', '.join(self.preset_names)}",
                    fix=f"Select one of: {', '.join(f'{self.name}:{name}' for name in self.preset_names)}",
                )
        return selected

    @property
    def constitution(self) -> Path | None:
        path = self.root / "AGENTS.md"
        if not path.exists() and not path.is_symlink():
            return None
        path = safe_source(self.root, "AGENTS.md")
        if not path.is_file():
            raise BundleError("constitution AGENTS.md must be a file")
        return path


def _mapping(value: Any, keys: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise BundleError(f"{context}: expected a table")
    if unknown := value.keys() - keys:
        raise BundleError(f"{context}: unknown keys {sorted(unknown)}")
    return value


def _slug(value: Any, context: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise BundleError(f"{context}: expected a lowercase slug")
    return value


def _authoring_path(value: Any, error: str) -> PurePosixPath:
    """A path as a bundle author writes it: canonical relative POSIX, and no backslash.

    ``devkit.core.paths`` accepts a backslash as a file-name character; an
    authored path rejects it so the same manifest means the same files on
    every platform.
    """
    if not isinstance(value, str) or not value:
        raise BundleError(error)
    if "\\" in value:
        raise BundleError(error)
    try:
        return normalize_relpath(value, canonical=True)
    except UnsafePathError as exc:
        raise BundleError(error) from exc


def safe_source(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise BundleError("source: expected a relative POSIX path")
    rel = _authoring_path(value, f"unsafe source path: {value}")
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise BundleError(f"source symlink: {value}")
    if not path.exists() or not (path.is_file() or path.is_dir()):
        raise BundleError(f"source missing or nonregular: {value}")
    return path


def seed_target(value: Any, context: str) -> str:
    """Validate a seeded asset's workspace-relative destination."""
    if not isinstance(value, str) or not value:
        raise BundleError(f"{context}: target: expected a relative POSIX path")
    rel = _authoring_path(value, f"{context}: unsafe target path: {value}")
    if rel.parts[0].casefold() in SEED_FORBIDDEN_ROOTS or value.casefold() in SEED_FORBIDDEN_FILES:
        raise BundleError(f"{context}: target may not be under devkit, Git, agent or root guidance paths: {value}")
    return value


def _ignored(path: Path, base: Path) -> bool:
    parts = path.relative_to(base).parts
    return any(part in IGNORED_NAMES for part in parts) or path.name.endswith(IGNORED_SUFFIXES)


def source_files(root: Path, source: str) -> list[Path]:
    """Every file of a source, sorted; editing by-products (``IGNORED_NAMES``, ``*.pyc``) are skipped."""
    path = safe_source(root, source)
    files = []
    for entry in sorted(path.rglob("*")) if path.is_dir() else [path]:
        if path.is_dir() and _ignored(entry, path):
            continue
        if entry.is_symlink() or not (entry.is_dir() or entry.is_file()):
            raise BundleError(f"nonregular source: {entry.relative_to(root)}")
        if entry.is_file():
            files.append(entry)
    if not files:
        raise BundleError(f"empty source: {source}")
    return files


def _check_source(root: Path, asset_id: str, kind: str, variant: str, source: str) -> None:
    """Validate the kind-specific content of one source."""
    path = safe_source(root, source)
    files = source_files(root, source)
    if kind == "skill" and (not path.is_dir() or not (path / "SKILL.md").is_file()):
        raise BundleError(f"{asset_id}: skill source must contain SKILL.md")
    if kind == "instruction":
        for file in files:
            read_instruction_header(file.read_bytes(), f"{asset_id}/{file.relative_to(root).as_posix()}")
    if kind == "playbook":
        read_playbook_header(playbook_entry(root, source).read_bytes(), f"{asset_id}/{source}")
    if kind == "workflow":
        read_workflow_header(workflow_entry(root, source).read_bytes(), f"{asset_id}/{source}")
    if kind == "subagent" and variant == "common":
        read_contract(subagent_entry(root, source).read_bytes(), f"{asset_id}/{source}", asset_id)


def _asset(root: Path, raw: Any) -> Asset:
    item = _mapping(raw, {"id", "kind", "source", "variants", "seeded", "target"}, "asset")
    asset_id = _slug(item.get("id"), "asset.id")
    kind = item.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        raise BundleError(f"unknown asset kind: {kind}")
    if ("source" in item) == ("variants" in item):
        raise BundleError(f"{asset_id}: declare exactly one of source or variants")
    seeded = item.get("seeded", False)
    if type(seeded) is not bool:
        raise BundleError(f"{asset_id}: seeded must be a boolean")
    if seeded and kind != "document":
        raise BundleError(f"{asset_id}: only document assets can be seeded")
    if seeded and "variants" in item:
        raise BundleError(f"{asset_id}: a seeded asset declares a single source")
    if ("target" in item) != seeded:
        raise BundleError(f"{asset_id}: target is required for seeded assets and not allowed otherwise")
    target_path = seed_target(item["target"], asset_id) if seeded else None
    if "source" in item:
        pairs = {"common": item["source"]}
    else:
        pairs = item["variants"]
        if not isinstance(pairs, dict) or not pairs:
            raise BundleError(f"{asset_id}: variants must be a nonempty table")
        if unknown := sorted(set(pairs) - set(AGENT_NAMES)):
            raise BundleError(f"{asset_id}: unknown variants {unknown}; expected agents {list(AGENT_NAMES)}")
    sources = []
    for variant, source in sorted(pairs.items()):
        _check_source(root, asset_id, kind, variant, source)
        sources.append((variant, source))
    return Asset(asset_id, kind, tuple(sources), seeded, target_path)


def load_bundle(root: Path) -> Bundle:
    root = root.resolve()
    manifest = safe_source(root, "bundle.toml")
    try:
        data = _mapping(
            tomllib.loads(manifest.read_text("utf-8")),
            {"schema", "name", "version", "assets", "presets", "default_preset"},
            "bundle",
        )
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BundleError(f"cannot read bundle.toml: {exc}") from exc
    if type(data.get("schema")) is not int or data["schema"] != 1:
        raise BundleError("unsupported schema; expected 1")
    name = _slug(data.get("name"), "name")
    version = data.get("version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise BundleError("version: expected X.Y.Z")
    raw_assets = data.get("assets")
    if not isinstance(raw_assets, list) or not raw_assets:
        raise BundleError("assets: expected a nonempty array of tables")
    assets: list[Asset] = []
    for raw in raw_assets:
        asset = _asset(root, raw)
        if any(existing.id == asset.id for existing in assets):
            raise BundleError(f"duplicate asset id: {asset.id}")
        assets.append(asset)
    ids = {asset.id for asset in assets}
    raw_presets = data.get("presets", {})
    if not isinstance(raw_presets, dict):
        raise BundleError("presets: expected a table")
    presets = {}
    for preset, raw in raw_presets.items():
        _slug(preset, "preset")
        if preset == ALL:
            raise BundleError(f"preset {ALL} is reserved")
        item = _mapping(raw, {"assets"}, f"preset {preset}")
        selected = item.get("assets")
        if not isinstance(selected, list) or not selected or not all(isinstance(v, str) for v in selected):
            raise BundleError(f"{preset}: assets must be a nonempty string array")
        if len(set(selected)) != len(selected) or set(selected) - ids:
            raise BundleError(f"{preset}: duplicate or unknown asset selection")
        presets[preset] = tuple(selected)
    default_preset = data.get("default_preset")
    if default_preset is not None and (not isinstance(default_preset, str) or default_preset not in {ALL, *presets}):
        raise BundleError(f"default_preset: expected {ALL} or a declared preset")
    bundle = Bundle(root, name, version, tuple(assets), presets, default_preset)
    if bundle.constitution is not None:
        try:
            bundle.constitution.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise BundleError("constitution AGENTS.md must be UTF-8") from exc
    return bundle
