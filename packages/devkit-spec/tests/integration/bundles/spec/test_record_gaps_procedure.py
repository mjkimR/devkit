"""The procedure text for closing challenger rounds, settled assumptions and proposal boundaries (AC-11 of
``SPEC-envelope-record-gaps``)."""

from __future__ import annotations

from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
REFERENCES = BUNDLE / "skills/spec/references"


def _text(path: Path) -> str:
    """The file's text with every whitespace run collapsed, so assertions do not depend on line wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_planning_closes_each_challenger_round_with_a_reverify() -> None:
    planning = _text(REFERENCES / "planning.md")
    assert "After folding a `challenger` round, close it with `devkit workflow envelope reverify" in planning
    assert "--from envelopes/challenger-NN.yaml`: `--resolve <N>` per folded finding" in planning
    assert "leave `Decision needed:` findings open for `plan-accept`" in planning
    loop = _text(REFERENCES / "review-loop.md")
    assert "`reverify --from envelopes/challenger-NN.yaml` for Planning" in loop
    assert "closed after its fold as in [planning](planning.md) step 3" in loop


def test_the_round_count_covers_unmarked_rounds_and_answer_folds() -> None:
    loop = _text(REFERENCES / "review-loop.md")
    assert "Each kind counts separately." in loop
    assert (
        "An unmarked round counts only when it precedes the first marked round and the segment's `worker` envelope"
        " records `activity_effort: high`" in loop
    )
    assert "the higher holds" in loop and "A `reverify` is never a round" in loop
    assert "continues the same loop with a new batch" in loop
    assert "gets one further fresh round outside the cap" in loop
    assert "for a Planning fold of answers, by the `answer` envelope" in loop


def test_settled_assumptions_go_into_settles() -> None:
    records = _text(REFERENCES / "worker-records.md")
    assert "goes into `--settle N=<decision>` (`N` its 1-based position), not `constraints`" in records


def test_planning_clears_boundary_reports_before_plan_accept() -> None:
    proposal = _text(BUNDLE / "workflows/sdd-proposal.md")
    assert "clears every `RULE-proposal-boundaries` report" in proposal
    assert "each `challenger` round with the `reverify` that closes it (`review=` on its line)" in proposal
    assert "clear every `RULE-proposal-boundaries` report" in _text(REFERENCES / "planning.md")
    template = _text(BUNDLE / "templates/proposal.md")
    assert "existing paths (RULE-proposal-boundaries); a path to create: its nearest existing parent" in template
