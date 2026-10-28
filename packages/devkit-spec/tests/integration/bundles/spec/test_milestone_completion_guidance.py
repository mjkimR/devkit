"""Shipped close-review procedure covers concrete decisions without a semantic evaluator."""

import pytest
from devkit_core.core.frontmatter import parse
from spec_support.bundle_text import flat, raw, text

# Scenario input and expected decision are human-review fixtures. Assertions below check that the
# deployed instruction contains the decision's required evidence and action; they do not decide delivery.
PROCEDURE = "skills/spec/references/milestone-completion.md"
SCENARIOS = [
    (
        "fresh planned/active candidate",
        PROCEDURE,
        ("in one Backlog commit, from `planned` or `active`", "the exit condition met for the agreed scope"),
    ),
    (
        "open legacy document lacks confirmations",
        PROCEDURE,
        ("Missing or previously confirmed assertions authorize nothing", "missing user confirmation separately"),
    ),
    (
        "empty members after unfinished handoff",
        PROCEDURE,
        ("empty membership proves nothing", "unfinished handed-off work blocks the close"),
    ),
    (
        "rejected/cancelled/reassigned work",
        PROCEDURE,
        (
            "A retained rejected member needs an explicit scope disposition",
            "rejection or reassignment alone proves no delivery",
            "Update the goal or exit condition when the scope shrank",
        ),
    ),
    ("inconclusive required inspection", PROCEDURE, ("missing or inconclusive", "name the remaining check")),
    (
        "semantic scope changed",
        "skills/spec/references/roadmap-catalog.md",
        ("Actual semantic scope changes reset both to pending",),
    ),
    (
        "unchanged interrupted approval",
        PROCEDURE,
        ("recheck the evidence", "an interruption alone does not invalidate the user's confirmation"),
    ),
    (
        "changed interrupted candidate",
        PROCEDURE,
        ("the approved candidate cannot be re-established after a pause, present the candidate again",),
    ),
    (
        "repeat close and historical done",
        PROCEDURE,
        ("Closing an unchanged `done` milestone writes nothing", "existing `done` records stay as they are"),
    ),
    (
        "done scope extension or dropped",
        PROCEDURE,
        (
            "reopen it to `active`",
            "another milestone",
            "A `dropped` milestone is no close candidate",
            "is not such an extension",
        ),
    ),
]


@pytest.mark.parametrize("environment", ["local", "cloud"])
@pytest.mark.parametrize(("scenario", "source", "required"), SCENARIOS, ids=[row[0] for row in SCENARIOS])
def test_close_review_scenarios(environment: str, scenario: str, source: str, required: tuple[str, ...]) -> None:
    backlog = text("skills/spec/references/backlog.md", environment)
    assert "[milestone completion](milestone-completion.md)" in backlog
    document = text(source, environment)
    for clause in required:
        assert clause in document, f"{scenario}: {clause}"


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_plain_assertions_and_entrypoints(environment: str) -> None:
    template = raw("templates/milestone.md", environment)
    body = flat(template.split("## Completion review\n", 1)[1])
    assert body.count("Decomposition: pending") == 1
    assert body.count("Direct proposal work: pending") == 1
    assert "- [ ]" not in body
    data = parse(template).data
    assert data is not None
    assert set(data) == {"id", "title", "summary", "status", "created_at", "depends_on"}
    assert "milestone-completion.md" in text("skills/spec-next/references/next-work.md", environment)
    assert "Done records stay as written unless merged" in text(
        "skills/spec/references/roadmap-catalog.md", environment
    )
    procedure = text(PROCEDURE, environment)
    for clause in (
        "--all-namespaces -n 0",
        "--direction in -n 0",
        "not prose references",
        "base commit used",
        "known `plan-`/`dev-` activity",
        "without switching another task's checkout",
        "persist no descendant graph",
    ):
        assert clause in procedure


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_normal_handoff_adds_no_milestone_ceremony(environment: str) -> None:
    assert "normal handoff does not" in text("skills/spec/references/roadmap-catalog.md", environment)
    assert "normal handoff does not" in text("skills/spec/references/roadmap-catalog.md", environment)
    for entrypoint in ("skills/spec/SKILL.md", "skills/spec-next/SKILL.md", "skills/spec/references/worktree.md"):
        assert "membership invalidation]" not in text(entrypoint, environment)


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_granularity_is_a_recommendation(environment: str) -> None:
    template = text("skills/spec/references/roadmap-catalog.md", environment)
    seed = text("skills/spec/references/roadmap-catalog.md", environment)
    assert "prefer a broader theme over a milestone that only sequences one proposal" in template
    assert "Prefer observable phase-level outcomes" in template
    assert "over a milestone that only sequences one proposal" in seed
    assert "Exit conditions are recommended to state observable phase-level outcomes" in seed
    for document in (template, seed):
        assert "SHOULD NOT" not in document and "SHOULD represent" not in document


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_merge_procedure(environment: str) -> None:
    backlog = text("skills/spec/references/backlog.md", environment)
    for clause in (
        "small milestones of any status may merge into a broader theme milestone",
        "on the user's decision",
        "list the merged IDs in the theme's `aliases`",
        "delete the merged files, run `devkit rules fix`",
        "remove `depends_on` edges between the merged milestones",
        "move remaining scope to draft proposals in the theme",
        "keep the theme `planned` or `active` while scope remains",
        "close it only through [milestone completion](milestone-completion.md)",
    ):
        assert clause in backlog, clause
    seed = text("skills/spec/references/roadmap-catalog.md", environment)
    assert "small milestones of any status may merge into a broader theme milestone" in seed
    assert "A merge is not an in-place extension" in seed
