"""Shipped close-review procedure covers concrete decisions without a semantic evaluator."""

import pytest
from devkit_core.core.frontmatter import parse
from distsupport.guidance import assert_rule, states_rule
from spec_support.bundle_text import flat, raw, text

# Scenario input and expected decision are human-review fixtures. Assertions below check that the
# deployed instruction states the decision's required evidence and action; they do not decide delivery.
# Each scenario lists its rules; a rule is the tokens one paragraph or list item must state together.
PROCEDURE = "skills/spec/references/milestone-completion.md"
SCENARIOS = [
    (
        "fresh planned/active candidate",
        PROCEDURE,
        (
            ("`status: done`", "one backlog commit", "from `planned` or `active`"),
            ("exit condition met", "agreed scope"),
        ),
    ),
    (
        "open legacy document lacks confirmations",
        PROCEDURE,
        (
            ("missing or previously confirmed assertions", "authorize nothing"),
            ("missing user confirmation", "separately", "evidence gaps"),
        ),
    ),
    (
        "empty members after unfinished handoff",
        PROCEDURE,
        (("empty membership", "proves nothing"), ("unfinished handed-off work", "blocks the close")),
    ),
    (
        "rejected/cancelled/reassigned work",
        PROCEDURE,
        (
            ("retained rejected member", "explicit scope disposition"),
            ("rejection or reassignment alone", "proves no delivery"),
            ("update the goal or exit condition", "scope shrank"),
        ),
    ),
    (
        "inconclusive required inspection",
        PROCEDURE,
        (("missing or inconclusive", "keep the milestone open", "name the remaining check"),),
    ),
    (
        "semantic scope changed",
        "skills/spec/references/roadmap-catalog.md",
        (("semantic scope changes", "reset both to pending"),),
    ),
    (
        "unchanged interrupted approval",
        PROCEDURE,
        (("before writing", "recheck the evidence", "interruption alone", "does not invalidate", "confirmation"),),
    ),
    (
        "changed interrupted candidate",
        PROCEDURE,
        (("cannot be re-established after a pause", "present the candidate again"),),
    ),
    (
        "repeat close and historical done",
        PROCEDURE,
        (
            ("closing an unchanged `done` milestone", "writes nothing"),
            ("existing `done` records", "stay as they are"),
        ),
    ),
    (
        "done scope extension or dropped",
        PROCEDURE,
        (
            ("extend a `done` milestone", "reopen it to `active`", "another milestone"),
            ("`dropped` milestone", "no close candidate"),
            ("theme milestone", "not such an extension"),
        ),
    ),
]


@pytest.mark.parametrize("environment", ["local", "cloud"])
@pytest.mark.parametrize(("scenario", "source", "required"), SCENARIOS, ids=[row[0] for row in SCENARIOS])
def test_close_review_scenarios(
    environment: str, scenario: str, source: str, required: tuple[tuple[str, ...], ...]
) -> None:
    backlog = text("skills/spec/references/backlog.md", environment)
    assert "[milestone completion](milestone-completion.md)" in backlog
    document = raw(source, environment)
    for rule in required:
        assert states_rule(document, *rule), f"{scenario}: {rule}"


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
    assert_rule(
        raw("skills/spec/references/roadmap-catalog.md", environment), "done records stay as written", "unless merged"
    )
    procedure = raw(PROCEDURE, environment)
    assert_rule(procedure, "--direction in -n 0", "--all-namespaces -n 0", "not prose references")
    assert_rule(
        procedure,
        "`plan-`/`dev-` activity",
        "without switching another task's checkout",
        "report the base commit",
        "persist no descendant graph",
    )


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_normal_handoff_adds_no_milestone_ceremony(environment: str) -> None:
    catalog = raw("skills/spec/references/roadmap-catalog.md", environment)
    assert_rule(catalog, "semantic scope changes reset both to pending", "normal handoff does not")
    for entrypoint in ("skills/spec/SKILL.md", "skills/spec-next/SKILL.md", "skills/spec/references/worktree.md"):
        assert "membership invalidation]" not in text(entrypoint, environment)


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_granularity_is_a_recommendation(environment: str) -> None:
    template = text("skills/spec/references/roadmap-catalog.md", environment)
    catalog = raw("skills/spec/references/roadmap-catalog.md", environment)
    assert_rule(catalog, "prefer a broader theme", "only sequences one proposal")
    assert_rule(catalog, "exit conditions are recommended", "prefer observable phase-level outcomes")
    assert "SHOULD NOT" not in template and "SHOULD represent" not in template


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_merge_procedure(environment: str) -> None:
    backlog = raw("skills/spec/references/backlog.md", environment)
    assert_rule(
        backlog,
        "on the user's decision",
        "small milestones of any status",
        "broader theme milestone",
        "merged ids in the theme's `aliases`",
        "delete the merged files",
        "`devkit rules fix`",
        "remove `depends_on` edges",
    )
    assert_rule(
        backlog,
        "after a merge",
        "remaining scope to draft proposals",
        "`planned` or `active` while scope remains",
        "close it only through [milestone completion](milestone-completion.md)",
    )
    seed = raw("skills/spec/references/roadmap-catalog.md", environment)
    assert_rule(seed, "small milestones of any status", "broader theme milestone", "not an in-place extension")
