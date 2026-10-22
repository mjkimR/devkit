---
id: UC-handle-delivery-problems-and-exceptions
title: Handle Delivery Problems and Exceptions
summary: "An AI coding agent separates benign choices and feedback from problems that break the agreed intent, records such a problem in a worker envelope that holds the unit, and recovers with a resolution or the exception stage, or closes the task cleanly."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - development-worker
  - planning-worker
  - User (decides recovery that changes the agreement, closes and exceptions)
status: active
created_at: 2026-10-21
capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DLV-workflow-envelopes
  - CAP-HARN-agent-guidance
  - CAP-WT-task-worktrees
---

# [UC-handle-delivery-problems-and-exceptions] Handle Delivery Problems and Exceptions

## 1. Goal

- **Goal**: The agent stops work only on a problem that breaks the agreed goal, scope or contract, records it, and
  recovers the work or closes the task, so that execution never halts for benign ambiguities, halts when agreed
  boundaries cannot be met, and keeps the evidence a recovery needs without leaving dangling worktrees or corrupting
  the base branch.
- **Scope**: the problem rule and `exception` stage of the delivery workflows, `worker` and `resolution` envelopes
  and the unit hold, closes without a merge, and `devkit worktree finish --discard`.
- **Trigger**: A Planning or Development run meets an obstacle.
- **Preconditions**: The run belongs to a Unit (a proposal or spec bundle) with an agreed intent, executed by a
  worker or by the agent itself in `direct` mode.

---

## 2. Main Success Scenario

1. The executor meets an obstacle and checks it against the agreed goal, scope and contract
   (`CAP-DLV-delivery-workflows`).
2. The executor finds that the obstacle cannot be solved without changing the agreement and records the run's
   `worker` envelope with the problem: its cause, the attempts and the recommended recovery
   (`CAP-DLV-workflow-envelopes`).
3. The executor commits its unfinished work together with the envelope and ends the run without integrating
   (`CAP-DLV-delivery-workflows`).
4. The system holds the Unit: no gate from the problem's stage on passes, the handoff is refused and the merge is
   refused (`CAP-DLV-workflow-envelopes`).
5. The agent decides the recovery inside the approved scope and fixes the root cause itself, or reverts
   (`CAP-DLV-delivery-workflows`).
6. The agent commits the fix together with a `resolution` envelope that names the problem's `worker` envelope
   (`CAP-DLV-workflow-envelopes`).
7. The envelope check reports no hold, and the workflow continues from the stage where the Unit is
   (`CAP-DLV-workflow-envelopes`).

---

## 3. Extensions

- **1a.** The obstacle is an implementation choice inside the agreed intent: the executor takes the recommended
  option and records it with its reason (`CAP-DLV-delivery-workflows`); the use case ends and the work continues.
- **1b.** The obstacle is an improvement that does not block the current work: the executor records it as feedback,
  or as a follow-up draft proposal (`CAP-DLV-delivery-workflows`); the use case ends and the work continues.
- **1c.** The task is `session` depth: the agent reports the problem in the conversation, writes no record and does
  not integrate the change (`CAP-DLV-delivery-workflows`); the use case ends. A `session` task that needs a lasting
  record instead raises its depth (`UC-route-development-intent`, extension \*a).
- **3a.** The envelope or the emergency commit itself cannot be written (a denied approval or record): the executor
  stops, preserves the state and returns `failed` with the cause, the commands tried, the recovery, the actual last
  commit, the dirty paths and the missing records, never an invented committed result; the agent blocks that return
  and owns a recovery run (`CAP-DLV-delivery-workflows`); resumes at step 5.
- **5a.** The agent sends the recovery request to a new worker: the worker that fixes the cause writes the
  `resolution` in the same commit as the fix (`CAP-DLV-workflow-envelopes`); resumes at step 7.
- **5b.** The recovery attempt does not resolve the cause: no `resolution` is written, and the problem stays open and
  keeps the Unit held (`CAP-DLV-workflow-envelopes`); the agent chooses another remedy and resumes at step 5, or
  reports a blocker and the use case ends.
- **5c.** The recovery needs the agreed goal, scope or contract changed, or the direction is unviable: the user
  decides a close (depth escalation to a new draft, supersede or abandon), committed to the base as Backlog work
  after feedback retirement; the agent closes the pull request and remote branch and drops the unmerged branch with
  `devkit worktree finish --discard`, which never removes a worktree with uncommitted changes
  (`CAP-HARN-agent-guidance`, `CAP-WT-task-worktrees`); the use case ends.
- **6a.** The `resolution` names a `worker` envelope that carries no problem: the system refuses with
  `ENVELOPE_REFERENCE_INVALID` and writes nothing (`CAP-DLV-workflow-envelopes`); resumes at step 6.
- **\*a.** A retry cap is exceeded, an execution or tool failure occurs, or a semantic conflict stays unresolved, and
  the agent cannot handle it itself: the workflow enters the `exception` stage, which ends only when the user has
  handled the cause, then returns to the stage that raised it (`CAP-DLV-delivery-workflows`); resumes at step 7.

---

## 4. Postconditions

- **Success guarantee**: Each problem that stopped the work is named by a `resolution` written by whoever fixed it,
  the Unit is no longer held, and the workflow continues from where the Unit stood; or the task is closed with its
  learnings preserved and its unmerged branch dropped.
- **Minimal guarantee**: An unresolved problem keeps the Unit held: no gate passes, no handoff runs and no merge
  lands. The failed range, head, open findings and attempted remedies stay in Git. Nothing is deleted without the
  user's decision, and the base branch receives nothing from a held or closed task.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: A breach of the agreement halts the worker through a problem envelope
- **Covers**: main success scenario
- **Given**: a worker executing a task that meets an insurmountable technical blocker or an unavoidable breach of the
  agreed constraints
- **When**: the worker completes its turn
- **Then**: it writes a `worker` envelope whose `problem` names the cause, the attempts and the recommended recovery,
  commits it with the unfinished work (using `--no-verify` only on an ordinary commit-gate refusal, naming each
  skipped check), and exits without attempting integration

### Scenario 2: A resolution envelope clears an open problem before integration
- **Covers**: main success scenario
- **Given**: an active Unit branch holding an unresolved problem envelope
- **When**: the agent or developer resolves the underlying issue and records a `resolution` envelope that names the
  `worker` envelope file in `resolves:`
- **Then**: `devkit workflow envelope check --unit <dir>` reports no `[BLOCKED]` line, and the gates and the
  integration guard let the Unit progress

### Scenario 3: A choice inside the agreed intent does not stop the work
- **Covers**: 1a
- **Given**: two implementation options that both satisfy the agreed goal, scope and contract
- **When**: the executor reaches the choice
- **Then**: it takes the recommended option and records the reason in `plan.md`, an envelope's assumptions or the
  final report, and writes no problem

### Scenario 4: A non-blocking improvement becomes feedback
- **Covers**: 1b
- **Given**: an improvement outside the current task that does not block it
- **When**: the executor notices it
- **Then**: it records a feedback observation or a follow-up draft proposal, and the workflow continues

### Scenario 5: A session problem is reported, not integrated
- **Covers**: 1c
- **Given**: a `session` task with a problem it cannot solve
- **When**: the agent ends the task
- **Then**: the conversation reports the problem, no envelope or other record is written, and the change is not
  integrated

### Scenario 6: A denied record is never invented
- **Covers**: 3a
- **Given**: a worker whose emergency commit is denied by the host
- **When**: it ends its run
- **Then**: it returns `failed` with the cause, the commands tried, the recovery, the actual last commit SHA, the
  dirty paths and the absent records, and the agent treats the return as blocked

### Scenario 7: A new worker resolves the problem
- **Covers**: 5a
- **Given**: a held Unit and a recovery request the agent passes to a new worker
- **When**: the worker fixes the cause
- **Then**: it commits the fix and `devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml
  --summary "..."` together, and the workflow proceeds

### Scenario 8: A failed recovery keeps the problem open
- **Covers**: 5b
- **Given**: a held Unit whose recovery attempt did not fix the cause
- **When**: the recovering worker ends its turn
- **Then**: it writes no `resolution`, `devkit workflow envelope check --unit <dir>` still prints `[BLOCKED: ...]`,
  and `devkit worktree finish --merge` refuses the branch with `WORKTREE_BLOCKED`

### Scenario 9: An unviable direction closes a task without corrupting history
- **Covers**: 5c
- **Given**: a Development task whose agreed direction the user decides to abandon
- **When**: the agent closes it after copying out what the branch learned
- **Then**: the close is committed to the base as Backlog work, and `devkit worktree finish dev-<slug> --discard`
  removes the clean worktree and deletes the unmerged branch, reporting `merged=no discarded=yes`

### Scenario 10: A resolution must name a problem
- **Covers**: 6a
- **Given**: a `worker` envelope with questions but no problem
- **When**: the agent runs `devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml --summary
  "..."`
- **Then**: the command refuses with `ENVELOPE_REFERENCE_INVALID` and writes no envelope

### Scenario 11: An exceeded retry cap enters the exception stage
- **Covers**: \*a
- **Given**: a Unit at `integrate` whose retry cap is exceeded
- **When**: the agent returns the stage to `exception` with the cause and evidence
- **Then**: the stage stays current until `exception-handled` is given by the user, then returns to `integrate`, and
  no new task is opened to bypass the cap
