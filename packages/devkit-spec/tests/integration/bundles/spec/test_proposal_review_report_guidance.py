"""Proposal review guidance verifies committed proposal without shared artifact report."""

from spec_support.bundle_text import text


def test_review_guidance_inspects_committed_proposal() -> None:
    review = text("skills/spec-review-proposal/SKILL.md")
    assert "[PROPOSAL_REVIEW_POLICY: auto_write=...]" not in review
    assert "--report-uri" not in review
    assert "Read the proposal, every PADR and the envelopes" in review
    assert "devkit spec proposal accept" in review


def test_workflow_does_not_require_shared_report_publication() -> None:
    workflow = text("workflows/sdd-proposal.md")
    assert "publish one source-bound report" not in workflow
    assert "Acceptance consumes and validates the exact report URI" not in workflow
    assert "devkit spec proposal accept" in workflow


def test_stale_recovery_guidance_preserves_no_report() -> None:
    completion = text("skills/spec/references/completion.md")
    assert "report URI" not in completion
    assert "A stale source or report" not in completion
    assert (
        "A stale source invalidates the old request: inspect the partial state and authorize only the remaining "
        "effects, preserving the source SHA, authority and recovery state."
    ) in completion
