---
sources:
  CAP-DLV-uiux-improvement: 7c2ea122d1db7d44dbb2ba890bd576beba070943
  UC-improve-an-interface-and-user-flow: d890a54fdf4c3bf947315a371672d9dac286cbb3
title: Improve an interface and user flow
---

# Improve an interface and user flow

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `f115e96c8059`, generated 2026-11-11. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Assess a selected test suite](assess-test-management.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Execute an isolated command](execute-an-isolated-command.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](import-third-party-agent-assets.md)
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

With the opt-in `app-uiux-improve` bundle selected, explicitly invoke `/app-uiux-improve <goal>` and supply the interface,
user task and constraints. An improvement request can carry requested implementation through the consumer's
existing workflow. A review-only request returns findings without product edits.

1. Inspect the representative task path, relevant artifacts and affected interface states.
2. Keep small requests inline or select useful designer, unconventional-designer, reference-researcher or critic
   perspectives. Fresh independent first passes are used where supported; missing support is disclosed.
3. Synthesize a coherent flow and visual direction, with consequential tradeoffs and missing product decisions.
4. Apply requested changes under the project's delivery, permission and approval rules.
   A scope decision outside current authority waits for your answer.
5. Check the changed interface and representative interactions, repair defects within scope and repeat affected checks.
6. Report what changed, actual verification and material limits.

Screenshot, source and text inspection are useful evidence when a running interface is unavailable;
they are not actual interaction verification. Missing tools or approvals leave useful partial work with a concrete blocker.
The optional roles return suggestions and evidence without editing retained files, index or HEAD.
No fixed team, scoring, debate rounds, persistent memory or companion invocation is required.

## Sources

- [UC-improve-an-interface-and-user-flow](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md)

## Object framing and optional Impeccable work

The entry is `/app-uiux-improve` from `app-uiux-improve`. For structure or flow changes, read the project's OOUX objects first. A user-selected Impeccable session receives one bounded brief while the coordinator pauses its product edits. Accept only its listed product-file changes; report unrelated changes without reverting or deleting them automatically. Consumer-owned context files stay in place. Stale OOUX documents are named for the consumer workflow to update.
