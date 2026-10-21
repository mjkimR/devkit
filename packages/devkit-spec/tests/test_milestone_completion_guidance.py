"""Shipped close-review procedure covers concrete decisions without a semantic evaluator."""

from pathlib import Path

import pytest
from devkit.core.frontmatter import parse
from devkit.distribution.bundles.templates import render_template

BUNDLE = Path(__file__).resolve().parents[1] / "src/devkit_spec/bundle"


def read(relative: str, environment: str) -> str:
    path = BUNDLE / relative
    if not path.exists():
        path = path.with_name(path.name + ".jinja")
    if path.suffix == ".jinja":
        return render_template(path.read_bytes(), {}, str(path), environment=environment).decode()
    return path.read_text()


# Scenario input and expected decision are human-review fixtures. Assertions below check that the
# deployed instruction contains the decision's required evidence and action; they do not decide delivery.
SCENARIOS = [
    (
        "fresh planned/active candidate",
        (
            "Closure is available from planned or active",
            "no third approval",
            "same Backlog edit/commit",
            "phase-level exit condition met",
        ),
    ),
    (
        "open legacy document lacks confirmations",
        ("Missing assertions", "mean unconfirmed", "missing user confirmation separately"),
    ),
    (
        "stored confirmations without current authority",
        ("Stored confirmed assertions alone never", "authorize a later close"),
    ),
    (
        "empty members after unfinished handoff",
        ("Empty membership alone establishes neither", "unfinished handed-off work still in scope blocks"),
    ),
    (
        "rejected/cancelled/reassigned work",
        ("retained rejected", "explicit scope disposition", "Distinguish delivery", "update the goal/exit condition"),
    ),
    ("inconclusive required inspection", ("missing/unreadable/inconclusive", "naming the remaining check")),
    (
        "semantic scope changed",
        (
            "Actual semantic scope changes",
            "new required work, exclusion or moving scope elsewhere",
            "assertions to pending",
        ),
    ),
    (
        "unchanged interrupted approval",
        ("pause or context compaction", "unchanged authorization persists", "Interruption alone does not invalidate"),
    ),
    (
        "changed interrupted candidate",
        ("present the changed candidate again", "approved candidate/evidence cannot be established"),
    ),
    ("repeat close and historical done", ("no-op: write nothing", "without migration or retrospective reopening")),
    (
        "done scope extension or dropped",
        ("reopen to active", "another milestone", "Dropped milestones are not close candidates"),
    ),
]


@pytest.mark.parametrize("environment", ["local", "cloud"])
@pytest.mark.parametrize(("scenario", "required"), SCENARIOS, ids=[row[0] for row in SCENARIOS])
def test_close_review_scenarios(environment: str, scenario: str, required: tuple[str, ...]) -> None:
    backlog = read("skills/spec/references/backlog.md", environment)
    assert "[milestone completion](milestone-completion.md)" in backlog
    procedure = read("skills/spec/references/milestone-completion.md", environment)
    for clause in required:
        assert clause in procedure, f"{scenario}: {clause}"


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
    backlog = read("skills/spec/references/backlog.md", environment)
    assert "Normal handoff or mechanical identity relocation" in backlog
    assert "no milestone review/reset" in backlog
    assert "milestone-completion.md" in read("skills/spec-next/references/next-work.md", environment)
    assert "Existing done records remain unchanged" in read("seed/docs/roadmap/README.md", environment)
    procedure = read("skills/spec/references/milestone-completion.md", environment)
    for clause in (
        "--all-namespaces -n 0",
        "--direction in -n 0",
        "ordinary prose references",
        "base",
        "commit used",
        "remote freshness",
        "relevant known Planning/Development activity",
        "without switching another task's checkout",
        "not reconstruct or persist a complete descendant graph",
    ):
        assert clause in procedure


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_normal_handoff_adds_no_milestone_ceremony(environment: str) -> None:
    procedure = read("skills/spec/references/milestone-completion.md", environment)
    assert "Normal PROP-to-SPEC handoff or mechanical identity relocation" in procedure
    assert "does not change scope/decomposition" in procedure
    assert "requires no milestone review, reset or reconfirmation" in procedure
    assert "No pre-handoff or integration hook is needed" in procedure
    for entrypoint in ("skills/spec/SKILL.md", "skills/spec-next/SKILL.md", "skills/spec/references/worktree.md"):
        assert "membership invalidation]" not in read(entrypoint, environment)
