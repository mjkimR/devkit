# Integration Reference

Canonical behavior: `CAP-INT-mcp-services`.

| Interface | Purpose |
| --- | --- |
| `devkit integration prepare BRANCH --task-kind unit|session --task-id ID [--unit DIR] [--claims JSON] [-w DIR] [--format json]` | Inspect readiness and exact scope, without approval or integration mutations |
| MCP `integration_prepare` | Optional preflight in the retained service process; not required before integrate |
| MCP `integration_integrate` | Normal entry point: prepare, obtain one native confirmation and execute; no prior chat approval |
| MCP `integration_status` | Inspect concise progress and observed Git state; detail=true returns full retained diagnostics |
| MCP `integration_resume` | Recover only the remaining scope of an already approved request in this process |
| `devkit worktree finish BRANCH --merge --local-only` | Public merge/cleanup operation excluding fetch and push (a merge commit, or a fast-forward under `[worktree] merge = "ff-only"`; the branch must contain the base HEAD); caller supplies existing authority |

Task tools accept `branch`, `task_kind`, `task_id`, optional `unit`, optional `claims`, and `route="local"|"pull-request"` (default local). On the PR route only, `task_id` must contain 1–256 characters matching `[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}`. Status accepts `request_id` and optional boolean `detail` (default false); resume accepts only `request_id`. No tool accepts an approval boolean, arbitrary command, cleanup path or merge strategy:
the merge method is the project policy (`[worktree] merge`, `ff-only` in either the base's or the source's policy wins).

The approving `integration_integrate` call absorbs target commits that land during the confirmation in one build
(Git 2.38 or later for `git merge-tree --write-tree`), and waits up to 20 seconds (`LOCK_WAIT`) for another devkit
integration; `integration_resume` continues only onto the last build target (or the confirmation target when no
build ran) and never waits for the lock. The result reports the confirmation target, build target and result commit
under `build`.

All four tools return concise scope/progress by default. Internal validation identities, policy hashes, registrations,
evidence and cleanup revisions remain bound to the request digest and are available through detailed status.
Partial results retain steps, errors, failing operation, observed state and the latest build. Text and structured MCP
outputs agree.

Public API: `devkit.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`, `Readiness`,
`ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`, `CleanupResult`,
`ScopedCleanup` and typed errors. `IntegrationContext.result_sha` is `None` at `prepare` and the result commit at a
build (whose `finish.target_sha` is the build target); `Readiness` binds `result_sha` and declares `target_bound` codes
and a one-line `disclosure` of at most 200 characters. `devkit.worktree` exports `FinishPlan` (with `merge_method`
and `already_merged`), `plan_finish`, `validate_finish` (`result=`, `target=`), `build_result`, `fast_forward`,
`merge_method`, `integration_lock`, `run_finish_guards`, `run_post_finish`; `finish` takes `network="allow"|"forbid"`,
`merge_method` and an optional `before_step` callback. Providers and scoped cleanup use only public exports.

| Code | Required next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Configure/install the provider and use the supported approval/PR policy |
| `INTEGRATION_NOT_READY` | Resolve completion conditions and prepare final committed work |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract |
| `INTEGRATION_REQUEST_STALE` | Inspect completed progress and approve a new request for the remaining scope |
| `INTEGRATION_TARGET_MOVED` | Nothing changed: resume while the target equals the last build target, else integrate again |
| `INTEGRATION_RECEIPT_CONFLICT` | Merge the target into the branch, re-sync, re-verify and integrate again |
| `INTEGRATION_AUTHORITY_REQUIRED` | Obtain native confirmation or use an approved request retained in this process |
| `INTEGRATION_CLEANUP_UNSCOPED` | Adapt the named legacy post-finish extension before approval |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Resolve the scoped cleanup condition and resume the same approved request |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | Move the server runtime to the retained base/installed environment |

Existing worktree/core advisories retain their codes; a build refusal passes its `WORKTREE_*` code through
(`WORKTREE_MERGE_CONFLICT`, `WORKTREE_GIT_UNSUPPORTED`, `WORKTREE_COMMIT_FAILED`, `WORKTREE_MERGE_NOT_FF`), and
`LOCK_HELD` from the approving call names `integration_resume` or a new `integration_integrate`. Successful operations return notices; execution failures
carry structured partial progress. The CLI preparation command follows normal devkit output and exit conventions;
the MCP adapter returns one structured tool result with its error/advisory data.

The native PR route binds the resolved GitHub repository and source SHA, pushes/creates the PR after approval,
merges synchronously with a head pin, verifies landing evidence and performs disclosed cleanup. `ff-only` refuses it.
Pending checks return `INTEGRATION_CHECKS_PENDING` as a successful incomplete result; resume on the same checked
target. `INTEGRATION_TARGET_MOVED` requires target integration into source, verification and new approval.
`INTEGRATION_LANDED_UNCHECKED` is a warning: run the provider's landed-target check after cleanup and do not report
checked integration. `INTEGRATION_SOURCE_NOT_CONTAINED` prevents deletion. Unknown mutations require remote
inspection before recovery. Network subprocesses have 5-second bounds and each phase a 20-second budget; readiness
and local checks can outlast host timeouts, leaving the server thread running. Inspect status before retrying.

| PR route code | Required next action |
| --- | --- |
| `INTEGRATION_REMOTE_UNSUPPORTED` | Inspect remote identity or queue configuration and use a supported same-repository route |
| `INTEGRATION_GH_UNAVAILABLE` | Install/authenticate gh for the bound host and inspect permissions |
| `INTEGRATION_TARGET_UPSTREAM` | Configure a same-named target upstream and reconcile unpublished local commits |
| `INTEGRATION_MERGE_COMMIT_FORBIDDEN` | Use another authorized route; never substitute squash/rebase |
| `INTEGRATION_PR_CONFLICT` | Inspect conflicting PR identity, draft, base or head and prepare again |
| `INTEGRATION_REMOTE_BRANCH_DIVERGED` | Reconcile the remote source without force and prepare again |
| `INTEGRATION_MERGE_REFUSED` | Resolve required checks, review, conflicts or platform policy and prepare again |
| `INTEGRATION_MERGE_UNCONFIRMED` | Preserve branches and report unconfirmed merge evidence |
| `INTEGRATION_STEP_UNKNOWN` | Inspect remote state through status/resume; never repeat an unconfirmed mutation |
| `INTEGRATION_LOCAL_TARGET_BLOCKED` | Restore a clean fast-forwardable target checkout and resume |
| `INTEGRATION_REMOTE_DELETE_BLOCKED` | Preserve the remote branch until changed-head/dependent-PR conditions resolve |

For shared or personal approval/response defaults, set `[presentation] language = "ko"` (`auto`, `en`, `ko`)
in shared config or ignored `.devkit/config.local.toml`. `devkit config show --effective` reports the requested and
resolved language, source and fallback. Run sync for response-style assets; approval forms read per request.
Explicit response-style bundle variables win. See `CAP-DIST-sync-and-transactions` and `CAP-INT-mcp-services`;
this does not localize host-owned controls or establish visible native Korean form support.
