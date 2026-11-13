---
sources:
  CAP-DLV-delivery-workflows: 747eec234d403705ebf34d9a03424bd87afb9ce4
  CAP-DLV-project-policy: 69045e11fa4d0e8998f0b1ac44a30b403ab93425
  CAP-DLV-workflow-envelopes: e65db42fb9d524cefed5d9d492025ef46a73443e
  CAP-INT-mcp-services: ef6ce6f9338b8d75e8cbd887f37932ecb58ac642
  CAP-MCP-runtime-registration: fa73a69e865c0b0e356d968a9d393df58e819942
  CAP-WT-task-worktrees: 2f5c45415f121e1d1d47046f255be4d4163e24dc
  UC-drive-development-to-integration: 2893591134de64be66238b4102062f02e0e370c8
title: Drive development to integration
---

# Drive development to integration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Assess a selected test suite](assess-test-management.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Discover and refine an idea](discover-and-refine-an-idea.md)
- [Execute an isolated command](execute-an-isolated-command.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](import-third-party-agent-assets.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Read decision supersession](read-decision-supersession.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Record a maintenance run](record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](snapshot-bundle-sources.md)
- [Speed up selected slow operations](speed-up-selected-slow-operations.md)
- [Advisories](../areas/advisory.md)
- [Agent-first CLI toolkit](../areas/cli.md)
- [Collaboration](../areas/collaboration.md)
- [Compact command output](../areas/compact.md)
- [Delivery](../areas/delivery.md)
- [Distribution](../areas/distribution.md)
- [Documents](../areas/documents.md)
- [Commit gates](../areas/gate.md)
- [Generated Files](../areas/generated.md)
- [Governance rules](../areas/governance.md)
- [Harness](../areas/harness.md)
- [Host](../areas/host.md)
- [Integration](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [Search](../areas/search.md)
- [Traceability](../areas/traceability.md)
- [Viewer](../areas/viewer.md)
- [Worktree](../areas/worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

After the intent is agreed, Development follows the branch's workflow through implementation, review,
Living Spec reflection and final reporting. The Host then authorizes Git integration and verifies the landed target.
See [Concepts](../concepts.md) for Units, gates and envelopes.

## 1. Follow the source workflow

```bash
uv run devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>
```

The agent states effort and follows the reported stages, checks and skills.
It writes the spec, plan and task boundaries before code, implements within them, runs the affected checks and
commits at stage boundaries. A bugfix records characterization, a reproduction (Red) and the fix (Green).
Screen drafts precede code, with an optional UX review; reconciliation retains them under `docs/ux/`.

## 2. Review, reconcile and report

Medium effort requires an initial independent code-reviewer. The implementer fixes findings and checks the fixes;
expanded scope or uncertain correctness can need another review. High uses bounded rounds; low allows self-review.
Close UX review findings at `build-verify`, including findings already fixed in drafts; this is a closure record
rather than another independent review round.

The implementer updates the Living Spec and resolves `reconcile.md`, with reconcile-check evidence at every effort.
An independent reconcile reviewer is required at high; medium can self-check only when all affected contracts
and diff agreement are clear and there is no cross-component interpretation. A closing reconcile check covers the
whole reflection, identifies the earlier check and marks each finding resolved or waived with a reason; required
contract mismatches cannot be waived.

Sweep feedback when the stage is enabled and write the final change report. Questions, problems, unresolved
reconciliation and incomplete checks remain visible. The Host checks the committed source with its own runtime;
integration does not evaluate these content conditions on its behalf.

## 3. Prepare and authorize

Save the premerge target SHA for final affected-test selection. From the retained base checkout:

```bash
uv run devkit integration prepare dev-<slug> --route local
```

The request pins source/target SHAs, policy, Git identities and exact cleanup effects.
Under `dev-integration=ask`, the Host presents the verified report and those effects for your conversational decision.
Under shared-base `auto`, verified local integration is delegated by policy.

```bash
uv run devkit integration integrate dev-<slug> --route local --expected-digest <digest>
```

A changed digest requires fresh preparation and authority. Local `no-ff` integration can merge a conflict-free
moved target itself. `ff-only` and PR routes still need the source to contain the target.
A content conflict returns to source preparation and the affected checks.

## 4. Land, synchronize and verify

Local integration constructs the result outside the target checkout, fast-forwards the base and performs the
scoped worktree/branch cleanup without fetch or push. `landed_sha` confirms landing;
`status=completed` describes Git effects and `verification=pending` leaves delivery verification to the Host.

Synchronize the landed dependencies, then use fresh processes for asset sync, generated checks and required
lint/type/rule/affected-test commands. Regenerate and commit stale artifacts before the final checks.
Compare affected tests with the saved premerge target, and report the final checked HEAD and actual outcomes.
A local-orchestrated batch can verify its combined target once after selected merges and repairs.
A failure keeps delivery pending while the target is repaired and checked again; there is no merge replay or automatic rollback.

## Variations

- **Session:** no Unit, envelope or reconcile record; report the change, effort, review and checks in conversation or
  the PR body. Integration still takes only the explicit source branch, not claims or task labels.
- **Local-orchestrated:** the Host inspects the worker's committed turn and cumulative rules, and can reuse
  git-operator for exact authorized lifecycle jobs while retaining decisions, semantic conflict handling and acceptance.
- **Required PR:** use `--route pull-request`; required platform checks/reviews and source pinning remain mandatory.
  A published but unmerged PR with pending checks needs fresh preparation and authority for the merge.
- **Generated conflict seeds:** `INTEGRATION_GENERATED_SEEDED` names seed/regeneration choices. The Host regenerates
  after synchronization; integration itself ran no generator.

## Recover from partial effects

Inspect Git/worktree/PR state before replaying an uncertain operation. A confirmed merge with remaining cleanup
uses guarded already-merged finish or the exact extension command; normal integration already includes cleanup.
`INTEGRATION_TARGET_MOVED` calls for fresh preparation; `INTEGRATION_REQUEST_STALE` means the presented scope changed.
An unanswered question or unresolved problem is handled through [Problems and exceptions](handle-delivery-problems-and-exceptions.md).
Full route and recovery details are in [Integration](../areas/integration.md).

## Sources

- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md)
- [CAP-DLV-workflow-envelopes](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md)
- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/mcp/CAP-MCP-runtime-registration.md)
- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md)
