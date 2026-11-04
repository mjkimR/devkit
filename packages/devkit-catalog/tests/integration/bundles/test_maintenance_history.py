from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3] / "src/devkit_catalog/maintenance/bundle/playbooks"


@pytest.mark.parametrize(
    "relative", ["weekly-report.md", "drift-reconciliation.md", "review-refactor/SKILL.md", "performance-pass/SKILL.md"]
)
def test_default_playbooks_are_independent_of_history_availability(relative: str) -> None:
    text = (ROOT / relative).read_text()
    # Installing history must not add probes, lifecycle commands, offers or completion gates.
    assert "maintenance history" not in text
    assert "history run" not in text
    assert "History completion" not in text
    assert "Recheck HEAD and dirty paths" in text or "captured SHA" in text
    assert len(text.encode()) <= 12288
    if relative in ("review-refactor/SKILL.md", "performance-pass/SKILL.md"):
        assert "Update it once each work item integrates or stops." in text
    if relative == "weekly-report.md":
        assert "Create a companion outcome record" in text
