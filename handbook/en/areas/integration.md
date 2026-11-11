---
sources:
  ADR-delivery-approval-and-lifecycle-authority: 4461afd0b9ad6fb44b8f9c3789e0dcef4b1b60f6
  ADR-local-and-pull-request-integration: 7eb3930816c804462db081f96e68512fe5522f32
  ADR-post-merge-verification: f997807c5b8be2e091a355fc3417d196d99c6aa8
  CAP-DLV-delivery-workflows: d8e0681c758ff00891d93ccad00a499d5bc55efb
  CAP-DLV-project-policy: 69045e11fa4d0e8998f0b1ac44a30b403ab93425
  CAP-GOV-evaluation-lifecycle: caf36057be3e5b74834b5a842eb9c35a17e5e22c
  CAP-INT-mcp-services: ef6ce6f9338b8d75e8cbd887f37932ecb58ac642
  CAP-WT-task-worktrees: 2f5c45415f121e1d1d47046f255be4d4163e24dc
  UC-drive-development-to-integration: 2893591134de64be66238b4102062f02e0e370c8
title: Integration
---

# Integration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `f115e96c8059`, generated 2026-11-11. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](../journeys/advance-an-idea.md)
- [Assess a selected test suite](../journeys/assess-test-management.md)
- [Design necessary command entry points](../journeys/design-command-entrypoints.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Execute an isolated command](../journeys/execute-an-isolated-command.md)
- [Explore a design problem](../journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](../journeys/import-third-party-agent-assets.md)
- [Improve an interface and user flow](../journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Read decision supersession](../journeys/read-decision-supersession.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](../journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](../journeys/snapshot-bundle-sources.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
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

Integration lands a committed activity branch on the base branch and performs its scoped cleanup.
The Host checks the source content before approval and checks the landed content afterward.
The CLI binds Git effects and policy; `status=completed` confirms those effects, while
`verification=pending` means the final project checks still remain.

## Prepare the exact effects

Run from the retained base checkout with a runtime outside the worktree that cleanup removes:

```bash
uv run devkit integration prepare dev-login --route local
uv run devkit integration integrate dev-login --route local --expected-digest <digest>
```

`prepare` binds source/target SHAs, worktree identity, policy, merge strategy and cleanup scope.
It lands and removes nothing. Under `dev-integration=ask`, the Host presents those effects and receives your
conversational decision before `integrate`. The digest detects changed scope; it authenticates no approval.
Under shared-base `auto` policy, local integration is delegated and reported as `authority: policy`.
A source-only policy edit cannot authorize its own merge.

Both SDD and adaptive development use these explicit-branch commands. There are no task-kind, task-id,
unit or claims arguments, and no readiness-provider selection. The `[integration]` table accepts no keys; remove the retired `provider` key.
The Host checks workflow holds and required source checks using the source runtime before invoking integration.

## Choose the route

- **Local:** builds the prospective merge outside the target checkout and fast-forwards the target onto it.
  Under `no-ff`, a conflict-free moved target can be merged without first merging it into the source.
  `ff-only` still requires the source to contain the target. This route performs no fetch, push or remote deletion.
- **Pull request:** uses authenticated `gh`, pins the approved source SHA, observes required checks/reviews and
  verifies landing before leased remote deletion and local cleanup. It is never automatic. Required PR policy
  refuses the local route; merge queues and operations requiring bypass are not supported.

If PR checks are pending, the PR stays unmerged with `INTEGRATION_CHECKS_PENDING`; the merge requires fresh
preparation and authority. Native host permissions and publication authority remain separate from integration policy.

## Verify after landing

Save the target SHA before the first merge. After confirmed landing:

1. Synchronize the target's declared dependencies.
2. Use fresh processes to synchronize assets and check tracked generated files.
3. Regenerate and commit stale artifacts, then run required lint, types, rules and affected tests against the saved target SHA.
4. Report the checked final HEAD, commands and outcomes.

A local-orchestrated batch may check its combined head once after selected merges and repairs. Every landed unit
remains pending until that head passes. A failing target is repaired and checked again in place; the merge is not
replayed and there is no automatic rollback.

`INTEGRATION_GENERATED_SEEDED` means known generated conflicts were kept from their declared seed side.
The result lists `generated.seeded` and `generated.regenerate`. Integration ran no regeneration; the Host does it
after synchronization and before final checks. Unknown conflicts need ordinary resolution.

## Recover only the remaining effects

| Result | Next action |
| --- | --- |
| `INTEGRATION_AUTHORITY_REQUIRED`, `INTEGRATION_REQUEST_STALE` | Prepare and present the current scope; obtain the decision under `ask`. |
| `INTEGRATION_TARGET_MOVED` | Prepare on the current target; the local route builds the merge, while PR integration needs the target in the source. |
| `INTEGRATION_RUNTIME_IN_WORKTREE`, `WORKTREE_RUN_FROM_BASE` | Use the retained base checkout and a runtime outside cleanup scope. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Inspect Git/worktrees, then finish only the reported remaining cleanup. |

For a marked worktree after a confirmed merge, `uv run devkit worktree finish <branch>`
performs guarded remaining cleanup. If only an extension remains, use its exact owning command, such as
`uv run devkit spec proposal prune <slug>`. An unknown remote outcome is inspected before any repeated write.
Exit zero with partial cleanup still means cleanup remains; `landed_sha` identifies confirmed landing.

In local-orchestrated work, a reusable `git-operator` can execute exact currently authorized lifecycle jobs.
The Host retains decisions, source preparation, conflict interpretation and result acceptance. Normal integration
already includes cleanup. See [Worktree](worktree.md) and [Drive development to integration](../journeys/drive-development-to-integration.md).

## Sources

- [ADR-delivery-approval-and-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md)
- [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-local-and-pull-request-integration.md)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md)
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md)
- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md)
- [ADR-post-merge-verification](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261104-post-merge-verification.md)
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)
