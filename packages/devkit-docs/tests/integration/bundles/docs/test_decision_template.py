"""The decision template keeps status, date and supersession in the frontmatter only and scaffolds one line per
option (SPEC-adr-body-metadata-removal, ADR-frontmatter-only-decision-status)."""

import re
from pathlib import Path

import devkit_docs

BUNDLE = Path(devkit_docs.__file__).parent / "bundles/docs/bundle"


def _body(text: str) -> str:
    """``text`` after its frontmatter block."""
    end = text.index("\n---\n", 4) + len("\n---\n")
    return text[end:]


def test_the_decision_template_has_no_body_metadata_block_or_separators() -> None:
    body = _body((BUNDLE / "templates/decision.md").read_text(encoding="utf-8"))
    assert not re.search(r"^- \*\*(Status|Date|Deciders|Involved Components/Capabilities)\*\*", body, re.MULTILINE)
    assert not re.search(r"^---[ \t]*$", body, re.MULTILINE)
    for scaffold in ("**Overview**", "**Pros**", "**Cons**"):
        assert scaffold not in body


def test_the_decision_template_scaffolds_one_line_per_option_with_the_selected_one_marked() -> None:
    body = _body((BUNDLE / "templates/decision.md").read_text(encoding="utf-8"))
    options = body.split("## 3. Considered Options\n", 1)[1].split("\n## ", 1)[0]
    items = [line for line in options.splitlines() if line.startswith("- ")]
    assert len(items) == 2
    assert re.match(r"- \*\*<[^>]+>\*\* \(selected\): ", items[0])
    assert re.match(r"- \*\*<[^>]+>\*\*: ", items[1])


def test_decision_writing_keeps_status_in_the_frontmatter_and_marks_the_selected_option() -> None:
    guide = " ".join((BUNDLE / "instructions/decision-writing.md").read_text(encoding="utf-8").split())
    assert "status, date and whole supersession only in `status`, `created_at` and `superseded_by`" in guide
    assert "Write no Status, Date, Deciders or Involved Components line in the body" in guide
    assert "one or two lines per option" in guide
    assert "mark the selected option `(selected)`" in guide
