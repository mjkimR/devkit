"""The ``high`` activity-effort procedure ships as one bounded review loop (``ADR-host-owned-review-loop-recovery``).

``skills/spec/references/review-loop.md`` holds the loop; every other bundle file names the level and cites it, so no
copy restates an unbounded re-review (``SPEC-high-effort-review-loop``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import BUNDLE, raw, text

LOOP = BUNDLE / "skills/spec/references/review-loop.md"
EFFORT = BUNDLE / "skills/spec/references/effort.md"
WORKFLOWS = sorted((BUNDLE / "workflows").glob("*.md"))


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def _row(text: str, first_cell: str) -> str:
    match = re.search(rf"^\| {re.escape(first_cell)} \|.*$", text, re.MULTILINE)
    assert match, first_cell
    return match.group(0)


# AC-01
def test_the_loop_defines_round_fixing_next_round_end_and_count() -> None:
    loop = raw(LOOP)
    assert_rule(loop, "fresh reviewer instance", "never a continued one")
    assert_rule(loop, "round 1 reviews the whole change")
    assert_rule(loop, "each later round", "every fix since the previous round", "what it affects")
    assert_rule(loop, "fix every finding of the round together")
    assert_rule(
        loop,
        "close the round",
        "`reverify` for code",
        "new `reconcile-check` for reconcile",
        "`reverify --from envelopes/challenger-NN.yaml` for Planning",
    )
    assert_rule(loop, "returns no finding", "every fix of the batch meets section 2")
    assert_rule(loop, "P1 you hold invalid", "stays open", "counter-evidence")
    assert_rule(loop, "next round", "whole batch", "contested P1 stays open")
    assert_rule(loop, "`round <N>;`", "`closes reconcile-check-<NN>;`")
    assert_rule(loop, "cap round", "the third after the initial review")
    assert_rule(loop, "`devkit workflow return` does not reset the count")


# AC-02
def test_minor_fix_self_verification_has_four_conditions_per_review_kind() -> None:
    table = raw(LOOP)
    assert "| Condition | Code review | Reconcile | Planning |" in table
    for condition in ("Location", "Nature", "Contract", "Evidence"):
        assert re.search(rf"^\| {condition} \|", table, re.MULTILINE), condition
    loop = raw(LOOP)
    assert_rule(loop, "any condition is uncertain", "next round", "whole batch")
    assert_rule(loop, "record the reason and evidence", "record that closes the round")
    assert_rule(loop, "recurring finding cannot be self-verified")
    assert_rule(loop, "round 1 is never replaced by a self-check")


# AC-03
def test_bounded_recovery_is_host_owned_without_an_extra_user_gate() -> None:
    loop = _section(raw(LOOP), "## 4. Bounded recovery")
    assert_rule(loop, "cap round", "third after the initial review", "fails section 2")
    assert_rule(loop, "same P1 recurs after its fix")
    assert_rule(loop, "contested P1", "still asserted after one more round", "counter-evidence")
    assert_rule(loop, "Host owns recovery", "authorized goal, scope and constraints", "adds no user approval gate")
    assert_rule(loop, "Host-directed recovery", "one further fresh round outside the cap")
    assert_rule(loop, "never integrate while required findings remain open")
    assert_rule(loop, "new worker or session resets nothing")
    assert_rule(raw(LOOP), "repeats an earlier one", "`recurs: <envelope> #<n>;`")


# AC-04
def test_severity_is_p1_p2_or_p3_on_every_review_finding() -> None:
    table = raw(LOOP)
    assert "| Level | Code review | Reconcile | Planning |" in table
    for level in ("`P1`", "`P2`", "`P3`"):
        assert re.search(rf"^\| {level} \|", table, re.MULTILINE), level
    loop = raw(LOOP)
    assert_rule(loop, "every `review`, `reconcile-check` and `challenger` finding", "one level", "at every effort")
    assert_rule(loop, "reviewer sets it", "implementer never relabels it")
    assert_rule(loop, "severity changes no check")
    envelope = raw(BUNDLE / "skills/spec/references/envelope.md")
    assert 'severity: "medium"' not in envelope and 'severity: "P2"' in envelope
    assert_rule(envelope, "`severity` per [review loop](review-loop.md) section 3", "`challenger` only")
    review = raw(BUNDLE / "skills/spec-review/SKILL.md")
    assert 'severity: "P2"' in review
    assert_rule(review, "`severity` of `P1`, `P2` or `P3`", "at every effort")
    for role in ("code-reviewer", "reconcile-reviewer", "challenger"):
        body = raw(BUNDLE / f"subagents/{role}.md")
        assert_rule(body, "at `high`", "review-loop.md`", "round's scope", "`recurs:` marking")
        if role == "code-reviewer":
            assert_rule(body, "fields of the `review` envelope", "Report section")
        else:
            assert_rule(body, "every finding a `severity`", '"Severity" section of `review-loop.md`')


# AC-05
def test_high_planning_runs_scout_and_the_request_reports_its_absence() -> None:
    planning_row = _row(raw(EFFORT), "Planning (`proposal`)")
    assert "`scout` and `challenger` required" in planning_row.split("|")[-2]
    loop = _section(raw(LOOP), "## 5. Planning at `high`")
    assert_rule(
        loop,
        "run `scout` before the first `challenger`",
        "`devkit docs refs <ID> --direction in`",
        "each capability and ADR the proposal touches",
    )
    proposal = raw(BUNDLE / "workflows/sdd-proposal.md")
    assert_rule(proposal, "`scout` at `high` that left none", "request names the gap")
    orchestrate = raw(BUNDLE / "skills/spec-orchestrate/SKILL.md")
    assert_rule(orchestrate, "first naming any support role", "effort required", "no envelope shows")


# AC-06
def test_high_session_work_gets_reclassification_advice() -> None:
    effort = raw(EFFORT)
    assert_rule(effort, "for `high` on a `session` task", "advise on depth")
    assert_rule(effort, "contract or document-kind change", "proposes `spec` depth")
    assert_rule(effort, "reversing an accepted decision", "proposes `proposal` depth")
    assert_rule(effort, "other work gets no depth advice")
    assert_rule(effort, "user keeps `session`", "runs at `high`")


STALE = ("re-review after", "High retains", "re-review at high")
CITING = [
    BUNDLE / "skills/spec-review/SKILL.md",
    BUNDLE / "skills/spec-delegate/references/payload.md",
    BUNDLE / "subagents/development-worker.md",
    BUNDLE / "skills/spec/references/planning.md",
    *WORKFLOWS,
]


# AC-07
@pytest.mark.parametrize(
    "path",
    sorted([*BUNDLE.glob("skills/**/*.md*"), *BUNDLE.glob("subagents/*.md*"), *WORKFLOWS]),
    ids=lambda path: str(path.relative_to(BUNDLE)),
)
def test_no_bundle_file_restates_an_unbounded_high_re_review(path: Path) -> None:
    document = text(path)
    for phrase in STALE:
        assert phrase not in document, phrase


@pytest.mark.parametrize("path", CITING, ids=lambda path: str(path.relative_to(BUNDLE)))
def test_every_restatement_cites_the_loop(path: Path) -> None:
    assert "review-loop.md" in text(path)


def test_the_workflow_bodies_are_all_cited() -> None:
    assert [path.stem for path in WORKFLOWS] == [
        "sdd-overall-refactor",
        "sdd-proposal",
        "sdd-session-bugfix",
        "sdd-session-feature",
        "sdd-spec-bugfix",
        "sdd-spec-feature",
    ]


# AC-08
@pytest.mark.parametrize("role", ("code-reviewer", "reconcile-reviewer", "challenger"))
def test_reviewer_payloads_carry_the_round_inputs(role: str) -> None:
    payload = raw(BUNDLE / "skills/spec-delegate/references/payload.md")
    assert "`activity-effort`" in _row(payload, f"`{role}`")
    assert_rule(payload, "later reviewer round at `high`", "earlier rounds' envelope files")
    assert_rule(payload, "later reviewer round", "`diff_scope`", "fixes since the previous round")
