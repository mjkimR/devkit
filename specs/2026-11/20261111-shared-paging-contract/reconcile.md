---
reconcile_id: REC-shared-paging-contract
status: resolved
targets:
  - file: docs/architecture/ARCH-08-1-agent-output.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-isolated-execution.md
    resolution: modified
  - file: docs/development/reference/exec.md
    resolution: modified
---

# Reconcile: `SPEC-shared-paging-contract`

- `ARCH-08-1-agent-output` §3 gains the **Paging** paragraph (the `[PAGE: ...]` and `[NEXT_CMD: ...]` grammar
  printed by `echo_page`, or with `fields_line` by a command that adds fields after `next` such as `docs list`;
  extra fields and lines documented in each capability; per-command limit bounds in each
  capability, no paging lines for an unpaged bounded listing) and §10 a checklist item (AC-07).
- `CAP-HARN-command-mount` §4.5 keeps the `docs`/`spec` group facts (`--limit/-n` default 20, `0` for all,
  `hidden`, `[HISTORY_CMD]`, `ARGUMENT_INVALID`, the creation `[NEXT_CMD]`) and points to `ARCH-08-1-agent-output`
  §3 for the grammar; no other section changed (§4.2 belongs to a concurrent spec).
- `CAP-HARN-isolated-execution` §4 drops `EXECUTION_LIST`, names the shared paging lines through
  `ARCH-08-1-agent-output` §3 (an empty list is a `[PAGE: ...]` line with `count=0`) and keeps exec's own limits
  (1-100, default 20, nonnegative offset, no `--limit 0`, `EXECUTION_LIST_ARGUMENT_INVALID`, JSON `next_offset`)
  (AC-01 to AC-06).
- `docs/development/reference/exec.md` (no ID) updates its sentinel sentence with a paging example and the
  unchanged JSON keys.

## No impact

- `UC-execute-an-isolated-command` describes the caller flow and no list output format; unchanged.
- `CAP-DLV-maintenance-history` and `docs/development/reference/maintenance-history.md`: `maintenance history list`
  stays unpaged by the agreed decision; unchanged.
- `docs/development/reference/core.md` already documents `echo_page`; `echo_page` is unchanged.
- `packages/devkit/README.md` and the `spec-orchestrate` isolated-execution reference name `exec list` without its
  output lines; unchanged.

## Entrypoints

`devkit spec entrypoints derive` proposed `isolated_execution/cli.py` and `test_output.py` for
`CAP-HARN-command-mount` and `test_output.py` for `CAP-HARN-isolated-execution`; none applied. The command mount
does not own the `exec` group, a test is no doorway, and `CAP-HARN-isolated-execution` already declares `cli.py`.

## Deferred work and source feedback

None. The Non-Goals are decisions, not deferred work. The source is finding C2-8 of the review material
`docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md`; no `FB-...` item was carried.
