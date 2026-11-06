"""Local-orch verification keeps exact coverage and repair responsibility with the Host."""

from spec_support.bundle_text import raw


def test_local_orch_launch_wait_work_collect_and_repair_order() -> None:
    main = raw("skills/spec-orchestrate/SKILL.md")
    assert "references/isolated-execution.md" in main
    text = raw("skills/spec-orchestrate/references/isolated-execution.md")
    markers = [
        "Run the project's established synchronous",
        "Start the required selected E2E",
        "Start one background",
        "continue independent work",
        "Collect the waiter's",
        "hold further merges",
        "Before completion",
    ]
    assert [text.index(m) for m in markers] == sorted(text.index(m) for m in markers)
    for required in (
        "--tier unit-integration",
        "--tier e2e",
        "--ref <A>",
        "--clean --format json",
        "earliest still-uncovered baseline",
        "generated repairs",
        "explicit empty selection",
        "pass at A proves only A",
        "one outstanding E2E",
        "without merge replay or automatic rollback",
        "no push event",
        "no survival guarantee",
        "never implicitly cancels",
    ):
        assert required in text


def test_wait_notification_does_not_replace_completion_boundary() -> None:
    text = raw("skills/spec-orchestrate/references/isolated-execution.md")
    assert "Keep integration approval and delivery completion with the Host" in text
    assert "git-operator remains a Git lifecycle executor" in text
    assert "no completion delivery" in text
    assert "execution, observer and cleanup outcomes separate" in text
    completion = raw("skills/spec/references/completion.md")
    assert "Required results remain pending" in completion


def test_async_groups_require_actual_coverage_discovery_and_synchronous_fallback() -> None:
    text = raw("skills/spec-orchestrate/references/isolated-execution.md")
    for phrase in (
        "documentation, scripts, runner configuration and CI",
        "retained synchronous command excludes",
        "asynchronous command covers",
        "independently runnable groups",
        "all existing required coverage",
        "directory names or test labels",
        "unseparated, unclear",
        "keep the existing required commands synchronously",
        "Do not require consumers to define E2E",
        "manufacture empty E2E coverage",
        "automatically restructure",
        "duplicate E2E invocation",
        "Devkit repository adoption example",
    ):
        assert phrase in text
    assert text.index("Inspect repository") < text.index("1. Save")
