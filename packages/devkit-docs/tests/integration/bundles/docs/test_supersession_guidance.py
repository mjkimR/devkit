"""The source of the replaced scope and its reciprocal copy are explicit in writing guidance."""

from pathlib import Path

import devkit_docs


def test_decision_guidance_names_statement_and_source_copy() -> None:
    bundle = Path(devkit_docs.__file__).parent / "bundles/docs/bundle"
    for relative in ("templates/decision.md", "instructions/decision-writing.md", "seed/docs/decisions/README.md"):
        text = (bundle / relative).read_text()
        assert "Supersedes in part `ADR-<old>`: <the replaced clauses>." in text
        assert "repeat" in text and "code spans" in text
