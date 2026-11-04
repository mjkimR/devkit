from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3] / "src/devkit_catalog/maintenance/bundle/playbooks"


@pytest.mark.parametrize(
    "relative", ["weekly-report.md", "drift-reconciliation.md", "review-refactor/SKILL.md", "performance-pass/SKILL.md"]
)
def test_history_steps_are_guarded_and_publication_remains_explicit(relative: str) -> None:
    text = (ROOT / relative).read_text()
    assert "If `devkit maintenance history --help` succeeds" in text
    assert "--report <report-path>" in text
    assert "history finish" in text and "history publish" in text and "history update" in text
    assert "separate authority" in text
    assert "configuration grants none" in text
    assert "freeze its digest" in text
    assert "--file <frozen-path>" in text
    assert "Without that command" in text
    assert "leave the report bytes unchanged" in text
    assert len(text.encode()) <= 12288
