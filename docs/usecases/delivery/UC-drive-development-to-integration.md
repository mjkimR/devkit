---
id: UC-drive-development-to-integration
title: Drive Development to Integration
summary: "An AI coding agent develops an explicitly instructed task, verifies and persists evidence, collects optional background verification and integrates locally or by pull request under Host authority and dev-integration policy."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - code-reviewer
  - reconcile-reviewer
  - development-worker (local-orchestrated mode only)
  - git-operator (reusable lifecycle executor in local-orchestrated mode)
  - User (gives dev-integration under policy ask)
  - GitHub (pull request route)
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/integration/cli.py
  - packages/devkit/src/devkit_agt/features/integration/usecases/service.py
  - packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/isolated-execution.md

created_at: 2026-10-21
capabilities:
  - CAP-DLV-delivery-roles
  - CAP-DLV-delivery-workflows
  - CAP-DLV-project-policy
  - CAP-DLV-workflow-envelopes
  - CAP-HARN-agent-guidance
  - CAP-INT-mcp-services
  - CAP-MCP-runtime-registration
  - CAP-WT-task-worktrees
---

# [UC-drive-development-to-integration] Drive Development to Integration

## 1. Goal

- **Goal**: The agent implements an agreed task, verifies it as thoroughly as its `activity-effort` asks, and lands
  it on the base branch, so that the change conforms to the agreed requirements and Living Spec contracts and lands
  cleanly with complete evidence.
- **Scope**: the Development stages of the `sdd-spec-*` and `sdd-session-*` workflows, workflow envelopes, the
  `devkit integration` CLI and `devkit worktree finish`.
- **Trigger**: A spec Unit has an explicitly instructed scope (`UC-route-development-intent`), or a proposal is handed off
  (`UC-plan-and-hand-off-a-proposal`).
- **Preconditions**: The Unit is on its `dev-<slug>` activity branch, in a task worktree or the current checkout.

---

## 2. Main Success Scenario

The main scenario follows a spec Unit at the default `activity-effort` `medium`, in `direct` mode, with
`dev-integration` policy `ask` and the local route.

1. The agent states the Development `activity-effort` with its reason and asks the workflow for the current stage
   (`CAP-DLV-delivery-workflows`).
2. The agent writes the spec, plan and tasks, implements each task within its boundary, runs the affected tests and
   commits at every stage boundary (`CAP-DLV-delivery-workflows`).
3. An initial `code-reviewer` pass verifies the change against the requirements and checks; the agent records its
   findings as a review envelope, fixes them, verifies the fixes and closes the round (`CAP-DLV-delivery-workflows`,
   `CAP-DLV-workflow-envelopes`).
4. The agent writes the Living Spec reflection and `reconcile.md`, and an independent `reconcile-reviewer` verifies
   them; the agent records the verification, resolves the reconcile and completes the spec
   (`CAP-DLV-delivery-workflows`).
5. The agent sweeps feedback and records the final change report with its test, build and lint results
   (`CAP-DLV-delivery-workflows`, `CAP-DLV-workflow-envelopes`).
6. The agent re-verifies only what docs reflection changed and runs the cumulative check; a base that moved since the
   branch was cut needs no merge into the branch (`CAP-DLV-delivery-workflows`, `CAP-INT-mcp-services`).
7. The agent reads the effective policy, prepares the scope, which checks the merge with a moved base, presents the
   verified report, the merged target SHA, the pending final-verification boundary and exact merge/cleanup effects, receives the
   user's conversational approval under `ask`, then requests integration pinned to the prepared scope (`CAP-DLV-project-policy`, `CAP-INT-mcp-services`).
8. The system builds the result commit outside the base checkout, fast-forwards the base onto it without network
   operations, removes the task worktree, deletes the local branch as the policy selects and runs the scoped
   post-finish cleanup (`CAP-INT-mcp-services`, `CAP-WT-task-worktrees`).
9. The Host synchronizes the landed runtime, commits generated changes, runs final required checks on the resulting
   target head and reports delivery completion with checked head and authority (`CAP-DLV-delivery-workflows`).

---

## 3. Extensions

The integration executor's coded refusals this section does not name, and their recoveries, are listed in
`CAP-INT-mcp-services`.

- **1a.** The task is `session` depth: the agent implements, tests and reviews it at the same effort levels, with the
  `code-reviewer` returning a message, writes no spec, envelope, gate record file or reconcile document, commits before
  approval and reports the change, effort, review result and verification in its final response or PR body
  (`CAP-DLV-delivery-workflows`); resumes at step 7 with the session's recorded check outcomes and no Unit metadata in the integration command.
- **1b.** The user instructs `local-orchestrated` mode: a `development-worker` runs the turn in its own `dev-`
  worktree from the stage the workflow names up to the final change report, nests the reviewers and commits at every
  stage boundary; the agent validates the cumulative committed range, and a range it rejects becomes a problem in its
  own `worker` envelope that blocks the Unit (`CAP-DLV-delivery-roles`). The Host reuses git-operator for
  read-only preparation and exact authorized execution, retaining source preparation and acceptance; normal
  integration includes cleanup (`CAP-INT-mcp-services`). Before starting the worker on a `prepare-worktree` or
  `handoff` result, the Host compares its `checks.worker_input` (`head`, `dirty_paths`) with its own Git observation
  and starts the worker only on a clean HEAD (`CAP-DLV-delivery-roles`). Once every unit of the run is finished
  (integrated, blocked with its problem recorded, waiting for a user decision or continued in `direct`) and no worker
  turn is running, the Host runs `devkit generated check` on the base branch HEAD, regenerates and commits any stale
  artifact (`devkit generated regen <ids>`), then runs the repository's integrated-content tests once on that head
  from the batch start and reports the tested head, command and result; a failure keeps every landed unit pending until in-scope target repair and recheck pass
  (`CAP-HARN-agent-guidance`); resumes at step 6.
- **3a.** The effort is `low`: the author reviews the change and self-checks the reconcile, still recorded as review
  and reconcile-check envelopes (`CAP-DLV-delivery-workflows`); resumes at step 5.
- **3b.** The effort is `high`: fresh `code-reviewer` instances review in bounded rounds, and the reconcile
  verification of step 4 runs in the same kind of loop with `reconcile-reviewer`; a loop ends when a round finds
  nothing, or when every fix of the batch is minor by all four minor-fix conditions and is self-verified with its
  reason and evidence (`CAP-DLV-delivery-workflows`); resumes at step 4.
- **3c.** At `high`, the cap round ends with a batch that is not minor, or a P1 recurs: the work stops as a problem in
  the run's `worker` envelope, and a session reports it without integrating (`CAP-DLV-delivery-workflows`); the use
  case ends and `UC-handle-delivery-problems-and-exceptions` continues.
- **4a.** At `medium`, every affected contract and document is identified, agreement with the diff is shown, and no
  cross-component impact or open interpretation remains: the agent omits the initial `reconcile-reviewer` call and
  records its self-check, omission reason and evidence in the reconcile verification (`CAP-DLV-delivery-workflows`);
  resumes at step 5.
- **5a.** One fully authored envelope is the sole pending file: the agent requests its explicit commit, and the system commits exactly that record through ordinary hooks with deterministic identity; an exact clean already-committed record succeeds without a second commit (`CAP-DLV-workflow-envelopes`); resumes at step 6.
- **5b.** An explicit record commit has an invalid file/identity or unsupported repository/dirty state: the system refuses with `ENVELOPE_COMMIT_INVALID` or `ENVELOPE_COMMIT_STATE` before staging. The agent corrects the cause or uses the required combined manual commit for accompanying changes (`CAP-DLV-workflow-envelopes`); resumes at step 5.
- **5c.** Git, signing or a hook rejects an explicit commit with known retained state: the system reports `ENVELOPE_COMMIT_FAILED` and preserves the record and observed index. The agent fixes the cause and retries that same file without authoring another envelope (`CAP-DLV-workflow-envelopes`); resumes at step 5.
- **5d.** Explicit commit effects are uncertain: the system reports `ENVELOPE_COMMIT_UNCERTAIN` and preserves every observed resource. The agent inspects HEAD, index and worktree before any further mutation (`CAP-DLV-workflow-envelopes`); the use case pauses until remaining effects are established.

- **6a.** A retry cap is exceeded or a tool fails during integration: the agent returns to the `exception` stage with
  the cause and evidence, never opening a new task to bypass the cap (`CAP-DLV-delivery-workflows`); the use case ends
  and `UC-handle-delivery-problems-and-exceptions` continues.
- **7a.** The shared base sets `dev-integration` to `auto`: the gate passes by policy once review, reconcile and
  checks hold, and the integration runs without a form, reported as `authority: policy` (`CAP-DLV-delivery-workflows`,
  `CAP-INT-mcp-services`); resumes at step 8.
- **7b.** The policy requires pull requests: the local path is refused with `WORKTREE_PR_POLICY`, and the agent
  integrates through the pull-request route, which publishes the branch, opens or reuses the pull request and merges it
  once the required checks and reviews pass (`CAP-DLV-project-policy`, `CAP-INT-mcp-services`); resumes at step 9.
- **7c.** The user declines conversational approval or objects to the change: nothing is integrated, and an objection about the
  change takes the workflow's return to review (`CAP-INT-mcp-services`, `CAP-DLV-delivery-workflows`); resumes at
  step 3.
- **7d.** Ask execution lacks a prepared digest or its scope changed: the system refuses before integration effects
  with `INTEGRATION_AUTHORITY_REQUIRED` or `INTEGRATION_REQUEST_STALE`; the agent prepares the current scope and
  obtains a fresh conversational decision (`CAP-INT-mcp-services`); resumes at step 7.
- **7e.** A Unit the branch changed holds a problem, pending question or malformed record: the Host detects the hold with the source runtime before approval and stops integration (`CAP-DLV-workflow-envelopes`); the use case ends and `UC-handle-delivery-problems-and-exceptions` continues.
- **7f.** The source upgrades its receipt schema beyond the old runtime: approved Git integration proceeds and reports pending final verification; the Host synchronizes the landed runtime before receipt validation (`CAP-INT-mcp-services`); resumes at step 9.
- **7g.** The CLI runtime is inside the worktree that integration would remove: the system refuses with
  `INTEGRATION_RUNTIME_IN_WORKTREE`; the agent uses a retained runtime outside that worktree, prepares the scope and
  obtains any required conversational decision (`CAP-INT-mcp-services`); resumes at step 7.
- **7h.** The source requires rule imports or CLI APIs absent from the old runtime: integration executes no source-content validation; the Host synchronizes the landed runtime and runs final checks (`CAP-INT-mcp-services`); resumes at step 9.
- **7i.** The prospective Git merge conflicts in a path no understood generated artifact settles: preparation refuses with `WORKTREE_MERGE_CONFLICT`, changing nothing. The Host merges the base into the branch, resolves conflicts and refreshes affected checks (`CAP-INT-mcp-services`); resumes at step 6.
- **7j.** Every conflict of the merge with a moved base is in a file a generated artifact owns, such as
  `.devkit/installation.json`, and no artifact to regenerate reads another conflict: preparation keeps each file at
  its artifact's seed side, validates its Git/policy effects and discloses the artifacts (`generated`,
  `INTEGRATION_GENERATED_SEEDED`); the agent presents them with the scope, and after landing runs the disclosed
  `devkit generated regen <ids>` on the base and commits, or leaves it to the batch completion of a
  `local-orchestrated` run (`CAP-INT-mcp-services`, `CAP-GEN-tracked-artifacts`); resumes at step 7.
- **8a.** The base moved after the result was built: the system refuses with `INTEGRATION_TARGET_MOVED`, or with
  `INTEGRATION_REQUEST_STALE` for a later request, and changes nothing on the target; the agent prepares again on
  the current base without merging it into the branch (`CAP-INT-mcp-services`); resumes at step 7.
- **8b.** A cleanup step stays incomplete after the merge: the partial result reports the failing operation and
  completed effects. The agent inspects Git and PR state, uses guarded finish while the marked local branch remains,
  or runs the owning extension command when Git cleanup already completed. A blocked PR remote deletion preserves
  the local recovery identity; after resolving the blocker the agent prepares and authorizes the remaining scope
  without repeating the merge (`CAP-INT-mcp-services`); resumes at step 9.
- **8c.** The command outcome is unknown: the agent inspects Git, worktree and PR state, then authorizes only the
  remaining effects whose source and cleanup identities can be verified (`CAP-INT-mcp-services`); resumes at step 8.

- **9a.** Setup, imports or final checks fail: delivery stays unfinished while the Host repairs the target and rechecks; no merge replay or automatic rollback occurs (`CAP-DLV-delivery-workflows`); resumes at step 9.

---

## 4. Postconditions

- **Success guarantee**: Required final checks passed on the reported target HEAD using the landed runtime, and the base branch contains the verified change with its Living Spec reflection, a resolved
  `reconcile.md` and a completed spec (a session: its final report), the task worktree is removed, the local branch is
  deleted or kept as `delete_branch` selects, and the report names the authority: Host-carried conversational
  approval or retained-base `policy`, with publication authority for the pull-request route.
- **Minimal guarantee**: Nothing reaches the base before `dev-integration`. Without required conversational
  approval, the Host invokes no integration. A refusal before the merge leaves the target unchanged, and a partial
  result reports completed effects and the remaining scope for recovery from observed state.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: A unit task runs code and reconcile review at medium effort
- **Covers**: main success scenario
- **Given**: an active spec Unit on `dev-<slug>` under `activity-effort = medium`
- **When**: the implementation stage completes and the agent reaches the review and reconcile stages
- **Then**: an initial `code-reviewer` subagent runs and is recorded as a `review` envelope, the agent updates
  `reconcile.md`, and an independent `reconcile-reviewer` verifies contract coverage, recorded as a
  `reconcile-check` envelope

### Scenario 2: Host-carried approval lands the change locally
- **Covers**: main success scenario
- **Given**: a verified `dev-<slug>` branch whose final change report holds, under `dev-integration = "ask"`,
  `pull_request = "auto"` and the default `merge = "no-ff"` and `delete_branch = true`
- **When**: the Host presents the verified report and cleanup scope, the user approves in conversation, and the agent
  runs `devkit integration integrate dev-<slug> --route local --expected-digest <request.digest>`
- **Then**: the base holds the merge commit `chore(merge): integrate dev-<slug> into <base>`, no fetch or push ran,
  the task worktree and the local `dev-<slug>` branch are gone, the scoped post-finish cleanup ran, and the agent
  passes `--given dev-integration` to later `devkit workflow next` calls

### Scenario 3: A session task completes without durable artifacts
- **Covers**: 1a
- **Given**: a task classified as `planning-depth = session` and `activity-effort = low`
- **When**: the agent implements the changes, runs the affected tests and reviews its own work
- **Then**: no `spec.md`, envelope file, gate record file or reconcile document is created, and the agent reports
  the verification results in its final response

### Scenario 4: A worker's committed range is validated before integration
- **Covers**: 1b
- **Given**: `local-orchestrated` mode on the user's instruction and a `development-worker` that returned a committed
  `dev-<slug>` range
- **When**: the agent inspects the range with `devkit spec worker inspect` and finds a path outside the allowed scope
- **Then**: the agent records the rejection as a problem in its own `worker` envelope, and the Unit is blocked from
  review and integration without discarding anything

### Scenario 5: Low effort keeps the review records
- **Covers**: 3a
- **Given**: a spec Unit under `activity-effort = low`
- **When**: the agent completes `review-refine` and `living-spec-draft`
- **Then**: a `review` envelope states the self-review and a `reconcile-check` envelope records the self-check, and no
  reviewer subagent ran

### Scenario 6: A bounded high-effort review loop ends on minor fixes
- **Covers**: 3b
- **Given**: a spec Unit under `activity-effort = high`
- **When**: a review round reports findings that the implementer resolves entirely through fixes meeting all four
  minor-fix conditions
- **Then**: the loop ends without another reviewer call, and the `reverify` envelope that closes the round records
  the self-verification reason and evidence

### Scenario 7: A non-minor batch at the cap round stops the work
- **Covers**: 3c
- **Given**: a spec Unit under `activity-effort = high` whose third round after the initial review returns a batch
  that is not minor
- **When**: the implementer ends the run
- **Then**: its `worker` envelope carries a `problem` naming the open findings, and the Unit is held from integration

### Scenario 8: Medium effort may self-verify the reconcile
- **Covers**: 4a
- **Given**: a medium-effort change confined to one package and one capability area whose affected contracts are all
  identified
- **When**: the agent completes the reconcile without calling `reconcile-reviewer`
- **Then**: the `reconcile-check` envelope records the self-check, the omission reason and the verification evidence

### Scenario 9: A retry cap sends integration to the exception stage
- **Covers**: 6a
- **Given**: the `integrate` stage, where a retry cap is exceeded or a tool fails
- **When**: the agent takes the stage's return to `exception`
- **Then**: the exception report carries the cause and evidence, the stage stays open until the user handles the cause
  (`exception-handled`), and no new task is opened

### Scenario 10: Policy authorizes local integration and scoped cleanup
- **Covers**: 7a
- **Given**: a completed task branch whose required source checks passed, under `[workflow.approvals]
  dev-integration = "auto"` in the shared base
- **When**: the agent runs `devkit integration integrate dev-<slug> --route local`
- **Then**: no form is shown, the result reports `authority: policy`, the base is advanced without fetch or push, the
  task worktree is removed, the local `dev-<slug>` branch is deleted and the scoped post-finish cleanup runs, and
  `devkit workflow next` lists `[GATE_PASSED: dev-integration ... source=policy]`

### Scenario 11: Pull request policy integrates through a remote pull request
- **Covers**: 7b
- **Given**: a project configured with `[worktree] pull_request = "required"`
- **When**: the agent attempts `devkit worktree finish --merge` or local integration
- **Then**: the local command is refused with `WORKTREE_PR_POLICY`, and the agent integrates through
  `devkit integration integrate` with `--route pull-request`, which merges the pull request only after the required checks
  and reviews pass

### Scenario 12: A conversational objection changes nothing
- **Covers**: 7c
- **Given**: a verified change under `dev-integration = "ask"`
- **When**: the user objects to the change in conversation
- **Then**: the agent does not invoke integration and returns with `devkit workflow return --unit <dir> --to
  review-refine --note "..."`

### Scenario 13: Ask execution refuses a missing or changed prepared scope
- **Covers**: 7d
- **Given**: a verified local change under `dev-integration = "ask"` whose prepared digest is missing or whose source
  changed after preparation
- **When**: the agent invokes integration without the digest or with the earlier digest
- **Then**: the system refuses with `INTEGRATION_AUTHORITY_REQUIRED` or `INTEGRATION_REQUEST_STALE` before merge or
  cleanup, and the Host prepares the current scope and obtains a fresh decision

### Scenario 14: A held Unit is not merged
- **Covers**: 7e
- **Given**: a branch whose Unit holds a `worker` envelope problem that no `resolution` names
- **When**: the agent runs `devkit worktree finish dev-<slug> --merge`
- **Then**: the merge is refused with `WORKTREE_BLOCKED`, one detail per unresolved problem, and nothing changes

### Scenario 15: A moved base refuses the fast-forward
- **Covers**: 8a
- **Given**: an approved local integration whose base branch receives another commit after the result commit is built
- **When**: the approving call reaches the fast-forward
- **Then**: it refuses with `INTEGRATION_TARGET_MOVED`, the merge step is `not_run`, the target is unchanged, and the
  agent prepares a new integration on the current base

### Scenario 16: An incomplete cleanup recovers from observed state
- **Covers**: 8b
- **Given**: an approved integration whose merge and Git cleanup completed but whose scoped cleanup extension
  reported `done=false`
- **When**: the agent inspects the completed effects and runs that extension's owning command against its exact
  reported target, such as `devkit spec proposal prune <slug>`
- **Then**: only that scoped cleanup runs and the merge is not repeated

### Scenario 17: A changed receipt reader is verified after landing
- **Covers**: 7f
- **Given**: a verified `dev-<slug>` branch that changes the receipt reader and commits a receipt accepted only by that reader
- **When**: the Host integrates the explicit branch under retained Git authority
- **Then**: Git effects land with `verification=pending`, and the Host validates the receipt with the synchronized landed runtime before reporting completion

### Scenario 18: A receipt upgrade waits for landed verification
- **Covers**: 7f
- **Given**: a source receipt unsupported by the retained runtime
- **When**: the Host integrates the verified branch under existing authority
- **Then**: Git effects land with verification pending and receipt validation runs only after landed runtime synchronization

### Scenario 19: A worktree-owned runtime cannot remove itself
- **Covers**: 7g
- **Given**: the CLI interpreter is inside the worktree selected for cleanup
- **When**: the Host requests integration
- **Then**: the system refuses with `INTEGRATION_RUNTIME_IN_WORKTREE`, and the Host uses a retained runtime outside
  that worktree before preparing and authorizing the scope again

### Scenario 20: A blocked remote deletion retains fresh-invocation recovery
- **Covers**: 8b
- **Given**: PR integration merged once but remote deletion is blocked by a dependent PR
- **When**: the Host resolves the blocker, inspects the merged PR and remote ref, prepares the remaining scope and
  retries with the new digest
- **Then**: remote deletion completes before local worktree and branch deletion, and the PR is not merged again

### Scenario 21: Source rule imports use the landed runtime
- **Covers**: 7h
- **Given**: source rules importing a module absent from the retained runtime
- **When**: the Host integrates the branch
- **Then**: integration performs no old-runtime rule evaluation and reports pending verification; the Host synchronizes dependencies and runs final checks in fresh processes

### Scenario 22: Local orchestration reuses its lifecycle executor
- **Covers**: 1b
- **Given**: a verified local-orchestrated Unit and an existing git-operator in this conversation/repository
- **When**: the Host requests preparation and later delegates exact authorized integration effects
- **Then**: the same identity handles both jobs with repeated current refs/authority; the Host retains decisions and
  accepts observed effects, and completed integration dispatches no redundant cleanup

### Scenario 23: Zero-exit partial cleanup remains incomplete in the role result
- **Covers**: 1b, 8b
- **Given**: delegated integration reports exit zero with `INTEGRATION_CLEANUP_INCOMPLETE` and requested cleanup remains
- **When**: git-operator inspects effects and finds an active writer or missing cleanup authority
- **Then**: it preserves the resource and returns needs_input with original CLI status/exit and completed/remaining
  effects; the Host quiesces writers and decides the supported remainder before any cleanup

### Scenario 24: Commit one authored record
- **Covers**: 5a
- **Given**: a valid authored final-report is the sole pending file after verified work is committed
- **When**: the agent requests its explicit commit
- **Then**: exactly that path/blob is added on the same branch through ordinary hooks, actual final HEAD is reported and evidence SHAs stay unchanged

### Scenario 25: Repeat a committed record
- **Covers**: 5a
- **Given**: the selected record has exact unchanged bytes in HEAD and the checkout is clean
- **When**: the agent repeats explicit commit
- **Then**: the result is already_committed with null subject and HEAD stays unchanged

### Scenario 26: Refuse an ineligible record commit
- **Covers**: 5b
- **Given**: an explicit commit selects a skeleton, modified history, partially staged record, or a checkout with unrelated dirty paths
- **When**: the agent invokes the command
- **Then**: it reports ENVELOPE_COMMIT_INVALID or ENVELOPE_COMMIT_STATE with the exact target and changes neither index nor HEAD

### Scenario 27: Retry a rejected hook
- **Covers**: 5c
- **Given**: a hook rejected an explicit record commit and left that exact record staged with unchanged HEAD/reference
- **When**: the agent fixes the cause and retries the same file
- **Then**: one commit is created with no new envelope sequence and no duplicate commit on repeat

### Scenario 28: Inspect uncertain effects
- **Covers**: 5d
- **Given**: a post-commit hook changes content or switches the symbolic branch
- **When**: the agent requests explicit record commit
- **Then**: it reports ENVELOPE_COMMIT_UNCERTAIN, preserves the hook's observed effects and directs inspection before further mutation

### Scenario 29: A conflict-free moved base integrates without a base merge
- **Covers**: 6, 7, 8
- **Given**: a verified task branch whose base gained an unrelated commit after the branch was cut
- **When**: the agent prepares and, after the user's approval, integrates it on the local route
- **Then**: preparation names the moved base as `target_sha`, integration completes, and the landed merge has the
  moved base as first and the approved source as second parent; the branch received no base merge

### Scenario 30: A conflicting moved base refuses at preparation
- **Covers**: 7i
- **Given**: a task branch and a base that changed the same lines of one file no generated artifact owns since the
  branch was cut
- **When**: the agent prepares the integration
- **Then**: it refuses with `WORKTREE_MERGE_CONFLICT`, the base, the branch and the worktree are unchanged, and the
  agent merges the base into the branch to resolve the conflict before preparing again

### Scenario 31: A local-orchestrated batch ends with one test run
- **Covers**: 1b
- **Given**: a `local-orchestrated` run that integrated two units and holds a third waiting for a user decision
- **When**: no worker turn of the run is still running
- **Then**: the Host runs `devkit generated check` on the base branch HEAD and commits `devkit generated regen <ids>`
  for any stale artifact, then runs `just test-affected --base <batch start>` (this repository's selector) once on
  that head and reports the head, the command and the result; a failure is recorded as feedback

### Scenario 32: A conflict only in the installation receipt is seeded and disclosed
- **Covers**: 7j
- **Given**: a task branch and a moved base that both changed `.devkit/installation.json` and nothing else in conflict
- **When**: the agent prepares and, after the user's approval, integrates on the local route
- **Then**: preparation and integration complete with `seeded=devkit-receipt` and an `INTEGRATION_GENERATED_SEEDED`
  warning naming `uv run devkit generated regen devkit-receipt`, the landed tree keeps the base's receipt and equals
  the prepared result, and the branch received no base merge

### Scenario 33: Final failure is repaired on the target
- **Covers**: 9a
- **Given**: confirmed landing and cleanup followed by a failing final check
- **When**: the Host repairs the target within scope and reruns required checks
- **Then**: only the passing resulting HEAD is reported complete, and the merge is neither replayed nor automatically rolled back

## Local-orchestrated asynchronous verification

Before choosing asynchronous verification, the Host inspects repository documentation, scripts, runner configuration and CI for actual required commands and coverage. It establishes independently runnable groups and verifies what the retained synchronous command excludes and what the asynchronous command covers, preserving all existing required coverage. Directory names and test labels establish neither E2E existence, cost nor independent runnability. If verification is unseparated, unclear or has no independently runnable subset, the Host keeps the existing required commands synchronously. Consumers need no E2E tier; guidance neither manufactures empty coverage nor automatically restructures verification. Overlapping broad commands do not establish reduced blocking by adding a duplicate E2E run. Devkit's selector commands are its own adoption example.

Where independent required groups are established, after landing and environment/artifact synchronization the Host performs the project's synchronous verification group, starts selected E2E at the fixed landed commit and observes it in the background while continuing independent work (`CAP-HARN-agent-guidance`, `CAP-DLV-delivery-workflows`). It collects execution and optional cleanup outcomes through the execution tool; missing notification requires later inspection. A failure/unknown result holds further merges at the next result check and prioritizes repair. Completion collects current-HEAD required results or explicit empty E2E selection for the full uncovered interval, preserving exact tested SHAs and generated-repair coverage.
