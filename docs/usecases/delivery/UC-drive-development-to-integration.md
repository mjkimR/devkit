---
id: UC-drive-development-to-integration
title: Drive Development to Integration
summary: "An AI coding agent implements an agreed task through workflow stages, completes effort-appropriate review and reconcile checks, obtains Host approval when required, then integrates locally or by pull request under dev-integration policy."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - code-reviewer
  - reconcile-reviewer
  - development-worker (local-orchestrated mode only)
  - User (gives dev-integration under policy ask)
  - GitHub (pull request route)
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/integration/cli.py
  - packages/devkit/src/devkit_agt/features/integration/usecases/service.py
created_at: 2026-10-21
capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DLV-project-policy
  - CAP-DLV-workflow-envelopes
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
- **Trigger**: A spec Unit's `plan-intent` is recorded (`UC-route-development-intent`), or a proposal is handed off
  (`UC-incubate-and-hand-off-a-proposal`).
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
6. The agent merges the base into the branch, re-verifies only what conflict resolution and docs reflection changed,
   rechecks the reconcile targets and runs the cumulative check (`CAP-DLV-delivery-workflows`).
7. The agent reads the effective policy, presents the verified report and exact merge/cleanup effects, receives the
   user's conversational approval under `ask`, then requests integration pinned to the prepared scope (`CAP-DLV-project-policy`, `CAP-INT-mcp-services`).
8. The system builds the result commit outside the base checkout, fast-forwards the base onto it without network
   operations, removes the task worktree, deletes the local branch as the policy selects and runs the scoped
   post-finish cleanup (`CAP-INT-mcp-services`, `CAP-WT-task-worktrees`).
9. The agent declares the approval and the runner checks to the workflow and reports the result with its authority
   (`CAP-DLV-delivery-workflows`).

---

## 3. Extensions

The integration executor's coded refusals this section does not name, and their recoveries, are listed in
`CAP-INT-mcp-services`.

- **1a.** The task is `session` depth: the agent implements, tests and reviews it at the same effort levels, with the
  `code-reviewer` returning a message, writes no spec, envelope, gate record file or reconcile document, commits before
  approval and reports the change, effort, review result and verification in its final response or PR body
  (`CAP-DLV-delivery-workflows`); resumes at step 7 with the session's declared claims in place of a Unit.
- **1b.** The user instructs `local-orchestrated` mode: a `development-worker` runs the turn in its own `dev-`
  worktree from the stage the workflow names up to the final change report, nests the reviewers and commits at every
  stage boundary; the agent validates the cumulative committed range, and a range it rejects becomes a problem in its
  own `worker` envelope that blocks the Unit (`CAP-DLV-delivery-workflows`); resumes at step 6.
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
- **7e.** A Unit the branch changed holds an unresolved problem, an unanswered question or a malformed worker
  envelope: the gate is held and the merge is refused with `WORKTREE_BLOCKED` (`CAP-DLV-workflow-envelopes`); the use
  case ends and `UC-handle-delivery-problems-and-exceptions` continues.
- **7f.** The source changes the receipt reader and commits a receipt only that reader accepts: the system refuses
  with `INTEGRATION_RECEIPT_READER_CHANGED` and changes nothing; restarting the service does not help, and the agent
  never changes the route itself but, with separately granted authority, finishes the branch through the local CLI
  path run from the source's code (`CAP-INT-mcp-services`); resumes at step 9.
- **7g.** The CLI runtime is inside the worktree that integration would remove: the system refuses with
  `INTEGRATION_RUNTIME_IN_WORKTREE`; the agent uses a retained runtime outside that worktree, prepares the scope and
  obtains any required conversational decision (`CAP-INT-mcp-services`); resumes at step 7.
- **7h.** A synchronized rule of the source, or of the result at a build, imports a module or name the running runtime
  does not provide, such as the implementation module of a rule the branch adds: the system refuses with
  `INTEGRATION_RULE_RUNTIME_MISMATCH` before readiness (after 7f and 7g) and changes nothing; the source needs no change, and the agent,
  with separately granted authority, runs integration from the base checkout with a runtime built from the source's
  code outside the worktree (`CAP-INT-mcp-services`); resumes at step 7.
- **8a.** The base moved after the result was built: the system refuses with `INTEGRATION_TARGET_MOVED`, or with
  `INTEGRATION_REQUEST_STALE` for a later request, and changes nothing on the target (`CAP-INT-mcp-services`); resumes
  at step 6.
- **8b.** A cleanup step stays incomplete after the merge: the partial result reports the failing operation and
  completed effects. The agent inspects Git and PR state, uses guarded finish while the marked local branch remains,
  or runs the owning extension command when Git cleanup already completed. A blocked PR remote deletion preserves
  the local recovery identity; after resolving the blocker the agent prepares and authorizes the remaining scope
  without repeating the merge (`CAP-INT-mcp-services`); resumes at step 9.
- **8c.** The command outcome is unknown: the agent inspects Git, worktree and PR state, then authorizes only the
  remaining effects whose source and cleanup identities can be verified (`CAP-INT-mcp-services`); resumes at step 8.

---

## 4. Postconditions

- **Success guarantee**: The base branch contains the verified change with its Living Spec reflection, a resolved
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
  runs `devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local --expected-digest <request.digest>`
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
- **Given**: a completed task branch satisfying every readiness check under `[workflow.approvals]
  dev-integration = "auto"` in the shared base
- **When**: the agent runs `devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local`
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
  agent merges the base into the branch and requests a new integration

### Scenario 16: An incomplete cleanup recovers from observed state
- **Covers**: 8b
- **Given**: an approved integration whose merge and Git cleanup completed but whose scoped cleanup extension
  reported `done=false`
- **When**: the agent inspects the completed effects and runs that extension's owning command against its exact
  reported target, such as `devkit spec proposal prune <slug>`
- **Then**: only that scoped cleanup runs and the merge is not repeated

### Scenario 17: A changed receipt reader refuses CLI integration
- **Covers**: 7f
- **Given**: a `dev-<slug>` branch whose range changes a receipt reader module and whose committed receipt only the
  changed reader accepts, under a retained service built from the target
- **When**: the agent runs `devkit integration integrate`
- **Then**: it refuses with `INTEGRATION_RECEIPT_READER_CHANGED`, the target is unchanged, and the agent resolves the
  receipt mismatch before obtaining fresh Host authority and retrying

### Scenario 18: An unknown result is inspected before retry
- **Covers**: 8c
- **Given**: the CLI result is unknown after a local merge or pull-request mutation
- **When**: the agent inspects Git, `devkit worktree status` and the pull request state
- **Then**: it invokes only a remaining operation whose target and cleanup identity are verified, and never repeats an
  unknown mutation or removes an unrelated worktree

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

### Scenario 21: A rule that needs the source's code is named before readiness
- **Covers**: 7h
- **Given**: a `dev-<slug>` branch whose committed receipt lists a synchronized rule importing a module the branch adds,
  under a retained runtime built from the target
- **When**: the Host runs `devkit integration prepare` or `integrate`
- **Then**: it refuses with `INTEGRATION_RULE_RUNTIME_MISMATCH` naming the rule file and the missing import, the
  readiness provider does not run, the target is unchanged, and the Host retries with a runtime built from the source's
  code after separately granted authority
