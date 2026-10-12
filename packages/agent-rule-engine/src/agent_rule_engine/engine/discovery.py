"""Rule files recorded by ``devkit sync`` in ``.devkit/installation.json``.

Bundles ship rules as ``kind = "rule"`` assets. The receipt lists each
deployed file under the asset's ``paths`` (an override under
``.devkit/overrides/`` replaces the managed copy there), so the CLI loads them
without a ``--rules-dir`` flag. Any other file under the asset is ignored.
"""

from __future__ import annotations

import json
from pathlib import Path

RECEIPT_PATH = ".devkit/installation.json"
RULE_KIND = "rule"


def managed_rule_paths(workspace_root: Path) -> list[Path]:
    """Python files of every synchronized rule asset, in receipt order."""
    receipt = workspace_root / RECEIPT_PATH
    if not receipt.is_file():
        return []
    try:
        data = json.loads(receipt.read_text("utf-8"))
    except (OSError, UnicodeError, ValueError):
        return []
    assets = data.get("assets") if isinstance(data, dict) else None
    if not isinstance(assets, list):
        return []
    found: list[Path] = []
    for asset in assets:
        if not isinstance(asset, dict) or asset.get("kind") != RULE_KIND:
            continue
        paths = asset.get("paths")
        if not isinstance(paths, list):
            continue
        for item in paths:
            if isinstance(item, str) and item.endswith(".py"):
                path = workspace_root / item
                if path.is_file():
                    found.append(path)
    return found
