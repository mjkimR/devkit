"""The procedure text for closing challenger rounds, settled assumptions and proposal boundaries (AC-11 of
``SPEC-envelope-record-gaps``)."""

from __future__ import annotations

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

PLANNING = "skills/spec/references/planning.md"
LOOP = "skills/spec/references/review-loop.md"


def test_planning_closes_each_challenger_round_with_a_reverify() -> None:
    planning = raw(PLANNING)
    assert_rule(
        planning,
        "after folding a `challenger` round",
        "`devkit workflow envelope reverify",
        "--from envelopes/challenger-NN.yaml`",
        "`--resolve <N>` per folded finding",
    )
    assert_rule(planning, "`challenger` round", "leave `Decision needed:` findings open", "`plan-accept`")
    loop = raw(LOOP)
    assert_rule(loop, "`reverify --from envelopes/challenger-NN.yaml` for Planning")
    assert_rule(loop, "`challenger-NN` envelope", "closed after its fold", "[planning](planning.md) step 3")


def test_the_round_count_covers_unmarked_rounds_and_answer_folds() -> None:
    loop = raw(LOOP)
    assert_rule(loop, "`round <N>;`", "each kind counts separately")
    assert_rule(loop, "unmarked round counts only when", "precedes the first marked round", "`activity_effort: high`")
    assert_rule(loop, "unmarked round", "the higher holds", "a `reverify` is never a round")
    assert_rule(loop, "Planning turn", "folds answers", "continues the same loop with a new batch")
    assert_rule(loop, "Host-directed recovery", "one further fresh round outside the cap")
    assert_rule(loop, "one further fresh round", "Planning fold of answers", "`answer` envelope")


def test_settled_assumptions_go_into_settles() -> None:
    records = raw("skills/spec/references/worker-records.md")
    assert_rule(records, "`assumptions`", "`--settle N=<decision>`", "1-based position", "not `constraints`")


def test_planning_clears_boundary_reports_before_plan_accept() -> None:
    proposal = raw("workflows/sdd-proposal.md")
    assert_rule(proposal, "before requesting it", "clears every `RULE-proposal-boundaries` report")
    assert_rule(proposal, "each `challenger` round", "`reverify` that closes it", "`review=`")
    assert_rule(raw(PLANNING), "devkit rules check", "clear every `RULE-proposal-boundaries` report")
    template = text("templates/proposal.md")
    assert "existing paths (RULE-proposal-boundaries); a path to create: its nearest existing parent" in template
