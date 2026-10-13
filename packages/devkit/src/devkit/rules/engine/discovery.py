"""Rule files recorded by ``devkit sync`` in ``.devkit/installation.json``.

Bundles ship rules as ``kind = "rule"`` assets. The receipt lists each
deployed file under the asset's ``entrypoints`` and ``paths`` (an override
under ``.devkit/overrides/`` replaces the managed copy there), so the CLI loads
them without a ``--rules-dir`` flag. Every listed ``.py`` file is loaded,
whatever its name; any other file under the asset is ignored.

Files are found and checked with ``devkit.core.verified_asset_files``, as the
commit gate registry and workflow plugin checks find theirs:

- a file the receipt records under ``files`` must match its SHA-256, so a
  managed rule edited by hand is a load error (``devkit sync`` restores it,
  ``devkit override create`` keeps the edit as a project override); a file
  without a record (a project override) is loaded as it is;
- a listed file that does not exist is an error, never a silent skip: the
  receipt says the rule is installed, so running without it would be a false
  pass.

Git snapshot gates materialize only tracked files, and the managed copies
under ``.devkit/managed/`` are normally Git-ignored. For a snapshot the caller
passes the working tree as ``source_root``; a file missing from the snapshot
is taken from there only when its SHA-256 matches the hash recorded in the
snapshot's receipt, so the committed receipt still pins what the gate runs.
The receipt is read with ``devkit.core.receipt``: a receipt that exists but is
malformed is an error as well, never an empty rule set.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import Actor
from devkit.core import RECEIPT_PATH, AssetFileError, ReceiptError, load_receipt, verified_asset_files
from devkit.rules.engine.errors import SYNC_FIX, RuleLoadError

RULE_KIND = "rule"


@dataclass(frozen=True)
class ManagedRules:
    """Rule files to load, in receipt order, and the receipt entries that could not be resolved."""

    paths: tuple[Path, ...] = ()
    errors: tuple[RuleLoadError, ...] = ()


def _unusable(error: AssetFileError) -> RuleLoadError:
    """The rule-level problem for an unusable rule file; a missing file keeps its ``AUTO`` ``devkit sync`` fix."""
    if error.actor is Actor.TOOL:
        return RuleLoadError(
            f"synchronized rule {error.message}", target_files=error.target_files, actor=Actor.TOOL, fix=error.fix
        )
    fix = SYNC_FIX if error.fix == AssetFileError.fix else error.fix
    return RuleLoadError(f"synchronized rule {error.message}", target_files=error.target_files, fix=fix)


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
        return ManagedRules(
            errors=(RuleLoadError(f"invalid installation receipt: {exc}", target_files=[RECEIPT_PATH], fix=exc.fix),)
        )
    if receipt is None:
        return ManagedRules()
    paths, errors = verified_asset_files(workspace_root, receipt, RULE_KIND, source_root=source_root)
    return ManagedRules(paths, tuple(_unusable(error) for error in errors))
