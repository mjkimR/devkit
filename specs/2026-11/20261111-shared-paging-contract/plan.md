---
id: PLAN-shared-paging-contract
spec: SPEC-shared-paging-contract
---

# Technical Plan: `SPEC-shared-paging-contract` One paging contract for listing commands

## 1. Constitution & Invariant Review

None. `ARCH-08-1-agent-output` §3 already requires one-line `[KIND: ...]` sentinels rendered through
`field_value`; the change adds a paging paragraph and a checklist item without changing a MUST. `exec list` keeps
its limit bounds and error code from `CAP-HARN-isolated-execution`, and its JSON payload. `isolated_execution/cli.py`
already imports `devkit_dist.adapters.cli`, so reusing `echo_page` adds no feature edge or import edge
(`.devkit/architecture.toml` unchanged). `echo_page` itself is not changed.

## 2. Architecture Overview & Impact

- `packages/devkit/src/devkit_agt/features/isolated_execution/cli.py` (`list_runs`): text mode prints the
  `[EXECUTION_RUN: ...]` lines, then calls
  `echo_page("uv run devkit exec", page["total"], page["offset"], page["limit"], len(page["runs"]), ["list", "--limit", str(page["limit"])])`.
  The `[EXECUTION_LIST: ...]` line is removed. The `--offset` help no longer names only `next_offset`. JSON mode is
  unchanged. `ListExecutions` is unchanged.
- `ARCH-08-1-agent-output` §3 gains a **Paging** paragraph: after the items a listing command that pages prints
  `[PAGE: total= offset= limit= count= next=]`; `next` is the following page's offset or `-` on the last page;
  `[NEXT_CMD: <command> ... --offset <next>]` repeats the command's own arguments and follows only when more items
  follow; both come from `devkit_dist.adapters.cli.echo_page`, except that a command adding fields after `next`
  (`docs list`'s `hidden`) MAY print `[PAGE: ...]` with `fields_line` under the same rules; each command's capability states its limit bounds, default and whether `--limit 0` means all.
  Enforced by `packages/devkit-dist/tests/unit/adapters/test_sentinels.py` for the line format; use of `echo_page`
  is review only. §10 gains the checklist item.
- `CAP-HARN-command-mount` §4.5 keeps its group facts (`--limit/-n` default 20, `0` for all, `hidden`,
  `[HISTORY_CMD]`, `ARGUMENT_INVALID`, the creation `[NEXT_CMD]`) and refers to `ARCH-08-1-agent-output` §3 for the
  grammar instead of restating it. Only §4.5 changes (a concurrent spec edits §4.2).
- `CAP-HARN-isolated-execution` §4: the sentinel list drops `EXECUTION_LIST`, names `PAGE` and `NEXT_CMD` per
  `ARCH-08-1-agent-output` §3 (an empty list is a `[PAGE: ...]` line with `count=0`), and the list sentence keeps
  limit 1-100, default 20, nonnegative offset, no `--limit 0`, JSON `next_offset`.
- `docs/development/reference/exec.md`: sentinel sentence updated the same way.

## 3. Error Handling & Edge Cases

- Invalid bounds raise `EXECUTION_LIST_ARGUMENT_INVALID` in `ListExecutions` before any output, so no `[PAGE]`
  line is printed (AC-05); unchanged code path.
- Empty list: `echo_page` with `total=0` prints `next=-` and no `[NEXT_CMD]` (AC-04).
- An offset beyond `total` prints `count=0 next=-`, as before.

## 4. Verification & Test Plan

- `packages/devkit/tests/unit/features/isolated_execution/test_output.py`: replace the empty-list assertion (AC-04);
  add CLI tests with a monkeypatched `ListExecutions` over 25 runs for the first page, last page and a custom limit
  (AC-01, AC-02, AC-03), JSON keys (AC-06), and invalid bounds through the CLI (AC-05). The existing use-case
  paging test stays.
- AC-07: `rg -n EXECUTION_LIST docs/architecture docs/capabilities docs/development packages/devkit/src` and
  `uv run devkit rules check --ci --base main`.
- `just lint`, `just check`, `just test-affected` (with its `mode=full` fallback), `uv run devkit sync --check`.
