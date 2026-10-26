---
sources:
  CAP-DIST-content-packages: dcd5bdbf45e7fbe1e26f52118902c300bbf646e6
  CAP-DIST-context-and-playbooks: 34185acd0c3f1a6432909d7718d9b18f52eda6cf
  CAP-DLV-delivery-workflows: e1366a8cbed7bace6c51651085abc7d50b588768
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  CAP-DLV-review-refactor: 4c9e10968504b3edfdd77c6698275db599416bfd
  UC-review-and-refactor-accumulated-slop: 99e3929f75bacf6df151e9a3cc803b8c46bc5867
title: Review and refactor accumulated slop
---

# Review and refactor accumulated slop

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `c94b6a08710e`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
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
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
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

Agents add code readily and remove it rarely. Over many features that leaves duplicated logic, helpers with one
caller, compatibility shims nobody needs, guidance repeated across skills and CLI options that overlap. Each piece
works; together they make every later change cost more. The `review-refactor` playbook is how you pay that down: your
agent reviews the code, guidance or CLI surfaces you select, shows you each finding with the maintenance cost it
causes, and applies only the consolidations and reductions you agree to, each with evidence that behavior is kept.

The goal is a smaller surface, not a list of problems. A mismatch between code and its contract is a different job:
the agent records it as a deferred finding for [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
(`CAP-DLV-drift-reconciliation`) and never starts that playbook itself. See [Concepts](../concepts.md) for playbooks
and workflows.

Source: [`UC-review-and-refactor-accumulated-slop`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md),
contract [`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-review-refactor.md),
playbook [`review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md).

## Before you start

- The opt-in `maintenance` catalog bundle is selected and synchronized: `uv run devkit add maintenance` (all three
  playbooks), `maintenance:upkeep` (with drift reconciliation) or `maintenance:refactoring` (this playbook alone)
  ([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-content-packages.md)).
- Good moments are before a release, after a stretch of feature growth, or whenever a part of the repository feels
  heavier than it should.
- Decide which surfaces (`code`, `guidance`, `cli`) and which roots of each you want reviewed. You will be asked.
- Commit or stash unrelated work first: the agent stops rather than touch changes that are not part of the run.

## Step by step

1. **Invoke the playbook.** Run `/devkit-playbook` and pick `review-refactor`, fetch it with
   `uv run devkit playbook get maintenance/review-refactor`, or confirm it when `/spec` offers it. It loads on demand
   and never runs because it is installed or because your wording sounds similar
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md)).
2. **Intake.** The agent records a run ID, the repository, `HEAD`, dirty paths, earlier reports and where the report
   goes. You name the surfaces and roots, and the run is split into one batch per surface.
3. **Review one batch.** The agent inventories the roots and asks each surface's review questions: duplicated
   behavior, repeated technical helpers, abstractions with one caller, speculative compatibility and unused code;
   derivable, duplicated or conflicting guidance; overlapping, unneeded or fragmented commands and inaccurate help.
   Detector output is a candidate only, and nothing is installed without asking. Where the host supports subagents,
   the review can be split across them, but the agent checks every claim at its cited location and re-runs their
   commands before using it.
4. **Record findings.** Each finding names its location, the question it answers, the maintenance cost (what a future
   change has to repeat, read or keep consistent), a proposed disposition and the evidence. A candidate with no named
   cost is dropped and counted; "an agent wrote it" or a line count is never a finding by itself.
5. **Decide in one round.** The agent presents the whole batch together, with the route, edited paths and write scope
   of each proposed change. For each finding you choose: consolidate, reduce or remove with behavior preserved; treat
   it as a contract change; defer it (with a destination and restart condition); or keep it (with a reason). Your
   approval is the intent of the resulting work item, not its integration approval.
6. **Apply.** The agreed behavior-preserving changes become one work item on its own branch. Across several modules
   it follows `sdd-overall-refactor` in direct mode, with no Unit or workers; inside one feature or module it follows
   that feature workflow at its own depth
   ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md),
   [delivery area](../areas/delivery.md)). Each change is verified before and after on the previous checkpoint,
   committed alone with its reachability evidence, and the final head passes the full verification on a clean tree.
7. **Review and integrate.** A fresh reviewer (or a recorded self-review) checks the work item's diff, the agent
   fixes the findings and reports every breaking change, and the work item integrates through the repository's
   integration path once you approve it.
8. **Report.** The agent completes the run report: coverage per batch, findings and changes as separate records,
   decisions, follow-ups and counts (found, applied, contract work items, deferred, kept, pending). With no decision
   pending, the batch is complete.

## What a change has to show

- **A ground for every reduction**: the content is derivable, duplicated with a named canonical copy, enforced by a
  check elsewhere, or shown unnecessary by a recorded check. A line or token delta is reported, never the reason.
- **Two real callers** before anything is consolidated into a shared implementation.
- **Reachability**: static references and dynamic reach (entry points, registries, configuration, string dispatch),
  each search named with its result. A characterization test is added only when a merged caller has no test.
- **For guidance**, a map of each constraint in the removed text and where it still lives.
- **Placement** at the lowest common owner under the declared layering; a new cross-package or foundation module is
  your decision in the round.

## When it goes wrong

- **No surfaces or roots given.** The agent asks first and inspects nothing until they are recorded.
- **The host has no subagents.** The agent runs the same review, and later the diff review, itself; the latter is
  recorded as a self-review.
- **A subagent claim does not hold**, for example an "unused" function a registry still references. It is dropped or
  recorded as a coverage gap and never reaches the decision round.
- **A finding lands on a surface you did not select.** It is deferred with a follow-up. If you add that surface, it
  gets its own batch, roots and decision round, recorded in the report.
- **Nobody answers**, or an external runner started the run. It stops at the decision round with outcome
  `stopped at decision round`; nothing is applied and only the report changes.
- **You approve removing a command, option or public interface.** That is a contract change: it becomes its own work
  item through the normal development workflow with contract and documentation updates, outside the refactor work
  item. A compatibility path the declared policy says has no external consumer can stay in the batch, with the
  inputs no longer accepted named.
- **A subagent edit leaves its assigned scope or departs from the agreed change.** The agent reverts those hunks
  without touching other scopes, then redoes the change or brings it back to the decision round.
- **`HEAD` or a relevant dirty path moved since intake.** The evidence is revalidated; a change whose intent shifts
  goes back to the decision round.
- **Receipt-owned files are involved** (`.devkit/managed/`, agent projections). They are never edited; the change goes
  to the source bundle, an upstream follow-up or `devkit override`.
- **It is a seeded exercise.** Decisions are labeled simulated and only the fixture changes.

## What you end up with

A smaller surface where every applied change was agreed, committed alone with its evidence, reviewed and integrated
under its own approval, and a report that keeps findings apart from changes and names its coverage, gaps and
follow-ups. Invoking the playbook alone changes nothing, no contract change is passed off as refactoring, and a
batch never claims the whole repository reviewed.
