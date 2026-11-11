"""Local-orch verification keeps exact coverage and repair responsibility with the Host."""

import tomllib

import pytest
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection
from spec_support.bundle_text import flat, raw


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
    assert "Required results remain pending" in text


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


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_worker_projection_keeps_native_checks_and_excludes_host_lifecycle(environment: str) -> None:
    source = raw("subagents/development-worker.md", environment)
    contract = read_contract(source.encode(), "development-worker.md")
    projection = render_projection("codex", contract, ".devkit/managed/spec/subagents/development-worker.md")
    assert projection is not None
    instructions = flat(tomllib.loads(projection.decode())["developer_instructions"])
    assert "Run required native checks synchronously in your assigned worktree" in instructions
    assert "including necessary selective E2E" in instructions
    assert "Do not launch or manage the Host exec lifecycle" in instructions
    assert "Common completion guidance does not transfer" in instructions
    assert "devkit exec start" not in instructions
    assert "devkit exec wait" not in instructions


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_common_completion_and_payload_route_by_actor_not_directory(environment: str) -> None:
    completion = flat(raw("skills/spec/references/completion.md", environment))
    assert "Only when acting as the local-orchestrated Host after integration, follow" in completion
    payload = flat(raw("skills/spec-delegate/references/payload.md", environment))
    assert "Keep Host exec launch, wait, cleanup and integrated-result acceptance out of worker payloads" in payload
    host = flat(raw("skills/spec-orchestrate/references/isolated-execution.md", environment))
    assert "only as the local-orchestrated Host" in host
    assert "after landing" in host
    assert "actor and task, not by whether the current directory is a worktree" in host
    assert "Do not copy exec start/wait/cleanup into worker checks" in host
    assert "Direct/session work keeps the project's existing native verification procedure" in host
    assert "no runtime role or cwd restriction" in host
    assert "Do not require consumers to define E2E" in host
