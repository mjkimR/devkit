---
sources:
  CAP-DLV-maintenance-history: ada7d8b89abb17dd3b396263b9b4aac18b2752e5
  UC-record-a-maintenance-run: 5721c55babd6970377eb6af4cfdaca70a1d4345f
title: Record a maintenance run
---

# Record a maintenance run

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

Maintenance history is an explicitly requested companion to a maintenance playbook.
Installing the commands or invoking a playbook alone starts no capture or recurring offer.
The default playbook report and completion procedure stay independent.

## Capture and freeze

Fix the maintenance scope, report path and local run directory, then use the command family:

```text
uv run devkit maintenance history start --playbook <playbook> --scope <scope> --into <run-dir> --report <report>
uv run devkit maintenance history finish --run <run-dir> --outcome completed
```

Start records HEAD, dirty paths, an inspected content tree and a dirty-diff digest while preserving the real index,
refs and working files outside the run directory. Write and verify the report, register additional evidence with
`finish --file <path>`, then freeze the checked bytes. Recognized secrets refuse completion with `HISTORY_SECRET_FOUND`.
`HISTORY_RUN_DRIFTED` asks for evidence revalidation when inspected content changed.

## Publish separately

Choose and authorize a credential-free repository and dedicated history branch. Destination configuration supplies
inputs only; `init`, `publish` and `update` each require explicit `--authority`.
`uv run devkit maintenance history publish --run <run-dir> --authority <authority>` publishes the record and report.
Select additional previously frozen evidence with repeated `--file` options.

Publication exposes the selected files, canonical record and year-index entry atomically through a non-forced ref
update. An absent branch needs separately authorized initialization. A foreign branch root is refused.
If a response is lost, inspect through the same operation with the original bytes; a matching remote record resolves
the original publication without resending. Changed frozen evidence needs a new run.

Run outcome (completed, failed, interrupted) and publication state (pending, published, failed, unknown) remain
separate. Later integration changes use an authorized `update --integration-state <state>` amendment;
published evidence is never rewritten. See [Find the latest maintenance run](find-the-latest-maintenance-run.md).

## Sources

- [UC-record-a-maintenance-run](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-record-a-maintenance-run.md)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md)
