"""Eligibility and deterministic messages for an explicitly selected envelope."""

from __future__ import annotations

import re

from devkit_agt.features.workflow.models.envelope import Envelope
from devkit_agt.features.workflow.models.errors import EnvelopeCommitInvalidError


def commit_message(anchor_id: str, envelope: Envelope) -> tuple[str, str]:
    """Derive identity from a tracked anchor, never from a branch name."""
    match = re.fullmatch(r"(?:SPEC|PROP)-([a-z0-9][a-z0-9-]*)", anchor_id)
    if match is None:
        raise EnvelopeCommitInvalidError(
            f"unsupported anchor id {anchor_id!r}",
            fix="Use a tracked SPEC-<slug> or PROP-<slug> anchor, or commit this record manually",
        )
    subject = f"chore(workflow): record {match[1]} {envelope.kind}-{envelope.seq:02d}"
    body = f"workflow: {envelope.workflow}\nsegment: {envelope.segment}\nstage: {envelope.stage}"
    return subject, body


def require_authored(envelope: Envelope, workflow: str, segment: int, stages: set[str]) -> None:
    """A summary and exact current identity exclude unfilled skeletons and stale segments."""
    if (
        not envelope.summary.strip()
        or envelope.stage not in stages
        or envelope.workflow != workflow
        or envelope.segment != segment
    ):
        raise EnvelopeCommitInvalidError(
            "envelope needs a nonempty summary, a declared stage and the current workflow/segment",
            target_files=[envelope.file],
            fix="Finish this existing envelope with its current Unit identity, or commit it manually",
        )
