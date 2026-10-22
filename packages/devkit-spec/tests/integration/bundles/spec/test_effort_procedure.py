"""The ``high`` activity-effort procedure ships as one bounded review loop (``ADR-bounded-high-effort-review-loop``).

``skills/spec/references/review-loop.md`` holds the loop; every other bundle file names the level and cites it, so no
copy restates an unbounded re-review (``SPEC-high-effort-review-loop``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
LOOP = BUNDLE / "skills/spec/references/review-loop.md"
EFFORT = BUNDLE / "skills/spec/references/effort.md"
WORKFLOWS = sorted((BUNDLE / "workflows").glob("*.md"))


def _text(path: Path) -> str:
    """The file's text with every whitespace run collapsed, so assertions do not depend on line wrapping."""
    return " ".join(_rendered(path).split())


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
    assert "each later round reviews every fix since the previous round and what it affects" in loop
    assert "Fix every finding of the round together" in loop
    assert (
        "`reverify` for code, a new `reconcile-check` for reconcile, `reverify --from envelopes/challenger-NN.yaml`"
        " for Planning" in loop
    )
    assert "The round returns no finding, or every fix of the batch meets section 2" in loop
    assert "A P1 you hold invalid stays open in that record with counter-evidence" in loop
    assert "a contested P1 stays open" in loop
    assert "starts with `round <N>;`" in loop and "`closes reconcile-check-<NN>;`" in loop
    assert "the third after the initial review" in loop
    assert "`devkit workflow return` does not reset the count" in loop


# AC-02
def test_minor_fix_self_verification_has_four_conditions_per_review_kind() -> None:
    raw = LOOP.read_text(encoding="utf-8")
    assert "| Condition | Code review | Reconcile | Planning |" in raw
    for condition in ("Location", "Nature", "Contract", "Evidence"):
        assert re.search(rf"^\| {condition} \|", raw, re.MULTILINE), condition
    loop = _text(LOOP)
    assert "If any condition is uncertain for any fix, run the next round for the whole batch" in loop
    assert "Record the reason and evidence in the record that closes the round" in loop
    assert "A recurring finding cannot be self-verified" in loop
    assert "Round 1 is never replaced by a self-check" in loop


# AC-03
def test_bounded_recovery_is_host_owned_without_an_extra_user_gate() -> None:
    loop = _section(_text(LOOP), "## 4. Bounded recovery")
    assert "The cap round, the third after the initial review, ends with a batch that fails section 2" in loop
    assert "The same P1 recurs after its fix" in loop
    assert "still asserted after one more round with your counter-evidence" in loop
    assert "The Host owns recovery within the authorized goal, scope and constraints" in loop
    assert "adds no user approval gate" in loop
    assert "one further fresh round outside the cap" in loop
    assert "Never integrate while required findings remain open" in loop
    assert "a new worker or session resets nothing" in loop
    assert "`recurs: <envelope> #<n>;`" in _text(LOOP)


# AC-04
def test_severity_is_p1_p2_or_p3_on_every_review_finding() -> None:
    raw = LOOP.read_text(encoding="utf-8")
    assert "| Level | Code review | Reconcile | Planning |" in raw
    for level in ("`P1`", "`P2`", "`P3`"):
        assert re.search(rf"^\| {level} \|", raw, re.MULTILINE), level
    loop = _text(LOOP)
    assert "Every `review`, `reconcile-check` and `challenger` finding carries one level, at every effort" in loop
    assert "The reviewer sets it; the implementer never relabels it" in loop
    assert "Severity changes no check" in loop
    envelope = _text(BUNDLE / "skills/spec/references/envelope.md")
    assert 'severity: "medium"' not in envelope and 'severity: "P2"' in envelope
    assert (
        "`severity` is `P1`, `P2` or `P3` on every finding of a `review`, `reconcile-check` or `challenger`" in envelope
    )
    assert "at every effort" in envelope and "recorded as the reviewer set it" in envelope
    review = _text(BUNDLE / "skills/spec-review/SKILL.md")
    assert 'severity: "P2"' in review and "a `severity` of `P1`, `P2` or `P3` at every effort" in review
    for role in ("code-reviewer", "reconcile-reviewer", "challenger"):
        body = _text(BUNDLE / f"subagents/{role}.md")
        assert "review-loop.md` for the round's scope and `recurs:` marking" in body, role
        if role == "code-reviewer":
            assert "The fields of the `review` envelope its Report section shows" in body
        else:
            assert 'Give every finding a `severity` from the "Severity" section of `review-loop.md`' in body, role


# AC-05
def test_high_planning_runs_scout_and_the_request_reports_its_absence() -> None:
    planning_row = _row(_rendered(EFFORT), "Planning (`proposal`)")
    assert "`scout` and `challenger` required" in planning_row.split("|")[-2]
    loop = _section(_text(LOOP), "## 5. Planning at `high`")
    assert "run `scout` before the first `challenger`" in loop
    assert "`devkit spec refs <ID> --direction in` for each capability and ADR the proposal touches" in loop
    proposal = _text(BUNDLE / "workflows/sdd-proposal.md")
    assert "or a `scout` at `high` that left none, the request names the gap" in proposal
    orchestrate = _text(BUNDLE / "skills/spec-orchestrate/SKILL.md")
    assert "first naming any support role the effort required but no envelope shows" in orchestrate


# AC-06
def test_high_session_work_gets_reclassification_advice() -> None:
    effort = _text(EFFORT)
    assert "For `high` on a `session` task, also advise on depth" in effort
    assert "a contract or document-kind change proposes `spec` depth" in effort
    assert "reversing an accepted decision proposes `proposal` depth" in effort
    assert "other work gets no depth advice" in effort
    assert "If the user keeps `session`, the work runs at `high`" in effort


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
    text = _text(path)
    for phrase in STALE:
        assert phrase not in text, phrase


@pytest.mark.parametrize("path", CITING, ids=lambda path: str(path.relative_to(BUNDLE)))
def test_every_restatement_cites_the_loop(path: Path) -> None:
    assert "review-loop.md" in _text(path)


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
    payload = _rendered(BUNDLE / "skills/spec-delegate/references/payload.md")
    assert "`activity-effort`" in _row(payload, f"`{role}`")
    later_round = " ".join(payload.split())
    assert "For a later reviewer round at `high`, also pass the earlier rounds' envelope files" in later_round
    assert "set `diff_scope` to the fixes since the previous round" in later_round


def _rendered(path: Path) -> str:
    from devkit_dist.features.distribution.services.bundles.templates import render_template

    if path.name.endswith(".md.jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment="local").decode()
    if path.exists():
        return path.read_text(encoding="utf-8")
    source = path.with_name(path.name + ".jinja")
    return render_template(source.read_bytes(), {}, str(source), environment="local").decode()
