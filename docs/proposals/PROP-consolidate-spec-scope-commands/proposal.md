---
id: PROP-consolidate-spec-scope-commands
title: Consolidate the spec scope commands around collect
summary: "Retires the devkit spec scope register, query, compare and hidden update commands with the registry update path and the second paths-changed pipeline, narrowing scope observation to collect beside release and sweep."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/collaboration/
priority: low                         # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/collaboration/
    - capabilities/harness/
    - capabilities/delivery/CAP-DLV-proposal-planning.md
    - usecases/collaboration/
    - decisions/2026-11/20261102-worktrees-and-scope.md
    - packages/devkit-spec/
    - .devkit/architecture.toml
  excludes:
    - packages/devkit/
    - packages/devkit-dist/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-consolidate-spec-scope-commands] Consolidate the spec scope commands around collect

## 1. Background & Hypothesis

Guidance uses only `devkit spec scope collect` (spec-orchestrate), plus `sweep` and `release` (worktree reference).
`register`, `query`, `compare` and the hidden `update` have no documented caller outside `CAP-COLL-work-scope-registry`,
yet they keep the registry write path (update ACK, `--request-id` idempotency, journal events) and a second
"paths changed since base" pipeline (code-pass SP-1). `collect` exposes `--mode snapshot|refs`, `--base`, `--fetch`
and two timeouts that no caller varies (C3-3). `query --history` switches the command into a journal reader with its
own paging grammar (C3-6). Sources: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` C3-2, C3-3, C3-6; `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` SP-1.

Hypothesis: one observation entry (`collect`) plus `release` and `sweep` covers every documented workflow with one
pipeline.

## 2. Technical Spike Questions

- **Q1**: Which commands does any Host procedure, extension or CI still need (`register` is reached internally by handoff)?
- **Q2**: `ADR-worktrees-and-scope` retains the hidden `update` and its ACK contract, and decides the collect modes. Which clauses need a superseding decision?
- **Q3**: Should `compare` fold into collect's declared and future evidence, and should the journal become `scope history`?

### Answers from Planning

Evidence: `materials/scope-command-callers.md` (scout at the Planning head).

- **Q1**: Only `collect` (spec-orchestrate, `CAP-HARN-agent-guidance`), `release` and `sweep` (spec worktree
  reference, spec-integrate, fix strings) have callers. devkit-agt reaches the post-finish cleanup through the
  `devkit.post_finish` entry point, which uses the `Registry` operations `query`, `release` and `sweep`, never the
  CLI. Creation registration calls `RegisterScopeUseCase` in-process. No CI job, script, other package or guidance
  invokes `register`, `query`, `query --history`, `compare` or `update`; `Registry.update`, `request_id` replay, the
  ACK model, the record's `last_*` fields and the journal's `update` events serve only the hidden `update`.
- **Q2**: In `ADR-worktrees-and-scope` §4 "Host-owned scope observation", the collect-modes clause and the clause
  keeping the maintenance `update` directly callable with its ACK contract; in §6, the clause that the maintenance
  ACK tests remain regression checks (the ownership and post-finish cleanup tests stay). The `query`/history wording
  of §4 "Registry storage and read access", §5 and §6 is reworded to the remaining read surfaces (collect and the
  `Registry` reads of release, sweep and cleanup) under the ADR-consolidation rule.
  `PADR-collect-only-scope-observation` supersedes the clauses in part; opt-in fetch, deadlines, read-only
  collection, `--base` (answer q4) and the post-finish cleanup stay.
- **Q3**: Decided by the user (§6): `compare` is retired without a replacement (q2), and the journal is removed with
  its reader (q1).

## 3. Proposed Design & Impact

One feature spec in devkit-spec. Retirement, collect narrowing and the pipeline consolidation change one capability
(`CAP-COLL-work-scope-registry`), one feature package and their tests together, and the pipeline consolidation
depends on `update` going, so no decomposition is needed. The design below folds the user's answers recorded in §6.

- **Retire** `devkit spec scope register`, `query` (and `--history`), `compare` and hidden `update`, with
  `UpdateScopeUseCase`, `Registry.update`, `request_id` replay, the `Ack` model and `[SCOPE_ACK]`,
  `QueryScopesUseCase`, `CompareScopesUseCase`, `services/compare.py` once nothing uses them, `_register_guidance`,
  and the codes `SPEC_SCOPE_ACK_FAILED`, `SPEC_SCOPE_TOKEN_MISSING` and `SPEC_SCOPE_RECORD_MISSING`. Keep `collect`,
  `release`, hidden `sweep`, creation registration and the post-finish cleanup.
- **One paths-changed pipeline (SP-1, answer q3)**: creation registration keeps recording the declarations, unresolved inputs,
  base anchors (`base_revision` = HEAD at creation, `base_ref`) and the worktree's staged, unstaged and untracked
  paths at creation (the uncommitted handoff output: promoted ADRs, supersession edits, moved materials, and any other
  dirty file), but obtains the dirty paths from collect's observation service (`services/observation.py`), not from
  `observe_git`. Its committed range is empty by construction (the start is the registration HEAD), so
  `observe_git`, its range logic and its registry-side runner go. Collect is the only implementation of the committed
  range and keeps the §4.1 registration cap and intersection rule for registered observations and the
  branch-relative range otherwise. Paths the observation service reports as invalid are stored as unresolved
  `invalid-path` instead of being dropped (rule 2).
- **Narrow `collect`** to `devkit spec scope collect [--base <ref>] [--fetch <remote>]... [--timeout <s>]
  [--source-timeout <s>]` (`--base` kept, answer q4): it always observes records, local and remote-tracking `plan-*`/`dev-*` refs and
  accessible worktrees. `--mode` goes, with the JSON `mode` field and the fix strings that named it.
- **Journal (answer q1)**: removed with its reader: no `journal.jsonl` appends, no `Event` model, journal
  lock deadline, `SPEC_SCOPE_JOURNAL_UNAVAILABLE` or `SPEC_SCOPE_JOURNAL_LINE_INVALID`. An existing `journal.jsonl`
  is left in place, unread and untouched.
- **Records**: existing records may carry `last_request_id`, `last_added`, `last_removed` and observed scopes from
  earlier updates; they stay readable and the `last_*` fields are no longer written.
- **Documents**: listed in `target-docs.md`, including CAP-COLL §2, §3 rules 5, 6 and 8, §4.1 (the Git-side reasons,
  the update re-detection paragraph and the register/update recollection sentence), §4.3 (record fields, operations,
  deadline, journal, and the read-access MUST re-anchored from `query` to collect and the registry reads of
  release, sweep and cleanup), §4.4-§4.6, §4.8, §4.9; CAP-HARN-command-mount §4.2 and §4.6; CAP-HARN-agent-guidance;
  CAP-DLV-proposal-planning; UC-run-parallel-work-safely; `ADR-worktrees-and-scope`. Code-side: the spec-orchestrate
  skill source, the target-docs scaffold comment, the `registered_dict` docstring and `.devkit/architecture.toml`'s
  `usecase_exceptions` entries for `query._record_warnings` and `query._spec_dir`.

### Expected acceptance scenarios

- **AC-01**: Given the CLI, when `devkit spec scope --help` is read or `register`, `query`, `compare` or `update` is
  run, then only `collect`, `release` (and hidden `sweep`) exist and the removed names fail as Click usage errors
  (exit 2, "No such command"), with no `[SCOPE_ACK]` anywhere.
- **AC-02**: Given a linked worktree with uncommitted handoff output, when `devkit spec proposal handoff` or
  `devkit spec new` registers the unit, then the record holds the declared scopes, the dirty paths at creation as
  `observed`, the declaration unresolved inputs (plus `invalid-path` for invalid dirty paths), `base_revision` and
  `base_ref`, and no committed-range reason; the `[SCOPE: ...]` line and JSON `scope` object keep their shape and the
  commands their exit codes.
- **AC-03**: Given registered and unregistered `dev-*`/`plan-*` sources, when `collect` runs with no options, then it
  reports snapshot, ref and worktree observations with the §4.1 cap for registered ones and `branch-relative` for
  unregistered ones, horizons and coverage as the current `worktrees` mode reports them.
- **AC-04**: Given `collect --mode <any>`, the CLI refuses the unknown option as a usage error; `--base`, `--fetch`,
  `--timeout` and `--source-timeout` keep their validation and effects.
- **AC-05**: Given a registry with records written before the change (with `last_*` fields and observed scopes) and an
  existing `journal.jsonl`, when `collect`, `release`, `sweep --apply` and the post-finish cleanup run, then they read
  the records without new warnings, keep their outputs, codes and the `ScopedCleanup` contract, and leave
  `journal.jsonl` unchanged.
- **AC-06**: CAP-COLL §4.8 lists exactly the `SPEC_SCOPE_*` codes the scope feature and the cleanup define, checked
  by a test that compares the defined codes with the table rows in both directions; every remaining `[FIX]` in the
  scope feature names only existing commands and options (a test scans them for `scope register|query|compare|update`,
  `--request-id`, `--task-id` outside `release`, and `--mode`).

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr consolidate-spec-scope-commands "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept consolidate-spec-scope-commands --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff consolidate-spec-scope-commands.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

## 5. Planning decisions

### Collect options

`--mode` goes: guidance passes only the default, every mode already reads the registry snapshots (so
`--mode snapshot` never rescued `SPEC_SCOPE_COLLECTION_FAILED`), and the only other uses are tests and two fix
strings. The `SPEC_SCOPE_COLLECTION_FAILED` fixes stop naming a mode; the report-metadata limit fix says to report
the limit. `--fetch` stays: it is the only bounded remote refresh (configured remotes, `plan-*`/`dev-*` namespace, no
tags or pruning) that the ADR keeps for multi-PC visibility. `--timeout` and `--source-timeout` stay:
`SPEC_SCOPE_COLLECTION_PARTIAL` names them as the recovery for `source-timeout`; its fix stops offering them for
`result-limit`, which a budget does not fix. `--base` stays (q4): it is the only override for remote-tracking
`plan-*`/`dev-*` refs, which carry no `devkitBase` marker, when `<remote>/HEAD` and the main checkout branch differ.
C3-3 is therefore taken for `--mode` only.

### Creation registration

Creation registration keeps its best-effort, verbose-only failure handling and its Git calls under the
`[tool.spec.scope] timeout`. The Git-side unresolved reasons of §4.1 (`missing-base-ref`, `missing-base-revision`,
`unknown-base-revision`) belonged to the committed range and are no longer stored on new records; collect reports an
unusable base as `unknown-base`.

### Codes and ownership lookup

`own()` returns no record when the token or its record is gone; its only remaining caller, the post-finish cleanup,
already treats both as nothing to release. `SPEC_SCOPE_TOKEN_MISSING` and `SPEC_SCOPE_RECORD_MISSING` therefore go
with `SPEC_SCOPE_ACK_FAILED` and the two journal codes (q1). Kept:
`SPEC_SCOPE_STALE_REVISION` (sweep), `SPEC_SCOPE_TOKEN_MISMATCH` (`release --task-id`), `SPEC_SCOPE_RECORD_INVALID`,
`SPEC_SCOPE_TIMEOUT` (fix without the `--request-id` retry), `SPEC_SCOPE_NOT_A_WORKTREE`,
`SPEC_SCOPE_SPEC_NOT_FOUND`, `SPEC_SCOPE_INPUT_INVALID`, `SPEC_SCOPE_LOCK_UNSUPPORTED`,
`SPEC_SCOPE_NAMESPACE_INVALID`, `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE`, the collection codes and
`SPEC_POST_FINISH_CLEANUP`. `SPEC_SCOPE_TOKEN_EXISTS`, `SPEC_SCOPE_TASK_EXISTS` and `SPEC_SCOPE_SHARED_WORKTREE` stay
as the codes of creation registration's verbose diagnostics; their fixes stop naming `scope query`, `scope update`
and `--task-id`. The sweep `--expect` argument fix names "a previous sweep". §4.8 marks the creation-only codes as
verbose diagnostics of automatic registration.

### Use case wording

`compare`'s retirement (q2) leaves queued Backlog drafts and drafts accepted with `--direct` on the base unobserved: collect
compares declarations once a unit has a `plan-*` or `dev-*` source. UC-run-parallel-work-safely step 1 and scenario 1
and CAP-DLV-proposal-planning say so instead of promising a comparison of every planned declaration. The practical
loss is small: `future`-only overlap does not serialize Planning, and a handed-off `dev-*` source is observed.

### Verification

Tests that exercise only retired commands are deleted; tests that used `register`, `query` or `update` as fixtures
(scope `test_localfs.py` with `tests/support/spec_support/scope_contract.py`, delivery `test_cleanup.py`, e2e
`test_integration.py`) register through the creation path or the `Registry` directly. The `observe_git` range tests
are compared with collect's range tests before removal; a range case collect does not cover moves to the collection
tests. The help-hidden assertion in `tests/integration/package/test_help_and_notices.py` changes with the command set.
`just test-affected` covers the package. `dev_effort: medium` stays: one package and capability, a contract change
without external consumers and no persisted-data migration (old records stay readable).

## 6. Open questions

None open. The user decided the first Planning turn's questions (`envelopes/answer-01.yaml`); each chose the
recommended option, folded above:

- **q1 Journal**: the scope journal and its reader are removed, together with the journal error codes.
- **q2 compare**: `devkit spec scope compare` is retired with no replacement.
- **q3 Creation dirty paths**: creation registration keeps recording the dirty paths at creation, read through
  collect's observation service.
- **q4 `--base`**: the `collect --base` option is kept.
