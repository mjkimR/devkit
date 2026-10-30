---
id: UC-route-development-intent
title: Route a Development Request to the Right Workflow
summary: "Routes SDD development requests by task-kind, planning-depth and activity-effort after shared approach inspection; adaptive development follows its own guidance without implicit SDD Units."
area: delivery
primary_actor: AI coding agent (Host)
supporting_actors:
  - User (confirms the classification and answers plan-intent)
status: active
created_at: 2026-10-13
capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DLV-delivery-workflows
  - CAP-DLV-spec-bundles
  - CAP-DLV-project-policy
  - CAP-WT-task-worktrees
---

# [UC-route-development-intent] Route a Development Request to the Right Workflow

## 1. Goal

- **Goal**: The agent puts a development request on exactly one delivery workflow with the user's intent agreed, so
  that work that needs nothing settled stays light, contract changes get a spec, open directions get a proposal, and
  every approval the user owns is asked at the right moment instead of being inferred or skipped.
- **Scope**: the `spec` skill's routing, `devkit spec policy`, `devkit spec new` and the delivery workflow
  definitions of `devkit-spec`.
- **Trigger**: The user states a development intent (`/spec <intent>` or any development request).
- **Preconditions**: The repository has `devkit-spec` installed and its `spec` bundle synchronized; the main scenario uses the effective SDD approach.

---

## 2. Main Success Scenario

The main scenario follows a `spec`-depth `feature` request in `direct` mode.

1. The agent inspects `devkit config show`, confirms the effective approach is SDD, loads the spec constitution once in its agent context and enters the `spec` skill with the user's
   intent. At this new task intake it runs one bounded `devkit playbook search`; no candidate names the requested
   operation, so it continues without a question (`CAP-HARN-agent-guidance`, `ADR-spec-intake-playbook-discovery`).
2. The agent reads the effective project policy (`CAP-DLV-project-policy`).
3. The agent classifies the request on `task-kind`, then `planning-depth` by what must be settled before
   implementation, then the mode and `activity-effort`, and states the classification to the user
   (`CAP-HARN-agent-guidance`).
4. The agent starts the activity branch `dev-<slug>` in the current checkout, as the Git policy allows
   (`CAP-DLV-project-policy`).
5. The agent creates the spec bundle, bound to the workflow of the task kind, with skeleton documents
   (`CAP-DLV-spec-bundles`).
6. The agent records `plan-intent` from the user's explicit task instruction (`CAP-DLV-delivery-workflows`).
7. The agent asks the workflow for the next stage and follows the stage, its unmet checks and the skill it names
   (`CAP-DLV-delivery-workflows`).

---

## 3. Extensions

- **1a.** The user asks for orientation instead of stating an intent, and no Unit is in progress: the agent filters
  the queued drafts by their direct prerequisites on one local base snapshot, ranks the eligible ones by milestone,
  priority and size, recommends one with Planning, a direct acceptance or a session reclassification, and reports
  decomposition (a `needs_decompose` or `XL` draft, through the `decomposer`) and milestone cleanup as Backlog actions (`CAP-HARN-agent-guidance`); intent approval and milestone
  transitions stay with the user; the use case ends.
- **1b.** The message is not a new task intake (a continuation, a same-task follow-up, an explicit ID or rule
  remediation, a step inside a running playbook, an information-only question, a message from another agent, or the
  user said not to use playbooks in this conversation): the agent runs no search (`CAP-HARN-agent-guidance`); resumes
  at step 2.
- **1c.** A candidate's description names the requested operation and its scope fits: the agent names it in one line
  with the classification statement and waits; on the user's confirmation, which is the explicit invocation, it
  follows the playbook (`feedback-hygiene` delegates its grouping to the read-only `triage` role above 5 open items on
  a host that runs it natively) and the use case ends; on a decline it never offers that candidate again in the conversation
  (`CAP-HARN-agent-guidance`, `CAP-DIST-context-and-playbooks`); resumes at step 2.
- **1d.** The effective approach is adaptive-dev: the agent uses the project's adaptive-dev guidance and independent document/project checks without creating an implicit SDD Unit or classifying this change into SDD depths. Existing bound history retains its checks; this routing use case ends.
- **1e.** The user explicitly invokes the approach-neutral research entry (`/deep-research`): the invocation is not
  development intake, so the agent runs no playbook search, classifies nothing and creates no Unit; the research
  entry's own skill takes over and work the research later informs starts as ordinary intake
  (`CAP-HARN-agent-guidance`); this routing use case ends.
- **2a.** The effective policy is invalid (a `[tool.spec]` key outside the table, or a `plan-intent` or main
  boundary policy other than `ask` or `auto`): the system refuses with `SPEC_CONFIG_INVALID`
  (`CAP-DLV-project-policy`); the agent stops policy-dependent work; the use case ends.
- **3a.** The task needs nothing settled before implementation (`session` depth): the agent agrees the intent in the
  conversation and follows the stages of `sdd-session-<task-kind>` itself, writing no Unit, envelope, gate record
  file or reconcile document (`CAP-DLV-delivery-workflows`); the use case ends.
- **3b.** The direction must be decided first (`proposal` depth): the agent creates a draft proposal bound to
  `sdd-proposal` and records `plan-intent` as the user's confirmation of the draft in Backlog
  (`CAP-DLV-delivery-workflows`); the use case ends and `UC-plan-and-hand-off-a-proposal` continues.
- **3c.** The request will not start now, or must be decomposed (it would need two or more specs or a different
  `task_kind`, `size: XL`): the agent keeps it as one or more draft proposals in
  Backlog, a rough `XL` draft only until it is decomposed before `plan-intent`, optionally assigns an existing global milestone, and preserves the origin in `decomposed_from` or
  `supersedes` through handoff, without an external tracker (`CAP-HARN-agent-guidance`); the use case ends.
- **3d.** The change adds no behavior and restructures several areas at once (`overall-refactor`): the agent runs
  `sdd-overall-refactor` in `direct` mode with the user, without a Unit, proposal or spec bundle
  (`CAP-DLV-delivery-workflows`); the use case ends.
- **4a.** The Git policy requires a worktree (`worktree=required`), or under `auto` the checkout holds unrelated
  changes, another task is in flight there, or the user asks: the agent starts `dev-<slug>` in its own task worktree
  and continues there (`CAP-DLV-project-policy`); resumes at step 5.
- **5a.** The checkout is not on `dev-<slug>`: the system refuses with `SPEC_WRONG_BRANCH` and writes nothing
  (`CAP-DLV-spec-bundles`); the agent starts or continues `dev-<slug>`; resumes at step 5.
- **5b.** A document, proposal or bundle already holds the slug: the system refuses with `SPEC_EXISTS` and writes
  nothing (`CAP-DLV-spec-bundles`); the agent chooses another slug; resumes at step 5.
- **5c.** The request is a defect against an agreed contract whose current, expected and preserved behavior must be
  written down: the agent creates the bundle bound to `sdd-spec-bugfix`, which holds only `spec.md`; its `reproduce`
  stage stays open until a reproduction is recorded (`CAP-DLV-spec-bundles`, `CAP-DLV-delivery-workflows`); resumes
  at step 6.
- **6a.** The request leaves the goal, scope, verification, `task-kind` or `planning-depth` unresolved under
  `plan-intent` policy `ask`: the workflow waits on the human gate, and the agent asks the user and records the answer
  only after the user's explicit reply (`CAP-DLV-delivery-workflows`); resumes at step 7.
- **6b.** `plan-intent` policy is `auto`: the gate passes by policy, reported as policy, never as the user's consent
  (`CAP-DLV-delivery-workflows`); resumes at step 7.
- **6c.** The user declines the intent: the agent records the decline with the user's reason
  (`CAP-DLV-delivery-workflows`); the use case ends.
- **\*a.** During Development, a `session` task turns out to need a lasting design record, a contract change or a
  Living Spec change: the agent raises the depth to `spec` itself under `depth_escalation=auto`, or after the user's
  confirmation under `ask`, and a worker reports the need as a problem instead (`CAP-HARN-agent-guidance`,
  `CAP-DLV-project-policy`); the agent adds a spec Unit on `dev-<slug>` in the current work environment with no close,
  new slug or new worktree, first starting that branch in the current checkout when it is missing, which carries the
  uncommitted changes over (`CAP-WT-task-worktrees`), and records the agreed intent and the work so far; resumes at
  step 7.

---

## 4. Postconditions

- **Success guarantee**: The task follows exactly one workflow `sdd-<planning-depth>[-<task-kind>]` (or
  `sdd-overall-refactor`), named by the bound Unit or, for a session, by the agreement in the conversation. A Unit's
  `plan-intent` is recorded from an explicit user instruction, the user's explicit answer or `auto` policy. A queued
  request exists as a draft proposal with its provenance.
- **Minimal guarantee**: No approval is inferred. A refused `devkit spec new` leaves the workspace unchanged. A policy
  error stops policy-dependent work. A depth is never lowered except through a proposal's handoff or the user's
  decision at pickup.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: A contract change becomes a bound spec bundle
- **Covers**: main success scenario
- **Given**: the policy reports `[GIT_POLICY: worktree=auto ...]`, the agent keeps the task in the current checkout
  on `dev-<slug>`, and the request changes a documented contract with a clear direction
- **When**: the agent runs `devkit spec new <slug>`
- **Then**: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` holds skeleton-marked `spec.md`, `plan.md` and `tasks.md`,
  `spec.md` is bound to `sdd-spec-feature` with no `kind` field, and the output ends with
  `[NEXT_CMD: uv run devkit workflow next --unit <dir>]`

### Scenario 2: Orientation recommends actionable queued work
- **Covers**: 1a
- **Given**: queued drafts exist and no Unit is in progress
- **When**: `spec-next` orients the agent
- **Then**: it recommends an eligible draft in the milestone, priority and size order of `CAP-HARN-agent-guidance`,
  reports decomposition or milestone cleanup as Backlog actions, and leaves intent approval and milestone transitions
  to the user

### Scenario 2a: A continuation runs no playbook search
- **Covers**: 1b
- **Given**: a Unit is in progress and the user asks to continue it
- **When**: the agent enters the `spec` skill
- **Then**: it runs no `devkit playbook search` and offers no playbook

### Scenario 2b: A matching playbook is offered in one line
- **Covers**: 1c
- **Given**: the user asks to triage the open feedback files, and the synchronized `feedback-hygiene` playbook's
  description names that operation
- **When**: the agent takes in the request
- **Then**: it names `feedback-hygiene` in one line with its classification statement, runs nothing before the user
  confirms, and offers no candidate the user declined earlier in the conversation

### Scenario 2c: An explicit research invocation is not intake
- **Covers**: 1e
- **Given**: an SDD repository with `spec:core` and `deep-research:core` selected
- **When**: the user invokes `/deep-research compare directions for X`
- **Then**: the agent runs no `devkit playbook search`, states no classification, and creates no proposal, spec bundle,
  gate record or envelope

### Scenario 3: An invalid intent policy stops routing
- **Covers**: 2a
- **Given**: `.devkit/config.toml` sets `[workflow.approvals] plan-intent = "off"`
- **When**: the agent runs `devkit spec policy`
- **Then**: the command fails with `SPEC_CONFIG_INVALID`, and the agent starts no policy-dependent work

### Scenario 4: A session task leaves no records
- **Covers**: 3a
- **Given**: a request with nothing to decide before implementation and no contract impact
- **When**: the agent classifies it as `session` and agrees the intent in the conversation
- **Then**: it follows the stages of `devkit workflow show sdd-session-<task-kind>`, and no Unit, envelope, gate record
  file or reconcile document is created

### Scenario 5: An open direction starts as a draft proposal
- **Covers**: 3b
- **Given**: a request whose direction must be decided before implementation
- **When**: the agent runs `devkit spec proposal new <slug>`
- **Then**: `docs/proposals/PROP-<slug>/proposal.md` exists with `status: draft`, bound to `sdd-proposal`, and the
  output ends with `[NEXT_CMD: uv run devkit workflow next --unit docs/proposals/PROP-<slug>]`

### Scenario 6: Queued requests retain repository provenance
- **Covers**: 3c
- **Given**: a request will not start now, or a draft must be decomposed
- **When**: the agent follows Backlog
- **Then**: it creates draft proposals, optionally assigns existing global milestone IDs, and preserves
  `decomposed_from` and `supersedes` through handoff without requiring an external tracker

### Scenario 7: A cross-area restructuring runs without a Unit
- **Covers**: 3d
- **Given**: a change that adds no behavior and restructures package boundaries across several areas
- **When**: the agent classifies it as `overall-refactor`
- **Then**: it runs `sdd-overall-refactor` in `direct` mode, and no proposal, spec bundle or Unit is created

### Scenario 8: A required worktree hosts the task
- **Covers**: 4a
- **Given**: the policy reports `[GIT_POLICY: worktree=required ...]` for a `spec`-depth task
- **When**: the agent starts the activity branch with `devkit worktree start dev-<slug>`
- **Then**: the branch runs in its own task worktree, and the spec bundle is created there

### Scenario 9: Spec creation refuses another branch
- **Covers**: 5a
- **Given**: a Git checkout on a branch other than `dev-<slug>`
- **When**: the agent runs `devkit spec new <slug>`
- **Then**: the command exits `2` with `SPEC_WRONG_BRANCH`, whose `[FIX]` starts or continues `dev-<slug>`, and
  nothing is written

### Scenario 10: Spec creation refuses a taken slug
- **Covers**: 5b
- **Given**: a document declares `PROP-<slug>`
- **When**: the agent runs `devkit spec new <slug>`
- **Then**: the command exits `2` with `SPEC_EXISTS`, `[TARGET]` lists the document, and nothing is written

### Scenario 11: A defect with a spec takes the spec bugfix workflow
- **Covers**: 5c
- **Given**: an observed behavior contradicts an existing contract and its current, expected and preserved behavior
  must be written down
- **When**: the agent runs `devkit spec new <slug> --workflow sdd-spec-bugfix`
- **Then**: the bundle holds only `spec.md`, bound to `sdd-spec-bugfix`, and the `reproduce` stage stays open until a
  `red` envelope records `checks.reproduced`

### Scenario 12: An unresolved intent waits for the user
- **Covers**: 6a
- **Given**: `[GATE_POLICY: plan-intent policy=ask source=default]`, a freshly created bundle, and a request that
  left its verification unresolved
- **When**: the agent runs `devkit workflow next --unit <dir>`
- **Then**: the output shows `[WAITING: human gate:plan-intent]`, and the agent records
  `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user` only after the user's
  explicit answer

### Scenario 13: Policy satisfies the intent gate
- **Covers**: 6b
- **Given**: `[GATE_POLICY: plan-intent policy=auto source=config]` and a freshly created bundle
- **When**: the agent runs `devkit workflow next --unit <dir>`
- **Then**: the workflow names the next stage without asking `gate:plan-intent`, and the agent reports the policy as
  the authority

### Scenario 14: A declined intent ends the task
- **Covers**: 6c
- **Given**: the workflow waits on `gate:plan-intent`
- **When**: the user rejects the stated intent and the agent runs `devkit workflow answer --unit <dir> --request
  gate:plan-intent --action decline --by user --note "<reason>"`
- **Then**: the decline is recorded with the reason, and the agent starts no Development stage

### Scenario 15: A session that needs a contract change is raised to `spec`
- **Covers**: \*a
- **Given**: a `session` task turns out to need a contract change or a Living Spec change during Development, and the
  policy reports `[ROUTING_POLICY: depth_escalation=auto]`
- **When**: the agent raises its depth
- **Then**: it adds a spec Unit with `devkit spec new <slug>` on `dev-<slug>` in the current work environment (first
  starting that branch with `devkit worktree start dev-<slug> --no-worktree`, which carries the uncommitted changes,
  when it does not exist yet), records the agreed intent and the work so far, and continues from the workflow's
  next stage, keeping the changes made so far
