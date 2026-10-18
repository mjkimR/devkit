# Integration Reference

Canonical behavior: `CAP-INT-mcp-services`.

| Interface | Purpose |
| --- | --- |
| `devkit integration prepare BRANCH --task-kind unit|session --task-id ID [--unit DIR] [--claims JSON] [-w DIR] [--format json]` | Inspect readiness and exact scope, without approval or integration mutations |
| MCP `integration_prepare` | Optional preflight in the retained service process; not required before integrate |
| MCP `integration_integrate` | Normal entry point: prepare, obtain one native confirmation and execute; no prior chat approval |
| MCP `integration_status` | Inspect concise progress and observed Git state; detail=true returns full retained diagnostics |
| MCP `integration_resume` | Recover only the remaining scope of an already approved request in this process |
| `devkit worktree finish BRANCH --merge --local-only` | Public FF/cleanup operation excluding fetch and push; caller supplies existing authority |

Task tools accept `branch`, `task_kind`, `task_id`, optional `unit`, optional `claims`. Status accepts `request_id` and optional boolean `detail` (default false); resume accepts only `request_id`. No tool accepts an approval boolean, arbitrary command, cleanup path or merge strategy.

All four tools return concise scope/progress by default. Internal validation identities, policy hashes, registrations,
evidence and cleanup revisions remain bound to the request digest and are available through detailed status.
Partial results retain steps, errors, failing operation and observed state. Text and structured MCP outputs agree.

Public API: `devkit.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`, `Readiness`,
`ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`, `CleanupResult`,
`ScopedCleanup` and typed errors. `devkit.worktree` exports `FinishPlan`, `plan_finish`, `validate_finish`,
`run_finish_guards`, `run_post_finish`; `finish` takes `network="allow"|"forbid"` and an optional `before_step`
callback. Providers and scoped cleanup use only public exports.

| Code | Required next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Configure/install the provider and use the supported approval/PR policy |
| `INTEGRATION_NOT_READY` | Resolve completion conditions and prepare final committed work |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract |
| `INTEGRATION_REQUEST_STALE` | Inspect completed progress and approve a new request for the remaining scope |
| `INTEGRATION_AUTHORITY_REQUIRED` | Obtain native confirmation or use an approved request retained in this process |
| `INTEGRATION_CLEANUP_UNSCOPED` | Adapt the named legacy post-finish extension before approval |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Resolve the scoped cleanup condition and resume the same approved request |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | Move the server runtime to the retained base/installed environment |

Existing worktree/core advisories retain their codes. Successful operations return notices; execution failures
carry structured partial progress. The CLI preparation command follows normal devkit output and exit conventions;
the MCP adapter returns one structured tool result with its error/advisory data.
