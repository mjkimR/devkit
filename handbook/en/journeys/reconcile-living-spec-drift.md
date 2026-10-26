---
sources:
  CAP-DIST-context-and-playbooks: 34185acd0c3f1a6432909d7718d9b18f52eda6cf
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  UC-reconcile-living-spec-drift: 972538db7ca3eccccada61d606ed7a176a4effe0
title: Reconcile Living Spec drift
---

# Reconcile Living Spec drift

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
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

Structural checks tell you that every reference resolves and every entrypoint exists. They cannot tell you that a
capability still describes what the code does. When you suspect that kind of semantic drift, you run the
`drift-reconciliation` playbook: your agent reviews a bounded batch of contracts against the implementation and its
consumer guidance, shows you each mismatch with evidence, and changes only what you decide.

Structural consistency is the separate journey [Keep the Living Spec consistent](keep-the-living-spec-consistent.md).
Per-feature reconciliation during delivery is `spec-sync`; this playbook catches what accumulates between features.
See [Concepts](../concepts.md) for the Living Spec and playbooks.

Source: [`UC-reconcile-living-spec-drift`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-reconcile-living-spec-drift.md),
contract [`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md).

## Before you start

- The opt-in `maintenance` catalog bundle is selected (`uv run devkit add maintenance`, or `maintenance:upkeep` for
  the upkeep playbooks, this one and review-refactor) and synchronized.
- Know roughly what you want reviewed: some contract IDs or an area, and which implementation and guidance roots the
  agent may read.

## Step by step

1. **Invoke the playbook.** Run `/devkit-playbook` and pick `drift-reconciliation`, or confirm it when the `spec`
   skill offers it in one line for a request such as "reconcile the Living Spec with the code". Playbooks never run
   on ordinary wording alone; your confirmation is the explicit invocation
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md),
   [distribution area](../areas/distribution.md)).
2. **Intake.** The agent records the repository, `HEAD` and dirty paths, the selected contracts or area, the
   permitted roots, any prior reports and where the report goes. It then lists the candidates of one bounded batch.
3. **Comparison.** For each contract it compares the documented commands, options, interfaces, terms, behavior and
   paths with the code, tests and guidance at the recorded revision. Each confirmed mismatch becomes a finding with
   citations on both sides, expected and observed behavior, evidence, a `deterministic` or `semantic-assessment`
   classification and a proposed disposition.
4. **One decision round.** The agent shows you all findings together. For each one you choose: update the
   documentation or guidance, fix the code, defer, or waive. Your decision and its reason are recorded per finding.
5. **Corrections.** The agent applies only what you decided, through the normal development workflow and within its
   write scope (see [Route a development request](route-development-intent.md)).
6. **Verification.** A code fix needs regression evidence; a documentation correction is rechecked against the
   disputed claims, references and applicable checks.
7. **Report.** After rechecking `HEAD` and dirty paths, the agent completes the batch report: coverage, findings,
   decisions, corrections, counts (detected, resolved, deferred, waived, pending), verification and follow-ups. With
   no decision pending, the batch is reconciled.

The report is ordinary Markdown under the owning unit's `materials/`, or the repository's existing materials location.

## When it goes wrong

- **No scope given.** The agent asks you for contracts, an area and permitted roots before inspecting anything broad.
- **The area is too big.** It splits it into explicit batches and records which candidates were reviewed and which
  were excluded. Completion covers that batch only.
- **A tool, document, entrypoint or check is missing.** That is a coverage gap with a reason, never a finding and
  never "consistent". The agent installs nothing without asking. A suspicion without evidence is an investigation gap.
- **Nothing differs.** The report still names what was reviewed and its gaps; zero findings needs coverage evidence.
- **You defer or waive.** A deferral names its destination (an open feedback file or proposal the agent found first,
  or one you authorize) and a restart condition; a waiver records the intentional gap and its rationale.
- **You leave a finding unanswered.** It stays pending, gets no correction, and the batch is not claimed fully
  reconciled.
- **An earlier report covers the batch.** Findings link the earlier report keys, and earlier deferrals and waivers are
  rechecked.
- **`HEAD` or a relevant dirty path moved.** The agent revalidates the evidence and asks again if a correction's intent
  changes.
- **A correction falls outside the scope, or is structural cleanup.** It is tracked as separate work.
- **It is a seeded exercise.** Decisions are labeled simulated and no real source changes.

## What you end up with

A report you can audit: every finding with evidence and your decision, applied corrections with their verification,
and explicit gaps. The report authorizes nothing by itself, a passing check is never presented as semantic
consistency, and a batch is never presented as the whole repository.
