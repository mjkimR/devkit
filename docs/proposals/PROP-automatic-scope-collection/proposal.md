---
id: PROP-automatic-scope-collection
title: Creation snapshots and explicit host work scope collection
summary: "Retains automatic creation snapshots and replaces worker scope updates with explicit host collection from snapshots, branch refs and accessible worktrees. Observation modes expose incomplete coverage and remote visibility limits without mutating worker registrations."
status: reviewing
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
    - packages/devkit-spec/tests/
    - docs/capabilities/collaboration/
    - docs/capabilities/harness/
    - docs/usecases/collaboration/
    - docs/decisions/
  excludes:
    - Workflow evaluation and workflow next collection hooks
    - Remote registry transports and cross-cloud aggregation
    - Native agent hooks and Git hooks
    - OpenTelemetry SDKs, exporters and collectors
    - Changes to overlap matching and workflow approval authority
task_kind: feature
workflow: sdd-proposal
---

# [PROP-automatic-scope-collection] Creation snapshots and explicit host work scope collection

## 1. Background & Hypothesis

The registry supports scheduling by comparing declared and observed work scope. Its snapshots do not grant write
permission or certify independence. `devkit spec proposal handoff` and `devkit spec new` already compose automatic
registration through `auto_register`. Registration currently applies only to linked worktrees. Initial spec
skeletons do not contain completed task boundaries or later implementation changes.

Worker guidance requires `scope update` after task writing, reconciliation and accepted worker changes. Remove
those duties. Retain creation snapshots as initial evidence and let the Host explicitly collect the evidence
available when it makes a scheduling or integration-order decision. Do not add collection to `workflow next`.

Hypothesis: creation snapshots plus on-demand Host observation provide useful overlap evidence with less worker
protocol and no workflow observation hooks. This accepts gaps between Host invocations and incomplete visibility
into other machines. The Host report must distinguish observed evidence from missing coverage.

## 2. Technical Spike Questions

- **Q1 — Inventory and active work**: How can the collector enumerate linked worktrees, local activity branches and
  remote-tracking activity refs without requiring registry participation? Recommend activity-branch conventions,
  unit lifecycle evidence and registry bindings as explicit selection evidence. Branch existence alone is not proof
  of active work. Include ambiguous candidates as unknown or excluded with a reason, never silently inactive.
- **Q2 — Ref inputs and attribution**: How can declaration parsers read a pinned commit tree without a checkout?
  Establish task identity, base selection and committed-diff semantics for unregistered branches. Do not use the
  current checkout's documents or changes for another ref. Report ambiguous identity/base inputs.
- **Q3 — Modes and reconciliation**: Validate the modes below. Settle CLI spelling, source precedence and local/remote
  deduplication. Recommend `worktrees` as the default. Preserve divergent refs and known snapshot-only tasks.
- **Q4 — Cost and partial coverage**: Set finite total and per-source budgets for inventory, declaration reads,
  Git observation and comparisons. Measure representative repositories. Define stable codes and output fields for
  complete, partial and failed observation; timeout or inaccessible candidates cannot become zero overlap.
- **Q5 — Creation and discovery**: Retain creation registration without worker recovery duties. Verify automatic-path
  failure isolation and hidden maintenance discovery in CLI and generated agent surfaces. Keep Host recovery guidance
  separate from worker publication/ACK obligations.

## 3. Proposed Design & Impact

### 3.1 Creation snapshots and worker responsibilities

Retain automatic registration after successful destination creation by both handoff forms and direct `spec new`.
Keep linked-worktree eligibility, registry storage, owner tokens and post-finish cleanup. Do not introduce
standalone-checkout auto-registration or require it for Host observation. A creation snapshot records incomplete
inputs as unresolved and remains initial evidence, not a claim about completed task declarations.

Automatic registration is best effort. A registration failure preserves the primary creation result, exit code and
`--strict` behavior. It emits no default advisory, result error/notice field or worker recovery instruction.
Diagnostics use verbose-only logging; diagnostic failure cannot fail creation. Preserve primary-operation errors
and notices. A pre-publication failure leaves no new record; a journal failure after publication retains the
published snapshot. Do not add retries, alternate storage, permission escalation or later workflow refresh triggers.

Remove worker `scope update`, manual registration and ACK obligations from task writing, reconciliation, delegated
worker acceptance and equivalent guidance/error actions. Keep normal delivery commands for their own purposes.
Neither explicit nor internal `workflow next` evaluation collects or publishes scope. No harness extension is needed.

Hide `scope update` from ordinary help and generated agent discovery. Preserve direct maintenance invocation and its
ACK/error semantics. Explicit maintenance commands remain operator tools, not a worker protocol. Keep `query`, history
and `compare` read-only with their existing meanings. Creation silence does not silence an explicitly invoked Host
collection failure or maintenance failure.

### 3.2 Explicit Host collection

Provide an explicit Host-facing operation under `devkit spec scope`. An illustrative invocation is
`devkit spec scope collect --mode worktrees`; Planning settles the command and option names.

The operation builds an invocation-local observation report. It does not update worker records, revisions, tokens
or journals, and it does not require worker token access. Reuse path parsing, source labels and overlap comparison
where their semantics apply. Extract reusable parsing/collection into the appropriate service layer when required.

Inventory comes from the repository's worktree list, local activity refs, remote-tracking activity refs and existing
registry records. State inclusion/exclusion reasons for candidates. A snapshot is not a complete active-work
inventory. A missing record does not exclude an otherwise discoverable task.

| Mode | Evidence collected | Visibility boundary |
| --- | --- | --- |
| `snapshot` | Stored creation/maintenance records and their scope paths | No live worktree or branch scope refresh; retain stored publication times |
| `refs` | Snapshot evidence plus declarations at pinned local/remote-tracking commits and committed paths against the selected base | No dirty worktree observation; remote refs reflect locally available fetched commits |
| `worktrees` | `refs` evidence plus declarations and committed, staged, unstaged and untracked paths in accessible worktrees | Inaccessible or other-machine checkout contents remain unobserved |

Higher modes attempt additional evidence rather than implying full visibility for every task. If a source cannot be
read, retain usable evidence and report the missing source and reason. Current declarations supersede older ones for
the same confirmed task/source. Unobserved portions remain explicitly snapshot-only or unresolved. Do not silently
union obsolete declarations into current scope or present fallback snapshots as fresh observations. Planning settles
exact source reconciliation rules, including snapshot fields unsupported by observable refs.

Select observation inputs with `--mode`; select network refresh separately with explicit `--fetch`. Without
`--fetch`, collection performs no network refresh. With it, fetch before pinning remote refs and report failure or
incomplete remote coverage. Reject `--fetch` with `snapshot` mode. Fetch may update local Git refs; collection still
leaves worker registrations unchanged. Do not add implicit branch checkout, worker commits or pushes.

### 3.3 Identity, provenance and incomplete coverage

Bind each observed source to exact task identity, ref/commit SHA or worktree path. A matching branch name alone is
insufficient to merge identities. Deduplicate confirmed copies at the same commit. If local and remote tips diverge,
preserve both observations and expose divergence rather than arbitrarily selecting one. Worktree dirty changes
remain separate evidence even when its HEAD matches a remote ref.

Each task result carries evidence source, observation time, pinned SHA where available, selected base, publication
time for stored snapshots, observed layers and missing layers/reasons. A commit timestamp is not a fetch timestamp.
If exact last-fetch information is unavailable, report it as unknown. Reading an old record does not refresh its
publication time. Pin refs before reading declarations and diffs.

Working directories can change during collection. Detect changes where feasible and report unstable observation;
never claim one atomic snapshot across all worktrees. Track collection start/end and the coverage attempted.

Return one structured report with inventory coverage, per-source problems, scopes and pairwise overlap evidence.
A partially readable inventory, timeout, unknown base or missing declaration is not evidence of no overlap.
Planning defines stable codes, text sentinels, JSON fields and exit semantics through the Agent Advisory Protocol.
Usable partial results carry notices; an operation that cannot run raises an advisory error. Do not manufacture
worker ACKs or permission requests. Scope evidence never grants or refuses writes.

### 3.4 Remote visibility and operating guidance

The default registry is shared by linked worktrees in one Git common directory, not automatically by separate clones
or machines. Initial handoff evidence helps a Host only when that snapshot, or the initial committed proposal/spec,
is actually available to it. Do not claim universal visibility from handoff alone.

The intended future direction is to allow a cloud-backed shared registry repository, for example Firestore, so
initial handoff snapshots published on one PC can be read by a Host on another. This assumes a configured shared
backend, repository/namespace identity, access credentials and a defined publication/ownership contract. It does
not follow from the local filesystem adapter. This proposal records the direction only: backend selection,
cloud adapter implementation and cross-machine registration eligibility are outside its acceptance scope.
Reconsider cloud support when multi-PC snapshot sharing becomes an implementation requirement. Even with that
backend, creation snapshots do not reveal subsequent private worktree changes without further publication.

Remote-tracking refs expose only fetched committed content. Another machine's uncommitted, untracked or unpushed
changes cannot be observed, including after `--fetch`. A registered other-host task without usable refs remains
snapshot-only or unverifiable. Unknown tasks cannot be discovered from an inaccessible machine.

For frequent multi-PC or isolated-cloud work, recommend a PR with pushed declarations and implementation changes as
the shared review/integration surface. A PR improves published-change visibility; it does not expose private dirty
worktrees or unpushed commits. This proposal adds no PR polling, distributed watcher or remote registry service.

### 3.5 Proposed acceptance evidence

- **AC-01 — Creation**: Both handoff forms and `spec new` retain registration in eligible linked worktrees.
  Skeleton inputs remain unresolved. Base and isolated checkouts do not gain automatic registration. Registration
  failures preserve primary text/JSON results and strict/non-strict exits without worker recovery output.
  Verbose diagnostics and post-publication journal failure follow section 3.1.
- **AC-02 — Worker removal**: Source guidance has no mandatory scope publication, registration or ACK steps.
  Help/discovery omit `update`; direct maintenance help and invocation retain their contract.
- **AC-03 — Workflow isolation**: Explicit `next`, internal evaluation, readiness and worker inspection perform no
  scope collection/publication. The harness needs no new provider or `devkit-spec` dependency.
- **AC-04 — Modes**: Fixtures distinguish snapshots, committed local/remote declarations and live dirty paths.
  Only the requested mode's live inputs are read. Host collection finds qualifying unregistered tasks without
  reading/creating owner tokens. Queries/history/compare stay unchanged.
- **AC-05 — Identity and refs**: Confirmed same-task/same-SHA copies deduplicate without losing dirty evidence.
  Divergent refs retain their evidence. Stale lifecycle evidence, ambiguous identity and unknown/moved/deleted bases
  have explicit classifications. Ref declarations come from pinned SHAs, not another checkout.
- **AC-06 — Coverage**: Inaccessible worktrees, malformed inputs, inventory failures and timeouts produce explicit
  gaps and stable codes. Unaffected evidence remains usable. Results do not certify independence or atomic
  cross-worktree observation. Budgets are finite and measured before acceptance.
- **AC-07 — Remote boundary**: Separate clones do not share snapshots by default. No-fetch results identify locally
  available refs; fetch success/failure has explicit coverage. Neither mode nor fetch claims another PC's dirty or
  unpushed changes. Reject snapshot-plus-fetch. PR guidance describes only published visibility.
- **AC-08 — Read separation**: Collection leaves registry records, revisions, tokens and journal unchanged.
  Only explicit `--fetch` updates remote-tracking refs. Registration ownership, optimistic concurrency,
  comparison and post-finish cleanup continue to work.

Non-goals: worker refresh protocols, `workflow next` observation, standalone auto-registration, continuous watching,
remote registry transport, cross-cloud aggregation, native/Git hooks, automatic dispatch, PR polling, exclusive
ownership, overlap-based refusal, semantic merge-conflict detection and workflow approval changes.

Silent creation-registration handling is an explicit exception for automatic observation failures. Explicit Host
operations and maintenance commands retain Agent Advisory Protocol error/notice semantics.

## 4. Lifecycle & Retirement Criteria

Keep the proposal draft until Planning settles Q1–Q5. The source-backed self-review in `materials/self-review.md`
is not independent Planning acceptance. Validate inventory, ref inputs, provenance, partial coverage and bounded cost
before direction acceptance. No worker update or workflow trigger may compensate for gaps.

Create a PADR replacing the skill-maintained refresh decision in ADR-worktrees-branches-and-scope with retained
creation registration and explicit Host observation. Preserve linked-worktree registration, storage, ownership and
cleanup decisions. Record silent creation failures and multi-machine visibility limits. Reconcile
CAP-COLL-work-scope-registry, UC-run-parallel-work-safely and CAP-HARN-agent-guidance during Development.
CAP-DLV-workflow-orchestration needs no observation-extension contract. No direction acceptance, Development handoff
or runtime implementation is part of this Backlog edit.
