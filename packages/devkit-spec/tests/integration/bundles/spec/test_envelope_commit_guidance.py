"""Record-only commit guidance retains evidence and combined transaction boundaries."""

from __future__ import annotations

import pytest
from spec_support.bundle_text import raw


@pytest.mark.parametrize("workflow", ["sdd-spec-feature", "sdd-spec-bugfix"])
def test_feature_and_bugfix_record_commit_boundary(workflow: str) -> None:
    text = raw(f"workflows/{workflow}.md")
    assert "devkit workflow envelope commit --unit <dir> --file envelopes/<kind>-<NN>.yaml" in text
    for term in (
        "review/reverify",
        "final-report",
        "combined manual",
        "source/document",
        "multiple records",
        "evidence SHAs",
        "prepare integration after",
        "HEAD",
        "ENVELOPE_COMMIT_UNCERTAIN",
    ):
        assert term in text


def test_skills_keep_authoring_and_commit_separate() -> None:
    envelopes = raw("skills/spec/references/envelope.md")
    for term in (
        "Authoring remains write-only",
        "read-only",
        "sole pending file",
        "ordinary Git hooks/signing",
        "already_committed",
        "multi-record Planning returns",
        "problem/emergency",
        "no approval, push or merge authority",
        "do not rerun authoring",
    ):
        assert term in envelopes
    assert "envelope commit" in raw("skills/spec-review/SKILL.md")
    assert "combined manual commit" in raw("skills/spec-feedback/SKILL.md")
