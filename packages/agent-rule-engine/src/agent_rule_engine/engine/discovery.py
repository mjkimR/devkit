"""Rule files recorded by ``devkit sync`` in ``.devkit/installation.json``.

Bundles ship rules as ``kind = "rule"`` assets. The receipt lists each
deployed file under the asset's ``paths`` (an override under
``.devkit/overrides/`` replaces the managed copy there), so the CLI loads them
without a ``--rules-dir`` flag. Any other file under the asset is ignored.

A listed file that does not exist is an error, never a silent skip: the
receipt says the rule is installed, so running without it would be a false
pass. Git snapshot gates materialize only tracked files, and the managed copies
under ``.devkit/managed/`` are normally Git-ignored. For a snapshot the caller
passes the working tree as ``source_root``; a file missing from the snapshot
is taken from there only when its SHA-256 matches the hash recorded in the
snapshot's receipt, so the committed receipt still pins what the gate runs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

RECEIPT_PATH = ".devkit/installation.json"
RULE_KIND = "rule"
SYNC_HINT = "run `devkit sync` and commit the receipt"


@dataclass(frozen=True)
class ManagedRules:
    """Rule files to load, in receipt order, and the receipt entries that could not be resolved."""

    paths: tuple[Path, ...] = ()
    errors: tuple[str, ...] = ()


def _rule_entries(workspace_root: Path) -> tuple[list[str], dict[str, str]]:
    """``.py`` paths of every rule asset and the receipt's ``files`` hashes; empty without a usable receipt."""
    receipt = workspace_root / RECEIPT_PATH
    if not receipt.is_file():
        return [], {}
    try:
        data = json.loads(receipt.read_text("utf-8"))
    except (OSError, UnicodeError, ValueError):
        return [], {}
    if not isinstance(data, dict):
        return [], {}
    assets = data.get("assets")
    entries: list[str] = []
    if isinstance(assets, list):
        for asset in assets:
            if not isinstance(asset, dict) or asset.get("kind") != RULE_KIND:
                continue
            paths = asset.get("paths")
            if not isinstance(paths, list):
                continue
            entries.extend(item for item in paths if isinstance(item, str) and item.endswith(".py"))
    hashes: dict[str, str] = {}
    files = data.get("files")
    if isinstance(files, dict):
        for name, meta in files.items():
            if isinstance(name, str) and isinstance(meta, dict) and isinstance(meta.get("sha256"), str):
                hashes[name] = meta["sha256"]
    return entries, hashes


def _from_source(item: str, source_root: Path, hashes: dict[str, str]) -> tuple[Path | None, str | None]:
    candidate = source_root / item
    if not candidate.is_file():
        return None, f"synchronized rule {item} is missing from the working tree; {SYNC_HINT}"
    expected = hashes.get(item)
    if expected is None:
        return None, f"synchronized rule {item} has no hash in the receipt; {SYNC_HINT}"
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected:
        return None, f"synchronized rule {item} differs from the hash in the receipt; {SYNC_HINT}"
    return candidate, None


def resolve_managed_rules(workspace_root: Path, *, source_root: Path | None = None) -> ManagedRules:
    """Python files of every synchronized rule asset, in receipt order.

    ``source_root`` is the working tree a Git snapshot was taken from. Files
    absent from ``workspace_root`` are read from there when their content
    matches the hash in the receipt; otherwise they are reported in ``errors``.
    """
    entries, hashes = _rule_entries(workspace_root)
    paths: list[Path] = []
    errors: list[str] = []
    for item in entries:
        path = workspace_root / item
        if path.is_file():
            paths.append(path)
            continue
        if source_root is None:
            errors.append(f"synchronized rule {item} is missing; {SYNC_HINT}")
            continue
        found, error = _from_source(item, source_root, hashes)
        if found is not None:
            paths.append(found)
        elif error is not None:
            errors.append(error)
    return ManagedRules(tuple(paths), tuple(errors))
