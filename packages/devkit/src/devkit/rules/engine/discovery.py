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
The receipt is read with ``devkit.core.receipt``: a receipt that exists but is
malformed is an error as well, never an empty rule set.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from devkit.core import Receipt, ReceiptError, load_receipt

RULE_KIND = "rule"
SYNC_HINT = "run `devkit sync` and commit the receipt"


@dataclass(frozen=True)
class ManagedRules:
    """Rule files to load, in receipt order, and the receipt entries that could not be resolved."""

    paths: tuple[Path, ...] = ()
    errors: tuple[str, ...] = ()


def _from_source(item: str, source_root: Path, receipt: Receipt) -> tuple[Path | None, str | None]:
    candidate = source_root / item
    if not candidate.is_file():
        return None, f"synchronized rule {item} is missing from the working tree; {SYNC_HINT}"
    expected = receipt.file_hash(item)
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
    A receipt that exists but cannot be read or does not match its schema is
    reported in ``errors`` too: running without the rules it records would be
    a false pass.
    """
    try:
        receipt = load_receipt(workspace_root)
    except ReceiptError as exc:
        return ManagedRules(errors=(f"invalid installation receipt: {exc}; {SYNC_HINT}",))
    if receipt is None:
        return ManagedRules()
    paths: list[Path] = []
    errors: list[str] = []
    for asset in receipt.assets(kind=RULE_KIND):
        for item in asset.paths:
            if not item.endswith(".py"):
                continue
            path = workspace_root / item
            if path.is_file():
                paths.append(path)
                continue
            if source_root is None:
                errors.append(f"synchronized rule {item} is missing; {SYNC_HINT}")
                continue
            found, error = _from_source(item, source_root, receipt)
            if found is not None:
                paths.append(found)
            elif error is not None:
                errors.append(error)
    return ManagedRules(tuple(paths), tuple(errors))
