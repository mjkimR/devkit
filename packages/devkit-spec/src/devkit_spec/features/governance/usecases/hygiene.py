"""``devkit.hygiene`` extension: rejected proposals waiting for their cleanup (01 §6.2, ``CAP-DLV-proposal-planning``).

A rejection only sets ``status: rejected`` (the user's reason is in the commit message) and merges the Planning
branch. The later cleanup is the Host's: a rejection ADR outside the proposal directory, referencing the proposal
and the rejection commit, and the deletion of the proposal in the same commit. A whole-workspace ``devkit rules check
--phase hygiene`` calls ``rejected_proposals(root)``, which reports each rejected proposal still in the base as a
``SPEC_PROPOSAL_REJECTED_PENDING`` warning, so the cleanup is not forgotten. A project without the ``spec`` bundle is
left alone.
"""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_agt.features.rules import workflow_ids
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project import read_development_approach

from devkit_spec.base.errors import ProposalRejectedPendingWarning
from devkit_spec.base.units import PROPOSALS


def _anchors(root: Path) -> list[Path]:
    directory = root / PROPOSALS
    if not directory.is_dir():
        return []
    bundles = [path / "proposal.md" for path in directory.glob("PROP-*") if path.is_dir()]
    singles = [path for path in directory.glob("PROP-*.md") if path.is_file()]
    return sorted(path for path in [*bundles, *singles] if path.is_file())


def rejected_proposals(root: Path) -> list[AdvisoryError] | None:
    """One ``SPEC_PROPOSAL_REJECTED_PENDING`` warning per rejected proposal of the base; ``None`` without the bundle."""
    adaptive = read_development_approach(root).approach == "adaptive-dev"
    if not adaptive and not (root / ".devkit" / "managed" / "spec").is_dir():
        return None
    found: list[AdvisoryError] = []
    for anchor in _anchors(root):
        try:
            data = parse(anchor.read_text("utf-8")).data or {}
            if adaptive and not any(w.startswith("sdd-") for w in workflow_ids(data)):
                continue
            status = data.get("status")
        except (FrontmatterError, OSError, UnicodeError):
            continue  # the spec-format rule reports an unreadable proposal
        if status != "rejected":
            continue
        rel = anchor.relative_to(root).as_posix()
        target = rel.removesuffix("/proposal.md")
        found.append(
            ProposalRejectedPendingWarning(
                f"{target} is rejected and waits for its cleanup",
                target_files=[rel],
                fix=f"Find the rejection commit and its reason (git log -1 --format='%H %B' -S'status: rejected' --"
                f" {rel}), write a rejection ADR under docs/decisions/ referencing {target} and that commit, and delete"
                f" {target} in the same commit",
            )
        )
    return [*found, *milestone_members(root)] or None


def milestone_members(root: Path) -> list[AdvisoryError]:
    """Warn from base documents only; branch checks belong to Backlog decisions."""
    from devkit_docs.features.documents import DocumentIndex
    from devkit_docs.features.documents.models.ids import Kind
    from devkit_docs.features.documents.models.model import is_unit_anchor

    from devkit_spec.base.errors import MilestoneDoneUnsettledWarning, MilestoneDroppedUnsettledWarning

    index = DocumentIndex.load(root)
    found: list[AdvisoryError] = []
    for milestone in index.documents:
        if milestone.kind is not Kind.MILESTONE or milestone.status not in {"done", "dropped"}:
            continue
        members = [
            d
            for d in index.documents
            if (
                read_development_approach(root).approach != "adaptive-dev"
                or any(w.startswith("sdd-") for w in workflow_ids(d.frontmatter))
            )
            and is_unit_anchor(d)
            and d.kind is Kind.PROPOSAL
            and isinstance(d.frontmatter.get("milestone"), str)
            and index.canonical_id(d.frontmatter["milestone"].strip()) == milestone.id
            and not (d.kind is Kind.PROPOSAL and d.status.lower() == "rejected")
        ]
        if not members:
            continue
        warning = MilestoneDoneUnsettledWarning if milestone.status == "done" else MilestoneDroppedUnsettledWarning
        found.append(
            warning(
                f"{milestone.id} is {milestone.status} with unsettled members: {', '.join(d.id for d in members)}",
                target_files=[milestone.path, *(d.path for d in members)],
                fix="Review each listed member in Backlog; reassign or clear its milestone, reject a proposal, or complete the outstanding work before closing the milestone",
            )
        )
    return found
