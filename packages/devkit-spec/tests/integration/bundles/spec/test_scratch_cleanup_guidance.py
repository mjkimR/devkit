"""Workers leave ignored scratch files to worktree removal (SPEC-feedback-guidance-and-scope, AC-01 and AC-02)."""

from __future__ import annotations

from pathlib import Path

import pytest
from spec_support.bundle_text import flat, text

PAYLOAD = "skills/spec-delegate/references/payload.md"
WORKER = "subagents/development-worker.md"
PLANNING_WORKER = "subagents/planning-worker.md"
ENVIRONMENTS = ["local", "cloud"]
WORKFLOWS = Path(__file__).resolve().parents[6] / "docs/capabilities/delivery/CAP-DLV-delivery-workflows.md"


# AC-01
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_development_worker_leaves_scratch_files_to_worktree_removal(environment: str) -> None:
    worker = text(WORKER, environment)
    assert "Keep authored scratch files in an ignored path inside the worktree and leave them there" in worker
    assert "removing the worktree cleans them, so never delete them yourself" in worker
    assert "Pytest-managed fixtures (`tmp_path`) may use an isolated system temporary directory" in worker
    assert "pass `--basetemp` on the command line, not through `PYTEST_ADDOPTS`" in worker


# AC-02
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_payloads_never_ask_for_create_then_delete(environment: str) -> None:
    payload = text(PAYLOAD, environment)
    assert "Never ask a worker to delete a scratch file or fixture it created" in payload
    assert "removing the worktree (`devkit worktree finish` or integration cleanup) cleans them" in payload
    planning = text(PLANNING_WORKER, environment)
    assert "Leave them there for removing the worktree to clean, never delete them yourself" in planning
    assert "Remove them before the last commit" not in planning


def test_the_delivery_workflow_contract_mirrors_the_guidance() -> None:
    contract = flat(WORKFLOWS.read_text(encoding="utf-8"))
    assert "The worker leaves temporary files and throwaway repositories" in contract
    assert "removing the Planning worktree cleans them" in contract
    assert "A payload never asks a worker, Planning or Development, to delete a scratch file or fixture" in contract
    assert "removes temporary files and throwaway repositories" not in contract
