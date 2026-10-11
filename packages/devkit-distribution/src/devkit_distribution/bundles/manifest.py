from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

KINDS = {"skill", "subagent", "instruction", "playbook", "rule"}
SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


class BundleError(ValueError):
    """Invalid bundle input."""


@dataclass(frozen=True)
class Asset:
    id: str
    kind: str
    sources: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Bundle:
    root: Path
    name: str
    version: str
    assets: tuple[Asset, ...]
    presets: dict[str, tuple[str, ...]]

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


def safe_source(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise BundleError("source: expected a relative POSIX path")
    rel = PurePosixPath(value)
    if rel.is_absolute() or ".." in rel.parts or "\\" in value or str(rel) != value or value == ".":
        raise BundleError(f"unsafe source path: {value}")
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise BundleError(f"source symlink: {value}")
    if not path.exists() or not (path.is_file() or path.is_dir()):
        raise BundleError(f"source missing or nonregular: {value}")
    return path


def source_files(root: Path, source: str) -> list[Path]:
    path = safe_source(root, source)
    files = []
    for entry in sorted(path.rglob("*")) if path.is_dir() else [path]:
        if entry.is_symlink() or not (entry.is_dir() or entry.is_file()):
            raise BundleError(f"nonregular source: {entry.relative_to(root)}")
        if entry.is_file():
            files.append(entry)
    if not files:
        raise BundleError(f"empty source: {source}")
    return files


def load_bundle(root: Path) -> Bundle:
    root = root.resolve()
    manifest = safe_source(root, "bundle.toml")
    try:
        data = _mapping(
            tomllib.loads(manifest.read_text()), {"schema", "name", "version", "assets", "presets"}, "bundle"
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
    assets = []
    ids: set[str] = set()
    for raw in raw_assets:
        item = _mapping(raw, {"id", "kind", "source", "variants"}, "asset")
        asset_id = _slug(item.get("id"), "asset.id")
        if asset_id in ids:
            raise BundleError(f"duplicate asset id: {asset_id}")
        ids.add(asset_id)
        kind = item.get("kind")
        if not isinstance(kind, str) or kind not in KINDS:
            raise BundleError(f"unknown asset kind: {kind}")
        if ("source" in item) == ("variants" in item):
            raise BundleError(f"{asset_id}: declare exactly one of source or variants")
        sources = []
        if "source" in item:
            pairs = {"common": item["source"]}
        else:
            pairs = item["variants"]
            if not isinstance(pairs, dict) or not pairs:
                raise BundleError(f"{asset_id}: variants must be a nonempty table")
        for target, source in sorted(pairs.items()):
            _slug(target, "variant")
            if "variants" in item and target == "common":
                raise BundleError("common is reserved for shared sources")
            path = safe_source(root, source)
            source_files(root, source)
            if kind == "skill" and (not path.is_dir() or not (path / "SKILL.md").is_file()):
                raise BundleError(f"{asset_id}: skill source must contain SKILL.md")
            sources.append((target, source))
        assets.append(Asset(asset_id, kind, tuple(sources)))
    raw_presets = data.get("presets", {})
    if not isinstance(raw_presets, dict):
        raise BundleError("presets: expected a table")
    presets = {}
    for preset, raw in raw_presets.items():
        _slug(preset, "preset")
        item = _mapping(raw, {"assets"}, f"preset {preset}")
        selected = item.get("assets")
        if not isinstance(selected, list) or not selected or not all(isinstance(v, str) for v in selected):
            raise BundleError(f"{preset}: assets must be a nonempty string array")
        if len(set(selected)) != len(selected) or set(selected) - ids:
            raise BundleError(f"{preset}: duplicate or unknown asset selection")
        presets[preset] = tuple(selected)
    bundle = Bundle(root, name, version, tuple(assets), presets)
    if bundle.constitution is not None:
        try:
            bundle.constitution.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise BundleError("constitution AGENTS.md must be UTF-8") from exc
    return bundle
