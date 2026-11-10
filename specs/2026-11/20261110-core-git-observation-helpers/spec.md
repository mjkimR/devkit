---
id: SPEC-core-git-observation-helpers
title: Public Git observation helpers in devkit-core
summary: Add public devkit-core functions that read git worktree list and git status porcelain records, and move the packages' private parsers to them, so each Git output is parsed once and tested once.
status: completed
created: 2026-11-10
related_capabilities: [CAP-CMP-bounded-execution, CAP-DLV-adaptive-assignments]
related_usecases: []
workflow: sdd-spec-feature
---
# [SPEC-core-git-observation-helpers] Public Git observation helpers in devkit-core

## 1. Problem Statement & Motivation

Handed off from proposal PROP-core-git-observation-helpers on 2026-11-10.
- **Preserved Materials**: `docs/materials/2026-11/20261110-core-git-observation-helpers`

### 1. Background & Hypothesis

`devkit_core.core` exports only `run_git`, `run_git_text` and `is_ancestor` for Git. Every feature that needs the
worktrees of a repository or the records of `git status --porcelain` parses the output itself:

- `git worktree list --porcelain` is read at 12 call sites in six packages (`devkit_agt` worktree lifecycle,
  execution, isolated execution and integration; `devkit_dist` shared repositories and host registrations;
  `devkit_spec` scope inventory and reconcile contract; `devkit_adaptive` assignment; `devkit_mcp` runtime
  configuration; `devkit_viewer` browse planning). Some use `-z`, some split on blank lines, some read only the first
  line.
- `git status --porcelain=v1 -z` records are parsed at seven places in three packages: the shared
  `devkit_agt.features.compact.services.porcelain` (a feature without a `public_modules` entry, used by `generated`
  and `gate`), `devkit_agt` maintenance history and envelope commit, `devkit_spec` worker inspection and native
  handoff, and `devkit_adaptive` assignment. Two more `devkit_spec` sites read paths from non `-z` output as
  `line[3:]`, which a quoted path breaks.
- Revision resolution (`git rev-parse`) is written inline wherever a full commit ID is needed: 26 lines resolve
  `<rev>^{commit}`, with three different error conventions and `--end-of-options` at only three of them.

The inventory with every site's semantics is `docs/materials/2026-11/20261110-core-git-observation-helpers/call-site-inventory.md`.

The details that are easy to get wrong are decided separately in each copy: the record order of a rename in `-z`
output, the trailing slash of an untracked nested repository, and the `bare`, `detached`, `locked` and `prunable`
worktree records. Packages that may not import `devkit_spec` or `devkit_agt` cannot reuse the existing parsers, so
each new feature adds another (the adaptive assignment commands added the latest pair).

Hypothesis: one public, tested reading of each output in `devkit_core.core` removes the duplicated parsers without
changing any command's behavior, and new features stop adding copies.

## 2. User Stories

- **US-1**: As a developer or agent adding a feature that reads Git worktrees or working-tree status, I want one
  public, tested reader of each output in `devkit_core.core`, so that I do not write another private parser.
- **US-2**: As a maintainer, I want every existing parser in scope moved to those readers, so that the details that
  are easy to get wrong (rename record order, the trailing `/` of an untracked directory, `bare`, `detached`,
  `locked` and `prunable` records, non-UTF-8 and newline paths) are decided and tested once.

## 3. Non-Goals

1. **Scope Excluded**: a public revision or commit resolver; the other 25 `<rev>^{commit}` lines stay unchanged.
2. **Scope Excluded**: the standard-library-only execution module (`devkit_agt.features.worktree.repositories.execution`
   and `devkit_agt.features.isolated_execution.repositories.runs`), `devkit_spec` scope observation's fingerprint
   of raw status output, and status calls that only test emptiness or compare text.
3. **Scope Excluded**: any change to a command's output, error code, feature edge (`.devkit/architecture.toml`) or
   decision document, apart from the accidental differences [AC-05] to [AC-09] name.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Worktree records

- **Given** a repository with a main worktree, a linked worktree on a branch, a detached linked worktree, a locked
  worktree with a reason and one without, a prunable worktree, a worktree whose path contains a newline, an unborn
  main branch, and separately a bare repository with a linked worktree
- **When** `devkit_core.core.worktree_records(cwd)` runs (it runs `git worktree list --porcelain -z`), or
  `parse_worktree_records(raw)` reads that output
- **Then** it returns one frozen `WorktreeRecord(path, head, branch, bare, detached, locked, prunable)` per worktree
  in Git's order, the main worktree (or the bare repository) first; `path` is Git's path, unresolved, newline
  included; `head` is Git's HEAD (all zeros for an unborn branch, `None` for a bare record); `branch` is the full
  ref or `None` when detached or bare; `locked` and `prunable` are `None` when absent, `""` with no reason and the
  reason otherwise; unknown keys are ignored and empty output is `[]`.

### [AC-02] Status records

- **Given** a working tree with a staged rename, a staged copy, an untracked nested repository, a file with a
  non-UTF-8 name, and pathspecs or options to apply
- **When** `devkit_core.core.status_records(cwd, *pathspecs, untracked="all", renames=True, optional_locks=False,
  ignore_submodules=None, deadline=None)` runs, or `parse_status_records(raw)` reads `git status --porcelain=v1 -z`
- **Then** each record is a frozen `StatusRecord(code, path, original)`: `code` the two-letter `XY`, `path` Git's
  path with the trailing `/` of an untracked directory kept and a non-UTF-8 byte kept by `surrogateescape`,
  `original` the source of a rename or copy (`R` or `C` in either column) and `None` otherwise; `renames=False`
  passes `--no-renames` and yields `D` and `A` records instead of `R`; pathspecs are passed after `--` and limit the
  records; `optional_locks=False` passes `--no-optional-locks`, `untracked` sets `--untracked-files` and
  `ignore_submodules` sets `--ignore-submodules`.

### [AC-03] Malformed status input

- **Given** status output whose rename or copy record lacks its second field, or empty output
- **When** `parse_status_records` reads it
- **Then** the missing field raises `GitError` (never a silent record) and empty output, empty fields and the trailing
  NUL yield no record.

### [AC-04] Parsers in scope moved; behavior preserved

- **Given** the parsers of `docs/materials/2026-11/20261110-core-git-observation-helpers/call-site-inventory.md`
  in scope (worktree lists: `devkit_agt` worktree lifecycle and integration service, `devkit_dist` shared
  repositories and host registrations, `devkit_spec` scope inventory and reconcile contract, `devkit_adaptive`
  assignment, `devkit_mcp` runtime configuration, `devkit_viewer` browse planning; status: `devkit_agt` generated
  engine, gate commands, maintenance history snapshot and envelope commit, `devkit_spec` worker inspection, native
  handoff and proposals report, `devkit_adaptive` assignment)
- **When** the change is applied
- **Then** each reads its output through `parse_worktree_records`/`worktree_records` or
  `parse_status_records`/`status_records`, keeping its own mapping, runner, options and error translation;
  `devkit_agt.features.compact.status_records`, its module and its unit test are gone; `devkit_adaptive`
  `parse_worktrees` and `parse_status` remain thin wrappers whose unit test passes unchanged; and every migrated
  feature's existing tests pass without change, apart from the removed `compact` test.

### [AC-05] Line-based status readers read real paths

- **Given** a checkout whose dirty paths include a name Git quotes under `core.quotePath` and a staged rename
- **When** `devkit_spec` native handoff's dirty base check or the proposals report's dirty source check refuses it
- **Then** the refusal's `target_files` name the real path and the rename's two names (new, then original), never
  a quoted name or the text `orig -> new`; the error codes stay `HANDOFF_BASE_DIRTY` and the report's dirty code.

### [AC-06] Native handoff reads a worktree-column rename

- **Given** status output whose rename record has `R` only in the worktree column (an intent-to-add rename)
- **When** native handoff's `-z` dirty reader reads it
- **Then** it lists both names, never a truncated pseudo-path.

### [AC-07] Runtime configuration tolerates a non-UTF-8 worktree path

- **Given** a repository with a linked worktree whose path is not valid UTF-8
- **When** `devkit_mcp`'s launch descriptor reads the worktree list
- **Then** it raises no `UnicodeDecodeError`; the base checkout is still the first record.

### [AC-08] Adaptive revision lookup refuses option-like input

- **Given** an adaptive assignment command given a revision `^HEAD`, a revision starting with `-`, or an empty one
- **When** it resolves the revision
- **Then** it runs `git rev-parse --verify --quiet --end-of-options <rev>^{commit}`, treats any output that is not a
  40- or 64-digit hexadecimal ID as unresolved, exits `2` with `ADAPTIVE_REVISION_UNRESOLVED` and appends nothing to
  the ledger; a valid revision still resolves to its full commit ID.

### [AC-09] Worktree lists read without `-z` now read a newline path

- **Given** a linked worktree whose path contains a newline
- **When** `devkit_dist` shared repositories, `devkit_viewer` browse planning or `devkit_spec` reconcile contract read
  the worktree list
- **Then** each reads the worktree's full path (the viewer lists it as a planning source on its `plan-<slug>`
  branch), and reconcile contract still takes the first `branch` record of the listing.

### [AC-10] Documents and boundaries

- **Given** the change
- **When** the reference and capability documents and the boundaries are checked
- **Then** `docs/development/reference/core.md` documents the four functions and two records beside `run_git`;
  `CAP-CMP-bounded-execution` no longer mentions `status_records`; `CAP-DLV-adaptive-assignments` names the command
  with `--end-of-options`; `devkit-core` imports no application package and `devkit-dist` tests pass without
  `devkit-agt` (`just test-dist`); `just lint-check`, `just check`, `just rules-check` and `just test-affected` pass.

## 5. Assumptions

- `optional_locks` keeps the proposal's default `False` (pass `--no-optional-locks`, as an observation should).
  Callers that ran `status` without it before (generated engine, gate commands, native handoff, proposals report)
  pass `optional_locks=True`, so none of them changes the index refresh it does today.
- `devkit_adaptive` `parse_worktrees` keeps returning its key-to-value dictionaries (built from the record), so its
  unit test and `require_worktree`'s `bare`/`prunable` checks stay unchanged.
- The worktree-list readers that ran `git worktree list --porcelain` without `-z` now run it with `-z`; the
  `devkit_viewer` reader keeps its own `run_git` import so its tests that patch it keep working.

## 6. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### Source feedback (when this proposal receives feedback)

- `FB-no-public-git-observation-helpers`: worktree records, status records with both names of a rename and moving the
  existing callers. Its revision resolver is declined (Planning decisions); the adaptive lookup it pointed at is fixed
  locally.

### 2. Technical Spike Questions

- **Q1**: Which call sites read Git output with semantics a shared helper must preserve (no `-z`, first line only,
  `--no-optional-locks`, `--no-renames`, `--ignore-submodules=none`, deadlines through `Deadline`, a local `git`
  wrapper instead of `run_git`), and which differences are accidental?
- **Q2**: Does the caller migration land in the same spec as the helpers, or does the spec add the helpers and move
  only the callers whose tests pin the behavior, leaving the rest to later touches?
- **Q3**: Is revision resolution worth a helper, given most `rev-parse` uses are one-line calls, or should it be limited
  to resolving a revision to a verified full commit ID?
- **Q4**: Which record shapes (dataclass fields, rename representation, path decoding with `surrogateescape`) serve
  every current caller without each one re-mapping them?

### 3. Proposed Design & Impact

#### Helpers in `devkit_core.core.git`

Exported from `devkit_core.core` beside `run_git`. Each reader is a pure parser over Git's bytes plus a thin runner
over `run_git`, so a caller with its own runner (an environment, a pathspec or a `Deadline` the runner does not take)
parses its own output with the same function.

- **Worktree records**: `parse_worktree_records(raw: bytes) -> list[WorktreeRecord]` and
  `worktree_records(cwd, *, deadline=None) -> list[WorktreeRecord]`, which always runs
  `worktree list --porcelain -z`. `WorktreeRecord` is a frozen dataclass: `path: Path` (as Git prints it, not
  resolved), `head: str | None` (as Git prints it, all zeros for an unborn branch; `None` when absent, as for a bare
  repository), `branch: str | None` (the full ref, `None` when detached or bare), `bare: bool`, `detached: bool`,
  `locked: str | None` and `prunable: str | None` (`None` when absent, otherwise the reason, `""` when Git gives
  none). Records keep Git's order, so the first is the main worktree. Unknown keys are ignored.
- **Status records**: `parse_status_records(raw: bytes) -> list[StatusRecord]` and
  `status_records(cwd, *pathspecs, untracked="all", renames=True, optional_locks=False, ignore_submodules=None,
  deadline=None) -> list[StatusRecord]`, which runs `status --porcelain=v1 -z` with the matching
  `--untracked-files`, `--no-renames`, `--no-optional-locks` and `--ignore-submodules` options and the pathspecs
  after `--`. `StatusRecord` is a frozen dataclass: `code: str` (the two-letter `XY`), `path: str` and
  `original: str | None` (the second field of a rename or copy, read only when `X` or `Y` is `R` or `C`). Empty
  fields and the trailing NUL produce no record; a rename without its second field is `GitError`, never a silent
  record. Paths are Git's, including the trailing `/` of an untracked directory.
- All decoding is UTF-8 with `surrogateescape`, which equals the `os.fsdecode` some callers use under a UTF-8
  file system encoding (the supported macOS and Linux setups); behavior preservation is claimed for that encoding. `devkit-core` keeps importing no application package.

#### Caller migration (in this spec)

Every parser in `docs/materials/2026-11/20261110-core-git-observation-helpers/call-site-inventory.md` moves to the helpers, feature by feature, with each caller keeping
its own mapping (path resolution, zero HEAD to `None`, the adaptive trailing-slash strip, its error translation and
record filtering):

- Worktree list: `devkit_agt` worktree lifecycle and integration service; `devkit_dist` shared repositories (both
  readers) and host registrations; `devkit_spec` scope inventory (parser only, over its own runner) and reconcile
  contract; `devkit_adaptive` assignment; `devkit_mcp` runtime configuration; `devkit_viewer` browse planning
  (parser only, over its own `run_git`, which its tests patch). `devkit_adaptive` keeps `parse_worktrees` and
  `parse_status` as thin wrappers over the core parsers that apply its path keys and trailing-slash strip, so their
  unit tests keep pinning that mapping.
- Status: `devkit_agt` generated engine, gate commands, maintenance history snapshot (parser only, over its own
  runner) and envelope commit; `devkit_spec` worker inspection and native handoff (the `-z` reader and the `line[3:]`
  reader), proposals report; `devkit_adaptive` assignment. `devkit_agt.features.compact.services.porcelain`, its
  export, its unit test and its sentence in `CAP-CMP-bounded-execution` are removed once no caller uses them.
- Revision lookup, fixed locally with no new helper: `devkit_adaptive` assignment's `revision`, the one full-commit
  site without `--end-of-options`, runs `rev-parse --verify --quiet --end-of-options <revision>^{commit}` and treats
  output that is not a 40- or 64-digit hexadecimal ID (a leading `^` makes `rev-parse` print `^<id>`) as unresolved.
  Every failure keeps mapping to `ADAPTIVE_REVISION_UNRESOLVED` as today; the command named in
  `CAP-DLV-adaptive-assignments` gains `--end-of-options`. The other 25 `^{commit}` lines stay unchanged.
- Not migrated: `devkit_agt.features.worktree.repositories.execution` and
  `devkit_agt.features.isolated_execution.repositories.runs`, which run Git through the standard-library-only
  execution module (`CAP-WT-task-worktrees`, `ADR-isolated-test-runs`); `devkit_spec` scope observation's
  fingerprint, which hashes raw output; status calls that test only emptiness.

#### Behavior

No command, output, error code or capability contract changes, except these accidental differences, which become
the shared behavior, each only for input no current test or contract uses:

- Worktree lists read without `-z` now read a path containing a newline.
- `devkit_mcp` no longer raises `UnicodeDecodeError` on a non-UTF-8 worktree path.
- The two `line[3:]` status readers (`devkit_spec` native handoff's dirty base check and proposals report) read a
  quoted path (`core.quotePath`) as its real name, and list a staged rename as its two names instead of the text
  `orig -> new`, which changes the listed paths and their count.
- `devkit_spec` native handoff's `-z` reader reads a rename's second field when either status column is `R` or `C`,
  not only the index column, so an intent-to-add rename no longer yields a truncated pseudo-path.
- `devkit_adaptive` refuses a revision with a leading `^` or `-` as unresolved instead of storing `^<id>` or passing
  it to Git as an option. `devkit_spec` reconcile contract
keeps reading the first `branch` record. Feature edges are unchanged (`gate` and `generated` keep their `compact` edge
for `run_command`); `.devkit/architecture.toml` is not edited.

#### Tests and documents

- New `devkit-core` integration tests (`packages/devkit-core/tests/integration/core/`) run real Git for: a rename and a
  copy, an untracked nested repository, a non-UTF-8 path, `--no-renames`, pathspecs; main, linked, detached, bare,
  locked (with and without reason), prunable and unborn worktrees, and a path with a newline. Unit tests cover the
  parsers' malformed input (missing rename field, empty output).
- Each migrated feature's existing tests stay green unchanged, except the removed `compact` porcelain test and test
  doubles that fed a removed private parser; `just test-affected` selects them. Each accidental difference above
  gets a test in the feature it changes, including a `^HEAD` revision test at the `devkit_adaptive` lookup.
- `docs/development/reference/core.md` documents the new functions beside `run_git`. Two capability lines change
  (the `status_records` sentence of `CAP-CMP-bounded-execution` and the resolution command of
  `CAP-DLV-adaptive-assignments`); no decision document changes.

### Planning decisions

- Size stays `L`: one spec and one task kind (`feature`); the migration is about twenty call sites in six packages,
  each a local swap verified by its feature's tests. Two specs would be needed only if the migration were split out
  (Q2 option b), and that second spec would be an `overall-refactor`, which has no proposal route.
- Q1 (settled from the inventory): `-z`, `surrogateescape` and Git's unresolved paths are the shared reading; path
  resolution, zero-HEAD mapping, bare/prunable filtering, the trailing-slash strip and error translation stay in the
  callers, which differ on them for stated reasons. The standard-library-only execution module is out of scope.
- Q4 (settled): flags with a reason are `str | None` so presence and an empty reason stay distinct (pinned by
  `devkit-adaptive` `test_values.py`); a rename keeps both names in one record; parsers are public so callers with
  their own runners reuse them.
- The `.devkit/architecture.toml` ownership the draft listed is dropped: no feature edge changes.
- Two capability files are owned by exception to the `docs/capabilities/` exclusion, each for the one line the
  migration makes stale; no other capability or decision text changes.
- Q2 (answered by the user): the helpers and the migration of every parser in scope land in one spec.
- Q3 (answered by the user): no public commit resolver. With one migrating caller it would be speculative API; the
  adaptive lookup gets `--end-of-options` and a hex check locally, and the other `^{commit}` lines stay.

### 4. Lifecycle & Retirement Criteria

- On acceptance (plan-accept): `devkit spec proposal accept core-git-observation-helpers --by user` records
  `gate:plan-accept` and `status: accepted`, then the Planning branch is merged; an eligible draft may instead be
  accepted with `--direct` on the base. Development starts with `devkit spec proposal handoff core-git-observation-helpers`.
- On rejection: change only `status: rejected`, with the user's decision and reason as a decision sentence in the
  commit message; a later hygiene pass writes the rejection ADR and deletes the proposal directory.

