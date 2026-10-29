"""Shared artifact guidance reflects optional MCP tools without sweep."""

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text


def test_local_orchestration_shared_guidance():
    orchestrate = text("skills/spec-orchestrate/SKILL.md")
    assert "shared_put" in orchestrate and "shared_get" in orchestrate and "shared_list" in orchestrate
    assert "shared_sweep" not in orchestrate
    assert_rule(raw("skills/spec-orchestrate/SKILL.md"), "`shared_put`", "sweeping", "expiration", "internally")
