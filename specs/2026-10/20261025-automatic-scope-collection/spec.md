---
id: SPEC-automatic-scope-collection
title: Creation snapshots and explicit host work scope collection
summary: "Retains creation snapshots and replaces worker scope publication with bounded explicit host observation of registry, branch and worktree evidence."
status: planned
created: 2026-10-25
related_capabilities: [CAP-COLL-work-scope-registry, CAP-HARN-agent-guidance]
related_usecases: [UC-run-parallel-work-safely]
workflow: sdd-spec-feature
---

# [SPEC-automatic-scope-collection] Creation snapshots and explicit host work scope collection

## Problem and user stories

The Host needs overlap evidence at scheduling time without worker publication/ACK duties. As the Host, I can
choose snapshot, ref or live-worktree evidence and see attribution, freshness and coverage gaps. As a worker, I
continue the normal workflow without maintaining scope records. ADR-host-owned-scope-observation authorizes this
change while preserving storage, registration eligibility and cleanup.

## Non-goals

**Scope Excluded**: workflow collection hooks, worker refresh protocols, cloud registry implementation, continuous
watching, PR polling, automatic dispatch, exclusive claims and semantic merge-conflict detection. Future cloud
snapshot sharing is a direction only; remote private work stays invisible.

## Acceptance Criteria

### [AC-01] Creation

- **Given** an eligible linked worktree and creation operation.
- **When** registration succeeds or any automatic observer component fails.
- **Then** initial registration is retained on success; failures produce no default notices/errors and preserve primary output and exits including strict.

### [AC-02] Worker removal

- **Given** source guidance and CLI discovery.
- **When** task writing, reconciliation or worker acceptance runs.
- **Then** no scope publication or ACK is required; update is hidden but directly callable.

### [AC-03] Workflow isolation

- **Given** explicit next, evaluation, readiness and worker inspection.
- **When** the operations run.
- **Then** no scope collection/publication or additional harness provider occurs.

### [AC-04] Observation modes

- **Given** snapshot records, activity refs and live dirty worktrees.
- **When** collect runs in each mode.
- **Then** only requested live layers are read; qualifying unregistered work is observable without reading or writing owner tokens.

### [AC-05] Identity and refs

- **Given** same-tip refs with equivalent or different base/cap inputs and divergent refs.
- **When** collection reconciles sources.
- **Then** only equivalent effective inputs deduplicate; distinct observations retain provenance and dirty paths; missing bases remain unresolved.

### [AC-06] Bounded partial coverage

- **Given** inaccessible, malformed, unstable, slow or oversized sources and dense overlap.
- **When** collection hits a source, deadline or data limit.
- **Then** coverage is partial with stable reason codes and bounded complete entries; explicit strict warnings exit 1 and ordinary usable results exit 0.

### [AC-07] Remote boundary

- **Given** separate clones and cached refs.
- **When** collect runs without fetch, with a requested fetch, or with invalid snapshot-plus-fetch.
- **Then** only requested fetch performs network refresh; no other-PC private changes are claimed; invalid combinations exit 2 with ARGUMENT_INVALID.

### [AC-08] Read separation

- **Given** existing registry, journal and token files.
- **When** host collection or ordinary query/history/compare runs.
- **Then** registry bytes, revisions and token files remain unchanged; creation ownership, maintenance ACK and cleanup retain their contracts.

## Approved operational contract

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

Provide an explicit Host-facing operation under `devkit spec scope`. The default invocation is
`devkit spec scope collect --mode worktrees`; The settled command is `collect`; the example omits optional filters and budgets.

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
union obsolete declarations into current scope or present fallback snapshots as fresh observations. Section 3.6 defines source reconciliation, including snapshot fields unsupported by observable refs.

Select observation inputs with `--mode`; select network refresh separately with explicit `--fetch`. Without
`--fetch`, collection performs no network refresh. With it, fetch before pinning remote refs and report failure or
incomplete remote coverage. Reject `--fetch` with `snapshot` mode. Fetch may update local Git refs; collection still
leaves worker registrations unchanged. Do not add implicit branch checkout, worker commits or pushes.

### 3.3 Identity, provenance and incomplete coverage

Bind each observed source to exact task identity, ref/commit SHA or worktree path. A matching branch name alone is
insufficient to merge identities. Deduplicate confirmed copies only when commit and effective scope inputs agree (section 3.6). If tips diverge,
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
Section 3.6 defines codes, output fields and exits through the Agent Advisory Protocol.
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

### 3.6 Settled operational contract

**Invocation and budgets.** Expose `devkit spec scope collect --mode snapshot|refs|worktrees` (default `worktrees`),
`--base <ref>` for an explicit integration-base override, repeatable `--fetch <remote>`, `--timeout <seconds>`
(default 30, integer 1–300) and `--source-timeout <seconds>` (default 5, integer 1–300). Existing output/workspace
options apply. The total deadline starts before inventory and includes optional fetch, parsing and comparison.
Each source gets at most the smaller of its source budget and total remaining time. Fetch is a source, never a
second independent total budget. Check the deadline during parsing and comparison; a long Python loop must yield
partial evidence rather than defeating the Git subprocess timeout. No retries run within the invocation. The total budget includes result preparation/encoding; blocking writes to a
slow output consumer are outside the computation deadline and are not a wall-clock completion guarantee.

Bound retained data as well as CPU time. Accept at most 1 MiB per declaration document and 16 MiB of declaration
content per invocation. Bound Git command output during reading, rather than buffering unlimited output before a
size check. The encoded report limit is 8 MiB, including notices and JSON/text framing. Reserve space for coverage
and summary before collecting evidence. Limit the report to 256 source observations, 10,000 returned pairs and
10,000 evidence entries in total; stop retaining entries earlier if the byte budget is reached. Check budgets
incrementally while reading, constructing and encoding the result, not after an unbounded allocation. Preserve
only complete result entries. Use `result-limit`/`input-limit` reasons, return coverage partial and mark remaining
sources/comparisons uncomputed. Represent omitted combinations by deterministic pair ordering plus counts and a
last-completed key, not by an unbounded list of missing pairs. These are fixed initial safety limits, not new
storage configuration; Development tests each limit and reserved-space behavior. Result-limit notices aggregate
counts and bounded examples so diagnostics cannot defeat the limit.

`--fetch <remote>` accepts only configured remotes. Fetch only branch refs into that remote's tracking namespace,
without tags, pruning or submodule recursion. Use noninteractive authentication and bounded subprocesses. Never
push, deepen history, invoke PR tooling or update local activity branches. Reject snapshot-plus-fetch and invalid
budgets/remotes as `ARGUMENT_INVALID`. After a failed fetch, retain cached refs with explicit fetch-failure coverage.
A successful fetch stamps this invocation's refresh time; cached refs have unknown freshness unless independently
known. This is not a remote registry transport.

**Candidate selection.** Snapshot mode reads existing records only. Refs mode adds all `plan-*` and `dev-*` full refs
under `refs/heads/` and configured `refs/remotes/<remote>/`, excluding symbolic remote HEAD aliases. Worktrees mode
also inventories all linked worktrees, including the main checkout and detached entries. Read registry records via
shared read locking without token lookup or cleanup. A missing registry is empty evidence, not a discovery failure;
an unreadable existing namespace is a coverage gap and does not prevent usable Git observation.

Resolve local branch markers `branch.<name>.devkitUnit` only after validating their target anchor at the pinned
SHA; otherwise use an exact activity-slug match. Remote refs have no remote branch-config authority. Prefer the
handed-off spec over its carried proposal when the relationship is unambiguous. Use the repository namespace,
anchor ID and unit path as the confirmed task key. Conflicting/malformed markers, zero/multiple matching anchors
or duplicate IDs on distinct unit paths yield unknown attribution, not a guessed identity. Detached or non-activity
worktrees without a verified record binding remain unknown candidates with separately attributable dirty paths;
do not assign their changes to every spec present in the tree.

An anchor with supported nonterminal lifecycle is an `active-candidate`, not proof of a running process. Terminal
`completed` specs and `rejected` proposals are `inactive` only when there is no contradictory evidence; in
worktrees mode this requires checking for dirty changes. Dirty terminal worktrees, unsupported statuses, mismatched
bindings or unreadable lifecycle are `unknown` and remain visible. Do not use commit age to infer inactivity.
The report retains inactive exclusions and reasons. Never read a registry-supplied path on another host merely
because it also exists locally. A live worktree read requires membership in this repository's Git worktree inventory
and matching common-directory identity; otherwise use its record as snapshot evidence only.

**Consistent source reads and bases.** The scope feature owns a small reader contract for text, existence, path kind
and file enumeration, with filesystem and pinned-tree adapters. Read anchors, `tasks.md`, reconciliation targets,
capability/use-case entrypoints and file/directory kinds from that same source. Extract shared parsing beneath use
cases; do not import worker/delivery use cases or add a cross-application dependency for discovery.

Base precedence is explicit `--base`, validated local `devkitBase`, a confirmed record's `base_ref`, then a uniquely
resolvable integration-base hint. Integration hints are the source remote's symbolic HEAD when available or the
non-activity branch of the base checkout; if both disagree, report an ambiguous base instead of choosing. Record
`base_source` and the pinned base SHA. A tracking peer of the same activity branch is not an integration base.
Missing bases, no common history or multiple merge bases leave committed coverage unresolved.

For confirmed registered observations, retain the existing registration-HEAD cap/intersection algorithm, with
pinned tip replacing `HEAD`. An explicit base does not remove that cap. If a recorded base ref is unavailable but
its historical revision remains readable, retain the existing historical fallback and mark its unresolved base.
For unregistered observations, use paths from `git diff --name-only --no-renames -z <unique merge-base> <tip>`.
Label this range `branch-relative`: it can include inherited stacked-task changes. Do not invent a registration cap
from the spec-creation commit. Missing history removes only the unavailable layer, not declarations or dirty paths.

**Observation reconciliation.** Give each source observation its own `observation_id` and `task_key` (nullable).
For one confirmed task, deduplicate committed evidence only when the pinned tip, selected base SHA, historical
registration cap, range method and declaration-source identity all agree. Same task/SHA with a different effective
base or cap remains a separate observation. Retain all aliases and distinct dirty worktree observations. At different SHAs, preserve separate observations and show ancestor/divergent relations;
never union their declaration lists. For a live worktree, current filesystem declarations supersede its committed
version; if unreadable, keep the committed version as labelled fallback. Preserve malformed/unreadable-input gaps.

A confirmed record supplies fallback only for layers that could not be observed. Retain historical evidence in
its own snapshot observation, with the original publication time. Do not mix its obsolete declarations or observed
paths into a successful current observation. Unmatched records remain snapshot-only candidates. Comparisons name
observation IDs, not ambiguous task IDs; skip comparisons within the same confirmed task. Unknown task identity
remains a separate candidate and may be compared conservatively. Pair counts are observation-pair counts.

**Output and outcome.** JSON is one object with `mode`, `started_at`, `finished_at`, `coverage`, `inventory`,
`observations`, `pairs`, `summary` and `notices`. `coverage` contains `status=complete|partial`, discovery/fetch layer
outcomes, pending/skipped source IDs and whether all requested comparisons finished. Complete means the requested
observable layers were attempted successfully for the discovered candidates; it never means all machines or private
changes are visible. Each observation carries task/commit/base provenance, observed/missing layers and unresolved
inputs. Each candidate has `activity=active-candidate|inactive|unknown`, identity evidence and inclusion reasons.
Text uses `[SCOPE_CANDIDATE: ...]`, `[SCOPE_OBSERVATION: ...]`, existing `[PAIR: ...]`/`[EVIDENCE: ...]` keyed by
observation IDs, and `[SUMMARY: ... coverage=complete|partial comparisons_complete=yes|no]`.

Use `SPEC_SCOPE_COLLECTION_PARTIAL` warnings for incomplete inventory, unstable reads, source failures and uncomputed
comparisons, with structured reasons such as `source-timeout`, `unknown-base`, `identity-ambiguous`, `fetch-failed`,
`source-unreadable`, `observation-changed`, `result-limit` or `input-limit`. Keep those reasons and affected IDs in result coverage as well as
notices. Positive overlap does not change the exit code. A usable result, including a genuinely empty successful
inventory, exits 0; warning-bearing partial results exit 1 only under `--strict`. If no selected inventory source
can be read and no usable observation exists, raise `SPEC_SCOPE_COLLECTION_FAILED` and exit 2. Preserve existing
argument and configuration errors. A failed command uses the ordinary error-boundary JSON/text contract.

Read worktree HEAD/status before and after collecting and compare fingerprints for declaration files actually read.
If any differ, mark that observation unstable and coverage partial without retrying. This is best-effort change
detection: a change-and-revert or concurrent edit of an unread file can escape it. Do not certify atomicity.

**Verification limits.** Performance probes establish feasibility, not production latency. Development must validate
total/source deadline enforcement with deterministic slow-reader, slow-Git and comparison fixtures, including
partial output preparation before the deadline and bounded retained/encoded evidence. The final implementation is not allowed to hide truncated pairs behind a
complete status. Source-reader extraction, identity classification and the public output contract require targeted
integration tests; ordinary overlap semantics and explicit maintenance behavior remain regression checks.


## Verification provenance

Planning experiments are in `docs/materials/2026-10/20261025-automatic-scope-collection/planning-evidence.md`.
They demonstrate feasibility only; Development must exercise AC-01–AC-08. No change to workflow approval authority
or overlap matching is authorized.
