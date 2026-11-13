---
sources:
  CAP-DLV-deep-research: c5d9044c1841d7ccb10a5578a562e79ee134ae8e
  CAP-HARN-agent-guidance: dff559b3349a28515857465630025e54b334b414
  UC-research-an-idea-and-shape-a-roadmap: 3744a97ed5ecfa404e7127489576ca54dc43223c
title: Research an idea and shape a roadmap
---

# Research an idea and shape a roadmap

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
- [Drive development to integration](drive-development-to-integration.md)
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

With the opt-in `deep-research` bundle selected, explicitly invoke `/deep-research <question or decision>`.
The entry works under either development approach without inspecting or changing that approach.
It produces sourced research, not an implementation or a delivery commitment.

## From question to retained evidence

1. Supply the requested artifact, intended use, constraints and a useful investigation bound.
2. The coordinator recovers supplied facts, frames the decision and selects useful independent questions.
   Small questions can stay inline. Optional roles investigate sources, explore directions, critique support or draft a synthesis.
3. The coordinator checks actual returns and reopens sources for consequential gaps or contradictions.
   Alternatives keep distinct premises; observations, inference, assumptions and unknowns remain separate.
4. Useful synthesis and stable supporting evidence enter one indexed material under
   `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`, with `id: MAT-<slug>` and `Status: complete` or `partial`.
5. The result names the material, evidence limits and next decision. Commit it under the project's Git policy
   before later proposals, specs, decisions or adaptive current context cite its ID.

Scratch stays under `.devkit/transient/deep-research/`; retained links do not depend on that transient directory.
The coordinator alone writes the retained material. The research entry stages, commits and publishes nothing,
creates no SDD Unit or envelope, and does not edit `.devkit/adaptive-dev.md`.

## Resume and limits

A material ID or destination collision selects another slug. A named `partial` material of the same investigation
can be updated; a complete material stays unchanged and later research cites it from a new material.
Earlier runs are read only when you name them as inputs.

Ordinary failed public retrieval can use a bounded retry or another accessible primary source, recording the
replacement actually inspected. An access refusal stops access to that resource. Missing evidence stays unverified.
A partial result remains useful without inventing a winner or requiring a comparison you declined.
Implementation informed by the result starts later through the project's ordinary development process.

## Optional cloud research

When useful, the coordinator can prepare a bounded safe request for a user-operated cloud research application. It records awaiting user result, never claims a provider task ran, and does not poll or infer progress from elapsed time. Actual returns are associated with their investigation and reviewed as evidence, not instructions. Missing or unreadable reports leave the material partial with a resumable collection action.

## Sources

- [UC-research-an-idea-and-shape-a-roadmap](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md)
- [CAP-DLV-deep-research](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-deep-research.md)
- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md)
