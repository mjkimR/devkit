"""``bundle.toml`` schema 1: load and validate a bundle source directory."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from devkit_core.base.errors import UnsafePathError
from devkit_core.core.paths import normalize_relpath
from devkit_core.core.plugins import PluginPackage, check_plugin_modules

from devkit.distribution.bundles.common import AGENT_NAMES, ALL, SHARED_SKILL_AGENTS, SLUG, VERSION, locate_frontmatter
from devkit.distribution.bundles.fragments import read_fragment, references
from devkit.distribution.bundles.instructions import read_instruction_header
from devkit.distribution.bundles.invocation import INVOCATIONS, check_skill_source, skill_entry
from devkit.distribution.bundles.playbooks import playbook_entry, read_playbook_header
from devkit.distribution.bundles.subagents import HOST_FILES, read_contract, subagent_entry
from devkit.distribution.bundles.templates import TEMPLATE_KINDS, Variable, declarations, output_path
from devkit.distribution.bundles.workflows import read_workflow_header, workflow_entry
from devkit.distribution.content import normal_mode
from devkit.distribution.errors import BundleError, SelectionError
from devkit.host import HookDefinitionError, read_hook

KINDS = frozenset(
    {
        "skill",
        "subagent",
        "instruction",
        "playbook",
        "rule",
        "workflow",
        "gate",
        "document",
        "guidance",
        "hook",
    }
)
# The kinds whose source is a plugin package directory of Python modules (``devkit_core.core.plugins``).
PLUGIN_KINDS = frozenset({"rule", "gate"})
# The kinds projected into agent directories (agent-projections.md); only they may ship per-agent ``variants``.
VARIANT_KINDS = frozenset({"skill", "subagent"})
# The entry skills ``devkit sync`` generates next to synchronized playbooks and workflows.
RESERVED_SKILL_IDS = frozenset({"devkit-playbook", "devkit-workflow"})
# Workspace roots a seeded target may never enter: devkit's own state, Git, agent projections
# and the root guidance file are owned by devkit, the host or the project in other ways.
# Compared case-insensitively: on a case-insensitive file system ``.GIT`` is ``.git``.
SEED_FORBIDDEN_ROOTS = frozenset({".devkit", ".git", ".agents", ".claude", ".codex"})
SEED_FORBIDDEN_FILES = frozenset({"agents.md"})
# By-products of editing a source in place (Finder metadata, bytecode caches); never bundle content.
IGNORED_NAMES = frozenset({".DS_Store", "__pycache__"})
IGNORED_SUFFIXES = (".pyc",)


@dataclass(frozen=True)
class Asset:
    id: str
    kind: str
    sources: tuple[tuple[str, str], ...]
    # ``seeded`` assets are written once to ``target`` (workspace-relative) and then project-owned.
    seeded: bool = False
    target: str | None = None
    # Who starts a skill: ``auto`` (the agent on its own) or ``user`` (explicit invocation only); see ``invocation``.
    invocation: str = "auto"


@dataclass(frozen=True)
class Bundle:
    root: Path
    name: str
    version: str
    assets: tuple[Asset, ...]
    presets: dict[str, tuple[str, ...]]
    default_preset: str | None = None
    # Selected without ``devkit add`` (with ``default_preset``) once its package is installed, for any package;
    # ``<bundle> = false`` in ``.devkit/config.toml`` opts out.
    auto_select: bool = False
    variables: dict[str, Variable] = field(default_factory=dict)

    @property
    def preset_names(self) -> list[str]:
        return [ALL, *sorted(self.presets)]

    def asset(self, asset_id: str) -> Asset | None:
        return next((asset for asset in self.assets if asset.id == asset_id), None)

    def single_file_source(self, asset_id: str) -> str | None:
        """The one source file of a deployed, non-guidance asset: what a ``{path:<asset-id>}`` placeholder may name."""
        asset = self.asset(asset_id)
        if asset is None or asset.kind == "guidance" or asset.seeded or len(asset.sources) != 1:
            return None
        ((variant, source),) = asset.sources
        return source if variant == "common" and (self.root / source).is_file() else None

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
        sources = [
            name
            for name in ("AGENTS.md", "AGENTS.md.jinja")
            if (self.root / name).exists() or (self.root / name).is_symlink()
        ]
        if len(sources) > 1:
            raise BundleError("constitution AGENTS.md and AGENTS.md.jinja collide")
        if not sources:
            return None
        path = safe_source(self.root, sources[0])
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

    ``devkit_core.core.paths`` accepts a backslash as a file-name character; an
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
    if (
        rel.parts[0].casefold() in SEED_FORBIDDEN_ROOTS
        or value.casefold() in SEED_FORBIDDEN_FILES
        # A nested repository's ``.git`` (hooks, config) is as much Git's as the workspace's own.
        or any(part.casefold() == ".git" for part in rel.parts)
    ):
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


def _check_plugin_package(asset_id: str, kind: str, source: str, path: Path) -> None:
    """A rule, gate or workflow check is a directory whose modules import by their dotted names."""
    if not path.is_dir():
        raise BundleError(
            f"{asset_id}: a {kind} asset's source must be a plugin package directory, not a file: {source}",
            fix=f"Move {source} into a directory (for example {PurePosixPath(source).with_suffix('')}/) "
            "and set source to that directory",
        )
    try:
        package = PluginPackage.from_directory(path)
        check_plugin_modules(package.modules)
    except ValueError as exc:
        raise BundleError(f"{asset_id}: invalid plugin package {source}: {exc}") from exc
    if not package.modules:
        raise BundleError(f"{asset_id}: plugin package {source} contains no Python module")


def _check_source(root: Path, asset_id: str, kind: str, variant: str, source: str) -> None:
    """Validate the kind-specific content of one source, as every agent projection will read it."""
    path = safe_source(root, source)
    files = source_files(root, source)
    templates = [file for file in files if file.name.endswith(".jinja")]
    if templates:
        if (
            kind not in TEMPLATE_KINDS
            or (kind == "subagent" and variant != "common")
            or any(not file.name.endswith(".md.jinja") for file in templates)
        ):
            raise BundleError(
                f"{asset_id}: templates require .md.jinja instruction, guidance, document or skill sources"
            )
        if kind == "guidance" and not path.is_file():
            raise BundleError(f"{asset_id}: guidance source must be one file")
        if kind == "subagent":
            subagent_entry(root, source)
        if path.is_file() and kind != "skill":
            return
    if kind == "skill":
        entry = skill_entry(path, f"{asset_id}/{source}")
        # Sync inserts the context prerequisite after the frontmatter, which must therefore be well-formed.
        if entry.name == "SKILL.md":
            locate_frontmatter(entry.read_bytes(), f"{asset_id}/{source}/SKILL.md", "skill")
        check_skill_source(path, f"{asset_id}/{source}")
    if kind in PLUGIN_KINDS:
        _check_plugin_package(asset_id, kind, source, path)
    if kind == "hook":
        if not path.is_file() or path.suffix != ".toml":
            raise BundleError(f"{asset_id}: hook source must be one .toml file")
        try:
            read_hook(path.read_bytes(), f"{asset_id}/{source}")
        except HookDefinitionError as exc:
            raise BundleError(exc.message, target_files=exc.target_files, fix=exc.fix) from exc
    if kind == "instruction":
        for file in files:
            if file.name.endswith(".md.jinja"):
                continue
            read_instruction_header(file.read_bytes(), f"{asset_id}/{file.relative_to(root).as_posix()}")
    if kind == "playbook":
        read_playbook_header(playbook_entry(root, source).read_bytes(), f"{asset_id}/{source}")
    if kind == "workflow":
        read_workflow_header(workflow_entry(root, source).read_bytes(), f"{asset_id}/{source}")
    if kind == "guidance":
        if not path.is_file():
            raise BundleError(f"{asset_id}: guidance source must be one file")
        read_fragment(path.read_bytes(), f"{asset_id}/{source}")
    if kind == "subagent" and variant == "common":
        read_contract(subagent_entry(root, source).read_bytes(), f"{asset_id}/{source}", asset_id)
    elif kind == "subagent" and (not path.is_file() or path.suffix != HOST_FILES[variant]):
        raise BundleError(f"{asset_id}/{source}: the {variant} subagent variant must be one {HOST_FILES[variant]} file")


def _tree(root: Path, source: str) -> list[tuple[str, bytes, int]]:
    """Each file of a source by relative path, with its bytes and normalized mode."""
    base = root / source
    return [
        (path.relative_to(base).as_posix(), path.read_bytes(), normal_mode(path.stat().st_mode))
        for path in source_files(root, source)
    ]


def _asset(root: Path, raw: Any) -> Asset:
    item = _mapping(raw, {"id", "kind", "source", "variants", "seeded", "target", "invocation"}, "asset")
    asset_id = _slug(item.get("id"), "asset.id")
    kind = item.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        raise BundleError(f"unknown asset kind: {kind}")
    if ("source" in item) == ("variants" in item):
        raise BundleError(f"{asset_id}: declare exactly one of source or variants")
    if kind == "skill" and asset_id in RESERVED_SKILL_IDS:
        raise BundleError(f"{asset_id}: skill id is reserved for the entry skill devkit sync generates")
    seeded = item.get("seeded", False)
    if type(seeded) is not bool:
        raise BundleError(f"{asset_id}: seeded must be a boolean")
    if seeded and kind != "document":
        raise BundleError(f"{asset_id}: only document assets can be seeded")
    if "variants" in item and kind not in VARIANT_KINDS:
        raise BundleError(
            f"{asset_id}: only skill and subagent assets declare variants; a {kind} asset declares a single source"
        )
    if ("target" in item) != seeded:
        raise BundleError(f"{asset_id}: target is required for seeded assets and not allowed otherwise")
    target_path = seed_target(item["target"], asset_id) if seeded else None
    invocation = item.get("invocation", "auto")
    if "invocation" in item and kind != "skill":
        raise BundleError(f"{asset_id}: only skill assets declare invocation")
    if invocation not in INVOCATIONS:
        raise BundleError(f"{asset_id}: invocation must be one of {list(INVOCATIONS)}")
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
        try:
            _check_source(root, asset_id, kind, variant, source)
        except OSError as exc:
            raise BundleError(f"{asset_id}: cannot read source {source}: {exc}") from exc
        sources.append((variant, source))
    shared = [pairs[agent] for agent in SHARED_SKILL_AGENTS if agent in pairs]
    if kind == "skill" and len(shared) == 2 and _tree(root, shared[0]) != _tree(root, shared[1]):
        raise BundleError(
            f"{asset_id}: codex and antigravity skill variants project to the same .agents/skills directory"
            " and must be identical"
        )
    return Asset(asset_id, kind, tuple(sources), seeded, target_path, invocation)


def _check_fragment_references(bundle: Bundle) -> None:
    """Every ``{path:<asset-id>}`` names a single-file asset that each preset selecting the fragment selects too."""
    for asset in bundle.assets:
        if asset.kind != "guidance":
            continue
        ((_, source),) = asset.sources
        if source.endswith(".md.jinja"):
            continue  # Final references and fragment limits are checked after project rendering.
        named = references(read_fragment((bundle.root / source).read_bytes(), f"{asset.id}/{source}"))
        for ref in named:
            if bundle.single_file_source(ref) is None:
                raise BundleError(
                    f"{asset.id}: {{path:{ref}}} must name a single-file, non-guidance asset of the bundle"
                )
        for preset, selected in bundle.presets.items():
            if asset.id in selected and (missing := [ref for ref in named if ref not in selected]):
                raise BundleError(f"{preset}: selects guidance {asset.id} without the assets it names: {missing}")


def _check_workflow_ids(bundle: Bundle) -> None:
    """Workflow definitions are found by their header ``id``: two assets of one bundle may not share it."""
    seen: dict[str, str] = {}
    for asset in bundle.assets:
        if asset.kind != "workflow":
            continue
        ((_, source),) = asset.sources
        header = read_workflow_header(workflow_entry(bundle.root, source).read_bytes(), f"{asset.id}/{source}")
        if header.id in seen:
            raise BundleError(f"{asset.id}: workflow id {header.id!r} is already declared by asset {seen[header.id]}")
        seen[header.id] = asset.id


def load_bundle(root: Path) -> Bundle:
    """Load and validate the bundle source directory ``root``.

    Every ``BundleError`` names the bundle directory under ``target_files``.
    """
    root = root.resolve()
    try:
        return _load(root)
    except OSError as exc:
        raise BundleError(f"cannot read bundle source: {exc}", target_files=[str(root)]) from exc
    except BundleError as exc:
        if not exc.target_files:
            exc.target_files = (str(root),)
        raise


def _load(root: Path) -> Bundle:
    if not root.is_dir():
        raise BundleError(f"bundle source must be a directory containing bundle.toml: {root}")
    manifest = safe_source(root, "bundle.toml")
    try:
        data = _mapping(
            tomllib.loads(manifest.read_text("utf-8")),
            {"schema", "name", "version", "assets", "presets", "default_preset", "auto_select", "variables"},
            "bundle",
        )
    except (OSError, UnicodeError, RecursionError, tomllib.TOMLDecodeError) as exc:
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
    auto_select = data.get("auto_select", False)
    if type(auto_select) is not bool:
        raise BundleError("auto_select must be a boolean")
    if auto_select and default_preset is None:
        raise BundleError("auto_select requires default_preset")
    bundle = Bundle(
        root,
        name,
        version,
        tuple(assets),
        presets,
        default_preset,
        auto_select,
        declarations(data.get("variables", {})),
    )
    destinations: dict[str, str] = {"bundle.toml": "bundle.toml"}
    if bundle.constitution is not None:
        destinations["AGENTS.md"] = "AGENTS.md"
    for asset in assets:
        for _, source in asset.sources:
            for file in source_files(root, source):
                rel = file.relative_to(root).as_posix()
                dest = output_path(rel)
                previous = destinations.setdefault(dest, rel)
                if previous != rel:
                    raise BundleError(f"template destination collision: {previous} and {rel}")
    for destination, source in destinations.items():
        for parent in PurePosixPath(destination).parents:
            if parent.as_posix() in destinations:
                raise BundleError(f"template destination collision: {destinations[parent.as_posix()]} and {source}")
    _check_fragment_references(bundle)
    _check_workflow_ids(bundle)
    if bundle.constitution is not None:
        try:
            bundle.constitution.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise BundleError("constitution AGENTS.md must be UTF-8") from exc
    return bundle
