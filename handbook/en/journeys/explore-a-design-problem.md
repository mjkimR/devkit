---
sources:
  CAP-DLV-design-exploration: 4fad9083aa058047d39e6956ff63b76f8232bd10
  UC-explore-a-design-problem: 747823775aad4b217b5b68d57c2d172e3bdd7f3e
title: Explore a design problem
---

# Explore a design problem

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Record a maintenance run](record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
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

Select the opt-in `design-explore` bundle, then explicitly invoke `/design-explore <problem>` for architecture,
data models, module boundaries or a processing/development workflow.
The outcome is a useful choice of mechanisms with benefits, tradeoffs and uncertainty.

1. Give the goal, existing design, hard constraints and open preferences.
2. The coordinator chooses distinct premises and evidence questions. A small problem stays inline;
   otherwise optional solution-explorer, reference-researcher and design-critic perspectives can help.
3. Independent first passes withhold peer conclusions where fresh children are supported.
   Without that support, the result discloses shared context and missing coverage.
4. The synthesis preserves useful differences and unconventional mechanisms rather than averaging them away.
   Criticism has evidence and failure conditions; zero findings is valid and one useful refinement is normally enough.
5. You receive directions and a justified recommendation in conversation. Only an explicitly requested destination
   authorizes the coordinator to retain the result in that destination's existing format.

There is no required cast, candidate count, score, prototype or proof-of-benefit experiment.
Roles leave product source, retained files, settings, index and HEAD unchanged.
Invocation authorizes no implementation, settings change, commit, approval or publication.
A refused destination stays blocked while the useful conversation result remains available.

## Sources

- [UC-explore-a-design-problem](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-explore-a-design-problem.md)
- [CAP-DLV-design-exploration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-design-exploration.md)
