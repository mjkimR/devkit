"""The base merge is conditional and a local-orchestrated batch ends with one test run (``ADR-moved-target-merge``,
``ADR-post-batch-test-run``)."""

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_integrate_step_one_merges_the_base_only_after_a_reported_refusal(environment: str) -> None:
    integrate = raw("skills/spec-integrate/SKILL.md", environment)
    assert_rule(
        integrate,
        "1. Merge the base into the task branch only to resolve what the CLI reports",
        "`WORKTREE_MERGE_CONFLICT`",
        "never rebase",
        "`devkit generated resolve` first",
        "`devkit rules fix`",
    )
    assert_rule(integrate, "2. After such a merge", "reuse the source's verification")
    assert "repeat after an integration refused on a later target" not in integrate


def test_orchestrate_no_longer_requires_a_base_merge_before_integration() -> None:
    orchestrate = text("skills/spec-orchestrate/SKILL.md")
    assert "first incorporates a moved base" not in orchestrate
    operations = raw("skills/spec-orchestrate/references/git-operator-operations.md")
    assert_rule(operations, "merges a conflict-free moved target itself", "a base merge after a reported conflict")


def test_orchestrate_completion_runs_the_batch_tests_once_finished_units_include_held_ones() -> None:
    orchestrate = raw("skills/spec-orchestrate/SKILL.md")
    completion = orchestrate.split("## Completion", 1)[1]
    assert_rule(
        completion,
        "Every unit is finished",
        "integrated",
        "blocked with its problem recorded",
        "waiting for a user decision",
        "`needs_input`",
        "continued in `direct`",
    )
    assert_rule(
        completion,
        "**Batch test run**",
        "batch start",
        "no worker turn of the run is still running",
        "once on the base branch HEAD",
        "`just test-affected --base <batch start>`",
        "full fallback",
        "feedback",
        "Every landed unit stays pending",
        "Repair a failing target and recheck",
        "never automatically roll back",
        "integrated no unit runs nothing",
    )


def test_proposal_review_merges_the_base_only_to_resolve_a_refusal() -> None:
    review = raw("skills/spec-review-proposal/SKILL.md")
    assert_rule(review, "merges a conflict-free moved base itself", "only to resolve such a refusal", "rules fix")
    assert "After merging the base into `plan-<slug>`, run" not in review


def test_completion_reference_makes_the_base_merge_conditional() -> None:
    completion = raw("skills/spec/references/completion.md")
    assert_rule(
        completion,
        "Integration checks Git effects only",
        "After landing",
        "steps 6-9 of the `spec-integrate` skill",
    )
    assert "prepare the task branch against the base" not in completion


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_seeded_generated_artifacts_are_presented_and_regenerated_on_the_base(environment: str) -> None:
    """``ADR-generated-conflicts-in-prepared-merge``: the disclosure is acted on after landing or at batch end."""
    integrate = raw("skills/spec-integrate/SKILL.md", environment)
    assert_rule(integrate, "A conflict confined to registered generated files does not refuse", "`generated`")
    assert_rule(
        integrate,
        "7. After bundle changes land",
        "`generated.regenerate` command in the base checkout",
        "commit the regenerated files",
        "batch completion step",
    )
    if environment == "local":
        assert_rule(integrate, "5. Run `devkit integration prepare", "generated artifacts it keeps from one side")


def test_batch_test_run_regenerates_stale_generated_artifacts_first() -> None:
    completion = raw("skills/spec-orchestrate/SKILL.md").split("## Completion", 1)[1]
    assert_rule(
        completion,
        "**Batch test run**",
        "first run `devkit generated check` on the base branch HEAD",
        "`INTEGRATION_GENERATED_SEEDED`",
        "`devkit generated regen <ids>`",
        "commit the regenerated files",
        "Then run the repository's verification",
    )
    operations = raw("skills/spec-orchestrate/references/git-operator-operations.md")
    assert_rule(operations, "`prepare-integration`", "any `generated` artifacts kept from one side")
    assert_rule(operations, "`execute-integration`", "the `generated` disclosure when present", "verification=pending")


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_final_verification_follows_landing_setup_and_regeneration(environment):
    integrate = raw("skills/spec-integrate/SKILL.md", environment)
    markers = [
        "6. After landing",
        "7. After bundle changes land",
        "8. Run required final project checks",
        "9. If setup, imports or final checks fail",
        "10. Report Git effects",
    ]
    assert [integrate.index(marker) for marker in markers] == sorted(integrate.index(marker) for marker in markers)
    assert "saved premerge target SHA" in integrate and "never the target branch compared to itself" in integrate
    assert "full fallback" in integrate and "frontend checks" in integrate
    assert "Do not replay the merge or automatically roll back" in integrate
    assert "verification=pending" in integrate and "delivery complete only after final verification passes" in integrate
    assert "INTEGRATION_RULE_RUNTIME_MISMATCH" not in integrate
    assert "--task-kind" not in integrate and "--claims" not in integrate
