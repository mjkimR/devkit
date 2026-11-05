---
sources:
  CAP-HARN-command-design: 55dfa957b84301d7a9897676145bec7e2486e71f
  UC-design-command-entrypoints: cd63eca79110e8fd57295ae3cf5858cf789998fc
title: Design necessary command entry points
---

# Design necessary command entry points

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Explore a design problem](explore-a-design-problem.md)
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

The opt-in `command-design` bundle guides creation, configuration and extension of justfile recipes,
CLI commands and MCP tools. Select it with `uv run devkit add command-design`;
`uv run devkit get-context command-design` lists the instruction for relevant work.
It generates and registers no commands itself.

1. Identify the operation, its caller and the existing execution path.
2. Reuse that path if it already serves the need. Add a wrapper or alias only for useful composition,
   a required execution context or a distinct caller contract.
3. Preserve established recipe names, keep commit checks fast and explicit, and avoid duplicate hook checks.
   Choose MCP operations by caller need rather than mirroring the entire CLI.
4. Implement the necessary addition under the project's conventions and verify it from the documented directory
   with the required tools. Each addition has a concrete purpose.

Removing an existing public command is a separate compatibility decision. A task that does not use a command
is no reason to remove it, and hypothetical future tasks do not justify placeholder commands.
For Python CLI implementation, see [Agent-first CLI toolkit](../areas/cli.md).

## Sources

- [UC-design-command-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/harness/UC-design-command-entrypoints.md)
- [CAP-HARN-command-design](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-command-design.md)
