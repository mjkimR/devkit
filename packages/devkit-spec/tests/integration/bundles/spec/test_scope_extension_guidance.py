"""Both shipped environments preserve typed extension evidence and independent sync-output admission."""

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_worker_three_tiers_and_final_record(environment: str) -> None:
    worker = raw("subagents/development-worker.md", environment)
    for tokens in [
        ("tier a", "initial payload", "literal", "directory prefixes", "globs"),
        ("tier b", "exact adjacent file", "existing task and ac", "first source commit", "scope extension:"),
        ("sole final", "emergency", "--scope-extensions-file", "positive checklist", "scanner ordinal"),
        ("reason", "nonempty", "without parentheses"),
        ("adjacent means", "documented feature", "test mirror"),
        ("existing living spec", "affected contract id"),
        ("tier c", "host projections", "architecture/dependency", "ci/release", "outside the repository"),
        ("explicit payload denies", "prevail"),
        ("tests", "never weakened"),
        ("sync output", "independent path class"),
        ("same rules", "local and cloud", "inspect remains optional", "hub"),
    ]:
        assert_rule(worker, *tokens)


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_review_and_host_check_annotation_before_record_and_final_agreement(environment: str) -> None:
    assert_rule(
        raw("skills/spec-review/SKILL.md", environment),
        "`_boundary:`",
        "initial payload",
        "writes outside",
        "(references/scope-extension.md)",
    )
    review = raw("skills/spec-review/references/scope-extension.md", environment)
    assert_rule(review, "scope extension:", "task", "ac", "before", "record exists")
    assert_rule(review, "p2", "p1", "explicit payload denies", "test weakening")
    assert_rule(review, "initial payload", "task diff", "omitted annotation", "material finding")
    assert_rule(review, "final host/inspect", "changed", "review")
    assert_rule(
        raw("subagents/code-reviewer.md", environment), "follow the steps", "spec-review/skill.md", "diff_scope"
    )
    host = raw("skills/spec-delegate/references/worker.md", environment)
    assert_rule(host, "prior-turn records", "retained", "highest worker sequence", "historical records alone")
    assert_rule(host, "checks.scope_extensions", "structural", "custom protected", "optional", "cloud")
    assert_rule(host, "--scope", "--scope-file", "replace", "never union")
    assert_rule(host, "each `(sync output)` entry", "scope pass", "no evidence")
    assert_rule(host, "sync_start", "PASS exit=0")
    assert_rule(host, "seeded", "files", "receipt")
