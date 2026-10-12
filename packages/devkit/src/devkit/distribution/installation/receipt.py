"""The installation receipt as its writer sees it: strict reading plus devkit's ownership policy, and serialization.

``devkit.core.receipt`` owns the schema and the typed model every package
reads. This module adds what only the writer knows (which destinations the
receipt may own, which agents and asset paths are valid) and turns the model
back into the JSON devkit writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devkit.core.errors import ConfigError, ReceiptError
from devkit.core.receipt import (
    AssetRecord,
    FileRecord,
    OverrideRecord,
    PackageRecord,
    Receipt,
    SeededRecord,
    Selection,
    ToolRecord,
    parse_receipt,
)

from ..bundles.common import AGENT_NAMES
from ..bundles.manifest import seed_target
from ..errors import BundleError
from .config import parse_presets
from .results import asset_json, package_json
from .transaction import json_content
from .workspace import (
    MANAGED,
    METADATA,
    OVERRIDES,
    OWNED_PREFIXES,
    RECEIPT,
    Content,
    checked_path,
    owned_path,
    snapshot,
)

__all__ = [
    "AssetRecord",
    "FileRecord",
    "OverrideRecord",
    "PackageRecord",
    "Receipt",
    "SeededRecord",
    "Selection",
    "ToolRecord",
    "read_receipt",
    "receipt_content",
    "receipt_json",
]


def asset_path_allowed(bundle: str, name: str) -> bool:
    """Whether an asset's recorded path is one devkit writes for ``bundle``: owned, or that bundle's override."""
    return name.startswith(f"{OVERRIDES}/{bundle}/") or (
        name not in METADATA and name.startswith((f"{MANAGED}/", ".agents/", ".claude/", ".codex/"))
    )


def read_receipt(root: Path) -> Receipt | None:
    """The validated receipt of ``root``; ``None`` when there is none.

    A malformed receipt, or one that claims paths devkit never writes, is
    ``ReceiptError`` (``RECEIPT_INVALID``); a symlink or non-regular file at a
    recorded path is ``UnsafeWorkspaceError``.
    """
    content = snapshot(root, RECEIPT)
    if content is None:
        return None
    receipt = parse_receipt(content.data)
    for name in receipt.file_records:
        if name in METADATA or name.startswith(f"{OVERRIDES}/"):
            raise ReceiptError(f"{RECEIPT}: receipt cannot own installation metadata: {name}")
        if not name.startswith(OWNED_PREFIXES):
            raise ReceiptError(f"{RECEIPT}: files: path outside what devkit owns: {name}")
        owned_path(root, name)
    if not set(receipt.selection.agents) <= set(AGENT_NAMES):
        raise ReceiptError(f"{RECEIPT}: selection.agents: unsupported agent")
    try:
        parse_presets({name: list(values) for name, values in receipt.selection.presets.items()}, "receipt")
        for entry in receipt.seeded:
            seed_target(entry.path, "receipt seeded")
    except (ConfigError, BundleError) as exc:
        raise ReceiptError(f"{RECEIPT}: {exc.message}") from exc
    for asset in receipt.asset_records:
        for name in (*asset.paths, *asset.entrypoints):
            if not asset_path_allowed(asset.bundle, name):
                raise ReceiptError(f"{RECEIPT}: invalid asset path: {name}")
            checked_path(root, name)
    return receipt


def receipt_json(receipt: Receipt) -> dict[str, Any]:
    """The JSON object devkit writes for ``receipt`` (optional keys only when they carry data)."""
    value: dict[str, Any] = {
        "schema": receipt.schema,
        "packages": [package_json(item) for item in receipt.packages],
        "selection": {
            "agents": list(receipt.selection.agents),
            "presets": {name: list(values) for name, values in receipt.selection.presets.items()},
        },
        "assets": [asset_json(asset) for asset in receipt.asset_records],
        "files": {
            name: {"sha256": record.sha256, "mode": record.mode} for name, record in receipt.file_records.items()
        },
    }
    if receipt.tool is not None:
        value["tool"] = {"package": receipt.tool.package, "version": receipt.tool.version}
    if receipt.overrides:
        value["overrides"] = {
            bundle: {
                asset_id: {
                    "kind": record.kind,
                    "relative_path": record.relative_path,
                    "baseline_upstream_sha256": record.baseline_upstream_sha256,
                    "override_sha256": record.override_sha256,
                }
                for asset_id, record in assets.items()
            }
            for bundle, assets in receipt.overrides.items()
        }
    if receipt.seeded:
        value["seeded"] = [{"bundle": item.bundle, "id": item.id, "path": item.path} for item in receipt.seeded]
    if receipt.guidance_block is not None:
        value["guidance_block"] = receipt.guidance_block
    return value


def receipt_content(receipt: Receipt) -> Content:
    return json_content(receipt_json(receipt))
