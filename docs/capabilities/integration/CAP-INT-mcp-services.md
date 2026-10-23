---
id: CAP-INT-mcp-services
title: Scoped CLI Integration
summary: "The Host prepares and integrates committed work through CLI operations that revalidate policy, readiness, source identity and cleanup scope. Under ask the Host carries conversational approval; auto authority comes only from the retained base policy."
area: integration
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/integration/
usecases:
  - UC-drive-development-to-integration
---

# [CAP-INT-mcp-services] Scoped CLI Integration

`devkit_agt.features.integration` prepares an immutable in-process request and executes it through the local or
pull-request route. The `devkit integration` CLI exposes the operation. Under `ask`, the Host presents the exact
source, target, report and cleanup effects, receives the user's conversational decision, then invokes the command.
The CLI revalidates the operation but does not authenticate that conversation. Under `auto`, it derives authority
from the retained base policy. `ADR-host-cli-lifecycle-authority` supersedes the former lifecycle MCP execution
interface. `ADR-local-and-pull-request-integration` remains authoritative for merge construction and route guards.

## CLI contract

```text
devkit integration prepare <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>]
devkit integration integrate <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>] [--expected-digest <digest>]
```

`prepare` validates the committed source, target, project policy, readiness provider and exact cleanup scope. It
performs no integration mutation. The Host presents its result and obtains the business decision before invoking
`integrate --expected-digest <digest>` under `ask`, using the `request.digest` from that preparation.
WHEN the owning policy is `ask`, the CLI MUST require the prepared digest and refuse a changed digest with
`INTEGRATION_REQUEST_STALE` before integration effects. The digest excludes the transient request ID and binds the
source, target, policy, readiness and cleanup scope. It is a concurrency precondition, not an approval credential.
Under `auto`, the digest is optional; a supplied digest MUST still match. These checks are covered by
`packages/devkit/tests/integration/features/integration/test_cli.py`.
`integrate` constructs a fresh request and repeats all checks before mutation. The CLI accepts
no approval boolean, token, request ID, cleanup path or merge strategy. Caller `claims` are provider declarations,
not evidence or authority.

Text output contains one `[INTEGRATION_PREPARED: ...]` or `[INTEGRATION: ...]` result line. `--format json` contains
one JSON object. Warnings and notices use the Agent Advisory Protocol on stderr. A refusal exits `2`; a negative or
partial execution result exits `1`; a successful result exits `0` unless `--strict` promotes warnings.

The `IntegrateUseCase` runs through the same request validator, provider, finish guards, integration lock and scoped
cleanup engine as other trusted in-process callers. Local integration builds a merge commit outside the base
checkout, checks the result and fast-forwards the base. It performs no fetch, push or remote branch deletion. The
`ff-only` project strategy remains supported.

## Authority and route limits

- `dev-integration=ask` means the Host carries the user's conversational decision. The CLI neither prompts for
  stdin nor accepts a proof of that decision.
- `dev-integration=auto` authorizes only local integration. The CLI reads effective policy from the retained base,
  rejects prospective revocation and reports `authority: policy`.
- Caller claims, local overlays and host command permission do not grant business authority.
- A required pull-request policy refuses the local route. Automatic pull-request execution is refused.
- Pull-request execution validates and discloses remote writes through the existing GitHub adapter. It preserves
  repository binding, head pinning, required checks, landing verification and leased branch cleanup.
- Neither route changes host tool permission, filesystem permission, trust or publication policy.

The result binds the repository, source and target SHAs, worktree identity, merge strategy, policy digests, readiness
provider identity, finish guards and scoped cleanup targets. A changed source, target, policy, provider, readiness
result or cleanup identity refuses before the affected mutation. The readiness provider may inspect the source and
prospective merged result; the request's digest keeps provider evidence distinct from caller claims.

## Partial results and recovery

Each result reports completed steps, the failing operation, stable error codes and observed Git state. No request ID,
approval or recovery journal survives the invocation.

- If local merge did not land, inspect the reported source and target and obtain fresh Host authority before running
  another integration.
- If local merge landed but worktree cleanup failed, inspect `devkit worktree status` and the target branch. When
  the marked worktree remains, run `devkit worktree finish <branch> --merge --local-only`; its already-merged checks
  perform only remaining guarded Git cleanup. When Git cleanup completed but a scoped post-finish action failed, run
  that extension's owning command against the exact reported cleanup target (proposal directories, for example, use
  `devkit spec proposal prune <slug>`).
- On the pull-request route, leased remote branch deletion MUST complete before local worktree and branch deletion.
  IF remote deletion fails or its outcome is unknown, THEN the operation MUST preserve the local recovery identity.
  After resolving the blocker and inspecting the merged PR and remote ref, prepare the remaining scope and execute
  with its fresh digest; the merged PR is validated and never merged twice. This is covered by
  `packages/devkit/tests/integration/features/integration/test_pull_request.py`.
- If the result is unknown, inspect Git or the pull request before another mutation. Never replay an unknown remote
  write or remove a worktree whose identity is ambiguous.
- A changed target requires the source to incorporate that target, fresh readiness and a fresh Host decision under
  `ask`.

The optional `devkit-mcp` runtime remains available for shared artifacts and proposal report publication. The
lifecycle tools `integration_prepare`, `integration_integrate`, `integration_status` and `integration_resume` are not
registered.

## Stable integration codes

| Code | Next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Configure or install the named readiness provider and use a supported route. |
| `INTEGRATION_NOT_READY` | Resolve the reported completion condition and prepare the committed source again. |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Inspect the retained base policy and selected route; under `ask`, obtain Host conversational approval before invoking `devkit integration integrate`. |
| `INTEGRATION_REQUEST_STALE` | Inspect completed effects and revalidate the remaining scope before fresh Host authority. |
| `INTEGRATION_TARGET_MOVED` | Merge the current base into the source, rerun required checks and obtain fresh Host authority or re-evaluate retained-base auto policy before `devkit integration integrate`. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git and worktree state; run guarded already-merged finish for a marked remaining worktree, or the owning extension command for a remaining scoped post-finish target. |
| `INTEGRATION_LANDED_UNCHECKED` | Run the provider's landed-target check and do not report checked integration until it passes. |

Public API: `devkit_agt.features.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`,
`Readiness`, `ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`,
`CleanupResult`, `ScopedCleanup` and typed errors. `devkit_agt.features.worktree` owns merge and finish primitives.
