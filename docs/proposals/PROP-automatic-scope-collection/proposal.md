---
id: PROP-automatic-scope-collection
title: Automatic work scope collection at delivery CLI boundaries
summary: "Collects work scope at proposal handoff, spec creation and explicit workflow next calls, removing mandatory agent scope updates while retaining a hidden maintenance command. Planning validates timing, ownership and isolated cloud checkout behavior."
status: draft
created_at: 2026-10-25
target_area: collaboration/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/base/errors.py
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/pyproject.toml
    - packages/devkit-spec/tests/
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit/tests/
    - docs/capabilities/collaboration/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/
    - docs/usecases/collaboration/
    - docs/decisions/
  excludes:
    - Remote registry transports and cross-cloud aggregation
    - Native agent hooks and Git hooks
    - OpenTelemetry SDKs, exporters and collectors
    - Changes to overlap matching and workflow approval authority
task_kind: feature
workflow: sdd-proposal
---

# [PROP-automatic-scope-collection] Automatic work scope collection at delivery CLI boundaries

## 1. Background & Hypothesis

Work scope publication depends on agents following explicit `devkit spec scope update` instructions in
`spec-tasks`, `spec-sync` and delegated-worker acceptance. These calls add procedural work and can become stale
when an agent omits one. The registry reports overlap evidence for scheduling; it grants no write authority.

The proposed collection points are exactly `devkit spec proposal handoff`, `devkit spec new` and explicit
`devkit workflow next --unit <dir>` calls. Each command collects only from its own execution checkout. Collection
must not depend on opening sibling worktrees, because isolated cloud checkouts cannot access them.

Source inspection shows that handoff and spec creation already call `auto_register`. That helper only registers
linked worktrees. The main implementation gap is refresh at explicit `workflow next`, followed by a deliberate
resolution of tokenless standalone checkout behavior. Creation produces skeletons; later calls must observe the
completed declarations and implementation changes.

Hypothesis: collecting at those existing delivery boundaries removes mandatory manual updates while providing
useful snapshots for overlap decisions. It does not provide continuous observation. The interval between calls,
first parallel dispatch and reconciliation timing require evidence before direction acceptance.

## 2. Technical Spike Questions

- **Q1 — Timing**: Do existing explicit `workflow next` calls occur after `tasks.md` and `reconcile.md` writes,
  before parallel dispatch and after accepted worker changes? Trace direct, orchestrated, resumed and cloud runs.
  Recommend snapshots at each explicit call. Do not add replacement instructions solely to trigger collection.
  If a required decision precedes the next snapshot, document that gap and revise the direction before acceptance.
- **Q2 — Checkout identity**: How does an isolated cloud checkout without a linked-worktree marker or token
  participate without a manual registration command? Recommend automatic initial participation for a safely
  identified single spec task, using its checkout's existing local registry location. Establish the eligibility
  test, existing-task recovery and protection against attributing a shared base checkout to the wrong unit.
  Existing `auto_register` alone does not meet this requirement.
- **Q3 — Dispatch boundary**: Which optional extension contract lets the explicit `workflow next` application
  operation invoke the spec collector once, without running it from internal evaluation, checks or integration
  readiness? Recommend a harness-owned typed contract implemented through the existing entry-point mechanism.
- **Q4 — Outcome and cost**: What separate budget, stable advisory codes and structured result fields expose
  collection failure while preserving the workflow verdict? Recommend one attempt per invocation, no retries or
  writes for an unchanged semantic snapshot, and warnings under the established `--strict` behavior.
- **Q5 — Ownership and concurrency**: How do a wrong `--unit`, concurrent calls, a moved/deleted base ref and a
  missing record/token behave? Recommend preserving token ownership and optimistic concurrency; never silently
  rebind an existing token to a different spec. Settle recovery without a mandatory `scope update` directive.

## 3. Proposed Design & Impact

### 3.1 Collection triggers

| Explicit CLI operation | Collection boundary | Expected observation |
| --- | --- | --- |
| `devkit spec proposal handoff <slug>` (including `--effort`) | After the actual destination bundle is successfully created, inside its execution checkout | Initial declared and Git-observed scope; reuse the existing composite registration path |
| `devkit spec new <slug>` | After successful bundle creation and binding | Initial skeleton scope and Git-observed paths; incomplete declarations remain unresolved |
| `devkit workflow next --unit <dir>` (including `--view requests` and `--no-lint`) | Once the actual spec unit is resolved and its workflow evaluation returns a result, before CLI rendering | Recollected declarations and Git-observed paths for that unit |

The proposed third trigger applies when evaluation returns a blocked or lint-error result as well as a ready
result. Resolution or configuration failures that prevent identifying the unit do not publish a snapshot.
Proposal units, session workflows and unrelated workflow units do not become spec registrations.

The trigger belongs to an explicit application operation, behind the thin CLI adapter. Pure evaluation and
library callers of `EvaluateUnitUseCase` or `Workspace.evaluate_unit` remain free of automatic scope mutation.
The shared CLI error boundary is not a trigger. Internal evaluation by `answer`, `handoff`, readiness, rules or
worker inspection must not refresh scope implicitly. The operation returns notices through the CLI boundary;
providers never print. `devkit-agt` must not import `devkit-spec` or require its installation.

### 3.2 Collection and publication

Reuse the declared-path parsers, Git observation, merge-base rules and comparison semantics of
CAP-COLL-work-scope-registry. Reuse the scope collection behavior behind `collect`; implementation may extract
it into an appropriate service rather than importing a higher-layer use case from a lower layer.

Collect only the resolved unit in the current checkout. Reuse an owned registration for the same unit. Compare
semantic scope content before publication: scope paths and their metadata, unresolved inputs, spec identity and
base ref. Timestamps and request IDs alone do not constitute a change. An unchanged snapshot leaves the stored
revision and update journal unchanged. A changed snapshot retains optimistic concurrency, first-seen metadata
and atomic publication. Automatic collection does not steal, replace or retarget another unit's registration.

Tokenless isolated checkouts require the Q2 solution before acceptance. No sibling-worktree reads, registry
relocation or automatic remote transport are proposed. A cloud job can collect locally; another cloud job cannot
see that snapshot without an independently available shared storage arrangement. This proposal does not claim
cross-cloud overlap detection.

Scope refresh has its own bounded execution budget. A failed refresh preserves the last successfully published
record and the workflow result. It returns a stable advisory with a deterministic action for the failing cause.
Ordinary workflow exit behavior remains, except for existing strict-warning handling. Successful no-change
collection adds no stdout lines, progress output or agent context. Settle structured failure reporting and
codes in Q4; failure must not be represented as a successful fresh observation.

### 3.3 Agent guidance and hidden maintenance command

Remove explicit `scope update` obligations from `spec-tasks`, `spec-sync` and delegated-worker acceptance.
Search source bundle guidance and error actions for equivalent obligations, then replace them with automatic
collection behavior or cause-specific recovery. Remove redundant manual registration instructions where creation
already registers automatically. Keep the existing normal workflow-boundary instructions; do not introduce a
replacement command solely for collection.

Declare the `update` subcommand hidden in Click. Preserve direct invocation, its own `--help`, ACK/result shapes,
request-id retry behavior and exit codes for maintenance. Hide it from ordinary scope help and generated
agent-facing command discovery. Inspect how those discovery surfaces handle hidden commands before changing
shared discovery code; expand the boundary explicitly if needed. Preserve visible compare/query/register/release/
sweep interfaces. `query`, `query --history` and `compare` remain read-only and do not perform refresh writes.

### 3.4 Proposed acceptance evidence

- **AC-01 — Creation**: Both handoff forms and direct spec creation collect in the destination checkout after
  successful creation. Initial incomplete declarations remain visible as unresolved inputs.
- **AC-02 — Refresh timing**: An explicit `next` after a boundary or reconciliation edit reflects that edit.
  Committed, staged, unstaged and untracked changes use existing Git observation rules. Representative execution
  traces show whether collection occurs before each scheduling decision that relies on the registry.
- **AC-03 — Invocation isolation**: Each supported explicit `next` variant collects at most once. Internal
  evaluation, rules, readiness, worker inspection, non-spec units and query/history/compare cause no refresh writes.
  A generic harness installation without `devkit-spec` continues to evaluate normally.
- **AC-04 — Ownership**: Repeated calls for the same unit are safe. A wrong unit, a foreign token or a different
  existing task never changes attribution. Concurrent publication preserves the revision guard and the winning
  snapshot. Q2 supplies a reproducible standalone cloud checkout test with no manual registration/update call.
- **AC-05 — Failure isolation**: Permission refusal, lock timeout, malformed scope inputs and stale revision
  preserve the workflow verdict and previous record, return stable warning codes/actions and respect `--strict`.
  A workflow result carrying a lint error retains that error alongside collection notices.
- **AC-06 — Bounded idempotence**: Unchanged inputs produce no revision or update-journal churn. Collection has
  a finite separate deadline, no nested retry loop and no sibling-checkout traversal. Measure added cost with
  representative small and large diffs during the spike; settle the performance threshold before acceptance.
- **AC-07 — Guidance and discovery**: Source guidance has no mandatory explicit `scope update` calls.
  Ordinary help and generated discovery omit the command. Explicit maintenance invocation and help remain valid.
- **AC-08 — Visibility boundary**: Two isolated clones do not appear mutually visible without shared storage.
  Existing local shared-registry overlap comparison and post-finish cleanup continue to work.

Non-goals: native/Git hooks, continuous observation, automatic worker dispatch, remote aggregation, OTel adoption,
exclusive ownership, overlap-based write refusal, and changes to workflow gates or approval authority.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in draft for Planning review. The author self-review in `materials/self-review.md` records
code evidence, folded corrections and unresolved acceptance blockers; it is not an independent Planning review.
Before direction acceptance, demonstrate Q1 timing traces, Q2 standalone ownership behavior, Q3 dispatch isolation
and Q4 bounded result reporting. A mandatory automatic-update call cannot be used to make those demonstrations
pass. Compare the chosen design with handoff-only snapshots and optional hooks during Planning.

Planning must create a PADR replacing the skill-maintained refresh decision in
ADR-worktrees-branches-and-scope and documenting the explicit `workflow next` observation side effect. If Q2
selects standalone registration, the PADR must also replace that ADR's linked-worktree-only participation decision. Reconcile
CAP-COLL-work-scope-registry, UC-run-parallel-work-safely, CAP-DLV-workflow-orchestration and
CAP-HARN-agent-guidance during Development. No direction acceptance, Development handoff or implementation is
part of this draft-writing task.
