"""The ``high`` activity-effort procedure ships as one bounded review loop (``ADR-bounded-high-effort-review-loop``).

``skills/spec/references/review-loop.md`` holds the loop; every other bundle file names the level and cites it, so no
copy restates an unbounded re-review (``SPEC-high-effort-review-loop``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1] / "src/devkit_spec/bundle"
LOOP = BUNDLE / "skills/spec/references/review-loop.md"
EFFORT = BUNDLE / "skills/spec/references/effort.md"
WORKFLOWS = sorted((BUNDLE / "workflows").glob("*.md"))


def _text(path: Path) -> str:
    """The file's text with every whitespace run collapsed, so assertions do not depend on line wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find(" ## ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def _row(text: str, first_cell: str) -> str:
    match = re.search(rf"^\| {re.escape(first_cell)} \|.*$", text, re.MULTILINE)
    assert match, first_cell
    return match.group(0)


# AC-01
def test_the_loop_defines_round_fixing_next_round_end_and_count() -> None:
    loop = _text(LOOP)
    assert "A fresh reviewer instance" in loop
    assert "Round 1 reviews the whole change" in loop
    assert "each later round reviews every fix made since the previous round" in loop and "never a subset" in loop
    assert "fixes every finding of the round, P1, P2 and P3 together" in loop
    assert "`reverify` for code; a new `reconcile-check` for reconcile;" in loop
    assert "the next `challenger-NN` summary or the `worker` envelope's summary" in loop
    assert "The round returns no finding, or every fix of the batch meets section 2 and is self-verified" in loop
    assert "starts with `round <N>;`" in loop and "`closes reconcile-check-<NN>;`" in loop
    assert "the third after the initial review" in loop
    assert "A `devkit workflow return` does not reset the count" in loop


# AC-02
def test_minor_fix_self_verification_has_four_conditions_per_review_kind() -> None:
    raw = LOOP.read_text(encoding="utf-8")
    assert "| Condition | Code review | Reconcile | Planning |" in raw
    for condition in ("Location", "Nature", "Contract", "Evidence"):
        assert re.search(rf"^\| {condition} \|", raw, re.MULTILINE), condition
    loop = _text(LOOP)
    assert "Uncertainty on any condition, for any fix, requires the next round for the whole batch" in loop
    assert (
        "in `reverify` for code, in the new `reconcile-check` for reconcile, in the `worker` envelope's summary" in loop
    )
    assert "A recurring finding can no longer be closed by self-verification" in loop
    assert (
        "The initial `code-reviewer`, `reconcile-reviewer` and `high` Planning `challenger` calls are mandatory" in loop
    )


# AC-03
def test_hand_over_uses_worker_problems_and_questions() -> None:
    loop = _section(_text(LOOP), "## 4. Hand-over to the user")
    assert "At the cap round, the third after the initial review, the batch does not meet section 2" in loop
    assert "The same P1 recurs after its fix" in loop
    assert "still asserted after one more round given the implementer's counter-evidence" in loop
    assert loop.count("`problem` in the `worker` envelope") == 2
    assert "`questions` entry with the reviewer's and the implementer's positions as options" in loop
    assert "Reported in the conversation; not integrated" in loop and "Asked in the conversation" in loop
    assert "citing the `answer` envelope: the only waiver a P1 may carry" in loop
    assert "one further fresh round outside the cap, named by the `resolution` envelope" in loop
    assert "`recurs: <envelope> #<n>;`" in _text(LOOP)
    worker = _text(BUNDLE / "subagents/development-worker.md")
    assert "or the `high` review loop hands over" in worker
    assert "a contested P1: a question in your `worker` envelope" in worker


# AC-04
def test_severity_is_p1_p2_or_p3_on_every_review_finding() -> None:
    raw = LOOP.read_text(encoding="utf-8")
    assert "| Level | Code review | Reconcile | Planning |" in raw
    for level in ("`P1`", "`P2`", "`P3`"):
        assert re.search(rf"^\| {level} \|", raw, re.MULTILINE), level
    loop = _text(LOOP)
    assert "Every finding of a `review`, `reconcile-check` or `challenger` envelope carries `severity`" in loop
    assert "the implementer records it as returned, never relabels it" in loop
    assert "It has no effect on checks" in loop
    envelope = _text(BUNDLE / "skills/spec/references/envelope.md")
    assert 'severity: "medium"' not in envelope and 'severity: "P2"' in envelope
    assert (
        "`severity` is `P1`, `P2` or `P3` on every finding of a `review`, `reconcile-check` or `challenger`" in envelope
    )
    assert "at every effort" in envelope and "the implementer records it unchanged" in envelope
    assert "changes no finding resolution, check or gate outcome" in envelope
    review = _text(BUNDLE / "skills/spec-review/SKILL.md")
    assert 'severity: "P2"' in review and "a `severity` of `P1`, `P2` or `P3` at every effort" in review
    for role in ("code-reviewer", "reconcile-reviewer", "challenger"):
        body = _text(BUNDLE / f"subagents/{role}.md")
        assert "`severity` (required at every effort" in body or "and `severity` at every effort" in body, role
        assert "`recurs: <envelope> #<n>;`" in body, role


# AC-05
def test_high_planning_runs_scout_and_the_request_reports_its_absence() -> None:
    planning_row = _row(EFFORT.read_text(encoding="utf-8"), "Planning (`proposal`)")
    assert "`scout` and `challenger` required" in planning_row.split("|")[-2]
    loop = _section(_text(LOOP), "## 5. Planning at `high`")
    assert "runs `scout` before the first `challenger`" in loop
    assert "`devkit spec refs <ID> --direction in` for each capability and ADR the proposal touches" in loop
    proposal = _text(BUNDLE / "workflows/sdd-proposal.md")
    assert "or a `scout` at `high` that left none, the request names the gap" in proposal
    orchestrate = _text(BUNDLE / "skills/spec-orchestrate/SKILL.md")
    assert "naming a `challenger`, or a `scout` at `high`, the effort required but no envelope shows" in orchestrate


# AC-06
def test_high_session_work_gets_reclassification_advice() -> None:
    effort = _text(EFFORT)
    assert "When `high` is proposed for a `session` task, the proposal SHOULD also advise on depth" in effort
    assert "creating or changing a contract or a document kind proposes `spec` depth" in effort
    assert "reversing an accepted decision proposes `proposal` depth" in effort
    assert "gets no depth advice" in effort
    assert "If the user keeps `session`, the work runs at `high` as defined" in effort


STALE = ("re-review after", "High retains", "re-review at high")
CITING = [
    BUNDLE / "skills/spec-review/SKILL.md",
    BUNDLE / "skills/spec-delegate/SKILL.md",
    BUNDLE / "subagents/development-worker.md",
    BUNDLE / "subagents/planning-worker.md",
    *WORKFLOWS,
]


# AC-07
@pytest.mark.parametrize(
    "path",
    sorted([*BUNDLE.glob("skills/**/*.md"), *BUNDLE.glob("subagents/*.md"), *WORKFLOWS]),
    ids=lambda path: str(path.relative_to(BUNDLE)),
)
def test_no_bundle_file_restates_an_unbounded_high_re_review(path: Path) -> None:
    text = _text(path)
    for phrase in STALE:
        assert phrase not in text, phrase


@pytest.mark.parametrize("path", CITING, ids=lambda path: str(path.relative_to(BUNDLE)))
def test_every_restatement_cites_the_loop(path: Path) -> None:
    assert "review-loop.md" in _text(path)


def test_the_five_workflow_bodies_are_all_cited() -> None:
    assert [path.stem for path in WORKFLOWS] == [
        "sdd-proposal",
        "sdd-session-bugfix",
        "sdd-session-feature",
        "sdd-spec-bugfix",
        "sdd-spec-feature",
    ]


# AC-08
@pytest.mark.parametrize("role", ("code-reviewer", "reconcile-reviewer", "challenger"))
def test_reviewer_payloads_carry_the_round_inputs(role: str) -> None:
    row = _row((BUNDLE / "skills/spec-delegate/references/payload.md").read_text(encoding="utf-8"), f"`{role}`")
    assert "the `activity-effort`" in row.lower()
    assert "in a later round also the earlier rounds' findings" in row
    assert "the round's diff scope" in row
