"""Shipped close-review procedure covers concrete decisions without a semantic evaluator."""

from pathlib import Path

import pytest
from devkit_core.core.frontmatter import parse
from devkit_dist.features.distribution.services.bundles.templates import render_template

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"


def read(relative: str, environment: str) -> str:
    path = BUNDLE / relative
    if not path.exists():
        path = path.with_name(path.name + ".jinja")
    if path.suffix == ".jinja":
        return render_template(path.read_bytes(), {}, str(path), environment=environment).decode()
    return path.read_text()


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
        "templates/milestone.md",
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
        ("reopen it to `active`", "another milestone", "A `dropped` milestone is no close candidate"),
    ),
]


@pytest.mark.parametrize("environment", ["local", "cloud"])
@pytest.mark.parametrize(("scenario", "source", "required"), SCENARIOS, ids=[row[0] for row in SCENARIOS])
def test_close_review_scenarios(environment: str, scenario: str, source: str, required: tuple[str, ...]) -> None:
    backlog = read("skills/spec/references/backlog.md", environment)
    assert "[milestone completion](milestone-completion.md)" in backlog
    text = read(source, environment)
    for clause in required:
        assert clause in text, f"{scenario}: {clause}"


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_plain_assertions_and_entrypoints(environment: str) -> None:
    template = read("templates/milestone.md", environment)
    body = template.split("## Completion review\n", 1)[1]
    assert body.count("Decomposition: pending") == 1
    assert body.count("Direct proposal work: pending") == 1
    assert "- [ ]" not in body
    data = parse(template).data
    assert data is not None
    assert set(data) == {"id", "title", "summary", "status", "created_at", "depends_on"}
    assert "milestone-completion.md" in read("skills/spec-next/references/next-work.md", environment)
    assert "Existing done records remain unchanged" in read("seed/docs/roadmap/README.md", environment)
    procedure = read(PROCEDURE, environment)
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
    assert "normal handoff does not" in read("templates/milestone.md", environment)
    assert "normal handoff does not" in read("seed/docs/roadmap/README.md", environment)
    for entrypoint in ("skills/spec/SKILL.md", "skills/spec-next/SKILL.md", "skills/spec/references/worktree.md"):
        assert "membership invalidation]" not in read(entrypoint, environment)
