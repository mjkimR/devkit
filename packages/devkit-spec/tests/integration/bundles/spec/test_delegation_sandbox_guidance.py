"""Delegated write scope, worker-producible baselines, reviewer probes and the sandbox-safe worktree route
(SPEC-delegation-sandbox-guidance, SPEC-seeded-paths-in-boundaries).

These tests pin the wording the Host, the workers and the reviewers apply; the documents are rendered for both
execution environments because two of them are templates.
"""

from __future__ import annotations

import re

import pytest
from devkit_agt.features.workflow.services.envelope.authoring import parse_check_flag
from spec_support.bundle_text import text

PAYLOAD = "skills/spec-delegate/references/payload.md"
PLANNING = "skills/spec/references/planning.md"
WORKTREE = "skills/spec/references/worktree.md"
WORKER = "subagents/development-worker.md"
WORKER_RESULTS = "skills/spec-delegate/references/worker.md"
REVIEWER = "subagents/code-reviewer.md"
ENVIRONMENTS = ["local", "cloud"]


# AC-01; SPEC-seeded-paths-in-boundaries AC-01, AC-02
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_a_selected_bundle_change_carries_its_sync_outputs(environment: str) -> None:
    payload = text(PAYLOAD, environment)
    assert "If a `_Boundary:` includes a bundle source the project selects" in payload
    assert "the write scope admits, as a class, every tracked path `devkit sync` writes in the worktree" in payload
    assert "not only the files `devkit sync --check` lists before the change" in payload
    assert "`.devkit/installation.json` and the managed `AGENTS.md` block" in payload
    assert "`.devkit/managed/` is ignored and never a write path" in payload
    assert "add the tracked files `devkit sync --check` lists for that change" not in payload
    worker = text(WORKER, environment)
    assert "Before your first edit, run `devkit sync --check`" in worker
    assert "record its exit as the `sync_start` check of your `worker` envelope" in worker
    assert "a problem and never a `(sync output)`" in worker
    assert "After editing a bundle source the project selects, run `devkit sync`" in worker
    assert "commit every tracked file it writes" in worker
    assert (
        "in the owning task's `_Boundary:` with the note `(sync output)` and in your `worker` envelope summary"
        in worker
    )
    assert "Never edit `.devkit/managed/` by hand" in worker
    assert "`.devkit/` (apart from those outputs)" in worker
    assert "A tracked sync output the write scope omits is a problem" not in worker


# SPEC-seeded-paths-in-boundaries AC-03
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_host_checks_each_sync_output_against_the_receipt(environment: str) -> None:
    validate = text(WORKER_RESULTS, environment)
    assert "Each `(sync output)` entry `tasks.md` gained between `<accepted>` and `<returned>`" in validate
    assert "its scope pass is no evidence for that entry" in validate
    assert "the worker's `sync_start` check is `PASS exit=0`" in validate
    assert "`devkit sync --check` exits `0` on `<returned>`" in validate
    assert "is under `seeded` or `files` in the returned head's `.devkit/installation.json`" in validate
    assert "is `.devkit/installation.json` itself" in validate
    assert "the file that holds the managed guidance block (`AGENTS.md`" in validate


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_documented_sync_start_can_be_recorded_and_verified(environment: str) -> None:
    worker = text(WORKER, environment)
    example = re.search(r'--check "(sync_start=[^"]+)"', worker)
    assert example is not None, "the worker needs an executable sync_start check example"
    key, value = parse_check_flag(example.group(1))
    assert (key, value) == ("sync_start", "PASS exit=0")
    assert f"the worker's `sync_start` check is `{value}`" in text(WORKER_RESULTS, environment)


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
    assert (
        "write throwaway probe tests through the shell only under the ignored probe path the payload names" in reviewer
    )
    assert "run the package's test command on them" in reviewer
    # SPEC-crlf-selection-and-viewer-probes AC-04: the viewer's test command for a probe outside src/
    assert "for a viewer frontend change that command is `just viewer probe <absolute round directory>`" in reviewer
    assert (
        "in this round's own subdirectory (the one the payload names, for example `<worktree>/scratch/review-NN/`)"
        in (reviewer)
    )
    assert "Never read or run another round's probes, and never delete a probe" in reviewer
    assert (
        "leave it for removing the worktree to clean; the path is ignored, so `git status --short` stays unchanged"
        in (reviewer)
    )
    assert "Delete every probe" not in reviewer
    assert "never one of the unit's tests" in reviewer
    assert "Modify, stage and commit nothing outside that probe path." in reviewer
    payload = text(PAYLOAD)
    assert (
        "an ignored probe path inside the worktree for throwaway probe tests, preparing one if none exists" in payload
    )
    assert "and this round's own subdirectory of it (for example `<probe path>/review-NN/`)" in payload


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
