"""Delegated write scope, worker-producible baselines, reviewer probes and the sandbox-safe worktree route
(SPEC-delegation-sandbox-guidance, SPEC-seeded-paths-in-boundaries).

These tests check that each rule the Host, the workers and the reviewers apply is still stated; the documents are
rendered for both execution environments because two of them are templates.
"""

from __future__ import annotations

import re

import pytest
from devkit_agt.features.workflow.services.envelope.authoring import parse_check_flag
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text

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
    payload = raw(PAYLOAD, environment)
    assert_rule(payload, "`_Boundary:`", "bundle source", "write scope", "every tracked path", "`devkit sync` writes")
    assert_rule(payload, "every tracked path", "not only", "`devkit sync --check`", "before the change")
    assert_rule(payload, "every tracked path", "`.devkit/installation.json`", "managed `AGENTS.md` block")
    assert_rule(payload, "`.devkit/managed/`", "ignored", "never a write path")
    assert "add the tracked files `devkit sync --check` lists for that change" not in text(PAYLOAD, environment)
    worker = raw(WORKER, environment)
    assert_rule(worker, "before your first edit", "`devkit sync --check`", "`sync_start`", "`worker` envelope")
    assert_rule(worker, "`sync_start`", "nonzero", "problem", "never a `(sync output)`")
    assert_rule(worker, "after editing a bundle source", "`devkit sync`", "commit every tracked file")
    assert_rule(worker, "`devkit sync`", "`_Boundary:`", "`(sync output)`", "`worker` envelope summary")
    assert_rule(worker, "never edit `.devkit/managed/`")
    assert_rule(worker, "denied", "`.devkit/`", "apart from those outputs")
    assert "A tracked sync output the write scope omits is a problem" not in text(WORKER, environment)


# SPEC-seeded-paths-in-boundaries AC-03
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_host_checks_each_sync_output_against_the_receipt(environment: str) -> None:
    validate = raw(WORKER_RESULTS, environment)
    assert_rule(validate, "`(sync output)`", "`<accepted>`", "`<returned>`", "scope pass", "no evidence")
    assert_rule(validate, "`sync_start`", "`PASS exit=0`")
    assert_rule(validate, "`devkit sync --check`", "`0`", "`<returned>`")
    assert_rule(validate, "`seeded`", "`files`", "returned head", "`.devkit/installation.json`")
    assert_rule(validate, "`seeded`", "`.devkit/installation.json` itself")
    assert_rule(validate, "`seeded`", "managed guidance block", "`AGENTS.md`")


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_documented_sync_start_can_be_recorded_and_verified(environment: str) -> None:
    worker = text(WORKER, environment)
    example = re.search(r'--check "(sync_start=[^"]+)"', worker)
    assert example is not None, "the worker needs an executable sync_start check example"
    key, value = parse_check_flag(example.group(1))
    assert (key, value) == ("sync_start", "PASS exit=0")
    assert_rule(raw(WORKER_RESULTS, environment), "the worker's `sync_start` check", f"`{value}`")


# AC-02
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_a_before_after_outcome_names_a_baseline_a_worker_can_produce(environment: str) -> None:
    planning = raw(PLANNING, environment)
    assert_rule(planning, "before/after outcome", "baseline", "development worker can produce", "worktree")
    assert_rule(planning, "before/after outcome", "change disabled", "Planning takes", "same machine")
    assert_rule(planning, "before/after outcome", "otherwise", "Host takes the base measurement")
    worker = raw(WORKER, environment)
    assert_rule(worker, "before/after outcome", "baseline the spec names", "never check out the base")
    assert_rule(worker, "before/after outcome", "missing base measurement", "Host", "`worker` envelope")
    assert_rule(
        worker, "Git:", "commit only", "never", "push", "merge", "rebase", "reset", "amend", "stash", "check out"
    )


# AC-03
def test_the_code_reviewer_may_run_probes_only_in_the_ignored_path() -> None:
    reviewer = raw(REVIEWER)
    assert_rule(reviewer, "throwaway probe tests", "only under the ignored probe path", "payload names")
    assert_rule(reviewer, "throwaway probe tests", "package's test command")
    # SPEC-crlf-selection-and-viewer-probes AC-04: the viewer's test command for a probe outside src/
    assert_rule(reviewer, "viewer frontend", "`just viewer probe <absolute round directory>`")
    assert_rule(reviewer, "this round's own subdirectory", "payload names", "`<worktree>/scratch/review-NN/`")
    assert_rule(reviewer, "never read or run another round's probes", "never delete a probe")
    assert_rule(
        reviewer, "never delete a probe", "removing the worktree", "ignored", "`git status --short`", "unchanged"
    )
    assert "Delete every probe" not in text(REVIEWER)
    assert_rule(reviewer, "probe", "never one of the unit's tests")
    assert_rule(reviewer, "commit nothing outside that probe path")
    payload = raw(PAYLOAD)
    assert_rule(
        payload, "`code-reviewer`", "ignored probe path", "throwaway probe tests", "preparing one if none exists"
    )
    assert_rule(payload, "`code-reviewer`", "this round's own subdirectory", "`<probe path>/review-NN/`")


# AC-04
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_worktree_procedure_states_the_sandbox_route(environment: str) -> None:
    worktree = raw(WORKTREE, environment)
    assert "### Sandboxed sessions" in worktree
    assert_rule(worktree, "always", "`<parent of base>/<base name>-wt-<branch>`")
    assert_rule(worktree, "`--workspace-root`", "inside the checkout", "does not move")
    assert_rule(worktree, "linked worktree", "commits", "shared Git directory")
    assert_rule(worktree, "writable roots", "request the host's approval", "each operation")
    assert_rule(worktree, "never move or re-create the worktree", "copy the repository", "change a host setting")
