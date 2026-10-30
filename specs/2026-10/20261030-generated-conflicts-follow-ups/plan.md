---
id: PLAN-generated-conflicts-follow-ups
spec: SPEC-generated-conflicts-follow-ups
---

# Technical Plan: `SPEC-generated-conflicts-follow-ups` Follow-ups of the generated conflict settling

## 1. Constitution & Invariant Review

None. `ARCH-05-2-components` keeps `devkit-core` free of application imports; the change adds a primitive there and
moves one application call onto it. `CAP-WT-task-worktrees` already states that worktree Git runs through
`devkit_core.core.git.run_git`; after the change that holds without the `merge-tree` exception. `ADR-post-batch-test-run`
and `ADR-generated-conflicts-in-prepared-merge` already decide the batch completion the guides describe. No ADR
changes.

## 2. Architecture Overview & Impact

- `devkit_core.core.git`: the subprocess run moves into `run_git_result`, which takes the accepted exit statuses;
  `run_git` keeps its signature, memo and errors and returns `run_git_result(...).stdout` with only `0` accepted.
- `devkit_agt.features.worktree.services.merging`: `_merge_tree_output` calls `run_git_result(..., ok_returncodes=(0, 1),
  timeout=MERGE_TREE_TIMEOUT)` and maps `GitError` to the same `MergeFailedError` messages; the `subprocess` call and
  its environment copy leave the module.
- `docs/development/reference/core.md`: the `devkit_core.core.git` row names `run_git_result`.
- `docs/development/workflow.md`, `docs/development/ci-cd.md`, root `AGENTS.md` (repository-owned Verification
  paragraph): one sentence each.
- `spec-delegate` `references/payload.md`: one Workers bullet. The `spec` bundle is a selected bundle source, so
  `devkit sync` runs and its outputs are committed.
- `scripts/affected_tests.py`: the `docs/` entry of `DATA` gains the citation test and a `specs/` entry maps to it;
  `specs/` leaves `UNTESTED_PREFIXES`; the selection list in `docs/development/ci-cd.md` follows.
- Root `AGENTS.md` Architecture and Boundaries: one sentence naming `.devkit/architecture.toml`'s
  `feature_dependencies` entries for a delegated cross-feature choice, since the shipped payload rule cannot name a
  path of this repository (spec assumption 2).
- Root `AGENTS.md` Documentation section: one bullet naming `agent-asset-writing`.

No new dependency. `devkit_core.core.__init__` is outside the write scope, so `run_git_result` is imported from
`devkit_core.core.git`, as `repository_facts` is.

## 3. Component & Interface Design

```python
# devkit_core.core.git
class GitResult(NamedTuple):
    returncode: int
    stdout: bytes

def run_git_result(
    cwd: Path,
    *args: str,
    ok_returncodes: Collection[int] = (0,),
    input: bytes | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    index: str | None = None,
    deadline: Deadline | None = None,
) -> GitResult: ...
```

Decision: an explicit accepted-status parameter on a sibling function rather than on `run_git` itself, because
`merge-tree` needs the status to tell a clean tree (`0`) from a conflict (`1`), and returning a tuple from `run_git`
would change every caller's type; rather than standard output on `GitError`, because an accepted answer is not an
error (spec assumption 1). The memo of repository-location facts stays in `run_git`: those queries accept only `0`.

`_merge_tree_output(base, target, source) -> tuple[int, bytes]` keeps its role; `_merge_tree` keeps its checks and
messages. The standard error of an accepted exit was unused, so the tuple drops it; the exit-status check outside
`(0, 1)` moves into the runner and its `GitError`, which the caller maps to `MergeFailedError("git merge-tree failed;
nothing was changed on the target: <stderr or exit status N>")`.

## 4. Error Handling & Edge Cases

| Case | Before | After |
| --- | --- | --- |
| exit 0 / 1 | tree / conflict entries | same |
| other exit | `MergeFailedError` "git merge-tree failed; ...: <stderr or exit status>" | same message from `GitError.stderr` / `returncode` |
| timeout | `MergeFailedError` "git merge-tree timed out after 120.0s; nothing was changed on the target" | `GitError` (returncode `None`) mapped to `MergeFailedError` "<GitError message>; nothing was changed on the target" |
| Git missing | `MergeFailedError` "git is not available: ...; nothing ..." | same through the `GitError` message |

The timeout message gains the runner's ` in <cwd>`; the code (`WORKTREE_MERGE_FAILED`) and the "nothing was changed"
clause are kept, and no test or document pins that message text.

## 5. Verification & Test Plan

- `just test devkit-core core` (new `run_git_result` tests: AC-01, AC-02; existing `run_git` tests unchanged).
- `just test devkit features/worktree` and `just test devkit features/integration` unchanged (AC-03); a structural
  assertion that `merging` does not import `subprocess`.
- `just test devkit-spec bundles/spec` (payload guidance test: AC-05; budgets) and the citation test.
- `uv run pytest packages/devkit/tests/e2e/package/test_affected_tests.py` (AC-06).
- AC-04 and AC-07: read the sentences; `git diff --check`; `uv run devkit rules check`.
- `just lint-check`, `just check devkit-core`, `just check devkit`, `just test-affected` (keeping its `mode=full`
  fallback), `uv run devkit sync --check`.
