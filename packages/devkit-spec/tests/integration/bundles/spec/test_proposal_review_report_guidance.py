"""Proposal review guidance verifies committed proposal without shared artifact report."""

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text


def test_review_guidance_inspects_committed_proposal() -> None:
    review = text("skills/spec-review-proposal/SKILL.md")
    assert "[PROPOSAL_REVIEW_POLICY: auto_write=...]" not in review
    assert "--report-uri" not in review
    assert_rule(
        raw("skills/spec-review-proposal/SKILL.md"),
        "read the proposal, every padr and the envelopes",
        "committed source",
    )
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
    assert_rule(
        raw("skills/spec/references/completion.md"),
        "stale source invalidates the old request",
        "partial state",
        "authorize only the remaining effects",
        "preserving the source sha, authority and recovery state",
    )
