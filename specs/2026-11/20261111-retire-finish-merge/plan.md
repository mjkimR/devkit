---
id: PLAN-retire-finish-merge
spec: SPEC-retire-finish-merge
---

# Technical Plan: `SPEC-retire-finish-merge` Retire worktree finish --merge

## 1. Constitution & Invariant Review

- **ADR required before implementation.** Accepted decisions describe or require `finish --merge`:
  `ADR-local-and-pull-request-integration` (`[worktree] merge` applies to `finish --merge`; the CLI `finish --merge`
  builds a merge only when the target did not advance and takes the lock; it keeps refusing a moved target; it passes
  no readiness evidence), `ADR-orchestration-workers` (devkit refuses `finish --merge` while a unit is held),
  `ADR-worktrees-and-scope` (`pull_request = "required"` makes devkit refuse `finish --merge`) and
  `ADR-package-ownership-and-release-version` (the `devkit.finish_guard` `workflow-envelopes` entry point stays with
  devkit-agt). A new ADR, ADR-single-local-landing-route (to be written)
  (`docs/decisions/2026-11/20261111-single-local-landing-route.md`), supersedes exactly those clauses in part:
  - Decision: `devkit integration integrate --route local` is the only local landing route; `finish --merge` refuses
    with `WORKTREE_MERGE_RETIRED`; the library `finish` keeps cleanup only.
  - Dropped with reasons: the finish guard group (`ADR-post-merge-verification`, `CAP-INT-mcp-services` §4), the base
    fetch and push (`ARCH-04-2-delivery-policy`), the moved-target refusal (replaced by the moved-target build).
  - Kept: the envelope hold through the workflow gates and the Host's source-runtime `envelope check`.
- **Capabilities whose MUST clauses change**: `CAP-WT-task-worktrees` (§3 `finish --merge`, `--local-only` wording,
  the `devkit.finish_guard` MUST in the overview, `pull_request` policy text), `CAP-DLV-workflow-envelopes`
  ("Integration is refused"). Both are rewritten from the ADR.
- **No conflict** with `CAP-INT-mcp-services`, `ARCH-04-2-delivery-policy` or `ADR-post-merge-verification`: the
  surviving route already satisfies them; only their mentions of `finish --merge` change.
- **No new feature edge.** The worktree refusal composes the integration command text itself
  (`devkit_command`); worktree never imports integration (integration already depends on worktree).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `features/worktree/usecases/lifecycle.py` | `finish()` loses `merge`, `pull_request`, `guard`, `network`, `merge_method` and its whole landing branch (identity, upstream fetch, guard call, result build, fast-forward, push), plus `_check_upstream`, `_upstream`, `_push`, `_short`, `PUSH_TIMEOUT`, `FETCH_TIMEOUT` and the marked-branch base check that only `merge` reached. `before_remove` and `before_step` lines stay untouched (another unit edits `before_remove`) |
| `features/worktree/models/lifecycle.py` | `FinishResult.push` removed (also from `to_dict()`) |
| `features/worktree/models/errors.py` | New `MergeRetiredError` (`WORKTREE_MERGE_RETIRED`); remove `BlockedError`, `GuardFailedError`, `BaseBehindError`, `PushFailedWarning`, `PushRejectedWarning`; `UnmergedError` `[FIX]` and docstrings name the integration route |
| `features/worktree/services/extensions.py` | Remove `FINISH_GUARD_GROUP` and `run_finish_guards`; the module covers `devkit.post_finish` and `devkit.attach_check` |
| `features/worktree/usecases/configured.py` | `FinishActivity` drops `merge`, the lock and the guard; it finishes or discards |
| `features/worktree/cli.py` | `--merge` becomes a hidden flag that raises `MergeRetiredError` before any lookup; output line drops `push=`; help text names the integration route |
| `features/worktree/__init__.py`, `repositories/config.py` | Exports follow the removals; the `pull_request` template comment names the integration route |
| `features/integration/usecases/service.py` | The cleanup call passes no `merge`/`network` |
| `features/workflow/usecases/integration.py` (devkit-agt) | Module removed: `finish_guard`, `changed_units` and `unit_hold_reasons` have no other caller |
| `packages/devkit/pyproject.toml` | The `devkit.finish_guard` entry point and its comment removed |
| Spec bundle text | `references/branches.md` §2, `references/backlog.md.jinja` step 2, `references/worktree.md.jinja`, `references/worker-records.md` name the integration commands; `devkit sync` outputs committed |
| Living Spec | `CAP-WT-task-worktrees`, `CAP-INT-mcp-services`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-delivery-workflows`, `CAP-DLV-cli-and-output`, `CAP-DLV-project-policy`, `CAP-DIST-sync-and-transactions` (template comment), `ARCH-04-2-delivery-policy`, `ARCH-05-2-components` (entry-point group list), `ARCH-06-runtime-view`, `UC-drive-development-to-integration` (scenarios 11, 14), `UC-handle-delivery-problems-and-exceptions` (scenario 8), `docs/development/reference/{worktree,integration}.md` |

## 3. Component & Interface Design

```text
devkit worktree finish BRANCH [--discard] [--local-only] [-w DIR] [--format text|json]
  --merge (hidden)  -> WORKTREE_MERGE_RETIRED, exit 2, nothing read or changed beyond argument parsing
[WORKTREE_FINISHED: <branch> path= merged= removed= branch_deleted= discarded=]
```

```python
def finish(
    position: Position,
    branch: str,
    *,
    delete_branch: bool = True,
    before_remove: Callable[[FinishResult], None] | None = None,
    before_step: Callable[[str, FinishResult], None] | None = None,
) -> FinishResult: ...

class MergeRetiredError(WorktreeError):
    code = "WORKTREE_MERGE_RETIRED"      # ERROR, INPUT_ERROR, exit 2
    # fix: "Run `uv run devkit integration prepare <b> --route local`, present its scope, then run
    #       `uv run devkit integration integrate <b> --route local --expected-digest <digest>`
    #       (the digest is optional under dev-integration = auto)"
```

`finish` also loses `pull_request`: only the landing branch read it, and the PR policy refusal of local landing stays
in `plan_finish`.

## 4. Error Handling & Edge Cases

- `--merge --discard`: the retirement refusal wins (the flag is checked first); exit 2.
- A rerun of a stopped `finish --merge` (worktree removed, branch merged and marked) resumes with plain `finish`, which
  already handles a marked merged branch.
- A local integration that landed but left cleanup: `CAP-INT-mcp-services` recovery names `finish <branch>
  --local-only` (no `--merge`), which passes the merged check.

## 5. Verification & Test Plan

- Unit/integration tests (rewritten or removed with the code they cover, never weakened for kept behavior):
  - `tests/integration/features/worktree/test_cli.py`: AC-01 refusal (code, exit, `[FIX]`, unchanged state, hidden
    help), AC-02 output line, AC-03 no network call (monkeypatched `run_git` recorder).
  - `tests/integration/features/worktree/test_branches.py`, `test_branch_refs.py`, `test_merging.py`,
    `tests/e2e/features/worktree/test_lifecycle.py`: cases that called `finish(merge=True)` either move to the
    integration service when they test a kept safeguard (PR policy, detached/dirty base, branch-only marked branch,
    `ff-only`/`no-ff` result) or are removed when they test a dropped behavior (push, base behind, guards).
  - `tests/integration/features/integration/test_service.py`: AC-04 branch-only marked branch and `plan-<slug>`
    landing without fetch/push; the existing `finish(merge=True)` setup at line 243 uses the service instead.
  - `tests/integration/features/workflow/test_envelope_hold.py`: remove the `finish_guard` and CLI `--merge` tests;
    AC-05 hold assertions use `envelope check --format json` (existing tests cover `next`).
  - `tests/integration/package/test_config_tables.py`: template comment.
  - `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`: the worker-records assertion follows
    the bundle text.
- Commands: `just lint devkit`, `just check devkit`, `just test-affected --base main`,
  `just test-affected --base main --tier e2e`, `uv run devkit rules check`, `uv run devkit sync --check`,
  `uv run devkit workflow envelope check --unit specs/2026-11/20261111-retire-finish-merge`, and the AC-06 `rg`.
