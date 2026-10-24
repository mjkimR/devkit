---
id: PROP-automatic-scope-collection
title: Automatic work scope collection at delivery CLI boundaries
summary: "Collects work scope at handoff, spec creation and explicit workflow next calls, removing agent update duties and hiding the maintenance command. Automatic collection failures stay silent and preserve primary outcomes; Planning validates timing and ownership."
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
- **Q4 — Outcome and cost**: What separate budget and diagnostic identifiers make it possible to inspect
  collection diagnostics only under `-v` while preserving the primary command result? Recommend one bounded
  attempt per invocation, no immediate retries and no writes for an unchanged semantic snapshot. Automatic
  collection failures produce no advisories or result fields and never affect `--strict`.
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
worker inspection must not refresh scope implicitly. Automatic collector diagnostics use logging visible only
under `-v`; providers never print. The collector does not add notices to the primary operation. `devkit-agt` must
not import `devkit-spec` or require its installation.

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

Automatic collection at all three triggers is best-effort observation, including initial registration.
It has a separate finite execution budget and makes one attempt per invocation. Failure produces no default
stdout, stderr, advisory block, JSON error/notice/status field, workflow request or agent-facing recovery task.
It never changes the primary command's result, exit code, gate verdict or `--strict` behavior. Existing errors
and notices from the primary operation retain their own semantics. Successful creation or handoff remains
successful when its automatic registration fails; explicit `next` preserves any original lint error.

The automatic collection boundary isolates collection, optional-provider loading and publication failures.
It does not suppress errors from the primary command or process cancellation/termination. Record diagnostic
identifiers and causes through logging visible only under `-v`, using the repository's verbose `[INFO]` channel;
do not emit default warning/error logs or prescribe a manual recovery action. Diagnostic logging failure must
not fail the primary command.

A failure before publication leaves the last successfully stored snapshot intact, or no record if initial
registration never succeeded. If publication succeeded but its journal append failed, retain the published
snapshot; do not roll it back or claim that no publication occurred. Respect existing atomicity, token cleanup
and optimistic concurrency. Do not add failure-journal writes, immediate retries, permission prompts or fallback
storage. The next ordinary eligible CLI invocation makes a fresh attempt, including safe initial registration
when no owned record exists; Q2/Q5 must settle incomplete-token and partial-registration recovery. The collector
must not request broader permissions on the agent's behalf.

Silent failure accepts that the registry can lag or omit a running task without notifying the agent. A workflow
result does not certify snapshot freshness. Queries retain the stored snapshot's actual revision and timestamp;
a failed attempt must not advance either. Scope evidence remains advisory and cannot certify independence.
The separate collection deadline bounds added latency; this is not a promise of zero execution cost.

This automatic-path policy does not change explicit maintenance commands: a directly invoked hidden
`scope update` retains its ACK, errors, notices and exit behavior. It also does not silence an explicitly invoked
`scope register`, query or other diagnostic command.

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
  preserve the primary result and exit code in text and JSON, both with and without `--strict`. Assert no added
  default stdout/stderr, notices, errors, requests or recovery directives for automatic collection failures at
  all three triggers. A primary lint error remains unchanged. Diagnostics appear only under `-v`; provider-loading
  and diagnostic-logging failures also cannot fail the primary command. A failure before publication preserves
  the previous snapshot; a journal failure after publication preserves the published snapshot. No immediate
  retry or escalation occurs. After transient failure, the next ordinary eligible call attempts collection again.
- **AC-06 — Bounded idempotence**: Unchanged inputs produce no revision or update-journal churn. Collection has
  a finite separate deadline, no nested retry loop and no sibling-checkout traversal. Measure added cost with
  representative small and large diffs during the spike; settle the performance threshold before acceptance.
- **AC-07 — Guidance and discovery**: Source guidance has no mandatory explicit `scope update` calls.
  Ordinary help and generated discovery omit the command. Explicit maintenance invocation and help remain valid.
- **AC-08 — Visibility boundary**: Two isolated clones do not appear mutually visible without shared storage.
  Existing local shared-registry overlap comparison and post-finish cleanup continue to work.

Non-goals: native/Git hooks, continuous observation, automatic worker dispatch, remote aggregation, OTel adoption,
exclusive ownership, overlap-based write refusal, and changes to workflow gates or approval authority.

The silent automatic-path failure policy is an explicit exception to treating those collection failures as operation advisories; explicit command failures keep the
Agent Advisory Protocol contract.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in draft for Planning review. The author self-review in `materials/self-review.md` records
code evidence, folded corrections and unresolved acceptance blockers; it is not an independent Planning review.
Before direction acceptance, demonstrate Q1 timing traces, Q2 standalone ownership behavior, Q3 dispatch isolation
and Q4 silent failure isolation with bounded diagnostics. A mandatory automatic-update call cannot be used
to make those demonstrations pass. Compare the chosen design with handoff-only snapshots and optional hooks during Planning.

Planning must create a PADR replacing the skill-maintained refresh decision in
ADR-worktrees-branches-and-scope and documenting the explicit `workflow next` observation side effect. If Q2
selects standalone registration, the PADR must also replace that ADR's linked-worktree-only participation decision. Reconcile
CAP-COLL-work-scope-registry, UC-run-parallel-work-safely, CAP-DLV-workflow-orchestration and
CAP-HARN-agent-guidance during Development. No direction acceptance, Development handoff or implementation is
part of this draft-writing task.
