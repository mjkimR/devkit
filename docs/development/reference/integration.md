# Integration Reference

Canonical behavior: `CAP-INT-mcp-services`.

| Interface | Purpose |
| --- | --- |
| `devkit integration prepare BRANCH --task-kind unit|session --task-id ID [--unit DIR] [--route local|pull-request] [--claims JSON] [-w DIR] [--format json]` | Inspect readiness and exact execution scope without integration mutations |
| `devkit integration integrate BRANCH --task-kind unit|session --task-id ID [--unit DIR] [--route local|pull-request] [--claims JSON] [--expected-digest DIGEST] [-w DIR] [--format json]` | Rebuild scope and execute after Host-carried approval under `ask`, or retained-base policy authority under `auto` |
| `devkit worktree finish BRANCH --merge --local-only` | Public merge/cleanup operation excluding fetch and push (a merge commit, or a fast-forward under `[worktree] merge = "ff-only"`; the branch must contain the base HEAD); caller supplies existing authority |

The CLI accepts `branch`, `task_kind`, `task_id`, optional `unit`, optional `claims`, and `route=local|pull-request` (default local). On the PR route only, `task_id` must contain 1–256 characters matching `[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}`. No command accepts an approval boolean, arbitrary command, cleanup path or merge strategy:
the merge method is the project policy (`[worktree] merge`, `ff-only` in either the base's or the source's policy wins).

Under `ask`, the Host presents the exact report, target and cleanup effects, receives the user's conversational decision, then invokes `integrate --expected-digest <digest>` with the prepared `request.digest`. Under `ask`, a missing digest refuses and a changed scope returns `INTEGRATION_REQUEST_STALE` before integration effects. Under `auto`, the digest is optional and checked when supplied. It is a concurrency precondition, not approval. The CLI revalidates the complete operation but does not authenticate that decision. Shared base `dev-integration="auto"` authorizes only local integration and reports `authority: policy`. Auto PR execution refuses, prospective revocation blocks before merge and remaining effects require unchanged policy. Host permissions remain independent. Prepare and source-only policy changes grant no authority.

Local `prepare` of a source that does not contain the target (a moved target) builds the prospective merge in the
object store (Git 2.38 or later for `git merge-tree --write-tree`) and runs readiness, the finish guards on the merge
base, the receipt check and the prospective policy on it before presenting the scope; a conflict no generated
artifact settles refuses with
`WORKTREE_MERGE_CONFLICT` and nothing changed (`ADR-moved-target-merge`). The source need not contain the target first.
A merge whose conflicts are all in files an enabled generated artifact owns (registry committed at the build target)
keeps each artifact's `seed` side instead, unless an artifact to regenerate reads another conflict; prepare and
integrate then disclose `generated` (`seeded`, `regenerate`), `seeded=<ids>` and `INTEGRATION_GENERATED_SEEDED`
(`ADR-generated-conflicts-in-prepared-merge`). Composed acceptance and the pull-request route settle no conflict.
The CLI execution absorbs target commits that land after its prepared-scope comparison in one build and waits up to
20 seconds (`LOCK_WAIT`) for another devkit integration. The result
reports the prepared target, build target and result commit under `build`. After an unknown outcome, inspect
`devkit worktree status`, Git or PR state. If local merge completed before cleanup failed, rerun
`devkit worktree finish BRANCH --local-only`; its already-merged guards perform only remaining cleanup.

CLI text emits concise sentinels (`prepare` names `target_sha=<confirmation target>` and adds `[INTEGRATION_SCOPE: ... seeded=<ids>|- disclosure="..."]` and its notices; `integrate` names `target_sha=`, `build_target=`, `result=`, `seeded=` and `disclosure=` and ends with `effects=<step>:<state>,...`) and JSON emits one result object (`prepare`: the approval scope, with `target.sha` and `readiness.disclosure`; `integrate`: also `build`; both add `generated` when the build seeded generated files). Internal validation identities, policy hashes,
registrations, evidence and cleanup revisions remain bound to the in-memory invocation. Partial results retain steps,
errors, failing operation, observed state and the latest build.

Public API: `devkit_agt.features.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`, `Readiness`,
`ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`, `CleanupResult`,
`ScopedCleanup` and typed errors. `IntegrationContext.result_sha` is `None` at `prepare` (an unlanded prospective
merge commit when the target moved) and the result commit at a build (whose `finish.target_sha` is the build target); `Readiness` binds `result_sha` and declares `target_bound` codes
and a one-line `disclosure` of at most 200 characters. `devkit_agt.features.worktree` exports `FinishPlan` (with `merge_method`
and `already_merged`), `plan_finish` (`advance=`, set only by local integration), `validate_finish` (`result=`,
`target=`), `build_result` (`advance=`, `prospective=`, `settle=` a `ConflictSettler`), `fast_forward`,
`merge_method`, `integration_lock`, `run_finish_guards`, `run_post_finish`; `finish` takes `network="allow"|"forbid"`,
`merge_method` and an optional `before_step` callback. Providers and scoped cleanup use only public exports.

| Code | Required next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | `INPUT_ERROR`: configure/install the provider and use the supported approval/PR policy (`[TARGET] .devkit/config.toml`), or correct the flag `[TARGET]` names (`--task-id`, `--unit`, `--claims`) |
| `INTEGRATION_NOT_READY` | `INPUT_ERROR`: for missing or invalid session claims, correct explicit `--claims` and retry the same prepare or integrate command; claims are not reused between commands. Resolve any other reported readiness conditions before retrying. Ordinary source-readiness failures still target the source worktree and require final committed work and preparation again. |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract |
| `INTEGRATION_REQUEST_STALE` | A digest that differs from the current scope: `INTERACTION`, `[FIX]` the exact `prepare` command that re-presents the scope, and a `[DETAIL]` with the exact `integrate` command and the current digest, for after the user approves it. Otherwise inspect completed progress and approve a new request for the remaining scope |
| `INTEGRATION_TARGET_MOVED` | Nothing merged: prepare again on the current target (no base merge on the local route) and obtain fresh Host approval before integrating again |
| `INTEGRATION_RECEIPT_CONFLICT` | Merge the target into the branch to resolve the receipt conflict, re-sync, re-verify what the merge changed and prepare again |
| `INTEGRATION_RECEIPT_READER_CHANGED` | The source changes the receipt reader and its receipt only that reader accepts; restarting the service does not help. With separately granted authority, run the CLI route (`devkit worktree finish <branch> --merge --local-only`) from the source's code |
| `INTEGRATION_RULE_RUNTIME_MISMATCH` | A synchronized rule of the source (or result) imports a module or name this runtime lacks; the source needs no change. With separately granted authority, run `devkit integration integrate <branch>` from the base checkout with a runtime built from the source's code outside the worktree |
| `INTEGRATION_AUTHORITY_REQUIRED` | Read the refusal: auto permits local execution only; resolve prospective policy revocation before retrying, never switch authority to bypass it. Under ask without a digest: `INTERACTION`, `[FIX]` the exact `prepare` command that presents the scope, and a `[DETAIL]` with the exact `integrate` command and its digest, for after the user approves it |
| `INTEGRATION_CLEANUP_UNSCOPED` | Adapt the named legacy post-finish extension before approval |
| `INTEGRATION_GENERATED_SEEDED` | `WARNING`: the merge kept the listed generated files from one side. After landing, run the `[FIX]` `devkit generated regen <ids>` on the target branch and commit; a `local-orchestrated` run does it before its batch test run |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git/worktree state; after a verified local landing, run `devkit worktree finish <branch> --local-only` for the remaining guarded cleanup |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | Move the server runtime to the retained base/installed environment |

Existing worktree/core advisories retain their codes; a build refusal passes its `WORKTREE_*` code through
(`WORKTREE_MERGE_CONFLICT`, `WORKTREE_GIT_UNSUPPORTED`, `WORKTREE_COMMIT_FAILED`, `WORKTREE_MERGE_NOT_FF`), and
`LOCK_HELD` requires inspection and a fresh invocation after the other devkit integration completes. Successful
operations return notices; execution failures carry structured partial progress. CLI results follow normal devkit
output and exit conventions.

The native PR route binds the resolved GitHub repository and source SHA, pushes/creates the PR after approval,
merges synchronously with a head pin, verifies landing evidence and performs disclosed cleanup. Leased remote deletion
precedes local worktree and branch deletion. A remote deletion failure preserves those local identities; inspect the
merged PR and remote ref, prepare the remaining scope and retry with its fresh digest. The confirmed merge is not
repeated. `ff-only` refuses the PR route.
Pending checks return `INTEGRATION_CHECKS_PENDING` as an incomplete result; inspect the pull request and checks before
invoking another operation. `INTEGRATION_TARGET_MOVED` requires target integration into source, verification and new approval.
`INTEGRATION_LANDED_UNCHECKED` is a warning: run the provider's landed-target check after cleanup and do not report
checked integration. `INTEGRATION_SOURCE_NOT_CONTAINED` prevents deletion. Unknown mutations require remote
inspection before recovery. Network subprocesses have 5-second bounds and each phase a 20-second budget; readiness
and local checks can outlast Host timeouts. Inspect GitHub state before retrying.

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
| `INTEGRATION_STEP_UNKNOWN` | Inspect GitHub state; never repeat an unconfirmed mutation |
| `INTEGRATION_LOCAL_TARGET_BLOCKED` | Restore a clean fast-forwardable target checkout and inspect the PR state before another invocation |
| `INTEGRATION_REMOTE_DELETE_BLOCKED` | Preserve the remote branch until changed-head/dependent-PR conditions resolve |

For shared or personal approval/response defaults, set `[presentation] language = "ko"` (`auto`, `en`, `ko`)
in shared config or ignored `.devkit/config.local.toml`. `devkit config show --effective` reports the requested and
resolved language, source and fallback; another value falls back to `en`, which `devkit sync`, `devkit status`
and `devkit config show` report as a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning. Run sync for response-style
assets. The Host presents conversational approval in its own language.
Explicit response-style bundle variables win. See `CAP-DIST-sync-and-transactions` and `CAP-INT-mcp-services`;
this does not localize host-owned controls or establish visible native Korean form support.


Proposal acceptance uses `devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff --by user`. Partial effects are recovered from observable state and require fresh Host authority. See `CAP-DLV-proposal-planning` and `CAP-INT-mcp-services`.
