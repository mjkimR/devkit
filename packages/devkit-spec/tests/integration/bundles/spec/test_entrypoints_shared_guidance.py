"""Shared artifact guidance reflects optional MCP tools without sweep."""

from spec_support.bundle_text import text


def test_local_orchestration_shared_guidance():
    orchestrate = text("skills/spec-orchestrate/SKILL.md")
    assert "shared_put" in orchestrate and "shared_get" in orchestrate and "shared_list" in orchestrate
    assert "shared_sweep" not in orchestrate
    assert "Sweeping and expiration are managed internally" in orchestrate
