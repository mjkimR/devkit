"""Consolidation budgets guide grouping while retaining fidelity and ordinary completion checks."""

from spec_support.bundle_text import raw


def test_adr_byte_budget_signals_content_size_with_fidelity() -> None:
    body = raw("playbooks/adr-consolidation/SKILL.md")
    assert "`consolidated_max_bytes`" in body and "resolved\n  `max_bytes`" in body
    assert "signal for loaded content size" in body
    assert "preserve every driver, decision, rejected option and consequence" in body
    assert "Never discard retained content to meet a budget" in body
    assert "Fidelity review:" in body
    assert "`uv run devkit rules check` exits `0`" in body
    assert "rules check --phase hygiene" not in body


def test_feedback_budget_does_not_authorize_grouping_changes() -> None:
    body = raw("playbooks/feedback-consolidation/SKILL.md")
    assert "`consolidated_max_bytes`" in body and "resolved\n  `max_bytes`" in body
    assert "preserving every retained outcome and disposition" in body
    assert "separate authorized grouping decision" in body
    assert "never split or discard entries" in body
    assert "Fidelity review:" in body
    assert "`uv run devkit rules check` exits `0`" in body
    assert "rules check --phase hygiene" not in body
