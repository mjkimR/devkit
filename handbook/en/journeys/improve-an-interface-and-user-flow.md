---
sources:
  CAP-DLV-uiux-improvement: 3f9f57ce40b41250bb87cc933295e5d0cb751cd4
  UC-improve-an-interface-and-user-flow: 148f4ac0d519887b7fc43f8a49390f6f26052459
title: Improve an interface and user flow
---

# Improve an interface and user flow

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

Explicitly invoke `/app-uiux-improve <goal>` with the interface, representative task and constraints. Review-only work returns findings without edits. Before implementation, choose the announced outside-workflow procedure or the consumer workflow; the latter keeps its required steps and reviews. Product constraints, host permissions and applicable checks remain effective on either route. Route choice supplies no separate Git authority.

1. Inspect the actual target and executable local branch before edits. Read relevant OOUX documents for structure or flow changes. A negative visual detector result does not prove the interface is absent.
2. Choose useful design perspectives and synthesize a direction. A focus orders work; only explicit constraints or deferrals become non-goals.
3. Apply the approved goal and verify the branch with the same representative task/data and a repeatable capture method. Label mock coverage and missing live coverage. Color changes include computed effective-color contrast ratios for key pairs and states.
4. Report accepted changes, checks, limits, stale document statements and their separate follow-up, plus any remaining Git effects needing authority.

## Optional Impeccable session

When you select an Impeccable session, it receives a bounded brief while the coordinator pauses product edits. Refinement that needs no Q&A can run in a fresh child agent that loads the skill natively. Interactive relay requires observed native skill loading and continuation in the same child agent; `shape` and `critique` also require their nested roles. The first phase reads the target and prepares the full question packet without editing files. All answers—including suggestions backed by repository sources—wait for your confirmation before that same child agent makes edits. If required capabilities are missing, continuation in the same child is lost, or a required autonomy probe is unavailable, stop dependent work and switch to a user-operated session or an authorized inline route without claiming the probe ran.

Accept only listed edits that stay within the approved goal, and report any other changes instead of reverting or deleting them unasked. Read local-only context by absolute path without assuming permission to copy, commit or remove it. Editing `PRODUCT.md` or `DESIGN.md` requires explicit permission for the file and action. If the supported upstream Impeccable capability provides no audit persistence operation, return the findings in the report and disclose that persistence is unavailable.

## Context links

On requested setup, `sh <installed-skill>/scripts/link-impeccable-context.sh` links root context to `docs/materials/impeccable` in the current worktree. Show `/PRODUCT.md`, `/DESIGN.md` and `/.impeccable` before adding these local Git excludes. `--check` inspects drift without writes. Preserve tracked roots and occupied or replaced entries; merge differing content only on your direction.

## Sources

- [UC-improve-an-interface-and-user-flow](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md)
