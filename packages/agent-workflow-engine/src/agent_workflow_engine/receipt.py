"""Read-only access to the devkit installation receipt (``.devkit/installation.json``)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RECEIPT_PATH = ".devkit/installation.json"


def receipt_exists(workspace_root: Path) -> bool:
    return (workspace_root / RECEIPT_PATH).is_file()


def receipt_assets(workspace_root: Path, kind: str) -> list[dict[str, Any]]:
    """Asset records of one ``kind`` from the receipt; an unreadable receipt yields none."""
    receipt = workspace_root / RECEIPT_PATH
    if not receipt.is_file():
        return []
    try:
        data = json.loads(receipt.read_text("utf-8"))
    except (OSError, UnicodeError, ValueError):
        return []
    assets = data.get("assets") if isinstance(data, dict) else None
    return [a for a in assets or [] if isinstance(a, dict) and a.get("kind") == kind]


def asset_paths(asset: dict[str, Any], suffix: str) -> list[str]:
    """Workspace-relative paths of one asset record ending in ``suffix``, ``entrypoints`` first."""
    out: list[str] = []
    for key in ("entrypoints", "paths"):
        for rel in asset.get(key) or []:
            if isinstance(rel, str) and rel.endswith(suffix) and rel not in out:
                out.append(rel)
    return out
