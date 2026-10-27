"""Resolve the instructions and playbooks a rule names as ``related`` to the files agents read.

A rule's guide explains the violation; the judgment or procedure behind it often lives in an instruction or a
playbook of a bundle. A rule names them as ``<bundle>:<asset-id>``; the installation receipt says where each one is
deployed (a project override replaces the managed copy in the receipt), so the path is always the file to read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_core.base.usecase import BaseUseCase
from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.project.repositories.receipt import load_receipt

from devkit_agt.features.rules.models.contracts import Rule
from devkit_agt.features.rules.models.errors import RelatedUnresolvedNotice

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


def _article(word: str) -> str:
    return "an" if word[:1] in "aeiou" else "a"


class ResolveRelatedUseCase(BaseUseCase):
    """Application entrypoint for resolve related."""

    def execute(self, root: Path, rule: Rule) -> tuple[list[RelatedAsset], list[RelatedUnresolvedNotice]]:
        """Each ``related`` entry of ``rule`` resolved through the receipt, and a notice for each one that is not.

        A receipt that cannot be read resolves nothing and is one notice naming the
        receipt's problem and its fix, not one "not deployed" notice per entry.
        """
        refs: tuple[str, ...] = tuple(getattr(rule, "related", ()) or ())
        if not refs:
            return [], []
        try:
            receipt = load_receipt(root)
        except ReceiptError as exc:
            notice = RelatedUnresolvedNotice(
                f"{rule.id}: related {', '.join(refs)} cannot be resolved: ({exc.code}) {exc.message}",
                target_files=list(exc.target_files),
                fix=exc.fix,
            )
            return [RelatedAsset(ref, None, None) for ref in refs], [notice]
        assets = {(asset.bundle, asset.id): asset for asset in receipt.assets()} if receipt is not None else {}
        resolved: list[RelatedAsset] = []
        notices: list[RelatedUnresolvedNotice] = []
        for ref in refs:
            bundle, _, asset_id = ref.partition(":")
            asset = assets.get((bundle, asset_id))
            if asset is None:
                notices.append(
                    RelatedUnresolvedNotice(
                        f"{rule.id}: related {ref} is not deployed", fix=f"uv run devkit add {bundle}"
                    )
                )
                resolved.append(RelatedAsset(ref, None, None))
                continue
            if asset.kind not in RELATED_KINDS:
                reason = f"{_article(asset.kind)} {asset.kind} asset, not an instruction or playbook"
                notices.append(RelatedUnresolvedNotice(f"{rule.id}: related {ref} is {reason}"))
                resolved.append(RelatedAsset(ref, asset.kind, None))
                continue
            path = _entry_file(asset.paths)
            if path is None:
                notices.append(
                    RelatedUnresolvedNotice(
                        f"{rule.id}: related {ref} is {_article(asset.kind)} {asset.kind} asset without a Markdown file",
                        fix=f"Add the {asset.kind}'s Markdown file to {ref} in bundle {bundle}, then run `uv run devkit sync`",
                    )
                )
                resolved.append(RelatedAsset(ref, asset.kind, None))
                continue
            resolved.append(RelatedAsset(ref, asset.kind, path))
        return resolved, notices
