---
sources:
  ADR-host-cli-lifecycle-authority: b827428c1717216975fb8b6119b1bc3dc128f8f2
  ADR-local-and-pull-request-integration: 8bfbc80942deeb24ba0d91d151c015528f18794e
  CAP-DLV-project-policy: 7cec046a7324de8f46048c80dea6a4286bf809ef
  CAP-INT-mcp-services: 41636553f0fe6331719d5d0cfaad2965deda6eb1
  CAP-WT-task-worktrees: a885013edf5dd548ffad4e9140c4b32b01b16ce2
  UC-drive-development-to-integration: bc214c7d80b401cf5b2ba5027c9144673d104393
title: Integration
---

# Integration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Integration is the last step of a task: the committed work on its activity branch lands on the base branch, and the
task worktree and branch are cleaned up. `devkit integration` (`CAP-INT-mcp-services`) does this in two steps,
prepare and integrate, through either a local merge or a pull request. It is where the journey
[Drive development to integration](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`) ends. For how branches, worktrees and gates fit together, see
[Concepts](../concepts.md).

## Who decides

Integration is a business decision, and the project's policy says who makes it (`dev-integration` in
`CAP-DLV-project-policy`):

- **`ask`**: the Host (the orchestrating agent session) shows you the exact source, target, report and cleanup
  effects, and you decide in the conversation. The Host then invokes the command. The CLI never prompts on stdin and
  accepts no approval flag or token; it revalidates the operation but does not authenticate the conversation.
- **`auto`**: authority comes from the policy committed on the base branch itself, and covers the local route only.
  The result reports `authority: policy`.

Workers never ask for this approval, and nothing else grants it: caller `--claims`, local configuration overlays and
host tool permissions are not business authority. The reasoning is recorded in `ADR-host-cli-lifecycle-authority`.

## Prepare, then integrate

```text
devkit integration prepare <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request]
devkit integration integrate <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--expected-digest <digest>]
```

1. `prepare` validates the committed source, the target, the project policy, the readiness provider and the exact
   cleanup scope. It changes nothing and prints `[INTEGRATION_PREPARED: ...]` with a `request.digest`.
2. The Host presents that result. Under `ask`, you approve it in the conversation.
3. `integrate --expected-digest <digest>` builds a fresh request and repeats every check before it changes
   anything. Under `ask` the digest is required; if anything it binds (source, target, policy, readiness, cleanup
   scope) changed, the command refuses with `INTEGRATION_REQUEST_STALE`. Under `auto` the digest is optional, but a
   supplied one still has to match.

The digest is a concurrency precondition, not a credential: it proves the request is the one you saw, not that you
approved it.

Exit codes follow the usual agent contract: `0` success, `1` a negative or partial result, `2` a refusal.

## Choose a route

- **Local** (`--route local`): devkit builds a merge commit outside the base checkout, checks it and fast-forwards
  the base, then runs the scoped cleanup. It never fetches, pushes or deletes remote branches. This is the same merge
  machinery as `devkit worktree finish` (see [Worktree](worktree.md)); `[worktree] merge = "ff-only"` is honoured.
- **Pull request** (`--route pull-request`): devkit discloses and performs the remote writes through its GitHub
  adapter, keeps the repository binding and head pinning, waits for required checks, verifies the landing and then
  removes the leased remote branch before local cleanup. It never runs automatically, and a policy of
  `[worktree] pull_request = "required"` refuses the local route.

Neither route changes host tool permissions, filesystem permissions, trust or publication policy. Merge construction
and route guards are part of the `CAP-INT-mcp-services` contract; `ADR-host-cli-lifecycle-authority` supersedes
`ADR-local-and-pull-request-integration`.

## When something goes wrong

Every result lists the completed steps, the failing operation, stable codes and the observed Git state. Nothing is
kept between invocations: no request ID, approval or recovery journal survives, so you recover by inspecting and
preparing again.

| Code | What to do |
| --- | --- |
| `INTEGRATION_NOT_READY` | Resolve the reported completion condition, then prepare again. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Check the base policy and route; under `ask`, get the decision before integrating. |
| `INTEGRATION_REQUEST_STALE` | Inspect what already happened, prepare the remaining scope, decide again. |
| `INTEGRATION_TARGET_MOVED` | Merge the current base into the branch, rerun checks, then decide again. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Finish the remaining cleanup (below). |
| `INTEGRATION_LANDED_UNCHECKED` | Run the provider's landed-target check before calling the work integrated. |
| `INTEGRATION_CONFIG_INVALID`, `INTEGRATION_PROVIDER_FAILED` | Install or repair the readiness provider, or use a supported route. |

Typical recoveries:

- The merge did not land: inspect source and target, then get a fresh decision before trying again.
- The merge landed but cleanup failed: check `devkit worktree status`. If the worktree remains, run
  `devkit worktree finish <branch> --merge --local-only`, which only performs the remaining guarded cleanup. If a
  post-finish action failed, run its own command on the reported target, for example
  `devkit spec proposal prune <slug>`.
- On the pull-request route, a remote branch deletion that failed or has an unknown outcome keeps the local worktree
  and branch. After you resolve the blocker, prepare and integrate the remaining scope; a merged PR is validated, never
  merged twice.
- When an outcome is unknown, look at Git or the pull request first. Never replay an unknown remote write.

## Extending integration

Packages plug in through `devkit_agt.features.integration`: a `ReadinessProvider` decides whether the work is complete,
and a `ScopedCleanup` adds bound cleanup targets (devkit-spec uses it to remove scope records and prune proposal
directories, see [Collaboration](collaboration.md)). The public API also exports `IntegrationService`,
`IntegrationRequest`, `IntegrationResult` and the typed errors.

The lifecycle MCP tools of earlier designs (`integration_prepare`, `integration_integrate`, ...) are not registered;
the MCP runtime remains for shared proposal-review artifacts, which acceptance does not require (see [MCP](mcp.md)).

## Sources

- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md):
  CLI contract, authority, routes, recovery and codes.
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-drive-development-to-integration.md).
- [ADR-host-cli-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md),
  [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261022-local-and-pull-request-integration.md).
- Related: [Worktree](worktree.md) (`CAP-WT-task-worktrees`).
