# Integration Reference

Canonical behavior: `CAP-INT-mcp-services`; final verification: `CAP-DLV-delivery-workflows`.

| Interface | Purpose |
| --- | --- |
| `devkit integration prepare BRANCH [--route local|pull-request] [-w DIR] [--format json]` | Show exact Git and cleanup scope without landing |
| `devkit integration integrate BRANCH [--route local|pull-request] [--expected-digest DIGEST] [-w DIR] [--format json]` | Execute under Host-carried ask approval or retained-base auto policy |
| `devkit worktree finish BRANCH` | Remaining cleanup after a landing whose cleanup stopped; it lands nothing (`--merge` refuses with `WORKTREE_MERGE_RETIRED`) |

The commands take no task-kind, task-id, unit or claims. Integration needs no readiness provider; `[integration]`
accepts no keys, and the retired `provider` key is refused with a fix to delete it. The explicit branch supplies
deterministic PR body and merge text. No approval token, arbitrary cleanup path or merge strategy is accepted.

Under ask, present exact source, target and cleanup effects, obtain the user's conversational decision, then use
`request.digest`. Missing or changed digests refuse before effects. Under auto the digest is optional and checked
when supplied; auto permits only local execution. Prospective policy cannot authorize its own merge or revoke
required authority. Host permissions and publication authority remain independent.

Local integration builds a conflict-free merge onto a moved target without a source base merge, then fast-forwards
only the checked Git target. Source identity, target advance, clean/locked worktrees, runtime location and scoped
cleanup remain guarded. `ff-only` and PR routes require source ancestry. Known generated conflicts retain their
registry seed side with `generated.seeded`, `generated.regenerate` and `INTEGRATION_GENERATED_SEEDED`.
Unknown artifact conflicts receive normal Git handling. No old-runtime rules, receipts or workflow content are
validated by integration. Standalone rule/workflow commands retain their checks.

JSON and text include `verification=pending` and `landed_sha` after confirmed landing; unperformed or unknown
landing is `verification=not_started`. `build` describes a prospective or executed Git build, not proof of landing.
Exit zero or `status=completed` proves the reported Git/cleanup effects only. Partial results preserve steps,
errors, failing operation and observed state. Errors before effects exit `2`, after effects `1`; warning-only
partial cleanup exits `0` unless strict warnings raise it.

After landing, synchronize declared dependencies using the project setup command and fresh processes. Sync
bundles, regenerate and commit stale tracked artifacts, then run required final checks on the resulting target
HEAD. Save the target SHA before the first merge for affected-test selection; never compare main against itself.
Report checked HEAD, commands and outcomes. A failed setup/import/check leaves delivery unfinished; repair the
target in scope and recheck without automatic rollback or merge replay. A batch may verify once, but all landed
units stay pending until the combined head passes.

Unknown PR outcomes preserve recovery identity until inspected. Confirmed landing with failed cleanup resumes
only the remaining approved cleanup. Required platform checks/reviews, pinned synchronous merge and leased remote
branch deletion remain. Remote deletion precedes local cleanup; a failure retains local branches/worktrees.

| Code | Required next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Correct the reported configuration or route; provider selection is not required |
| `INTEGRATION_PROVIDER_FAILED` | Inspect the failing operation and completed effects, repair and prepare remaining scope |
| `INTEGRATION_REQUEST_STALE` | Present current scope and obtain fresh authority for changed effects |
| `INTEGRATION_TARGET_MOVED` | Inspect the moved target and prepare again under the route's ancestry policy |
| `INTEGRATION_AUTHORITY_REQUIRED` | Under ask present scope and obtain approval; auto authorizes local effects only |
| `INTEGRATION_CLEANUP_UNSCOPED` | Adapt the named cleanup extension to exact scoped identity |
| `INTEGRATION_GENERATED_SEEDED` | Synchronize, regenerate the named artifacts and commit before final checks |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect effects and finish only guarded remaining cleanup |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | Invoke from a retained runtime outside the worktree being removed |
| `INTEGRATION_CHECKS_PENDING` | Wait for required PR checks/reviews, inspect and prepare remaining scope |

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


Proposal acceptance keeps its explicit direction authority and eligibility. A local Host accepts a reviewed Planning
branch with `devkit spec proposal accept-plan <slug> --by user|policy --mode accept_only|accept_and_handoff`;
`accept_and_handoff` yields with
verification pending and handoff not started. Synchronize/check the landed head, then invoke its existing handoff
command in a fresh process with retained scope and effort (`CAP-DLV-proposal-planning`).
