"""Delegated write scope, worker-producible baselines, reviewer probes and the sandbox-safe worktree route
(SPEC-delegation-sandbox-guidance).

These tests pin the wording the Host, the workers and the reviewers apply; the documents are rendered for both
execution environments because two of them are templates.
"""

from __future__ import annotations

import pytest
from spec_support.bundle_text import text

PAYLOAD = "skills/spec-delegate/references/payload.md"
PLANNING = "skills/spec/references/planning.md"
WORKTREE = "skills/spec/references/worktree.md"
WORKER = "subagents/development-worker.md"
REVIEWER = "subagents/code-reviewer.md"
ENVIRONMENTS = ["local", "cloud"]


# AC-01
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_a_selected_bundle_change_carries_its_sync_outputs(environment: str) -> None:
    payload = text(PAYLOAD, environment)
    assert "If a `_Boundary:` includes a bundle source the project selects" in payload
    assert "add the tracked files `devkit sync --check` lists for that change" in payload
    assert "`.devkit/installation.json` and the managed `AGENTS.md` block" in payload
    assert "`.devkit/managed/` is ignored and never a write path" in payload
    worker = text(WORKER, environment)
    assert "After editing a bundle source the project selects, run `devkit sync`" in worker
    assert "commit the tracked files it writes, which the payload names in the write scope" in worker
    assert "never edit `.devkit/managed/` by hand" in worker
    assert "A tracked sync output the write scope omits is a problem" in worker


# AC-02
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_a_before_after_outcome_names_a_baseline_a_worker_can_produce(environment: str) -> None:
    planning = text(PLANNING, environment)
    assert "If the proposal states a before/after outcome against the base" in planning
    assert "name a baseline a development worker can produce in its worktree" in planning
    assert "the head with the change disabled, or a measurement Planning takes on the same machine" in planning
    assert "Otherwise state that the Host takes the base measurement" in planning
    worker = text(WORKER, environment)
    assert "Measure a before/after outcome against the baseline the spec names" in worker
    assert "never check out the base" in worker
    assert "report the missing base measurement for the Host in your `worker` envelope" in worker
    assert "Git: commit only; never push, merge, rebase, reset, amend, stash or check out." in worker


# AC-03
def test_the_code_reviewer_may_run_probes_only_in_the_ignored_path() -> None:
    reviewer = text(REVIEWER)
    assert "write throwaway probe tests only under the ignored probe path the payload names" in reviewer
    assert "run the package's test command on them" in reviewer
    assert "Delete every probe before you return, so `git status --short` stays unchanged" in reviewer
    assert "never one of the unit's tests" in reviewer
    assert "Modify, stage and commit nothing outside that probe path." in reviewer
    assert "an ignored probe path inside the worktree for throwaway probe tests" in text(PAYLOAD)


# AC-04
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_worktree_procedure_states_the_sandbox_route(environment: str) -> None:
    worktree = text(WORKTREE, environment)
    assert "### Sandboxed sessions" in worktree
    assert "The task worktree is always `<parent of base>/<base name>-wt-<branch>`" in worktree
    assert "`--workspace-root` only names a directory inside the checkout to start from; it does not move" in worktree
    assert "A linked worktree's commits write the base's shared Git directory" in worktree
    assert "request the host's approval for each operation that needs it" in worktree
    assert "Never move or re-create the worktree elsewhere, copy the repository, or change a host setting" in worktree
