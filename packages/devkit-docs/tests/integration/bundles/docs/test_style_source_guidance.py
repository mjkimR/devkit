"""A missing style file uses project ownership without seeding or expanding scope."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_docs/bundles/docs/bundle"


def test_style_source_fallback_is_conditional_project_owned_and_scoped() -> None:
    guide = (BUNDLE / "instructions/ux-writing.md").read_text()
    section = guide.split("## What stays with the project", 1)[1].split("## Candidates", 1)[0]
    assert "existing project-owned style/token source" in section
    assert "If no style source exists and the change decides visual style" in section
    assert "within the agreed task/document scope" in section
    assert "cite it from the Screens drafts and UX documents" in section
    assert "follow `living-spec-writing` for its location, title and summary" in section
    assert "no fixed filename or seeded file is required" in section
    assert "record the needed path for the scope" in section and "before writing it" in section
    assert "fallback grants no additional write authority" in section
    assert not (BUNDLE / "seed/docs/steering/visual-style.md").exists()
