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
