---
id: UC-drive-development-to-integration
title: Drive Development to Integration
summary: "An AI coding agent executes an agreed development task through its workflow stages, runs review and reconcile verification at the chosen activity-effort, and integrates the verified change locally or through a pull request under the project's dev-integration policy."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - code-reviewer
  - reconcile-reviewer
  - development-worker (local-orchestrated mode only)
  - User (gives dev-integration under policy ask)
  - GitHub (pull request route)
status: active
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
   user's conversational approval under `ask`, then invokes `devkit integration integrate` (`CAP-DLV-project-policy`, `CAP-INT-mcp-services`).
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
- **7c.** The user declines the form or objects to the change: nothing is integrated, and an objection about the
  change takes the workflow's return to review (`CAP-INT-mcp-services`, `CAP-DLV-delivery-workflows`); resumes at
  step 3.
- **7d.** Native confirmation is unavailable under `ask`: no authority is inferred; with the user's conversational
  approval the agent finishes the branch through the local CLI path from the base checkout and reruns the cumulative
  check on the result (`CAP-INT-mcp-services`, `CAP-WT-task-worktrees`); resumes at step 9.
- **7e.** A Unit the branch changed holds an unresolved problem, an unanswered question or a malformed worker
  envelope: the gate is held and the merge is refused with `WORKTREE_BLOCKED` (`CAP-DLV-workflow-envelopes`); the use
  case ends and `UC-handle-delivery-problems-and-exceptions` continues.
- **7f.** The source changes the receipt reader and commits a receipt only that reader accepts: the system refuses
  with `INTEGRATION_RECEIPT_READER_CHANGED` and changes nothing; restarting the service does not help, and the agent
  never changes the route itself but, with separately granted authority, finishes the branch through the local CLI
  path run from the source's code (`CAP-INT-mcp-services`); resumes at step 9.
- **7g.** The retained MCP service runs devkit code that differs from the installed code: the system refuses the call
  with `MCP_RUNTIME_STALE` before it runs, and the agent restarts or reconnects the retained service and calls again
  (`CAP-MCP-runtime-registration`, `CAP-INT-mcp-services`); resumes at step 7.
- **8a.** The base moved after the result was built: the system refuses with `INTEGRATION_TARGET_MOVED`, or with
  `INTEGRATION_REQUEST_STALE` for a later request, and changes nothing on the target (`CAP-INT-mcp-services`); resumes
  at step 6.
- **8b.** A cleanup step stays incomplete after the merge: the result is partial with
  `INTEGRATION_CLEANUP_INCOMPLETE`, and the agent resumes the approved request for the remaining steps without a second
  form (`CAP-INT-mcp-services`); resumes at step 9.

---

## 4. Postconditions

- **Success guarantee**: The base branch contains the verified change with its Living Spec reflection, a resolved
  `reconcile.md` and a completed spec (a session: its final report), the task worktree is removed, the local branch is
  deleted or kept as `delete_branch` selects, and the report names the authority: the user's native approval, the
  conversational approval, the pull request's ready state or `policy`.
- **Minimal guarantee**: Nothing reaches the base before `dev-integration`. A declined, cancelled or unavailable
  confirmation changes nothing. A refusal before the merge leaves the target unchanged, and a partial result reports
  its completed steps for resumption.

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
  runs `devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local`
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

### Scenario 13: The Host carries approval to the CLI
- **Covers**: 7d
- **Given**: a verified local change under `dev-integration = "ask"`
- **When**: the user approves the integration in the conversation
- **Then**: the agent runs `devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local`,
  and declares `devkit workflow next --unit <dir> --given dev-integration --given lint-ci-clean --given merged`

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
- **Given**: an approved integration whose merge completed and whose cleanup extension reported `done=false`
- **When**: the agent inspects `devkit worktree status` and verifies the merge landed, then runs
  `devkit worktree finish <branch> --local-only`
- **Then**: only the remaining guarded cleanup runs and the merge is not repeated

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
