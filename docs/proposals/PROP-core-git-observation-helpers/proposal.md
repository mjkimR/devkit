---
id: PROP-core-git-observation-helpers
title: Public Git observation helpers in devkit-core
summary: "Add public devkit-core functions that read git worktree list and git status porcelain records and resolve a revision to a commit ID, and move the packages' private parsers to them, so each Git output is parsed once and tested once."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: packages/devkit-core/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-core/
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit/tests/
    - packages/devkit-dist/src/devkit_dist/features/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/tests/
    - packages/devkit-adaptive/src/devkit_adaptive/features/
    - packages/devkit-adaptive/tests/
    - packages/devkit-mcp/src/devkit_mcp/features/
    - packages/devkit-mcp/tests/
    - packages/devkit-viewer/src/devkit_viewer/features/
    - packages/devkit-viewer/tests/
    - docs/development/reference/
    - docs/capabilities/compact/CAP-CMP-bounded-execution.md
    - docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md
  excludes:
    - docs/capabilities/
    - docs/decisions/
    - packages/devkit-spec/src/devkit_spec/bundles/
    - packages/devkit-adaptive/src/devkit_adaptive/bundles/
    - .devkit/architecture.toml
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-core-git-observation-helpers] Public Git observation helpers in devkit-core

## 1. Background & Hypothesis

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

The inventory with every site's semantics is `materials/call-site-inventory.md`.

The details that are easy to get wrong are decided separately in each copy: the record order of a rename in `-z`
output, the trailing slash of an untracked nested repository, and the `bare`, `detached`, `locked` and `prunable`
worktree records. Packages that may not import `devkit_spec` or `devkit_agt` cannot reuse the existing parsers, so
each new feature adds another (the adaptive assignment commands added the latest pair).

Hypothesis: one public, tested reading of each output in `devkit_core.core` removes the duplicated parsers without
changing any command's behavior, and new features stop adding copies.

## Source feedback (when this proposal receives feedback)

- `FB-no-public-git-observation-helpers`: the whole observation (worktree records, status records with both names of a
  rename, revision resolution, moving the existing callers).

## 2. Technical Spike Questions

- **Q1**: Which call sites read Git output with semantics a shared helper must preserve (no `-z`, first line only,
  `--no-optional-locks`, `--no-renames`, `--ignore-submodules=none`, deadlines through `Deadline`, a local `git`
  wrapper instead of `run_git`), and which differences are accidental?
- **Q2**: Does the caller migration land in the same spec as the helpers, or does the spec add the helpers and move
  only the callers whose tests pin the behavior, leaving the rest to later touches?
- **Q3**: Is revision resolution worth a helper, given most `rev-parse` uses are one-line calls, or should it be limited
  to resolving a revision to a verified full commit ID?
- **Q4**: Which record shapes (dataclass fields, rename representation, path decoding with `surrogateescape`) serve
  every current caller without each one re-mapping them?

## 3. Proposed Design & Impact

### Helpers in `devkit_core.core.git`

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
- **Commit resolution** (Q3, recommended option): `resolve_commit(cwd, revision) -> str | None` runs
  `rev-parse --verify --quiet --end-of-options <revision>^{commit}` and returns the full commit ID, `None` when Git
  reports the revision unknown (exit 1) or prints anything but a 40- or 64-digit hexadecimal ID (a leading `^`
  makes `rev-parse` print `^<id>`), and raises `GitError` otherwise.
- All decoding is UTF-8 with `surrogateescape`, which equals the `os.fsdecode` some callers use under a UTF-8
  file system encoding (the supported macOS and Linux setups); behavior preservation is claimed for that encoding. `devkit-core` keeps importing no application package.

### Caller migration (Q2, recommended option: in this spec)

Every parser in `materials/call-site-inventory.md` moves to the helpers, feature by feature, with each caller keeping
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
- Commit resolution: only `devkit_adaptive` assignment's `revision`, the one site without `--end-of-options`. It
  maps both `None` and `GitError` with exit status 128 to `ADAPTIVE_REVISION_UNRESOLVED`, as today; the command it
  names in `CAP-DLV-adaptive-assignments` gains `--end-of-options`. The other 25 `^{commit}` lines are single calls,
  not parsers, and stay.
- Not migrated: `devkit_agt.features.worktree.repositories.execution` and
  `devkit_agt.features.isolated_execution.repositories.runs`, which run Git through the standard-library-only
  execution module (`CAP-WT-task-worktrees`, `ADR-isolated-test-runs`); `devkit_spec` scope observation's
  fingerprint, which hashes raw output; status calls that test only emptiness.

### Behavior

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

### Tests and documents

- New `devkit-core` integration tests (`packages/devkit-core/tests/integration/core/`) run real Git for: a rename and a
  copy, an untracked nested repository, a non-UTF-8 path, `--no-renames`, pathspecs; main, linked, detached, bare,
  locked (with and without reason), prunable and unborn worktrees, and a path with a newline. Unit tests cover the
  parsers' malformed input (missing rename field, empty output).
- Each migrated feature's existing tests stay green unchanged, except the removed `compact` porcelain test and test
  doubles that fed a removed private parser; `just test-affected` selects them. Each accidental difference above
  gets a test in the feature it changes, and `resolve_commit` a `^HEAD` test.
- `docs/development/reference/core.md` documents the new functions beside `run_git`. Two capability lines change
  (the `status_records` sentence of `CAP-CMP-bounded-execution` and the resolution command of
  `CAP-DLV-adaptive-assignments`); no decision document changes.

## Planning decisions

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
- Q2 and Q3 are open; the design above follows the recommended option of each.

## 4. Lifecycle & Retirement Criteria

- On acceptance (plan-accept): `devkit spec proposal accept core-git-observation-helpers --by user` records
  `gate:plan-accept` and `status: accepted`, then the Planning branch is merged; an eligible draft may instead be
  accepted with `--direct` on the base. Development starts with `devkit spec proposal handoff core-git-observation-helpers`.
- On rejection: change only `status: rejected`, with the user's decision and reason as a decision sentence in the
  commit message; a later hygiene pass writes the rejection ADR and deletes the proposal directory.
