# Isolated execution reference

`CAP-HARN-isolated-execution` owns the contract; `UC-execute-an-isolated-command` owns the caller flow.

```sh
uv run devkit exec start --ref <full-local-SHA> -- just test-affected --base <baseline> --tier e2e
uv run devkit exec wait <run-id> --clean --format json
uv run devkit exec list --format json
uv run devkit exec logs <run-id> --tail 100
```

Devkit's `just test-affected` defaults to `--tier unit-integration`, excluding E2E even when E2E tests changed. `--tier e2e` selects only E2E; `--tier all` or compatibility `--e2e` selects both. Explicit data mappings and broad directories obey the selected tier. Unknown-input and shared-foundation full fallback stays within that tier, preserving embedded rule coverage in unit/integration or all selections. An empty tier runs no pytest command; required frontend checks remain separately reported.

Background the waiter through a tool that delivers completion if independent work should proceed. Without that delivery, inspect later. Wait timeout/interruption does not cancel; cancel retains the checkout; clean preserves logs/results outside it. Retain native artifacts before requesting clean. Setup uses worktree configuration or `--setup`; no implicit `.env` copy, profile map or local/cloud selector exists.

Text output uses `[EXECUTION_RESULT: ...]`, `[EXECUTION_RUN: ...]`, `[EXECUTION_CLEANUP: outcome=... code=... detail=...]` (whenever cleanup evidence exists), `[EXECUTION_DETAIL: ...]` and `[EXECUTION_LOG_LINE: ...]` sentinels. `list` ends its runs with the shared paging lines (`ARCH-08-1-agent-output` section 3), for example `[PAGE: total=25 offset=0 limit=20 count=20 next=20]` and `[NEXT_CMD: uv run devkit exec list --limit 20 --offset 20]`; JSON keeps `runs`, `total`, `offset`, `limit` and `next_offset`.

| Code | Caller action |
| --- | --- |
| `EXECUTION_ARGUMENT_INVALID` | Supply a full local commit SHA, native argv and nonempty setup. |
| `EXECUTION_LIST_ARGUMENT_INVALID` | Use limit 1–100 and a nonnegative offset. |
| `EXECUTION_ID_INVALID` | Use a retained 32-character run ID from list/start. |
| `EXECUTION_REF_UNKNOWN` | Make the requested commit available locally. |
| `EXECUTION_RECORD_UNREADABLE` | Inspect retained evidence; never infer a passing result. |
| `EXECUTION_REPOSITORY_UNREADABLE` | Use an accessible local Git repository. |
| `EXECUTION_REPOSITORY_UNSUPPORTED` | Use a retained non-bare checkout. |
| `EXECUTION_PLATFORM_UNSUPPORTED` | Use POSIX macOS/Linux. |
| `EXECUTION_TAIL_INVALID` | Request 0–1000 log lines. |
| `EXECUTION_TIMEOUT_INVALID` | Supply a finite nonnegative timeout. |
| `EXECUTION_WAIT_TIMEOUT` | Retain execution; collect later or explicitly cancel. |
| `EXECUTION_CLEAN_IN_PROGRESS` | Inspect the retained cleanup operation; wait for its remover before retrying. |
| `EXECUTION_CLEAN_UNFINISHED` | Inspect the original result and checkout; an explicit clean retry revalidates ownership. |
| `EXECUTION_CLEAN_REFUSED` | Inspect active/unknown ownership, checkout identity and dirty files; retain evidence and repair deliberately. |
| `EXECUTION_CLEANED` | Checkout removal is complete or already complete; evidence remains. |

Execution outcomes remain separate from native exit codes and observer/cleanup outcomes. Status pending/pass exits 0, known negative exits 1, unknown/unreadable exits 2. Wait timeout or cleanup refusal exits 2 even when the original command passed or failed. The executor owns evidence and resource effects; the Host owns delivery completion.

Cleanup requires explicit persisted positive managed-group quiescence; older terminal records without that proof remain readable but refuse removal. Cleanup progress is persisted before removal, and interruption leaves incomplete evidence. Retry never force-removes dirty or unrelated content.
