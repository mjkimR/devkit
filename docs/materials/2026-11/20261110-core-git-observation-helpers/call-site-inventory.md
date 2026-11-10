# Git observation call-site inventory

Planning evidence for `SPEC-core-git-observation-helpers`, taken at worktree HEAD `467c5dbb` (`scout-01`). Paths are
relative to `packages/`. Counts are matching lines in `packages/*/src/**/*.py`, tests excluded.

## 1. `git worktree list --porcelain` (12 sites)

Six sites use `-z` and six do not. Classes: **L** load-bearing (a helper or the caller must keep it), **A** accidental
(differs from the others with no stated reason).

| # | Site | Runner, decode, `-z` | Reads | Load-bearing | Accidental | Test that pins it |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `devkit_agt` `worktree/usecases/lifecycle.py:179-197` `_entries` | `run_git`, `os.fsdecode`, `-z` | path (custom `_resolve`), HEAD (all zeros mapped to `None`: unborn base), short branch, `prunable`, `locked` as bools | zero HEAD to `None`, flag presence | bare not modelled | e2e `devkit/tests/e2e/features/worktree/test_lifecycle.py:680` (indirect) |
| 2 | `devkit_agt` `worktree/repositories/execution.py:54-` `remove` | stdlib `subprocess`, `GIT_*` stripped, text, no `-z` | exact `worktree <checkout>` line, HEAD, `detached` | **standard library only** (module docstring; `CAP-WT-task-worktrees` "standard-library subprocess Git calls", `ADR-isolated-test-runs`) | `\n\n` split | none direct |
| 3 | `devkit_agt` `isolated_execution/repositories/runs.py:40` `Runs.__init__` | `execution.git`, no `-z` | first line only | first record is the base; built on the stdlib-only `execution.git` | none | none direct |
| 4 | `devkit_agt` `integration/usecases/service.py:362` `_observe` | `run_git_text`, `-z` | exact field `worktree <plan.path>` | unresolved exact match; `GitError` sets `inspection_incomplete` | none | e2e `test_base_advance.py` (indirect) |
| 5 | `devkit_dist` `shared/repositories/local.py:82` `discover` | `run_git_text` + `Deadline`, no `-z` | first record, refuses `bare` | first record is main; `GitError` to `WorkspaceError` | `\n\n` split (newline in a path) | `devkit-dist/tests/integration/features/shared/test_shared.py` (indirect) |
| 6 | `devkit_dist` `shared/repositories/local.py:126-` `_worktrees` | `run_git_text` + `Deadline`, no `-z` | every path, unresolved | none | line split | same (indirect) |
| 7 | `devkit_dist` `host/usecases/registrations.py:288-` `_foreign_worktree` | `run_git_text`, `-z` | every path, raw `other != root` | unresolved compare | none | none direct |
| 8 | `devkit_spec` `scope/services/inventory.py:36` `worktrees` | `collection_git.git` (Popen, `Deadline`, `GIT_OPTIONAL_LOCKS=0`), `-z` | path, raw HEAD, full and short branch; bare skipped; detached gives `ref=""` | own runner; bare excluded; detached empty ref | none | `devkit-spec/tests/integration/features/scope/test_collection.py:83-150` (indirect) |
| 9 | `devkit_spec` `governance/usecases/reconcile_contract.py:118-132` `_integration_base` | `_git` (`GitError` to `None`), no `-z` | first `branch ` line of the whole listing | `GitError` to `None` | comment says "first entry" but a detached or bare first record is skipped | rule test `test_rule.py:187` (absence only) |
| 10 | `devkit_adaptive` `assignment/repositories/git.py:11-22,38` `parse_worktrees` | `run_git`, surrogateescape, `-z` | all keys; resolved path keys; flags by key presence | flags with empty reason; resolved keys | none | `devkit-adaptive/tests/unit/features/assignment/test_values.py:19-24`, `tests/integration/.../test_commands.py:230-244` |
| 11 | `devkit_mcp` `runtime/usecases/configuration.py:94` | `run_git`, strict `.decode()`, `-z` | resolved paths; first is the executor | first record order | strict decode raises on a non-UTF-8 path | none direct |
| 12 | `devkit_viewer` `browse/repositories/planning.py:61-88` `_worktrees` | `run_git`, surrogateescape, no `-z` | path, branch (`refs/heads/plan-<slug>`) | `GitError` appended to `errors` | `\n\n` split | `devkit-viewer/tests/integration/features/browse/test_planning.py:78-99` |

## 2. `git status --porcelain=v1 -z` parsers

| Site | Options | Rename second field | Decode | Trailing `/` | Returns |
| --- | --- | --- | --- | --- | --- |
| `devkit_agt` `compact/services/porcelain.py:8-20` `status_records` | caller's | skipped | bytes | kept | `(XY, path)` bytes; pinned by `devkit/tests/unit/features/compact/test_porcelain.py` |
| caller `generated/usecases/engine.py:195` | `--untracked-files=all` | via `status_records` | UTF-8 surrogateescape (`_decode`, `engine.py:136`) | kept | path to (status, digest) |
| caller `gate/usecases/gates/commands.py:54-58` | `--untracked-files=normal`; keeps worktree column non-blank | via `status_records` | `os.fsdecode` | kept | unstaged paths |
| `devkit_agt` `maintenance_history/repositories/snapshot.py:26-37` | `--untracked-files=all`, `-- . :(top,literal,exclude)...`, env `GIT_OPTIONAL_LOCKS=0`, own runner | skipped by index | `os.fsdecode` | kept | dirty paths (emptiness) |
| `devkit_agt` `workflow/repositories/envelope_commit.py:88-94` | `--untracked-files=all --ignore-submodules=none --no-renames`, `--literal-pathspecs` | none (`--no-renames`) | surrogateescape | kept | path to XY |
| `devkit_spec` `worker/usecases/inspect.py:125-142` | `--no-optional-locks`, `--untracked-files=all` | kept (both names) | `os.fsdecode` | kept | sorted set of both names |
| `devkit_spec` `delivery/usecases/native_handoff.py:79-89` | `--untracked-files=all` | kept when the index column is `R`/`C` | surrogateescape | kept | paths in Git order |
| `devkit_spec` `scope/services/observation.py:236-238` | default untracked | not parsed: raw output hashed | n/a | n/a | fingerprint (not a parser) |
| `devkit_adaptive` `assignment/repositories/git.py:25-34,56-57` | `--no-optional-locks`, `--untracked-files=all` | kept; `next()` raises on a missing field | surrogateescape | **stripped** (pinned: `test_values.py:19-20`) | sorted unique paths |

Non `-z` uses: ten test only emptiness or compare the text (`lifecycle.py:216`, `execution.py:86`, `pull_request.py:436`,
`native_plan_accept.py:208-209,305`, `native_handoff.py:62,326`) and need no helper. Two read paths as `line[3:]`
(`native_handoff.py:158-161`, `proposals/usecases/report.py:110-113`), which a quoted path (`core.quotePath`) breaks.

## 3. `git rev-parse` (107 lines)

| Category | Lines |
| --- | --- |
| A: full commit (`<rev>^{commit}`) | 26 |
| B: plain `rev-parse HEAD` | 23 |
| C: location (`--show-toplevel`, `--git-common-dir`, `--absolute-git-dir`, ...), 3 of them `_FACTS` data in `core/git.py` | 40 |
| D: other (`^{tree}`, `--verify` of a ref, `--symbolic-full-name`, ...) | 19 |

Category A error semantics differ: `--verify` raises on any failure; `--verify --quiet` through `lifecycle._query` maps
exit 1 to `None`; `devkit_adaptive` `git.py:50` accepts exits 0, 1 and 128 and passes `value + "^{commit}"` without
`--end-of-options`. `--end-of-options` appears only at `lifecycle.py:297`, `worker/usecases/inputs.py:231` and
`workflow/usecases/envelopes.py:51`. Of the 26 lines, 9 are in `lifecycle.py` and 5 in `worktree/usecases/planning.py`.

## 4. Existing shapes and exposure

- No current shape keeps the status code together with the rename's original path, and none keeps `locked` or
  `prunable` as a flag plus reason.
- No `public_modules` entry exposes a worktree or status parser; `devkit_core.core` is a root module every package may
  import (`.devkit/architecture.toml:14`).
- Removing `devkit_agt.features.compact.status_records` changes no feature edge: `gate` and `generated` keep their
  `compact` edge for `run_command`.
