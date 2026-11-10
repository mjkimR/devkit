---
id: PLAN-core-git-observation-helpers
spec: SPEC-core-git-observation-helpers
---

# Technical Plan: `SPEC-core-git-observation-helpers` Public Git observation helpers in devkit-core

## 1. Constitution & Invariant Review

None. `devkit_core.core` is a root module every package may import (`ARCH-05-2-components`); `devkit-core` keeps
importing no application package. No feature edge changes: `gate` and `generated` keep their `compact` edge for
`run_command`, so `.devkit/architecture.toml` is not edited. The standard-library-only execution module
(`CAP-WT-task-worktrees`, `ADR-isolated-test-runs`) is untouched. No decision document changes; the two capability
lines that become stale (`CAP-CMP-bounded-execution`, `CAP-DLV-adaptive-assignments`) are updated in place.

## 2. Architecture Overview & Impact

- `packages/devkit-core/src/devkit_core/core/git.py` gains `WorktreeRecord`, `StatusRecord`,
  `parse_worktree_records`, `worktree_records`, `parse_status_records` and `status_records`, exported from
  `devkit_core.core`. Each runner is a thin call of `run_git`; each parser is pure, so a caller with its own runner
  (maintenance history snapshot, envelope commit, scope inventory, viewer planning) reuses the parser.
- Callers swap their private parsing for the records and keep their own mapping:

| Feature | Site | New reading | Mapping kept in the caller |
| --- | --- | --- | --- |
| `devkit_agt` worktree | `lifecycle._entries` | `worktree_records(base)` | `_resolve` path, zero HEAD to `None`, short branch, flags as bools |
| `devkit_agt` integration | `service._observe` | `worktree_records(root)` | exact unresolved path compare; `GitError` to `inspection_incomplete` |
| `devkit_agt` generated | `engine.snapshot` | `status_records(top, optional_locks=True)` | path to `(code, digest)` |
| `devkit_agt` gate | `commands._unstaged` | `status_records(root, untracked="normal", optional_locks=True)` | worktree column non-blank |
| `devkit_agt` maintenance history | `snapshot.capture` | own `git` runner + `parse_status_records` | path (rename source not listed, as before) |
| `devkit_agt` workflow | `envelope_commit.dirty` | own runner + `parse_status_records` | path to code |
| `devkit_agt` compact | `services/porcelain.py` | removed with its export and unit test | none |
| `devkit_dist` shared | `local.discover`, `local._worktrees` | `worktree_records(top, deadline=budget)` | first record, `bare` refused; `GitError` to `WorkspaceError` |
| `devkit_dist` host | `registrations._foreign_worktree` | `worktree_records(root)` | raw `path != root` |
| `devkit_spec` scope | `inventory.worktrees` | own `git` runner + `parse_worktree_records` | bare skipped; detached `ref=""`; raw HEAD |
| `devkit_spec` governance | `reconcile_contract._integration_base` | `worktree_records` with `GitError` to `None` | first record with a branch |
| `devkit_spec` worker | `inspect.dirty_paths` | `status_records(root)` (`--no-optional-locks` default) | sorted set of both names |
| `devkit_spec` delivery | `native_handoff._dirty_paths`, dirty base check | `status_records(..., optional_locks=True)` | Git order, both names |
| `devkit_spec` proposals | `report` dirty source check | `status_records(root, untracked="normal", optional_locks=True)` | first 20 names |
| `devkit_adaptive` assignment | `parse_worktrees`, `parse_status`, `worktrees`, `dirty`, `revision` | core parsers; `--end-of-options` + hex check | resolved path keys, key dictionaries, trailing `/` strip |
| `devkit_mcp` runtime | `BuildLaunchDescriptorUseCase` | `worktree_records(root)` | resolved paths, first is the executor |
| `devkit_viewer` browse | `planning._worktrees` | module `run_git(... "-z")` + `parse_worktree_records` | `plan-<slug>` branch, `GitError` to `errors` |

## 3. Component & Interface Design

```python
@dataclass(frozen=True)
class WorktreeRecord:
    path: Path              # as Git prints it, unresolved
    head: str | None        # all zeros for an unborn branch; None when absent (bare)
    branch: str | None      # full ref; None when detached or bare
    bare: bool
    detached: bool
    locked: str | None      # None absent, "" without reason, else the reason
    prunable: str | None


@dataclass(frozen=True)
class StatusRecord:
    code: str               # XY
    path: str
    original: str | None    # second field of a rename or copy (R or C in either column)


def parse_worktree_records(raw: bytes) -> list[WorktreeRecord]: ...
def worktree_records(cwd: Path, *, deadline: Deadline | None = None) -> list[WorktreeRecord]: ...
def parse_status_records(raw: bytes) -> list[StatusRecord]: ...
def status_records(
    cwd: Path, *pathspecs: str, untracked: str = "all", renames: bool = True, optional_locks: bool = False,
    ignore_submodules: str | None = None, deadline: Deadline | None = None,
) -> list[StatusRecord]: ...
```

`status_records` runs `git [--no-optional-locks] status --porcelain=v1 -z --untracked-files=<untracked>
[--no-renames] [--ignore-submodules=<value>] [-- <pathspecs>]`. Decoding is UTF-8 with `surrogateescape`.

The adaptive revision lookup runs `rev-parse --verify --quiet --end-of-options <value>^{commit}` and accepts the
output only when it matches `^(?:[0-9a-f]{40}|[0-9a-f]{64})$`; anything else raises `RevisionUnresolved`
(`ADAPTIVE_REVISION_UNRESOLVED`).

## 5. Error Handling & Edge Cases

- A rename or copy record without its second field raises `GitError("malformed git status output: ...")`; callers
  that translated Git failures keep translating (`devkit_dist` to `WorkspaceError`, viewer to `errors`, reconcile
  contract to `None`).
- Worktree parsing never fails on content: fields before the first `worktree` and unknown keys are ignored.
- Non-UTF-8 paths decode with `surrogateescape`, which equals `os.fsdecode` under the supported UTF-8 file system
  encoding.

## 6. Verification & Test Plan

- New `packages/devkit-core/tests/integration/core/test_git_observation.py` (real Git): main, linked, detached,
  bare, locked with and without reason, prunable, unborn and newline-path worktrees; rename, copy, untracked nested
  repository, non-UTF-8 path (skipped where the file system refuses such a name), `--no-renames`, pathspecs.
  New `packages/devkit-core/tests/unit/core/test_git_observation.py`: missing rename field, empty output, a
  worktree-column rename, unknown keys.
- Accidental-difference tests in the features: native handoff quoted path and rename (`AC-05`, `AC-06`), proposals
  report quoted path (`AC-05`), `devkit_mcp` non-UTF-8 worktree path (`AC-07`), adaptive `^HEAD` and `-` revision
  (`AC-08`), newline worktree path at `devkit_dist` shared, viewer planning and reconcile contract (`AC-09`).
- Checks: `just lint-check`, `just check`, `just rules-check`, `just test-affected --base
  1f8e0954cd2bd25cb93f0c0907e852440b2ba73f`, `just test-dist`; selective E2E (`--tier e2e`) when its selection
  covers the changed callers.
