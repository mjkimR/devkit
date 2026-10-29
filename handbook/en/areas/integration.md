---
sources:
  ADR-host-cli-lifecycle-authority: b827428c1717216975fb8b6119b1bc3dc128f8f2
  ADR-local-and-pull-request-integration: 8bfbc80942deeb24ba0d91d151c015528f18794e
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-GOV-evaluation-lifecycle: 3e13fc27305e7933a1876ea9879a7423b5a771e0
  CAP-INT-mcp-services: ee8088a63e89abb3519c1744c540c41e95352ea2
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-drive-development-to-integration: ede0ca1f9647c2e9e1a520d97818d09fa7bcb5e4
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
devkit integration prepare <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>]
devkit integration integrate <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>] [--expected-digest <digest>]
```

Run both from the base checkout, not from inside the task worktree that integration would remove; there either
command refuses with `WORKTREE_RUN_FROM_BASE`, whose fix is the same command with `-w` naming the base checkout.

1. `prepare` validates the committed source, the target, the project policy, the readiness provider and the exact
   cleanup scope. It changes nothing and prints `[INTEGRATION_PREPARED: ...]` with the digest, route and network
   use, followed by an `[INTEGRATION_SCOPE: ...]` line saying whether the worktree and branch will be removed, which
   extension cleanups run and what the readiness provider discloses. `--format json` returns the same approval scope
   and the planned steps.
2. The Host presents that result. Under `ask`, you approve it in the conversation.
3. `integrate --expected-digest <digest>` builds a fresh request and repeats every check before it changes
   anything. Under `ask` the digest is required; if anything it binds (source, target, policy, readiness, cleanup
   scope) changed, the command refuses with `INTEGRATION_REQUEST_STALE`. Under `auto` the digest is optional, but a
   supplied one still has to match.

The digest is a concurrency precondition, not a credential: it proves the request is the one you saw, not that you
approved it. When `integrate` runs under `ask` without a digest, or with one that no longer matches, the refusal
(`INTEGRATION_AUTHORITY_REQUIRED` or `INTEGRATION_REQUEST_STALE`) is an interaction for you: its fix is the
`prepare` command that presents the current scope, and the matching `integrate` command is given only as a detail for
after you approve it.

Caller `--claims` (for example the review, test and lint results of a session) are explicit on each command; neither
command stores or reuses the other's claims, so pass them to both.

Exit codes: `0` success, including a `partial` result whose only problem is the `INTEGRATION_CLEANUP_INCOMPLETE`
warning (Git integration is done, scoped cleanup remains); `1` an execution stopped by an error after some effect;
`2` a refusal before any effect. `--strict` raises a warning to `1` but never lowers a `2`.

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
| `INTEGRATION_NOT_READY` | Resolve the reported completion condition, then prepare again. When the evidence is `SESSION_CLAIMS_INVALID`, nothing in the source needs to change: correct `--claims` and rerun the same command. |
| `INTEGRATION_RULE_RUNTIME_MISMATCH` | A synchronized rule of the source imports something the running runtime (built from the target) lacks. The source needs no change: with separately granted authority, build a runtime from the source's code outside the worktree and integrate from the base checkout with it. |
| `INTEGRATION_AUTHORITY_REQUIRED` | Under `ask` without a digest: present the scope with the suggested `prepare`, then integrate once approved. Otherwise check the base policy and route. |
| `INTEGRATION_REQUEST_STALE` | For a changed scope: present it again and decide. After partial effects: inspect what already happened, prepare the remaining scope, decide again. |
| `INTEGRATION_APPROACH_MISMATCH`, `INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED` | Project readiness met SDD work (below): use the spec provider's lifecycle, or run the named Unit's lifecycle validation. |
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

## A runtime from the target judges the source's rules

Readiness runs with the installed devkit of the runtime that invokes it, which is built from the target, while the
synchronized rules it evaluates are the source's (`CAP-GOV-evaluation-lifecycle`). When a branch adds a rule whose
module the target's runtime does not have, integration names each rule file and missing import with
`INTEGRATION_RULE_RUNTIME_MISMATCH` before the provider runs, and changes nothing. The check only parses the rule
modules; it never executes source code, and integration never builds a runtime from the source by itself
(`UC-drive-development-to-integration`, extension 7h).

## Integration without SDD

In a project whose committed development approach is incubation, the installed `project` readiness provider handles
`--task-kind session` integration without inventing SDD units, stages or envelopes. Its `--claims` must report
passing `review`, `tests` and `lint` results; the provider runs the cumulative linter rules against the prospective
result, but it does not rerun your review, tests or lint, and it discloses them as claims. It refuses committed SDD
targets (`INTEGRATION_APPROACH_MISMATCH`), and refuses a change that touches the records of a retained workflow Unit
until that Unit's lifecycle validation has run (`INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED`). The spec provider hands
ordinary incubation sessions to this provider.

## Extending integration

Packages plug in through `devkit_agt.features.integration`: a `ReadinessProvider` decides whether the work is complete,
and a `ScopedCleanup` adds bound cleanup targets (devkit-spec uses it to remove scope records and prune proposal
directories, see [Collaboration](collaboration.md)). The public API also exports `IntegrationService`,
`IntegrationRequest`, `IntegrationResult` and the typed errors.

The lifecycle MCP tools of earlier designs (`integration_prepare`, `integration_integrate`, ...) are not registered;
the MCP runtime remains for shared proposal-review artifacts, which acceptance does not require (see [MCP](mcp.md)).

## Sources

- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md):
  CLI contract, authority, routes, recovery and codes.
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-drive-development-to-integration.md).
- [ADR-host-cli-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md),
  [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261022-local-and-pull-request-integration.md).
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md):
  which rules run where.
- Related: [Worktree](worktree.md) (`CAP-WT-task-worktrees`).
