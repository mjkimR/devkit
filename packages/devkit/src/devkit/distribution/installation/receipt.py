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
from devkit.core.receipt import MANAGED_PATH, OVERRIDES_PATH, RECEIPT_PATH, Receipt, parse_receipt
from devkit.distribution.bundles.common import AGENT_NAMES
from devkit.distribution.bundles.manifest import seed_target
from devkit.distribution.content import Content, json_content
from devkit.distribution.errors import BundleError
from devkit.distribution.installation.config import parse_presets
from devkit.distribution.installation.results import (
    asset_json,
    overrides_json,
    package_json,
    seeded_json,
    selection_json,
    tool_json,
)
from devkit.distribution.installation.workspace import METADATA, OWNED_PREFIXES, checked_path, owned_path, snapshot


def asset_path_allowed(bundle: str, name: str) -> bool:
    """Whether an asset's recorded path is one devkit writes for ``bundle``: owned, or that bundle's override."""
    return name.startswith(f"{OVERRIDES_PATH}/{bundle}/") or (
        name not in METADATA and name.startswith((f"{MANAGED_PATH}/", ".agents/", ".claude/", ".codex/"))
    )


def read_receipt(root: Path, *, check_disk: bool = True) -> Receipt | None:
    """The validated receipt of ``root``; ``None`` when there is none.

    A malformed receipt, or one that claims paths devkit never writes, is
    ``ReceiptError`` (``RECEIPT_INVALID``); a symlink or non-regular file at a
    recorded path is ``UnsafeWorkspaceError``, unless ``check_disk`` is off for
    a reader that checks each path itself (``devkit status`` reports them).
    """
    content = snapshot(root, RECEIPT_PATH)
    if content is None:
        return None
    receipt = parse_receipt(content.data)
    for name in receipt.file_records:
        if name in METADATA or name.startswith(f"{OVERRIDES_PATH}/"):
            raise ReceiptError(f"{RECEIPT_PATH}: receipt cannot own installation metadata: {name}")
        if not name.startswith(OWNED_PREFIXES):
            raise ReceiptError(f"{RECEIPT_PATH}: files: path outside what devkit owns: {name}")
        if check_disk:
            owned_path(root, name)
    if not set(receipt.selection.agents) <= set(AGENT_NAMES):
        raise ReceiptError(f"{RECEIPT_PATH}: selection.agents: unsupported agent")
    try:
        parse_presets({name: list(values) for name, values in receipt.selection.presets.items()}, "receipt")
        for entry in receipt.seeded:
            seed_target(entry.path, "receipt seeded")
    except (ConfigError, BundleError) as exc:
        raise ReceiptError(f"{RECEIPT_PATH}: {exc.message}") from exc
    for asset in receipt.asset_records:
        for name in (*asset.paths, *asset.entrypoints):
            if not asset_path_allowed(asset.bundle, name):
                raise ReceiptError(f"{RECEIPT_PATH}: invalid asset path: {name}")
            if check_disk:
                checked_path(root, name)
    return receipt


def receipt_json(receipt: Receipt) -> dict[str, Any]:
    """The JSON object devkit writes for ``receipt`` (optional keys only when they carry data)."""
    value: dict[str, Any] = {
        "schema": receipt.schema,
        "packages": [package_json(item) for item in receipt.packages],
        "selection": selection_json(receipt.selection),
        "assets": [asset_json(asset) for asset in receipt.asset_records],
        "files": {
            name: {"sha256": record.sha256, "mode": record.mode} for name, record in receipt.file_records.items()
        },
    }
    if receipt.tool is not None:
        value["tool"] = tool_json(receipt.tool)
    if receipt.overrides:
        value["overrides"] = overrides_json(receipt.overrides)
    if receipt.seeded:
        value["seeded"] = seeded_json(receipt.seeded)
    if receipt.guidance_block is not None:
        value["guidance_block"] = receipt.guidance_block
    return value


def receipt_content(receipt: Receipt) -> Content:
    return json_content(receipt_json(receipt))
