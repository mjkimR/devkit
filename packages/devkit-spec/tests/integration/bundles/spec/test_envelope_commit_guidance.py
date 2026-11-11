"""Record-only commit guidance retains evidence and combined transaction boundaries."""

from __future__ import annotations

from spec_support.bundle_text import raw


def test_feature_record_commit_boundary_and_bugfix_inheritance() -> None:
    text = raw("workflows/sdd-spec-feature.md")
    assert "devkit workflow envelope commit --unit <dir> --file envelopes/<kind>-<NN>.yaml" in text
    for term in (
        "review/reverify",
        "final-report",
        "combined manual",
        "source/document",
        "multiple records",
        "references/envelope.md",
    ):
        assert term in text
    assert "All other rules of the `sdd-spec-feature` body apply" in raw("workflows/sdd-spec-bugfix.md")


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
        "evidence SHAs",
        "prepare integration after",
        "HEAD",
        "ENVELOPE_COMMIT_UNCERTAIN",
        "source/document",
    ):
        assert term in envelopes
    assert "envelope commit" in raw("skills/spec-review/SKILL.md")
    assert "combined manual commit" in raw("skills/spec-feedback/SKILL.md")


def test_final_report_authoring_example_is_eligible_for_commit() -> None:
    text = raw("workflows/sdd-spec-feature.md")
    example = next(line for line in text.splitlines() if "**Final change report.**" in line)
    assert "--stage final-change-report" in example
    assert '--summary "<verified change and remaining limits>"' in example
