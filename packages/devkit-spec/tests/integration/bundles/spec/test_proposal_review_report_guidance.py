"""Proposal Planning publishes a report before acceptance, and acceptance only consumes it."""

from spec_support.bundle_text import text


def test_review_guidance_uses_the_project_publication_policy() -> None:
    review = text("skills/spec-review-proposal/SKILL.md")
    assert "[PROPOSAL_REVIEW_POLICY: auto_write=...]" in review
    assert "reuse a complete report already bound to the final committed head" in review
    assert "if none exists, do not author or publish it automatically" in review
    assert "Acceptance only validates and consumes the already-published report" in review
    assert "do not compose or publish a report in this step" in review


def test_workflow_requires_publication_before_plan_accept() -> None:
    workflow = text("workflows/sdd-proposal.md")
    assert "publish one source-bound report for the final committed head before requesting acceptance" in workflow
    assert (
        "Acceptance consumes and validates the exact report URI and never composes or publishes another report"
        in workflow
    )
