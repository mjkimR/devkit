---
sources:
  CAP-DLV-maintenance-history: b1e327e613097e1cc9b843934824a35b5f174e6c
  UC-find-the-latest-maintenance-run: 9e1fb97dadca64caa06a7a0a75c9e74f80495f1a
title: Find the latest maintenance run
---

# Find the latest maintenance run

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

Use maintenance history when you need an earlier published report or its later integration outcome.
Know the playbook and repository identity before selecting the evidence.

```bash
uv run devkit maintenance history list --playbook <playbook> --limit 20
uv run devkit maintenance history get --run-id <run-id> --file report.md
```

List reads newest year shards first, merges the latest amendments and omits superseded runs by default.
Narrow by `--source-sha` or `--outcome`, or include older replaced runs with `--include-superseded`.
The listed source SHA is the HEAD inspected at intake; `inspected_tree` additionally identifies dirty content.

Choose a run and file; get defaults to `record.json`. `HISTORY_FILE` returns base64 content so arbitrary bytes
are preserved. Retrieval fetches no local Git refs and changes no checkout or evidence.

An absent history branch yields an empty list with a notice. A missing run/file is `HISTORY_RUN_MISSING`.
Rate limiting returns `HISTORY_DEFERRED` with `retry_after`; retry later.
Missing history is no claim that an earlier maintenance run succeeded or that the repository is clean.
See [Record a maintenance run](record-a-maintenance-run.md) for capture and publication.

## Sources

- [UC-find-the-latest-maintenance-run](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-find-the-latest-maintenance-run.md)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md)
