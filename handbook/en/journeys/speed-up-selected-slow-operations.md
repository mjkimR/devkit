---
sources:
  CAP-DIST-content-packages: 71d426703b854a24bdce4cd0c44b130ed8a106dc
  CAP-DIST-context-and-playbooks: 73e324739a17d8af4b885dce3d6cdf2593762fc0
  CAP-DLV-performance-pass: b37939e6d8e45835bae34bf596322b6bdc5d74b3
  UC-speed-up-selected-slow-operations: 894ab77ba693970784eb66025a03e2a4b955e452
title: Speed up selected slow operations
---

# Speed up selected slow operations

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](adopt-sdd-from-incubation.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
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

When a command feels slow, guessing at the cause and timing a single run tends to report savings that vanish on the
next try. The `performance-pass` playbook makes the work measurable: you pick the operations, your agent measures them
unprofiled and interleaved, uses a profiler only to find where the time goes, and applies only the speedups you agree
to, each committed with its before and after numbers and evidence that behavior did not change.

Source: [`UC-speed-up-selected-slow-operations`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-speed-up-selected-slow-operations.md),
contract [`CAP-DLV-performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-performance-pass.md),
playbook [`performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass/SKILL.md).
Maintenance cost is a different job: [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md),
whose application procedure this playbook reuses.

## Before you start

- The opt-in `maintenance` catalog bundle is selected with `all` (`uv run devkit add maintenance`) or
  `maintenance:performance`. Both also deploy `review-refactor`, which this playbook needs
  ([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md)).
- Know which operations matter: the exact command, its working directory and environment, and the metric (wall time,
  subprocess count or peak memory). A goal is optional.
- Keep the machine quiet while it measures. No timing script ships with the playbook; the agent uses an installed
  tool such as `hyperfine` or writes a short loop.

## Step by step

1. **Invoke.** Run `/devkit-playbook` and pick `performance-pass`, fetch it with
   `uv run devkit playbook get maintenance/performance-pass`, or confirm it when `/spec` offers it. It loads on demand
   and never runs because it is installed
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md)).
2. **Intake.** The agent records the run ID, repository, `HEAD`, dirty paths, earlier reports, the report destination
   and the environment (machine, operating system, runtime versions, current load). You name each target. The run is
   in `survey` mode (find and rank, apply nothing) or `targeted` mode (measure and apply what you approve).
3. **Baseline.** Each target is measured as the real process with its exact arguments: a warm-up run discarded, at
   least five interleaved repetitions, exit codes and output digests checked, and median, minimum and range
   reported, with warm or cold state labeled and the load recorded before and after.
4. **Attribute.** A profiler locates the cost but never reports a saving; each hotspot's share is confirmed
   unprofiled, subprocesses are counted and timed separately, and a composite target's parts are timed and checked
   against the total.
5. **Candidates.** Each candidate records its location, mechanism, measured share, proposed change, expected saving,
   risk, classification, planned comparison inputs, route and edited paths. One whose saving is below the noise floor
   is dropped and counted; removing repeated work (one scan instead of many, a memo within one run, fewer processes)
   is preferred over tuning a single call. The agent then fetches `review-refactor` by exact ID and reads its
   application and evidence sections as reference text, without starting that playbook.
6. **Decide in one round.** You see every candidate with its route and edited paths and choose: apply with behavior
   preserved; treat as a contract change; defer (with destination and restart condition); or keep (with a reason).
   Approving one in a `survey` run turns it `targeted`. Your approval is the work item's intent, not its integration
   approval.
7. **Apply.** The agreed changes form one work item through the repository's feature workflow at its own depth,
   whatever the number of modules (never the overall-refactor route). It follows `review-refactor`'s branch, edit,
   commit, review and report sections. Each change is measured old against new on the previous checkpoint, with the
   numbers in its commit body beside a differential comparison over the repository's corpus and error cases
   (unreadable entries, symbolic link loops, differently spelled paths, a vanished working directory). Old code runs
   from an extracted copy or a separate worktree; the working checkout is never stashed or switched. No timing runs
   while an edit task or verification is active.
8. **Review and final measurement.** A fresh reviewer, briefed with each change's classification, its claim of equal
   behavior, the error paths of replaced APIs and any cache or memo keys, looks for inputs that break it. Then every
   target is measured interleaved against the intake revision in one session.
9. **Report.** The run report records intake, mode, baselines, coverage, candidates and changes, decisions,
   follow-ups, the final measurement and the outcome (`stopped at decision round`, `applied` or `partially applied`)
   with the integration state, updated when the work item integrates or stops.

## What counts as behavior-preserving

A change preserves behavior only when stdout, stderr, exit codes, written files and their bytes, persisted formats,
error behavior and the order of observable side effects stay the same for every accepted input. A private cache
format qualifies when a version or fingerprint invalidates old entries and output matches with the cache off, cold
and warm; a memo within one run qualifies when its key covers every input that changes the answer and it never
memoizes a failure. Changed output, new state kept between runs, concurrency, changed defaults, accuracy or error
handling, and a removed option are contract changes: each becomes its own work item through the normal development
workflow.

## When it goes wrong

- **A target's command, metric or directory is missing.** The agent asks before any timed run.
- **The machine was busy**, or a run's own verification was active. The measurement is discarded and repeated later.
- **One outlier decides the result.** Five more repetitions per variant run before concluding; a median difference
  below the noise floor is reported as no measurable change.
- **A cited `review-refactor` heading is missing**, for example after an override renamed it. The run stops with a
  report naming the section and applies nothing.
- **Nobody answers**, the run is unattended, or a `survey` approves nothing. It stops at the decision round with
  nothing applied.
- **The host has no subagents.** Changes are applied one after another, and the diff review is a recorded self-review.
- **The comparison or the reviewer finds a difference.** The change is fixed or goes back to the decision round as a
  contract change; it is never kept as an approved difference inside this work item.
- **A change shows no measurable gain.** It returns to the decision round unless you approved it for another measured
  reason, such as fewer subprocesses or lower peak memory.
- **`HEAD` or a relevant dirty path moved since intake.** The baseline is re-run and evidence revalidated first.

## What you end up with

Every applied change was agreed, preserves behavior, and is committed alone with measured before and after and
differential evidence, reviewed and integrated under its own approval. Every reported saving comes from unprofiled,
interleaved runs in one session, ending with a final comparison against the intake revision. Invoking or measuring
alone changes nothing, and `review-refactor`'s own intake and decision rounds never start.
