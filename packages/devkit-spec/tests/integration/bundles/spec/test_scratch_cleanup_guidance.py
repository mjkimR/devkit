"""Workers leave ignored scratch files to worktree removal (SPEC-feedback-guidance-and-scope, AC-01 and AC-02)."""

from __future__ import annotations

from pathlib import Path

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import flat, raw, text

PAYLOAD = "skills/spec-delegate/references/payload.md"
WORKER = "subagents/development-worker.md"
PLANNING_WORKER = "subagents/planning-worker.md"
ENVIRONMENTS = ["local", "cloud"]
WORKFLOWS = Path(__file__).resolve().parents[6] / "docs/capabilities/delivery/CAP-DLV-delivery-workflows.md"


# AC-01
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_development_worker_leaves_scratch_files_to_worktree_removal(environment: str) -> None:
    worker = raw(WORKER, environment)
    assert_rule(worker, "authored scratch files", "ignored path inside the worktree", "leave them")
    assert_rule(worker, "authored scratch files", "removing the worktree cleans them", "never delete them yourself")
    assert_rule(worker, "pytest-managed fixtures (`tmp_path`)", "isolated system temporary directory")
    assert_rule(worker, "`--basetemp`", "command line", "not through `PYTEST_ADDOPTS`")


# AC-02
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_payloads_never_ask_for_create_then_delete(environment: str) -> None:
    payload = raw(PAYLOAD, environment)
    assert_rule(payload, "never ask a worker", "delete", "scratch file or fixture", "it created")
    assert_rule(payload, "scratch file", "removing the worktree", "`devkit worktree finish`", "integration cleanup")
    assert_rule(raw(PLANNING_WORKER, environment), "removing the worktree", "never delete them yourself")
    assert "Remove them before the last commit" not in text(PLANNING_WORKER, environment)


def test_the_delivery_workflow_contract_mirrors_the_guidance() -> None:
    contract = flat(WORKFLOWS.read_text(encoding="utf-8"))
    assert "The worker leaves temporary files and throwaway repositories" in contract
    assert "removing the Planning worktree cleans them" in contract
    assert "A payload never asks a worker, Planning or Development, to delete a scratch file or fixture" in contract
    assert "removes temporary files and throwaway repositories" not in contract
