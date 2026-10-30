"""The guidance names who decided each answer and refuses closed findings (AC-08 of ``SPEC-envelope-answer-decider``)."""

from __future__ import annotations

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw

RECORDS = "skills/spec/references/worker-records.md"


def test_worker_records_name_the_decider_of_each_answer() -> None:
    records = raw(RECORDS)
    assert (
        '--answers-file -    # - { question: q1, choice: a, decision: "...", constraints: [...], by: user }' in records
    )
    assert_rule(records, "`by`", "`user`", "`host`", "`policy`", "rewritten answers name `by` per answer")


def test_payload_and_worker_references_hand_over_the_decider() -> None:
    assert_rule(
        raw("skills/spec-delegate/references/payload.md"), "`planning-worker`", "rewritten answers", "`by: user`"
    )
    assert_rule(
        raw("skills/spec-delegate/references/worker.md"), "rewritten answers", "`by: user`", "`host`", "`policy`"
    )


def test_planning_refuses_a_closed_finding_number() -> None:
    assert_rule(
        raw("skills/spec/references/planning.md"),
        "pass only the findings that turn closes",
        "`ENVELOPE_FINDING_CLOSED`",
    )
