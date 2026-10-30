---
id: CAP-INT-mcp-services
title: Scoped CLI Integration
summary: "Host-authorized integration revalidates policy, readiness and cleanup. A reusable git-operator may execute exact delegated effects while the Host retains decisions; role completion preserves CLI partial effects and never follows exit zero alone."
area: integration
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/integration/
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
usecases:
  - UC-drive-development-to-integration
---

# [CAP-INT-mcp-services] Scoped CLI Integration

`devkit_agt.features.integration` prepares an immutable in-process request and executes it through the local or
pull-request route. The `devkit integration` CLI exposes the operation. Under `ask`, the Host presents the exact
source, target, report and cleanup effects, receives the user's conversational decision, then invokes the command
directly or delegates its exact effects to git-operator.
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
or delegating `integrate --expected-digest <digest>` under `ask`, using the `request.digest` from that preparation.
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

Text `prepare` prints `[INTEGRATION_PREPARED: <id> branch=... target="..." target_sha=<confirmation target> digest=...
route=... network=...]` and
`[INTEGRATION_SCOPE: worktree_remove=yes|no delete_branch=yes|no cleanup=<extensions>|- seeded=<ids>|- disclosure="<text>"]`
and its notices on stderr;
`--format json` prints the approval scope (`request`: digest, approval, task, source, target, worktree, cleanup,
route, `pull_request` (`null` on the local route, `create` before the PR exists), `readiness.disclosure`), the
planned `steps` and, when the build seeded generated files, `generated`, never internal identities, policy digests or Git directories. `integrate` prints
`[INTEGRATION: status=... ... target_sha=<confirmation target> build_target=<sha>|- result=<sha>|- ...
seeded=<ids>|- disclosure="<text>" effects=<step>:<state>,...]` or one JSON object, whose `build` names the confirmation target,
the build target and the landed result. Every result that carries a request thus states the merged target and what
was checked on the merged result (`ADR-moved-target-merge`); a cleanup-only result names only the prepared target. Warnings and notices use the Agent
Advisory Protocol on stderr, then the errors, last. A refusal before any effect exits `2`; an execution stopped by an
error after an effect exits `1`; a successful result exits `0`, also a `partial` one whose only advisory is the
`INTEGRATION_CLEANUP_INCOMPLETE` or `INTEGRATION_GENERATED_SEEDED` warning, unless `--strict` raises a
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

WHEN the source does not contain the confirmation target under `[worktree] merge = "no-ff"`, local `prepare` MUST
build the prospective merge in the object store and run the finish guards on `merge-base(target, source)`, the
readiness provider, the receipt check and the prospective policy digest on it before it returns a request; the
source need not contain the target first (`ADR-moved-target-merge`). A conflict refuses with
`WORKTREE_MERGE_CONFLICT`, a failing check with `INTEGRATION_NOT_READY` or `INTEGRATION_RECEIPT_CONFLICT`, Git
below 2.38 with `WORKTREE_GIT_UNSUPPORTED`, a missing committer identity with `WORKTREE_COMMIT_FAILED`, each with
nothing changed; only after a conflict or a failing check does the Host merge the target into the task branch. The prospective commit is unsigned, referenced by no ref and copies the committer line of the
parent with the later committer date, so two preparations of one source and target yield one digest whatever the
Git identity or `TZ`. Cleanup is planned from the approved context, and `build` names only real builds. `ff-only`,
`devkit worktree finish --merge` and the pull-request route keep refusing a moved target with
`WORKTREE_MERGE_NOT_FF`. Covered by `packages/devkit/tests/e2e/features/integration/test_base_advance.py` and
`packages/devkit/tests/integration/features/integration/test_cli.py`.

WHEN every conflict of a local prepare or integrate build is in a path an enabled generated artifact owns
(`CAP-GEN-tracked-artifacts`; the built-in artifacts plus the `.devkit/generated.toml` committed at the build target)
and no artifact to regenerate reads or updates another conflict, the build MUST keep each owned path from the
artifact's `seed` side (`ours` the target, `theirs` the source; removed where that side deleted it) instead of
refusing, and run every check above on that result (`ADR-generated-conflicts-in-prepared-merge`). Nothing is
regenerated. The prospective and the real build of one source and target produce one tree. The result discloses the
seeded artifacts in `generated` (`{"seeded": [{"id", "paths", "seed", "kept": "target"|"source"}], "regenerate":
"uv run devkit generated regen <ids>"}`), in the `seeded=` sentinel field and with an `INTEGRATION_GENERATED_SEEDED`
warning; integrate replaces prepare's disclosure with its own build's. Any other conflict refuses with
`WORKTREE_MERGE_CONFLICT`, one `[DETAIL]` per such path (`<path>: owned by no generated artifact` or
`<path>: read by <ids>`), nothing changed. Composed proposal acceptance and the pull-request route settle no conflict.

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

In `local-orchestrated`, git-operator may prepare and execute the exact currently authorized CLI job
(`ADR-reusable-lifecycle-resource-manager`, `CAP-DLV-delivery-workflows`). The Host keeps approval, publication
authority, source preparation, semantic decisions and result acceptance. WHEN execution is delegated, the operator
MUST revalidate job identity/refs and preserve CLI readiness, digest, route and cleanup checks.

WHEN a delegated CLI result is partial or unknown, git-operator MUST inspect the actual completed effects and exact
remaining cleanup identity before a supported retry. Its role result carries completed_effects and remaining_effects,
plus original CLI status, exit code and effects separately. IF requested effects remain after a zero-exit
`INTEGRATION_CLEANUP_INCOMPLETE`, THEN the role MUST return needs_input or failed rather than completed.
Normal integration includes cleanup; no redundant cleanup job follows a completed integration. The asset boundary
is checked by `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`; real CLI effects are
checked by `packages/devkit/tests/integration/features/integration/test_cli.py`.

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
- A changed target requires a fresh preparation, which checks the new prospective merge, and a fresh Host decision
  under `ask`. The local route needs no base merge unless that preparation reports a conflict or failing check; the
  pull-request route still requires the source to contain the target.

The optional `devkit-mcp` runtime remains available for shared proposal-review artifacts (`CAP-COLL-shared-artifacts`),
which acceptance does not require. The
lifecycle tools `integration_prepare`, `integration_integrate`, `integration_status` and `integration_resume` are not
registered.

## Stable integration codes

| Code | Next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Configure or install the named readiness provider and use a supported route. |
| `INTEGRATION_NOT_READY` | `INPUT_ERROR`: missing or invalid session claims are identified by provider evidence `SESSION_CLAIMS_INVALID`; `[TARGET]` names `--claims` and `[FIX]` directs correction and retry of the same prepare or integrate command with explicit claims. Other readiness failures direct source-worktree fixes, commit and preparation again; a CI-rule or unit-directory reason found on a prospective or built result names the conditional base merge (merge the target into the task branch, `devkit rules fix`, re-verify what the merge changed, prepare again). |
| `INTEGRATION_PROVIDER_FAILED` | Repair the installed provider or its evidence contract. |
| `INTEGRATION_RULE_RUNTIME_MISMATCH` | The source needs no change. With separately granted authority, build a runtime from the source's code outside the worktree being removed and run `devkit integration integrate <branch>` from the base checkout with it; never edit the rules, skip readiness or use the worktree's own runtime. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Under `ask` without a digest, `INTERACTION`: run `[FIX]` to present the scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise `BLOCKED`: inspect the retained base policy and selected route. |
| `INTEGRATION_REQUEST_STALE` | For a digest that differs from the current scope, `INTERACTION`: run `[FIX]` to present the current scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise inspect completed effects and revalidate the remaining scope before fresh Host authority. |
| `INTEGRATION_TARGET_MOVED` | Nothing changed on the target. Prepare again on the current target (the local route builds the merge itself; the pull-request route needs the target merged into the source), then obtain fresh Host authority or re-evaluate retained-base auto policy before `devkit integration integrate`. |
| `INTEGRATION_GENERATED_SEEDED` | `WARNING`: the merge kept the named generated files from one side without regenerating them. After the integration lands, run the `[FIX]` command (`devkit generated regen <ids>`) on the target branch and commit the regenerated files; a `local-orchestrated` run does it once before its batch test run. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git and worktree state; run guarded already-merged finish for a marked remaining worktree, or the owning extension command for a remaining scoped post-finish target. |
| `INTEGRATION_LANDED_UNCHECKED` | Run the provider's landed-target check and do not report checked integration until it passes. |

Public API: `devkit_agt.features.integration` exports `IntegrationService`, `Task`, `IntegrationContext`, `Evidence`,
`Readiness`, `ReadinessProvider`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`, `CleanupScope`,
`CleanupResult`, `ScopedCleanup` and typed errors. `devkit_agt.features.worktree` owns merge and finish primitives.


## Independent adaptive-development project readiness

The installed `project` provider in devkit-agt supports `session` integration when the retained committed target
approach is `adaptive-dev`. Its explicit claims require passing `review`, `tests` and `lint` results, accepting `true`,
`PASS`, `PASSED` or a `PASS ...` string. Missing/failed claims produce `SESSION_CLAIMS_INVALID` evidence and existing
`INTEGRATION_NOT_READY` recovery. No SDD depth, effort, Unit or lifecycle envelope is manufactured.

The provider runs cumulative linter rules against the prospective result (source before build) and binds source,
target/result identity, the target/proposed development approaches, verification claims, `CI_RULES` and
`LIFECYCLE=omitted:adaptive-dev`. Reported rule omissions remain distinct from successful execution. Review/tests/lint
are disclosed source claims; they are not secretly rerun by the provider. Existing receipt/runtime/route/approval,
request freshness, worktree and exact cleanup checks remain in the common executor.

IF a project provider sees a committed SDD target, THEN it MUST refuse with `INTEGRATION_APPROACH_MISMATCH`.
The common policy digest includes the validated development approach. A proposed source-only switch cannot select
weaker target readiness. The installed spec provider delegates ordinary adaptive-development sessions to project readiness.

Before treating a diff as an ordinary session, ownership discovery examines parsed bindings/history in both prior
and proposed committed trees. IF changed/deleted anchors or companions belong to a retained workflow Unit, THEN
project readiness MUST refuse with `INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED` and identify the Unit. The caller must
run its matching Unit lifecycle validator explicitly; task labels and optional package absence are not evidence that
validation ran. Untouched history does not require the SDD package. The ordinary doc-only path is exercised by
`packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`; actual prepare/integrate and retained cases by
`packages/devkit/tests/integration/features/integration/test_project_readiness.py`.
