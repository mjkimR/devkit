"""Resolve the instructions and playbooks a rule names as ``related`` to the files agents read.

A rule's guide explains the violation; the judgment or procedure behind it often lives in an instruction or a
playbook of a bundle. A rule names them as ``<bundle>:<asset-id>``; the installation receipt says where each one is
deployed (a project override replaces the managed copy in the receipt), so the path is always the file to read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit.core import ReceiptError, load_receipt
from devkit.rules.engine.errors import RelatedUnresolvedNotice
from devkit.rules.engine.models import Rule

RELATED_KINDS = ("instruction", "playbook")


@dataclass(frozen=True)
class RelatedAsset:
    """``ref`` as the rule names it; ``kind`` and the workspace-relative ``path`` when it is deployed, else ``None``."""

    ref: str
    kind: str | None
    path: str | None

    def to_dict(self) -> dict[str, str | None]:
        return {"ref": self.ref, "kind": self.kind, "path": self.path}


def _entry_file(paths: tuple[str, ...]) -> str | None:
    """The file an agent reads: a playbook directory's ``SKILL.md``, else the first Markdown file."""
    markdown = [path for path in paths if path.endswith(".md")]
    skill = [path for path in markdown if path.endswith("/SKILL.md")]
    return (skill or markdown or [None])[0]


def resolve_related(root: Path, rule: Rule) -> tuple[list[RelatedAsset], list[RelatedUnresolvedNotice]]:
    """Each ``related`` entry of ``rule`` resolved through the receipt, and a notice for each one that is not."""
    refs: tuple[str, ...] = tuple(getattr(rule, "related", ()) or ())
    if not refs:
        return [], []
    try:
        receipt = load_receipt(root)
    except ReceiptError:
        receipt = None
    assets = {(asset.bundle, asset.id): asset for asset in receipt.assets()} if receipt is not None else {}
    resolved: list[RelatedAsset] = []
    notices: list[RelatedUnresolvedNotice] = []
    for ref in refs:
        bundle, _, asset_id = ref.partition(":")
        asset = assets.get((bundle, asset_id))
        path = _entry_file(asset.paths) if asset is not None and asset.kind in RELATED_KINDS else None
        if asset is None or path is None:
            reason = "not deployed" if asset is None else f"a {asset.kind} asset, not an instruction or playbook"
            notices.append(
                RelatedUnresolvedNotice(
                    f"{rule.id}: related {ref} is {reason}",
                    fix=f"devkit add {bundle}" if asset is None else None,
                )
            )
            resolved.append(RelatedAsset(ref, asset.kind if asset else None, None))
        else:
            resolved.append(RelatedAsset(ref, asset.kind, path))
    return resolved, notices
