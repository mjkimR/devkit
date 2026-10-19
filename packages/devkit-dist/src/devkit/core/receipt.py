"""Typed, strict reader for the installation receipt ``.devkit/installation.json``.

``devkit sync`` (``devkit``) writes the receipt; every other
package only reads it, through ``load_receipt``. A receipt that is absent means
"nothing installed" (``None``). A receipt that is present but unusable is a
``ReceiptError``, never an empty result: a consumer that silently skipped a
corrupt receipt would run without the rules, gates or checks it records.

Schema (``schema = 1``)::

    {
      "schema": 1,
      "packages": [{"package", "package_version", "bundle", "bundle_version"}],
      "selection": {"agents": [str], "presets": {bundle: [preset]}},
      "assets": [{"bundle", "id", "kind", "paths": [path],
                  "entrypoints"?: [path], "seeded"?: [path]}],
      "files": {path: {"sha256": hex64, "mode": 0o644 | 0o755}},
      "tool"?: {"package", "version"},
      "overrides"?: {bundle: {asset: {"kind", "relative_path",
                                      "baseline_upstream_sha256", "override_sha256"}}},
      "seeded"?: [{"bundle", "id", "path"}],
      "guidance_block"?: hex64,
      "host_hooks"?: [{"host", "asset", "event", "handler", "command", "matcher", "timeout"}]
    }

Unknown or missing keys, wrong types, duplicate JSON keys and unsafe paths
(see ``devkit.core.paths``; receipt paths must also be canonical) are errors.
Policy that belongs to the writer (which destinations the receipt may own,
which agents exist) is validated by ``devkit``.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

from devkit.advisory import Actor
from devkit.core.errors import AssetFileError, ReceiptError, UnsafePathError
from devkit.core.paths import normalize_relpath, resolve_within
from devkit.core.plugins import PluginPackage, plugin_module_name, plugin_modules

RECEIPT_PATH = ".devkit/installation.json"
SYNC_COMMAND = "devkit sync"  # restores missing managed copies (the fix of a missing asset file)
CONFIG_PATH = ".devkit/config.toml"
MANAGED_PATH = ".devkit/managed"
OVERRIDES_PATH = ".devkit/overrides"
# The guidance block ``devkit sync`` manages in the root ``AGENTS.md`` (its digest is ``guidance_block``).
AGENTS_FILE = "AGENTS.md"
GUIDANCE_START = "<!-- DEVKIT:START -->"
GUIDANCE_END = "<!-- DEVKIT:END -->"
SCHEMA = 1
FILE_MODES = frozenset({0o644, 0o755})

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
_REQUIRED = frozenset({"schema", "packages", "selection", "assets", "files"})
_OPTIONAL = frozenset({"tool", "overrides", "seeded", "guidance_block", "host_hooks"})


@dataclass(frozen=True)
class PackageRecord:
    package: str
    package_version: str
    bundle: str
    bundle_version: str


@dataclass(frozen=True)
class Selection:
    agents: tuple[str, ...]
    presets: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class AssetRecord:
    """One synchronized asset. ``paths`` are the deployed files (an override replaces its managed copy)."""

    bundle: str
    id: str
    kind: str
    paths: tuple[str, ...]
    entrypoints: tuple[str, ...] = ()
    seeded: tuple[str, ...] = ()

    def files(self, suffix: str = "") -> tuple[str, ...]:
        """``entrypoints`` then ``paths`` ending in ``suffix``, without duplicates."""
        out: list[str] = []
        for rel in (*self.entrypoints, *self.paths):
            if rel.endswith(suffix) and rel not in out:
                out.append(rel)
        return tuple(out)


@dataclass(frozen=True)
class FileRecord:
    sha256: str
    mode: int

    def matches(self, data: bytes) -> bool:
        """Whether ``data`` has the recorded SHA-256."""
        return hashlib.sha256(data).hexdigest() == self.sha256


@dataclass(frozen=True)
class ToolRecord:
    package: str
    version: str


@dataclass(frozen=True)
class OverrideRecord:
    kind: str
    relative_path: str
    baseline_upstream_sha256: str
    override_sha256: str


@dataclass(frozen=True)
class SeededRecord:
    bundle: str
    id: str
    path: str


@dataclass(frozen=True)
class HostHookRecord:
    """One owned matcher group in a shared host configuration file; host code defines its rendering."""

    host: str
    asset: str
    event: str
    handler: str
    command: str
    matcher: str
    timeout: int


@dataclass(frozen=True)
class Receipt:
    """A validated receipt. Mappings are read-only views."""

    schema: int
    packages: tuple[PackageRecord, ...]
    selection: Selection
    asset_records: tuple[AssetRecord, ...]
    file_records: Mapping[str, FileRecord]
    tool: ToolRecord | None = None
    overrides: Mapping[str, Mapping[str, OverrideRecord]] = field(default_factory=lambda: MappingProxyType({}))
    seeded: tuple[SeededRecord, ...] = ()
    guidance_block: str | None = None
    host_hooks: tuple[HostHookRecord, ...] = ()

    def assets(self, kind: str | None = None) -> tuple[AssetRecord, ...]:
        """Asset records in receipt order, optionally only those of one ``kind``."""
        if kind is None:
            return self.asset_records
        return tuple(asset for asset in self.asset_records if asset.kind == kind)

    def file(self, path: str) -> FileRecord | None:
        """The ``files`` entry of a workspace-relative path, if the receipt owns it."""
        return self.file_records.get(path)

    def file_hash(self, path: str) -> str | None:
        """The recorded SHA-256 of a workspace-relative path, if the receipt owns it."""
        record = self.file_records.get(path)
        return record.sha256 if record is not None else None


def _fail(where: str, problem: str) -> ReceiptError:
    return ReceiptError(f"{RECEIPT_PATH}: {where}: {problem}")


def _object(value: Any, where: str, required: set[str], optional: frozenset[str] | set[str] = frozenset()) -> dict:
    if not isinstance(value, dict):
        raise _fail(where, "expected an object")
    missing = required - value.keys()
    if missing:
        raise _fail(where, f"missing keys {sorted(missing)}")
    unknown = value.keys() - required - optional
    if unknown:
        raise _fail(where, f"unknown keys {sorted(unknown)}")
    return value


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail(where, "expected a nonempty string")
    return value


def _slug(value: Any, where: str) -> str:
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise _fail(where, "expected a lowercase slug")
    return value


def _sha256(value: Any, where: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise _fail(where, "expected a lowercase hex SHA-256")
    return value


def _list(value: Any, where: str) -> list:
    if not isinstance(value, list):
        raise _fail(where, "expected an array")
    return value


def _strings(value: Any, where: str) -> tuple[str, ...]:
    return tuple(_string(item, f"{where}[{index}]") for index, item in enumerate(_list(value, where)))


def _path(value: Any, where: str) -> str:
    if not isinstance(value, str):
        raise _fail(where, "expected a path string")
    try:
        normalize_relpath(value, canonical=True)
    except UnsafePathError as exc:
        raise _fail(where, f"unsafe path: {exc}") from exc
    return value


def _paths(value: Any, where: str) -> tuple[str, ...]:
    return tuple(_path(item, f"{where}[{index}]") for index, item in enumerate(_list(value, where)))


def _packages(value: Any) -> tuple[PackageRecord, ...]:
    records = []
    for index, item in enumerate(_list(value, "packages")):
        where = f"packages[{index}]"
        item = _object(item, where, {"package", "package_version", "bundle", "bundle_version"})
        records.append(
            PackageRecord(
                package=_string(item["package"], f"{where}.package"),
                package_version=_string(item["package_version"], f"{where}.package_version"),
                bundle=_slug(item["bundle"], f"{where}.bundle"),
                bundle_version=_string(item["bundle_version"], f"{where}.bundle_version"),
            )
        )
    return tuple(records)


def _selection(value: Any) -> Selection:
    value = _object(value, "selection", {"agents", "presets"})
    presets = value["presets"]
    if not isinstance(presets, dict):
        raise _fail("selection.presets", "expected an object")
    return Selection(
        agents=_strings(value["agents"], "selection.agents"),
        presets=MappingProxyType(
            {
                _slug(bundle, "selection.presets"): _strings(names, f"selection.presets.{bundle}")
                for bundle, names in presets.items()
            }
        ),
    )


def _assets(value: Any) -> tuple[AssetRecord, ...]:
    records = []
    for index, item in enumerate(_list(value, "assets")):
        where = f"assets[{index}]"
        item = _object(item, where, {"bundle", "id", "kind", "paths"}, {"entrypoints", "seeded"})
        records.append(
            AssetRecord(
                bundle=_slug(item["bundle"], f"{where}.bundle"),
                id=_slug(item["id"], f"{where}.id"),
                kind=_slug(item["kind"], f"{where}.kind"),
                paths=_paths(item["paths"], f"{where}.paths"),
                entrypoints=_paths(item.get("entrypoints", []), f"{where}.entrypoints"),
                seeded=_paths(item.get("seeded", []), f"{where}.seeded"),
            )
        )
    return tuple(records)


def _files(value: Any) -> Mapping[str, FileRecord]:
    if not isinstance(value, dict):
        raise _fail("files", "expected an object")
    records: dict[str, FileRecord] = {}
    for name, meta in value.items():
        where = f"files.{name}"
        _path(name, "files")
        meta = _object(meta, where, {"sha256", "mode"})
        mode = meta["mode"]
        if type(mode) is not int or mode not in FILE_MODES:
            raise _fail(f"{where}.mode", "expected 420 (0o644) or 493 (0o755)")
        records[name] = FileRecord(_sha256(meta["sha256"], f"{where}.sha256"), mode)
    return MappingProxyType(records)


def _tool(value: Any) -> ToolRecord:
    value = _object(value, "tool", {"package", "version"})
    return ToolRecord(_string(value["package"], "tool.package"), _string(value["version"], "tool.version"))


def _overrides(value: Any) -> Mapping[str, Mapping[str, OverrideRecord]]:
    if not isinstance(value, dict):
        raise _fail("overrides", "expected an object")
    result: dict[str, Mapping[str, OverrideRecord]] = {}
    for bundle, assets in value.items():
        _slug(bundle, "overrides")
        if not isinstance(assets, dict):
            raise _fail(f"overrides.{bundle}", "expected an object")
        records: dict[str, OverrideRecord] = {}
        for asset_id, meta in assets.items():
            where = f"overrides.{bundle}.{asset_id}"
            _slug(asset_id, f"overrides.{bundle}")
            meta = _object(meta, where, {"kind", "relative_path", "baseline_upstream_sha256", "override_sha256"})
            records[asset_id] = OverrideRecord(
                kind=_slug(meta["kind"], f"{where}.kind"),
                relative_path=_path(meta["relative_path"], f"{where}.relative_path"),
                baseline_upstream_sha256=_sha256(meta["baseline_upstream_sha256"], f"{where}.baseline_upstream_sha256"),
                override_sha256=_sha256(meta["override_sha256"], f"{where}.override_sha256"),
            )
        result[bundle] = MappingProxyType(records)
    return MappingProxyType(result)


def _seeded(value: Any) -> tuple[SeededRecord, ...]:
    records = []
    for index, item in enumerate(_list(value, "seeded")):
        where = f"seeded[{index}]"
        item = _object(item, where, {"bundle", "id", "path"})
        records.append(
            SeededRecord(
                bundle=_slug(item["bundle"], f"{where}.bundle"),
                id=_slug(item["id"], f"{where}.id"),
                path=_path(item["path"], f"{where}.path"),
            )
        )
    return tuple(records)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError(f"{RECEIPT_PATH}: duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(name: str) -> Any:
    raise ReceiptError(f"{RECEIPT_PATH}: {name} is not valid JSON")


def parse_receipt(raw: bytes | str) -> Receipt:
    """Validate receipt content (the file's bytes or text) and return the typed receipt."""
    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        data = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except UnicodeDecodeError as exc:
        raise ReceiptError(f"{RECEIPT_PATH}: not UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"{RECEIPT_PATH}: invalid JSON: {exc}") from exc
    except RecursionError as exc:
        raise ReceiptError(f"{RECEIPT_PATH}: invalid JSON: nested too deeply") from exc
    data = _object(data, "receipt", set(_REQUIRED), _OPTIONAL)
    schema = data["schema"]
    if type(schema) is not int or schema != SCHEMA:
        raise _fail("schema", f"unsupported receipt schema {schema!r}; expected {SCHEMA}")
    return Receipt(
        schema=schema,
        packages=_packages(data["packages"]),
        selection=_selection(data["selection"]),
        asset_records=_assets(data["assets"]),
        file_records=_files(data["files"]),
        tool=_tool(data["tool"]) if "tool" in data else None,
        overrides=_overrides(data["overrides"]) if "overrides" in data else MappingProxyType({}),
        seeded=_seeded(data["seeded"]) if "seeded" in data else (),
        guidance_block=_sha256(data["guidance_block"], "guidance_block") if "guidance_block" in data else None,
        host_hooks=_host_hooks(data["host_hooks"]) if "host_hooks" in data else (),
    )


def _host_hooks(value: Any) -> tuple[HostHookRecord, ...]:
    records: list[HostHookRecord] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(_list(value, "host_hooks")):
        where = f"host_hooks[{index}]"
        item = _object(item, where, {"host", "asset", "event", "handler", "command", "matcher", "timeout"})
        host = _slug(item["host"], f"{where}.host")
        asset = _string(item["asset"], f"{where}.asset")
        parts = asset.split(":")
        if len(parts) != 2 or not all(_SLUG.fullmatch(part) for part in parts):
            raise _fail(where, "asset must be bundle:asset using lowercase slugs")
        if (host, asset) in seen:
            raise _fail(where, "duplicate host hook asset")
        seen.add((host, asset))
        matcher, timeout = item["matcher"], item["timeout"]
        if not isinstance(matcher, str) or type(timeout) is not int or not 1 <= timeout <= 600:
            raise _fail(where, "matcher must be a string; timeout must be an integer from 1 to 600")
        records.append(
            HostHookRecord(
                host,
                asset,
                _string(item["event"], where),
                _slug(item["handler"], f"{where}.handler"),
                _string(item["command"], where),
                matcher,
                timeout,
            )
        )
    return tuple(records)


def load_receipt(root: Path) -> Receipt | None:
    """Read ``root/.devkit/installation.json``; ``None`` only when it does not exist.

    Raises ``ReceiptError`` when the file exists but cannot be read or does not
    match the schema (including a dangling symlink or a directory in its place).
    """
    path = root / RECEIPT_PATH
    try:
        if not path.exists() and not path.is_symlink():
            return None
        raw = path.read_bytes()
    except OSError as exc:
        raise ReceiptError(f"{RECEIPT_PATH}: cannot be read: {exc}") from exc
    return parse_receipt(raw)


def _asset_file_fix(item: str, asset: AssetRecord) -> str:
    if item.startswith(f"{OVERRIDES_PATH}/"):
        return f"Run `devkit sync` to record the edited override {item}, then commit the receipt"
    return (
        f"Run `devkit sync` to restore {item}, or `devkit override create {asset.bundle}:{asset.id}` "
        "to keep the edit as a project override"
    )


def verified_asset_file(
    root: Path, item: str, receipt: Receipt, asset: AssetRecord, *, source_root: Path | None = None
) -> Path:
    """The file to load for ``item``, one of ``asset.paths``, checked against the receipt.

    The one verification every consumer of receipt-listed code (rules and gates)
    applies before importing a synchronized file:

    - ``item`` must stay inside ``root`` once symlinks are resolved;
    - a file with a ``files`` entry must match its SHA-256; only a project
      override (under ``.devkit/overrides/``) may lack one and is then used as
      it is; any other file without one is refused;
    - ``source_root`` is the working tree a Git snapshot at ``root`` was taken
      from: a file absent from ``root`` (a Git-ignored managed copy) is read
      from there, and only when the receipt records a hash it matches.

    Returns ``root / item`` or ``source_root / item``. A loader must run the
    bytes that were checked, not re-read the file: ``verified_asset_packages``
    passes them on as the package's ``sources``. Raises ``AssetFileError``
    (message ``"<item> <problem>"``) when the file cannot be used, including
    when it cannot be read. A missing file is ``AUTO`` with the fix
    ``devkit sync``, which restores it (a fresh clone or worktree has no
    Git-ignored managed copies); every other problem is ``MAINTENANCE``.
    """
    return _verified_asset_source(root, item, receipt, asset, source_root)[0]


def _verified_asset_source(
    root: Path, item: str, receipt: Receipt, asset: AssetRecord, source_root: Path | None
) -> tuple[Path, bytes]:
    """``verified_asset_file``'s path and the bytes it verified, read once."""
    try:
        resolve_within(root, item)
    except UnsafePathError as exc:
        raise AssetFileError(f"{item} is unsafe: {exc}", target_files=[item]) from exc
    record = receipt.file(item)
    path = root / item
    try:
        if not path.is_file():
            if source_root is None:
                raise AssetFileError(f"{item} is missing", target_files=[item], actor=Actor.TOOL, fix=SYNC_COMMAND)
            try:
                resolve_within(source_root, item)
            except UnsafePathError as exc:
                raise AssetFileError(f"{item} is unsafe in the working tree: {exc}", target_files=[item]) from exc
            path = source_root / item
            if not path.is_file():
                raise AssetFileError(
                    f"{item} is missing from the working tree", target_files=[item], actor=Actor.TOOL, fix=SYNC_COMMAND
                )
            if record is None:
                raise AssetFileError(f"{item} has no hash in the receipt", target_files=[item])
        if record is None and not item.startswith(f"{OVERRIDES_PATH}/"):
            raise AssetFileError(f"{item} has no hash in the receipt", target_files=[item])
        data = path.read_bytes()
        if record is not None and not record.matches(data):
            raise AssetFileError(
                f"{item} differs from the hash in the receipt", target_files=[item], fix=_asset_file_fix(item, asset)
            )
    except OSError as exc:
        raise AssetFileError(f"{item} cannot be read: {exc}", target_files=[item]) from exc
    return path, data


def _asset_source_path(asset: AssetRecord, item: str) -> str:
    """``item`` relative to its bundle: without the ``.devkit/managed/<bundle>/`` or ``.devkit/overrides/<bundle>/`` prefix."""
    for prefix in (f"{MANAGED_PATH}/{asset.bundle}/", f"{OVERRIDES_PATH}/{asset.bundle}/"):
        if item.startswith(prefix):
            return item[len(prefix) :]
    return item


def _common_directory(paths: list[str]) -> tuple[str, ...]:
    """The deepest directory (as parts) containing every one of ``paths``."""
    parents = [PurePosixPath(path).parent.parts for path in paths]
    common = parents[0] if parents else ()
    for parts in parents[1:]:
        length = 0
        while length < min(len(common), len(parts)) and common[length] == parts[length]:
            length += 1
        common = common[:length]
    return common


def verified_asset_packages(
    root: Path, receipt: Receipt, kind: str, *, source_root: Path | None = None
) -> tuple[tuple[PluginPackage, ...], tuple[AssetFileError, ...]]:
    """One plugin package per ``kind`` asset, every module file verified, and the files that cannot be used.

    This is how rules and gates find their
    synchronized code. Each asset's files (``entrypoints`` then ``paths``,
    ``AssetRecord.files``) are taken relative to the asset's source directory:
    the ``.devkit/managed/<bundle>/`` or ``.devkit/overrides/<bundle>/`` prefix
    is removed, then the directory common to all of the asset's paths. Every
    file that is a module there (``devkit.core.plugins.plugin_module_name``:
    not a test file) goes through ``verified_asset_file``, so one package may
    mix project overrides, managed copies and, in a Git snapshot, working-tree
    copies; none is skipped for its name (a ``_helpers.py`` is a module like
    any other). An asset with any unusable module file yields no package, and
    each such file is reported. The package's ``sources`` hold the verified
    bytes, so loading it compiles exactly what was checked, never a file
    changed since or a bytecode cache. The package's ``root`` is the asset's
    directory under the managed root, and its ``key`` names the workspace,
    bundle and asset.
    """
    packages: list[PluginPackage] = []
    errors: list[AssetFileError] = []
    for asset in receipt.assets(kind):
        items = asset.files()
        relative = {item: _asset_source_path(asset, item) for item in items}
        common = _common_directory(list(relative.values()))
        modules: list[tuple[str, Path]] = []
        sources: dict[str, bytes] = {}
        failed = False
        for item in items:
            dotted = plugin_module_name(PurePosixPath(*PurePosixPath(relative[item]).parts[len(common) :]).as_posix())
            if dotted is None:
                continue
            try:
                path, data = _verified_asset_source(root, item, receipt, asset, source_root)
                modules.append((dotted, path))
                sources[dotted] = data
            except AssetFileError as exc:
                errors.append(exc)
                failed = True
        if failed:
            continue
        directory = root / MANAGED_PATH / asset.bundle / PurePosixPath(*common)
        try:
            mapping = plugin_modules(modules)
        except ValueError as exc:
            errors.append(
                AssetFileError(
                    f"{asset.bundle}:{asset.id} {exc}",
                    target_files=list(items),
                    fix=f"Rename the files of {asset.bundle}:{asset.id} so each module has one file",
                )
            )
            continue
        packages.append(
            PluginPackage(
                f"{(root / MANAGED_PATH / asset.bundle).as_posix()}:{asset.id}",
                directory,
                mapping,
                MappingProxyType(sources),
            )
        )
    return tuple(packages), tuple(errors)
