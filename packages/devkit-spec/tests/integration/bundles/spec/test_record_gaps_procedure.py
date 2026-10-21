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
    assert "At `medium` and `high`, after folding a `challenger` round into the proposal, close it with one" in planning
    assert "--from envelopes/challenger-NN.yaml`: `--resolve <N>` for each folded finding" in planning
    assert "`Decision needed:` findings left open for `plan-accept`" in planning
    loop = _text(REFERENCES / "review-loop.md")
    assert "closed after its fold by a `reverify --from envelopes/challenger-NN.yaml` as at `medium`" in loop
    assert "For Planning that is the reverify closing the `challenger` round" in loop
    assert "--from envelopes/challenger-NN.yaml` closes a Planning `challenger` round" in _text(
        BUNDLE / "skills/spec-delegate/SKILL.md"
    )


def test_the_round_count_covers_unmarked_rounds_and_answer_folds() -> None:
    loop = _text(REFERENCES / "review-loop.md")
    assert "Each loop counts its own kind (`challenger`, `review`, `reconcile-check`)" in loop
    assert (
        "only when it precedes the loop's first marked round in the segment and a `worker` envelope of the segment"
        " written before that marker records `activity_effort: high`" in loop
    )
    assert "a `high` loop that follows them starts at round 1" in loop
    assert "the higher number holds" in loop and "A `reverify` is never a round" in loop
    assert "treats the fold as a new batch of the same loop, never a fresh loop" in loop
    assert "it gets one further fresh round outside the cap" in loop
    assert "cites the `answer` envelope in place of a `resolution`" in loop


def test_settled_assumptions_go_into_settles() -> None:
    records = _text(REFERENCES / "worker-records.md")
    assert (
        "goes into `settles` (`--settle N=<decision>`, `N` its 1-based position), never into `constraints`" in records
    )
    assert "Settling holds and releases nothing" in records
    assert "`--settle N=<decision>` for each of the worker's `assumptions`" in _text(REFERENCES / "planning.md")


def test_planning_clears_boundary_reports_before_plan_accept() -> None:
    proposal = _text(BUNDLE / "workflows/sdd-proposal.md")
    assert "clears every `RULE-proposal-boundaries` report" in proposal
    assert "each `challenger` round with the `reverify` that closes it (`review=` on its line)" in proposal
    assert "clear every `RULE-proposal-boundaries` report" in _text(REFERENCES / "planning.md")
    template = _text(BUNDLE / "templates/proposal.md")
    assert "existing paths (RULE-proposal-boundaries); a path to create: its nearest existing parent" in template
