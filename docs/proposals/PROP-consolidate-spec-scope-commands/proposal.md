---
id: PROP-consolidate-spec-scope-commands
title: Consolidate the spec scope commands around collect
summary: Retires or folds the devkit spec scope register, query, compare and hidden update commands and the second paths-changed pipeline into the Host's collect observation, keeping release, sweep and the journal.
status: reviewing                     # draft | reviewing | accepted | rejected
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

Hypothesis: one observation entry (`collect`) plus `release`, `sweep` and at most a journal reader covers every
documented workflow with one pipeline.

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
- **Q2**: In `ADR-worktrees-and-scope` §4 "Host-owned scope observation", the collect-modes clause and the retained
  hidden `update` with its ACK contract; in §6, the sentence keeping the maintenance ACK tests as regression checks.
  `PADR-collect-only-scope-observation` supersedes them in part; opt-in fetch, deadlines, read-only collection and
  the post-finish cleanup stay.
- **Q3**: Open questions for the user (below); the recommendation retires `compare` without folding it and drops the
  journal reader.

## 3. Proposed Design & Impact

One feature spec in devkit-spec. Retirement, collect narrowing and the pipeline removal change one capability
(`CAP-COLL-work-scope-registry`), one feature package and their tests together, and none is independently useful
without the others (the pipeline goes away only because `update` goes), so no decomposition is needed.

- **Retire** `devkit spec scope register`, `query` (and `--history`), `compare` and hidden `update`, with
  `UpdateScopeUseCase`, `Registry.update`, `request_id` replay, the `Ack` model and `[SCOPE_ACK]`,
  `QueryScopesUseCase`, `CompareScopesUseCase` and `services/compare.py` once nothing uses them, and the codes
  `SPEC_SCOPE_ACK_FAILED` and `SPEC_SCOPE_TOKEN_MISSING`. Keep `collect`, `release`, hidden `sweep`, creation
  registration, the post-finish cleanup and journal writes.
- **One paths-changed pipeline (SP-1)**: creation registration stores declarations, unresolved inputs and the base
  anchors (`base_revision` = HEAD at creation, `base_ref`) and no observed Git paths; `observe_git` and its
  registry-side runner go. At creation the registration HEAD is the range start, so the committed range is empty
  by construction and only the creation's own dirty files were observed, which collect reads live. Collect keeps the
  §4.1 registration cap and intersection rule for registered observations and the branch-relative range otherwise.
- **Narrow `collect`** to `devkit spec scope collect [--fetch <remote>]... [--timeout <s>] [--source-timeout <s>]`:
  it always observes records, local and remote-tracking `plan-*`/`dev-*` refs and accessible worktrees. `--mode`
  and `--base` go; the fix strings that named `--mode` are rewritten. `--fetch` and the two budgets stay (below).
- **Journal**: keeps its writes. Its reader follows the answer on the journal question.
- **Records**: existing records may carry `last_request_id`, `last_added`, `last_removed` and journal files may hold
  `update` events; both stay readable (tolerated, not written).
- **Documents**: CAP-COLL §2, §3 rules 5-6, §4.1, §4.3-§4.6, §4.8, §4.9; CAP-HARN-command-mount §4.2 and §4.6;
  CAP-HARN-agent-guidance (spec-orchestrate row, Host scope observation); CAP-DLV-proposal-planning's
  `target-docs.md` sentence; UC-run-parallel-work-safely; the supersession line in `ADR-worktrees-and-scope`; the
  spec-orchestrate skill source; the target-docs scaffold comment; `.devkit/architecture.toml`'s
  `usecase_exceptions` entries for `query._record_warnings` and `query._spec_dir`. Blueprint: `target-docs.md`.

### Expected acceptance scenarios

- **AC-01**: Given the CLI, when `devkit spec scope --help` is read or `register`, `query`, `compare` or `update` is
  run, then only `collect`, `release` (and hidden `sweep`) exist and the removed names fail as Click usage errors
  (exit 2, "No such command"), with no `[SCOPE_ACK]` anywhere.
- **AC-02**: Given a linked worktree, when `devkit spec proposal handoff` or `devkit spec new` registers the unit,
  then the record holds the declared scopes, unresolved inputs, `base_revision` and `base_ref`, no `observed` scope,
  and zeroed or absent `last_*` fields; primary output and exit codes are unchanged.
- **AC-03**: Given registered and unregistered `dev-*`/`plan-*` sources, when `collect` runs with no options, then it
  reports snapshot, ref and worktree observations with the §4.1 cap for registered ones and `branch-relative` for
  unregistered ones, horizons and coverage unchanged from the current `worktrees` mode.
- **AC-04**: Given `collect --mode` or `--base`, then the CLI refuses the unknown option as a usage error; `--fetch`, `--timeout` and
  `--source-timeout` keep their validation and effects.
- **AC-05**: Given a registry with records and journal lines written before the change (with `last_*` fields and
  `update` events), when `collect`, `release`, `sweep --apply` and the post-finish cleanup run, then they read them
  without new warnings and keep their outputs, codes and the `ScopedCleanup` contract.
- **AC-06**: Every remaining error and warning `[FIX]` in the scope feature names only existing commands and options,
  and CAP-COLL §4.8 lists exactly the codes the feature can raise.
- **AC-07** (per the journal answer): either no journal reader exists and CAP-COLL says how the journal file is read
  for diagnostics, or the chosen reader passes its paging scenarios.

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

`--mode` goes: guidance passes only the default, snapshot candidates are already part of every mode, and the only
other uses are tests and two fix strings. `--base` goes: no guidance or fix names it, and the selection chain
(`devkitBase`, record base, integration hints) with `unknown-base` as a visible gap covers it. `--fetch` stays: it is
the only bounded remote refresh (configured remotes, `plan-*`/`dev-*` namespace, no tags or pruning) that the ADR
keeps for multi-PC visibility, and a plain `git fetch` would not keep those limits. `--timeout` and
`--source-timeout` stay: `SPEC_SCOPE_COLLECTION_PARTIAL` names them as the recovery for `source-timeout` and
`result-limit`. The JSON `mode` field is dropped with the option. C3-3 is therefore taken for `--mode` and `--base`
only.

### Creation registration

Creation registration keeps its best-effort, verbose-only failure handling. Without `observe_git` it reads
declarations and runs Git only for HEAD and the base checkout's branch, under the same `[tool.spec.scope] timeout`.
Its unresolved inputs keep the §4.1 declaration reasons; the Git-side reasons (`missing-base-ref`,
`missing-base-revision`, `unknown-base-revision`) are no longer stored on records and remain collect's concern
(`unknown-base`).

### Codes

`SPEC_SCOPE_RECORD_MISSING`, `SPEC_SCOPE_STALE_REVISION`, `SPEC_SCOPE_TOKEN_MISMATCH` and `SPEC_SCOPE_RECORD_INVALID`
stay because `release`, `sweep` and the cleanup still raise them; their CAP-COLL conditions drop `update`/`query`.
`SPEC_SCOPE_TIMEOUT`'s fix drops the `--request-id` retry. `SPEC_SCOPE_SPEC_NOT_FOUND` stays as the code creation
registration's verbose diagnostic names.

### Verification

Tests that exercise only retired commands are deleted; tests that used `register`, `query` or `update` as fixtures
(scope `test_localfs.py` with `tests/support/spec_support/scope_contract.py`, delivery `test_cleanup.py`, e2e
`test_integration.py`) register through the creation path or the `Registry` directly. `observe_git` range tests are
checked against collect's existing range tests before removal; a range case collect does not yet cover moves to the
collection tests. `just test-affected` covers the package; the help-hidden assertion in
`tests/integration/package/test_help_and_notices.py` changes with the command set. `dev_effort: medium` stays: one
package and capability, a contract change without external consumers and no persisted-data migration (old records
stay readable).
