"""Shared artifact guidance preserves the explicit connection precondition."""

from spec_support.bundle_text import text


def test_local_orchestration_requires_project_connection():
    orchestrate = text("skills/spec-orchestrate/SKILL.md")
    assert "shared_put" in orchestrate and "shared_sweep_apply" in orchestrate
    assert "stop that operation; do not fall back to CLI unless the user chooses an authorized CLI route" in orchestrate
