---
id: PROP-git-operator-pilot-follow-up
title: Refine git-operator lifecycle contracts from a consumer pilot
summary: "Separate lifecycle effects from worker readiness, close the Planning acceptance execution gap, and distinguish activity write boundaries from future implementation overlap. Evaluate bounded batch dispatch using observed consumer pilot evidence."
status: draft
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: XL
needs_decompose: true
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/collaboration/
    - docs/capabilities/worktree/
    - docs/materials/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-git-operator-pilot-follow-up] Refine git-operator lifecycle contracts from a consumer pilot

## 1. Background & Hypothesis

The resource-indexer consumer pilot reused one named `git-operator` for six worktree preparations and one
Development handoff. All seven guarded operations returned exit 0 and the Host checked their effects.
The operator kept operational details outside the Host context and returned refs, paths and remaining effects.
The pilot has not established a net token, cost or latency benefit.

Four gaps appeared at the boundary between Host decisions, guarded execution and worker input:

1. The Host accepted and integrated a verified Planning result with `accept --mode accept_only` itself because the
   operating reference lists handoff and integration, but no Planning-acceptance execution job.
2. A successful handoff left a known generated transaction uncommitted. CLI effect completion did not by itself
   mean clean committed worker input, and the return did not give a uniform next-action owner.
3. Scope observations exposed future implementation candidates while current Planning writers owned distinct
   proposal directories. The Host had to explain that difference before parallel Planning could proceed.
4. Preparing five exact worktrees required an ad hoc multi-job payload and aggregate return under a role contract
   written for one job. The operations succeeded; partial-batch behavior remains unverified.

A related readiness ambiguity appeared when `workflow next` returned no current stage and `complete=yes` under
`plan-accept=auto`, although proposals remained `reviewing` and no acceptance command had run. Planning workers
needed Host guidance to record their return at `direction-handoff` rather than use the printed `-` sentinel.

The hypothesis is that a small set of explicit lifecycle jobs and clearer result semantics will preserve the
role's narrow remit while reducing Host interpretation. This is a Backlog hypothesis, not an implemented contract.
CAP-DLV-delivery-workflows owns the role boundary; CAP-COLL-work-scope-registry owns informational overlap evidence;
CAP-WT-task-worktrees owns worktree effects. MAT-git-operator-consumer-pilot records this pilot separately from
MAT-git-operator-development-evidence.

## 2. Technical Spike Questions

- Can a Host-authorized Planning acceptance job invoke the existing composed CLI without adding an approval grant,
  another gate or arbitrary Git execution? Which exact source/target refs and effects must it receive?
- How should a return distinguish requested effect completion, verified worker readiness, known dirty outputs,
  and the next actor's work? Preserve the existing three role statuses and original CLI exit/effects.
- Should `workflow next` expose a record/return stage when policy-derived readiness has no current stage, or is an
  explicit worker-guidance mapping sufficient? Do not infer executed acceptance from policy readiness.
- Can scope output show current activity write boundaries beside declared/candidate implementation impact,
  without hiding unresolved inputs, suppressing overlaps or becoming write authority?
- Is bounded batch preparation worth a new CLI operation, or does a typed list of existing independent jobs in
  the role contract suffice? Compare dispatch/result size, permission overhead and failure recovery.
- Which parts can ship independently, and what evidence is needed before claiming lower Host burden or total cost?

## 3. Proposed Design & Impact

### Retain the narrow role

The Host continues to choose work, schedule workers, accept semantic results, resolve design conflicts and carry
current authority. Workers author source, documents and records. The operator executes exact authorized lifecycle
effects through existing guarded commands and verifies them. It gains no production-authoring, approval-grant,
arbitrary branch-deletion, force-operation or global-lock authority.

### Candidate workstreams for decomposition

| Workstream | Bounded candidate | Evidence and decision still needed |
| --- | --- | --- |
| Planning acceptance execution | Add an explicitly named job for the already authorized `accept_only` path; combined handoff remains an explicit effect list. | Pin source/target identity and current Host authority; retain policy, readiness and publication checks. |
| Lifecycle and worker readiness | Return CLI effects separately from worker-input readiness, known generated dirty paths and next-action ownership; define the terminal Planning return stage. | Settle minimal field/guidance changes; a successful effect is not a clean-input claim, and unknown checks stay unknown. |
| Activity-aware scope explanation | Present actual activity writes and future declared/candidate impact as distinct evidence. | Preserve current candidate/observed provenance, partial coverage and Host scheduling authority; do not redefine overlap to hide it. |
| Bounded batch preparation | Accept an exact finite job list with per-item identity, authority, effects, checks and outcome. | Choose role-only composition versus CLI support; validate partial completion and narrow remainder retry. |

The first two workstreams may form one lifecycle-contract unit. Scope presentation and batch execution are
independently useful outcomes, so this umbrella is XL and must be decomposed before Planning starts.
No child is created or selected by this draft.

### Verification candidates

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-01 | A verified committed Planning source and exact current Host authority | The operator executes Planning acceptance | Only named existing CLI effects run; source drift or missing authority preserves resources and returns the required Host action. |
| GOP-02 | A successful handoff with generated uncommitted files | The operator returns its result | Original CLI success/effects, exact dirty paths, worker-readiness evidence and next-action owner are distinguishable; no clean committed input is implied. |
| GOP-03 | Auto-policy Planning readiness with no current stage and a reviewing proposal | A worker authors its final return | The record uses an explicit valid workflow stage; no acceptance/handoff effect is invented. |
| GOP-04 | Disjoint proposal-only Planning writes and overlapping future implementation candidates | Scope is inspected for scheduling | Both facts and unresolved coverage remain visible; the result grants or refuses no write and the Host retains the decision. |
| GOP-05 | An authorized finite preparation list with one denied or partial item | A batch stops or continues within its stated policy | Each item's original CLI result and completed/remaining effects are retained; retries target only inspected authorized remainders. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host/implementer and performs no such mutation. |
| GOP-07 | Integration, cleanup or permission-recovery evidence not yet exercised by this consumer pilot | Reports are updated after actual observations | Live effects, isolated engine fixtures, instructed replays and untested cases remain separate; unknown cost/latency is not reported as an improvement. |

Tests should exercise deterministic result mapping, partial effects and stale identity with isolated repositories.
Selected-host mutation and recovery observations should be added when those operations occur; do not induce
destructive failures in a person's repository merely to fill an evidence row.

### Non-goals

- **Scope Excluded**: implementing this umbrella without decomposition, or starting its Planning through this intake.
- **Scope Excluded**: a daemon, persistent approval store, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: claiming that informational scope observations authorize writes, or that unresolved coverage means no conflict.
- **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token/cost/latency savings.

## 4. Lifecycle & Retirement Criteria

This feature / proposal intake records a consumer pilot at Backlog depth. Size is XL with `needs_decompose: true`
because the candidate outcomes can require separate specs. Planning and Development hints are medium; choose them
again for each selected child. There is no direct prerequisite Unit and no matching milestone is assigned.

Before pickup, review the candidate workstreams and retained evidence, choose the deliverable split, and preserve
unverified cases. The draft's author may update its material as this consumer session observes later integration
or recovery, provided the draft is still editable. A Planning-owned draft is left to its assigned worker.
Creating this proposal does not accept its direction or change current role, workflow or scope contracts.
