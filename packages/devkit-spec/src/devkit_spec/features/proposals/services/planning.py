"""The ``devkit.docs.status_overlay`` extension: how ``devkit docs list`` shows proposals under Planning.

A draft proposal whose ``plan-<slug>`` branch exists is shown as ``reviewing`` with its ``planning_branch``
(01 §5.1). Only the display changes; the base's ``status`` is not written.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from devkit_docs.features.documents import Document, Kind

from devkit_spec.features.policy.repositories.branches import planning_branches


def planning_overlay(root: Path, documents: Sequence[Document]) -> Mapping[str, Mapping[str, str]]:
    """``PROP-<slug> -> {status: reviewing, planning_branch: <ref>}`` for each draft proposal under Planning."""
    drafts = [document for document in documents if document.kind is Kind.PROPOSAL and document.status == "draft"]
    if not drafts:
        return {}
    planning = planning_branches(root)
    return {
        document.id: {"status": "reviewing", "planning_branch": planning[slug]}
        for document in drafts
        if (slug := document.id.removeprefix("PROP-")) in planning
    }
