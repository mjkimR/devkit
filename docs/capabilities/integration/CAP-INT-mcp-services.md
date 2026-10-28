---
id: CAP-INT-mcp-services
title: Scoped CLI Integration
summary: "Host-authorized integration revalidates retained policy, readiness and cleanup. Independent incubation project readiness preserves explicit verification claims and refuses unvalidated retained workflow Units."
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
interface and `ADR-local-and-pull-request-integration`; the merge construction and route guards below are this
capability's current contract.

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

Session claims remain explicit on both `prepare` and `integrate`; neither command persists or reuses the other's claims.
Correcting invocation input alone requires no source change. Ordinary source-readiness, digest and authority checks
remain in force (`packages/devkit/tests/integration/features/integration/test_cli.py`).

Text `prepare` prints `[INTEGRATION_PREPARED: <id> branch=... target="..." digest=... route=... network=...]` and
`[INTEGRATION_SCOPE: worktree_remove=yes|no delete_branch=yes|no cleanup=<extensions>|- disclosure="<text>"]`;
`--format json` prints the approval scope (`request`: digest, approval, task, source, target, worktree, cleanup,
route, `pull_request` (`null` on the local route, `create` before the PR exists), `readiness.disclosure`) and the
planned `steps`, never internal identities, policy digests or Git directories. `integrate` prints
`[INTEGRATION: status=... ... effects=<step>:<state>,...]` or one JSON object. Warnings and notices use the Agent
Advisory Protocol on stderr, then the errors, last. A refusal before any effect exits `2`; an execution stopped by an
error after an effect exits `1`; a successful result exits `0`, also a `partial` one whose only advisory is the
`INTEGRATION_CLEANUP_INCOMPLETE` warning (Git integration done, scoped cleanup remains), unless `--strict` raises a
warning to `1`. `--strict` never lowers `2`.

WHEN `ask` integration is invoked without a digest or with one that differs from the current scope, the refusal
(`INTEGRATION_AUTHORITY_REQUIRED` or `INTEGRATION_REQUEST_STALE`) MUST be `INTERACTION`: `[REPORT]` asks the user to
approve the scope, `[FIX]` is the exact `prepare` command that shows it (re-presenting the scope, never integrating
it), and a `[DETAIL]` names the exact `integrate` command with the current digest, only for after the user approves
the presented scope. The automatic policy refusing the pull-request route stays `BLOCKED`. Run inside the worktree
it would remove, either command is `WORKTREE_RUN_FROM_BASE`, whose `[FIX]` is the same command with `-w` naming the
devkit project in the base checkout.

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

Readiness runs with the installed code of the runtime that invokes it, which is built from the target, while the
source's synchronized rules are the source's (`CAP-GOV-evaluation-lifecycle`). Before the provider runs, WHEN a
synchronized rule module listed in the source's committed receipt, or the result's at a build, imports at module level
a module or name of an installed top-level package that the running runtime does not provide, the integration MUST
refuse with `INTEGRATION_RULE_RUNTIME_MISMATCH`, naming each rule file and missing import, and change nothing. The
refusal comes after `INTEGRATION_RUNTIME_IN_WORKTREE` and `INTEGRATION_RECEIPT_READER_CHANGED`, so a source meeting
several of these cases receives the earlier code. The check parses the rule modules and resolves their imports against
the running runtime; it executes no source code. A rule that fails for another reason, such as an import nothing
installed provides or a syntax error, is left to the provider's own refusal. Integration never builds or selects a
runtime from the source by itself: the source would then be judged by its own rule engine and provider. Covered by
`packages/devkit/tests/integration/features/integration/test_rule_runtime.py` and
`packages/devkit-spec/tests/e2e/features/delivery/test_integration_rule_runtime.py`.

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

The optional `devkit-mcp` runtime remains available for shared proposal-review artifacts (`CAP-COLL-shared-artifacts`),
which acceptance does not require. The
lifecycle tools `integration_prepare`, `integration_integrate`, `integration_status` and `integration_resume` are not
registered.

## Stable integration codes

| Code | Next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Configure or install the named readiness provider and use a supported route. |
| `INTEGRATION_NOT_READY` | `INPUT_ERROR`: missing or invalid session claims are identified by provider evidence `SESSION_CLAIMS_INVALID`; `[TARGET]` names `--claims` and `[FIX]` directs correction and retry of the same prepare or integrate command with explicit claims. Other readiness failures direct source-worktree fixes, commit and preparation again. |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract. |
| `INTEGRATION_RULE_RUNTIME_MISMATCH` | The source needs no change. With separately granted authority, build a runtime from the source's code outside the worktree being removed and run `devkit integration integrate <branch>` from the base checkout with it; never edit the rules, skip readiness or use the worktree's own runtime. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Under `ask` without a digest, `INTERACTION`: run `[FIX]` to present the scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise `BLOCKED`: inspect the retained base policy and selected route. |
| `INTEGRATION_REQUEST_STALE` | For a digest that differs from the current scope, `INTERACTION`: run `[FIX]` to present the current scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise inspect completed effects and revalidate the remaining scope before fresh Host authority. |
| `INTEGRATION_TARGET_MOVED` | Merge the current base into the source, rerun required checks and obtain fresh Host authority or re-evaluate retained-base auto policy before `devkit integration integrate`. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git and worktree state; run guarded already-merged finish for a marked remaining worktree, or the owning extension command for a remaining scoped post-finish target. |
| `INTEGRATION_LANDED_UNCHECKED` | Run the provider's landed-target check and do not report checked integration until it passes. |

Public API: `devkit_agt.features.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`,
`Readiness`, `ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`,
`CleanupResult`, `ScopedCleanup` and typed errors. `devkit_agt.features.worktree` owns merge and finish primitives.


## Independent incubation project readiness

The installed `project` provider in devkit-agt supports `session` integration when the retained committed target
approach is incubation. Its explicit claims require passing `review`, `tests` and `lint` results, accepting `true`,
`PASS`, `PASSED` or a `PASS ...` string. Missing/failed claims produce `SESSION_CLAIMS_INVALID` evidence and existing
`INTEGRATION_NOT_READY` recovery. No SDD depth, effort, Unit or lifecycle envelope is manufactured.

The provider runs cumulative linter rules against the prospective result (source before build) and binds source,
target/result identity, the target/proposed development approaches, verification claims, `CI_RULES` and
`LIFECYCLE=omitted:incubation`. Reported rule omissions remain distinct from successful execution. Review/tests/lint
are disclosed source claims; they are not secretly rerun by the provider. Existing receipt/runtime/route/approval,
request freshness, worktree and exact cleanup checks remain in the common executor.

IF a project provider sees a committed SDD target, THEN it MUST refuse with `INTEGRATION_APPROACH_MISMATCH`.
The common policy digest includes the validated development approach. A proposed source-only switch cannot select
weaker target readiness. The installed spec provider delegates ordinary incubation sessions to project readiness.

Before treating a diff as an ordinary session, ownership discovery examines parsed bindings/history in both prior
and proposed committed trees. IF changed/deleted anchors or companions belong to a retained workflow Unit, THEN
project readiness MUST refuse with `INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED` and identify the Unit. The caller must
run its matching Unit lifecycle validator explicitly; task labels and optional package absence are not evidence that
validation ran. Untouched history does not require the SDD package. The ordinary doc-only path is exercised by
`packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`; actual prepare/integrate and retained cases by
`packages/devkit/tests/integration/features/integration/test_project_readiness.py`.
