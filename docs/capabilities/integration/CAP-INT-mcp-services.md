---
id: CAP-INT-mcp-services
title: Scoped CLI Integration
summary: "Host-authorized integration binds Git effects and scoped cleanup, reports pending verification after confirmed landing, and leaves final content checks to the synchronized landed runtime."
area: integration
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/integration/
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
usecases:
  - UC-drive-development-to-integration
---

# [CAP-INT-mcp-services] Scoped CLI Integration

The integration CLI prepares and executes local or pull-request Git effects. The Host verifies branch content
before approval and final landed content afterward. `ADR-post-merge-verification` defines this separation;
`CAP-DLV-delivery-workflows` owns final delivery verification.

## CLI contract

```text
devkit integration prepare <branch> [--route local|pull-request]
devkit integration integrate <branch> [--route local|pull-request] [--expected-digest <digest>]
```

1. **Explicit source.** The CLI MUST accept the explicit branch without task-kind, task-id, unit or claims inputs.
   Removed options produce normal argument errors. It MUST NOT infer a hidden task or session claims. PR bodies
   and merge messages derive deterministically from the source branch and target.
2. **Git scope.** `prepare` MUST bind source and target revisions, retained and prospective policy, worktree identity,
   merge strategy and scoped cleanup identities. It performs no landing or cleanup. WHEN the source does not
   contain the local confirmation target under `no-ff`, preparation builds an unreferenced prospective merge to
   detect Git conflicts and prospective policy changes. The merge remains unsigned and deterministic across
   identity and time-zone changes. `ff-only` and PR routes retain their source-contains-target requirement.
3. **Approval.** Under `ask`, the Host MUST present the exact scope and receive the user's conversational decision
   before `integrate --expected-digest <digest>`. A missing digest raises `INTEGRATION_AUTHORITY_REQUIRED`; a changed
   digest raises `INTEGRATION_REQUEST_STALE`. Both direct the Host to present fresh scope, with the integrate command
   only for after approval. The digest excludes the transient request ID and is a concurrency condition, not an
   approval credential. Under `auto`, a supplied digest still MUST match. The CLI authenticates no conversation.
4. **Content boundary.** Integration MUST NOT discover readiness providers, evaluate source snapshots or workflow
   envelopes, run content finish guards, validate rule imports or validate receipt schemas/consistency. The Host
   checks source workflow holds through its branch runtime and runs final checks after synchronizing landed
   dependencies. No test runner, runtime installer or verification ledger is part of integration.
5. **Legacy configuration.** `[integration]` MAY be absent. Its legacy `provider` value is ignored and excluded from
   the digest; unknown keys or invalid table shapes raise actionable `INTEGRATION_CONFIG_INVALID` diagnostics.
6. **Confirmed landing.** JSON and text MUST report `verification=pending` only after confirmed landing, including
   cleanup-only retries, and `verification=not_started` otherwise. `landed_sha` names the confirmed revision and is
   null before confirmation. `status=completed` and exit zero attest Git/cleanup effects only. The Host's later
   report owns final verification outcomes.

These contracts are covered by `packages/devkit/tests/integration/features/integration/test_cli.py`,
`packages/devkit/tests/integration/features/integration/test_service.py` and
`packages/devkit-spec/tests/e2e/features/delivery/test_integration_rule_runtime.py`.

Text preparation prints `[INTEGRATION_PREPARED: ... target_sha= digest= route= network=]` and
`[INTEGRATION_SCOPE: worktree_remove= delete_branch= cleanup= seeded= verification=]`. Integration prints
`[INTEGRATION: status= ... target_sha= build_target= result= ... seeded= verification= landed_sha= effects=]`.
JSON contains `request`, `status`, `verification`, `landed_sha`, `steps`, `errors`, `notices` and applicable
`build`, `landing`, `cleanup_steps` and `generated`. `build` describes a constructed result, which is not landing
proof; `landing` records PR provenance comparisons, which are not content-check results. Detailed serialization
adds internal policy and cleanup identity. Warnings/notices precede decisive errors on stderr.
A refusal before effects exits `2`; an error after partial effects exits `1`; a warning-only partial cleanup exits
`0` unless `--strict` raises it to `1`. `--strict` never lowers `2`.
JSON also carries `authority`: `none` from `prepare`, else `policy` or `host-conversation` for the authority used.

Local integration builds outside the target checkout, validates the permitted target advance and policy, then
fast-forwards only while the target still equals the build target. It performs no fetch, push or remote deletion.
Source-tip pinning, clean/locked worktree checks, runtime-outside-cleanup checks, the integration lock and exact
cleanup extensions remain mandatory. A source-only policy change cannot authorize its own merge. A runtime inside
the removed worktree is `INTEGRATION_RUNTIME_IN_WORKTREE`; running from that worktree is `WORKTREE_RUN_FROM_BASE`.

WHEN every local conflict belongs to an enabled artifact in the understood target registry and no regeneration
reads another conflict, integration MUST retain each artifact's seed side and disclose `generated.seeded` and
`generated.regenerate` with `INTEGRATION_GENERATED_SEEDED`. It runs no regeneration itself. Unknown artifacts receive
ordinary `WORKTREE_MERGE_CONFLICT` handling. Other Git failures retain `WORKTREE_GIT_UNSUPPORTED`,
`WORKTREE_COMMIT_FAILED` or `WORKTREE_MERGE_NOT_FF`. Composed acceptance and PR integration seed no conflicts.
The Host synchronizes first, then regenerates and commits before final checks. Tests:
`packages/devkit/tests/e2e/features/integration/test_base_advance.py`.

## Authority and route limits

- `dev-integration=ask` means the Host carries the user's conversational decision. The CLI neither prompts for
  stdin nor accepts a proof of that decision.
- `dev-integration=auto` authorizes only local integration. The CLI reads effective policy from the retained base,
  rejects prospective revocation and reports `authority: policy`.
- Local overlays and host command permission do not grant business authority.
- A required pull-request policy refuses the local route. Automatic pull-request execution is refused.
- Pull-request execution validates and discloses remote writes through the existing GitHub adapter. It preserves
  repository binding, head pinning, required checks, landing verification and leased branch cleanup.
- **GitHub through `gh`.** The pull-request route MUST reach GitHub only through `gh` under `gh`'s own
  authentication; devkit MUST NOT store or read a token, call GitHub over its own HTTP client or bypass protection.
- **Refusal before approval.** IF `gh` is missing or unauthenticated, cannot resolve the selected remote, an
  existing PR is cross-repository (fork) or the target has a merge queue, THEN `prepare` MUST refuse with a stable code
  (`INTEGRATION_GH_UNAVAILABLE`, `INTEGRATION_REMOTE_UNSUPPORTED`) before the Host presents the scope.
- **No queue or bypass.** The route MUST NOT enqueue, auto-merge or admin-merge (`--auto`, `--admin`); a merge that
  needs them is either pending or refused by the platform.
- **Synchronous pinned merge.** The merge MUST be the synchronous `gh api --hostname <host> --method PUT
  repos/<owner>/<repo>/pulls/<number>/merge` with the approved source `sha` and `merge_method=merge`. IF the platform
  answers 403, 405, 409 or 422 and the PR is not merged, THEN integrate MUST fail with `INTEGRATION_MERGE_REFUSED`;
  any other unmerged outcome is `INTEGRATION_STEP_UNKNOWN`, resolved only from the PR state.
- **Leased remote deletion.** Remote branch deletion MUST use only `git push
  --force-with-lease=refs/heads/<branch>:<sha> <remote> --delete <branch>`; integration MUST NOT run
  `gh pr merge --delete-branch`, which deletes the local branch outside devkit's guards.
- **Checks pending.** WHEN required checks, required reviews or platform mergeability are not yet satisfied after the
  checked build, integrate MUST publish the source and PR, make no merge call and return `status=pending` with the
  `INTEGRATION_CHECKS_PENDING` notice. The merge then takes a fresh `prepare` and Host decision.
  Covered by `packages/devkit/tests/integration/features/integration/test_github.py` and
  `packages/devkit/tests/integration/features/integration/test_pull_request.py`.
- Neither route changes host tool permission, filesystem permission, trust or publication policy.

In `local-orchestrated`, git-operator may prepare and execute the exact currently authorized CLI job
(`ADR-delivery-approval-and-lifecycle-authority`, `CAP-DLV-delivery-workflows`). The Host keeps approval, publication
authority, source preparation, semantic decisions and result acceptance. WHEN execution is delegated, the operator
MUST revalidate job identity/refs and preserve CLI Git identity, digest, route and cleanup checks.

WHEN a delegated CLI result is partial or unknown, git-operator MUST inspect the actual completed effects and exact
remaining cleanup identity before a supported retry. Its role result carries completed_effects and remaining_effects,
plus original CLI status, exit code and effects separately. IF requested effects remain after a zero-exit
`INTEGRATION_CLEANUP_INCOMPLETE`, THEN the role MUST return needs_input or failed rather than completed.
Normal integration includes cleanup; no redundant cleanup job follows a completed integration. The asset boundary
is checked by `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`; real CLI effects are
checked by `packages/devkit/tests/integration/features/integration/test_cli.py`.

The request binds Git and retained approval policy, without content-readiness evidence. Permitted descendant
target advances are rebuilt once; changed source, disallowed target history, policy or cleanup identity refuses
before the affected mutation. Platform-required PR checks and reviews remain mandatory.

## Partial results and recovery

Each result reports completed steps, the failing operation, stable error codes and observed Git state. No request ID,
approval or recovery journal survives the invocation.

- If local merge did not land, inspect the reported source and target and obtain fresh Host authority before running
  another integration.
- If local merge landed but worktree cleanup failed, inspect `devkit worktree status` and the target branch. When
  the marked worktree remains, run `devkit worktree finish <branch> --local-only`; its already-merged checks
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
- A changed target requires a fresh preparation, which checks the prospective Git merge and policy, and a fresh Host decision
  under `ask`. The local route needs no base merge unless that preparation reports a Git conflict; the
  pull-request route still requires the source to contain the target.

The optional `devkit-mcp` runtime remains available for shared proposal-review artifacts (`CAP-COLL-shared-artifacts`),
which acceptance does not require. The
lifecycle tools `integration_prepare`, `integration_integrate`, `integration_status` and `integration_resume` are not
registered.

A final-check failure preserves landed history and completed cleanup. The Host repairs the target in scope and
rechecks; it MUST NOT replay the merge or automatically roll back. A deliberate revert requires existing authority.

## Stable integration codes

| Code | Next action |
| --- | --- |
| `INTEGRATION_CONFIG_INVALID` | Correct the reported configuration or route; provider selection is not required. |
| `INTEGRATION_PROVIDER_FAILED` | Inspect the failing operation and completed effects, repair the cause and prepare remaining scope. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Under `ask` without a digest, `INTERACTION`: run `[FIX]` to present the scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise `BLOCKED`: inspect the retained base policy and selected route. |
| `INTEGRATION_REQUEST_STALE` | For a digest that differs from the current scope, `INTERACTION`: run `[FIX]` to present the current scope; the `[DETAIL]` integrate command is for after the user approves it. Otherwise inspect completed effects and revalidate the remaining scope before fresh Host authority. |
| `INTEGRATION_TARGET_MOVED` | Nothing changed on the target. Prepare again on the current target (the local route builds the merge itself; the pull-request route needs the target merged into the source), then obtain fresh Host authority or re-evaluate retained-base auto policy before `devkit integration integrate`. |
| `INTEGRATION_GENERATED_SEEDED` | `WARNING`: the merge kept the named generated files from one side without regenerating them. After the integration lands, run the `[FIX]` command (`devkit generated regen <ids>`) on the target branch and commit the regenerated files; a `local-orchestrated` run does it once before its batch test run. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git and worktree state; run guarded already-merged finish for a marked remaining worktree, or the owning extension command for a remaining scoped post-finish target. |
| `INTEGRATION_CHECKS_PENDING` | `NOTICE`: the PR is published and unmerged. Wait for its checks and reviews with an agent bound, inspect the PR, then prepare again and integrate with the new digest after Host approval. |


Public API: `IntegrationService`, `IntegrationContext`, `IntegrationRequest`, `IntegrationResult`, `CleanupTarget`,
`CleanupScope`, `CleanupResult`, `ScopedCleanup` and typed errors. `Evidence` and `Readiness` remain internal
acceptance-preview value types; they do not register a generic provider. Worktree merge and finish primitives
remain owned by `CAP-WT-task-worktrees`.
