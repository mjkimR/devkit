"""Acceptance edits only the frontmatter value, preserving the reviewed source bytes."""

import pytest

from devkit_spec.features.proposals.services.status import accepted_text


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("status", ["reviewing", '"reviewing"', "'reviewing'"])
def test_acceptance_preserves_comments_line_endings_and_body(newline: str, status: str) -> None:
    before = newline.join(
        ["---", f"status: {status} # retained comment", "title: Reviewed", "---", "status: draft", ""]
    )
    expected = newline.join(
        ["---", "status: accepted # retained comment", "title: Reviewed", "---", "status: draft", ""]
    )
    assert accepted_text(before) == expected


@pytest.mark.parametrize("text", ["status: reviewing\n", "---\ntitle: X\n---\nstatus: reviewing\n"])
def test_body_status_cannot_supply_missing_frontmatter_status(text: str) -> None:
    with pytest.raises(ValueError):
        accepted_text(text)
