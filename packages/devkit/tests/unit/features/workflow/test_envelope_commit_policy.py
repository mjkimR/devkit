"""Message identity is independent of Git branch naming and safely bounded by anchor IDs."""

from __future__ import annotations

import pytest
from devkit_agt.features.workflow.models.errors import EnvelopeCommitInvalidError
from devkit_agt.features.workflow.services.envelope.commit import commit_message
from devkit_agt.features.workflow.services.envelope.model import parse_envelope_text


@pytest.mark.parametrize("prefix", ["SPEC", "PROP"])
@pytest.mark.parametrize("seq", [1, 100])
def test_message_uses_only_anchor_and_record_identity(prefix: str, seq: int) -> None:
    name = f"final-report-{seq:02d}.yaml"
    envelope = parse_envelope_text(
        name,
        f"envelopes/{name}",
        "kind: final-report\nstatus: completed\nsummary: Ready\nworkflow: w\nsegment: 2\nstage: report\n",
    )
    assert commit_message(f"{prefix}-example", envelope) == (
        f"chore(workflow): record example final-report-{seq:02d}",
        "workflow: w\nsegment: 2\nstage: report",
    )


@pytest.mark.parametrize("anchor", ["custom", "SPEC-", "SPEC-two words", "SPEC-x\nmalicious", "SPEC-../escape"])
def test_unsupported_anchor_ids_refuse(anchor: str) -> None:
    envelope = parse_envelope_text("review-01.yaml", "envelopes/review-01.yaml", "kind: review\nstatus: completed\n")
    with pytest.raises(EnvelopeCommitInvalidError) as refused:
        commit_message(anchor, envelope)
    assert refused.value.fix is not None
    assert "git commit" in refused.value.fix and "<" not in refused.value.fix
