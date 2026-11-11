# Detection matrix: `devkit status` and `devkit sync --check` (Q1)

Measured at `ba3bcce4` (worktree `plan-single-sync-readiness-gate`), on 2026-11-11.

## Method

The probe `tmp/probe/matrix.py` (ignored, kept with the worktree) builds one fixture project: a fresh Git
repository whose `.devkit/config.toml` selects `agents = ["claude-code"]` and `advisory = "python"`, plus a root
`AGENTS.md`, synchronized once with `devkit sync`. Each scenario copies that project, applies one change and
runs `devkit status` (JSON) and `devkit sync --check --format json`. The table records the exit code and the
codes under `errors` (for an exit-`2` failure, the `error.code` of `{"error": ...}`). Run it again with
`python3 -I tmp/probe/matrix.py <worktree> <worktree>/tmp/probe`.

Both commands also exit `0` on this worktree itself (356 managed files `ok`, no planned action).

## Measured scenarios

| Scenario | `status` | `sync --check` | Who detects |
| --- | --- | --- | --- |
| Clean fixture | 0 | 0 | none (correct) |
| Managed file deleted | 1 `NOT_SYNCHRONIZED` | 1 `NOT_SYNCHRONIZED` | both |
| Managed file edited | 1 `SYNC_CONFLICT` | 2 `SYNC_CONFLICT` | both |
| Managed file execute bit changed | 1 `SYNC_CONFLICT` | 2 `SYNC_CONFLICT` | both |
| Managed file replaced by a symlink | 1 `WORKSPACE_UNSAFE` | 2 `WORKSPACE_UNSAFE` | both |
| Pending sync journal | 1 `TRANSACTION_PENDING` | 2 `TRANSACTION_PENDING` | both |
| Guidance block edited | 1 `SYNC_CONFLICT` | 2 `SYNC_CONFLICT` | both |
| Root `AGENTS.md` is a symlink | 1 `WORKSPACE_UNSAFE` | 2 `WORKSPACE_UNSAFE` | both |
| Uninstalled bundle selected in `config.toml` | 1 `SELECTION_INVALID` | 2 `SELECTION_INVALID` | both |
| Receipt record moved, copy as last sync left it (stale) | 1 `NOT_SYNCHRONIZED` | 1 `NOT_SYNCHRONIZED` | both |
| Agent added to `config.toml`, no sync | 1 `NOT_SYNCHRONIZED` (subagent projections) | 1 `NOT_SYNCHRONIZED` (66 actions) | both |
| Local `environment = "cloud"`, no sync | 1 `NOT_SYNCHRONIZED` (render environment) | 1 `NOT_SYNCHRONIZED` (17 actions) | both |
| Guidance block removed from `AGENTS.md` | **0** (state `missing`) | 1 `NOT_SYNCHRONIZED` | `sync --check` only |
| Preset added to `config.toml`, no sync | **0** | 1 `NOT_SYNCHRONIZED` (6 actions) | `sync --check` only |
| `guidance_block = false`, no sync | **0** | 1 `NOT_SYNCHRONIZED` (2 actions) | `sync --check` only |
| Receipt deleted | **0** (empty installation) | 1 `NOT_SYNCHRONIZED` | `sync --check` only |
| Stray file under `.devkit/managed/` | 0 | 0, `MANAGED_FILE_STRAY` warning | neither fails (by contract) |

## Read from code, not measured

| Condition | `status` | `sync --check` | Evidence |
| --- | --- | --- | --- |
| Installed package content changed (upgrade or lock change) without a sync | 0: compares the disk with the receipt only (except subagent projections and render environment) | 1: plans against the installed bundles | `usecases/status.py` `get_project_status`; `usecases/sync.py` `commit_locked` |
| Override drift under `override_drift = "block"` | 1 `OVERRIDE_DRIFT` | 2: the planner refuses (`_refuse_override_drift`) | `status.py`, `sync.py` |
| Selected bundle whose package fails to load | 1 `BUNDLE_PACKAGE_INVALID` | 2: `_resolve_selection` stops the sync (`unusable_notices`) | `status.py` `_unusable_packages`, `sync.py` |
| Native host hook registration missing, edited or duplicated | 1 `HOST_HOOK_MISSING` (config file absent) / `HOST_HOOK_CONFLICT` (`InspectHost`) | missing file: 1 (`plan_host_hooks` plans a create); edited or duplicated recorded group: 2 (`plan_config` raises `HookConflictError`) | `host/usecases/status.py:59-68`, `services/installation/host_hooks.py:26-35`, `host/services/configuration.py:65-82` |
| Hook definition and receipt registration differ | 1 `HOST_HOOK_DISPATCH_FAILED` | 1 when the receipt or host config would be rewritten from the inventory; 2 when `plan_config` refuses | `host/usecases/status.py`, `host/services/configuration.py` |
| Local MCP registration pending (devkit-mcp with a retained runtime, `[mcp] register` not false, after `sync --locked`) | 0: not reported (`ADR-mcp-runtime-and-shared-artifacts`) | 1 `NOT_SYNCHRONIZED`: planned registration writes are added to `actions`, dry run included, until `sync --registrations-only` or a plain sync | `sync.py:1018-1035,1051`, `cli/output.py:75-81`; not measured: the fixture had no retained runtime (`MCP_RUNTIME_UNAVAILABLE`) |
| `devkit.status_checks` providers (gate hooks) | `WARNING`/`NOTICE` only, exit unchanged | not run | reference `devkit status` |

## Findings

1. Every measured problem that fails `status` also fails `sync --check`. No measured scenario fails `status` alone,
   and the challenger found no condition in code where it would (historical Git `eb2d5dba4bfd08a06e492a0d427ad4a7afa27309:docs/proposals/PROP-single-sync-readiness-gate/envelopes/challenger-01.yaml`).
2. `sync --check` fails four measured scenarios that `status` passes, and by code also a package content change:
   `status` compares the disk with the receipt (what the last sync wrote), `sync --check` compares it with the
   desired state (what a sync would write now). Only the second answers "is this checkout synchronized".
3. One `sync --check`-only condition is a choice, not a defect: pending optional MCP registration in a clone that
   uses MCP (table above). Counting it makes registration part of readiness.
4. Where both fail, `sync --check` exits `2` and returns `{"error": ...}` (the planner raises the first refusal),
   while `status` exits `1` and lists every problem at once. Both are nonzero, so a criterion of "exits `0`" is
   unaffected; the list of all problems is the diagnostic value `status` keeps.
5. The overlapping detection is not two implementations of one check: `status` already reuses the planner's
   helpers (`block_conflict`, `edited_files_error`, `guidance_block_error`, `planned_guidance_block`,
   `planned_subagent_changes`, `missing_selection_error`). Its own logic is the file-state classification
   (`missing`, `stale`, `modified`, `mode-mismatch`, `unsafe`) and the report fields.

## Answer to Q2

`sync --check` can be the single readiness gate: it detects a strict superset of the measured problems. `status`
stays a diagnostic report of the installed state against the receipt. Requiring both adds no detection; requiring
only `status` (as the in-repo bundle and project-bundle criteria do today) misses desired-state changes.
