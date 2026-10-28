---
id: CAP-DLV-performance-pass
title: Performance Pass
summary: "An invoked or confirmed maintenance playbook measures user-selected slow operations unprofiled and interleaved, and applies only agreed behavior-preserving speedups with measured and differential evidence through review-refactor's application procedure; contract changes are separate work items."
area: delivery
status: active
usecases:
  - UC-speed-up-selected-slow-operations
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass/SKILL.md
created_at: 2026-10-28
---

# [CAP-DLV-performance-pass] Performance Pass

## 1. Summary

The opt-in `maintenance` catalog bundle supplies the `performance-pass` playbook beside `review-refactor`
(`CAP-DIST-content-packages`, `ADR-keep-performance-passes-in-a-separate-maintenance-playbook`). It is a
directory-form asset: `SKILL.md` holds the entry condition, intake, modes, the resolution of `review-refactor`, the
decision round, the report and completion; `references/measurement.md`, `references/profiling.md`,
`references/candidates.md` and `references/changes.md` hold the phases only some runs need, each read when its phase
starts. Explicit invocation through `devkit-playbook`, exact `devkit playbook get maintenance/performance-pass` or the
user's confirmation of a `spec` intake offer loads it on demand (`CAP-DIST-context-and-playbooks`). Its goal is the
latency, subprocess count or peak memory of operations the user selects; maintenance cost belongs to
`CAP-DLV-review-refactor`, whose application and evidence procedure it reuses by reference.

## 2. Scope & Boundary

- **In scope**: measurement of user-selected operations, attribution of their cost, ranked candidates with measured
  shares and expected savings, classification of each candidate by observable behavior, and application of agreed
  behavior-preserving changes with per-change measurement, differential evidence and a fresh review.
- **Out of scope**:
  - a regression-investigation mode or bisection, added when a real regression run shows the need
    (`SPEC-performance-pass`);
  - a bundled timing script; the run uses an installed benchmark tool or the agent's own loop
    (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`);
  - a scheduler or trigger (external runners, `ADR-external-playbook-execution`) and a history store
    (`PROP-maintenance-history`);
  - the direct-mode overall-refactor route, which stays granted to `CAP-DLV-review-refactor` runs only;
  - a contract-changing speedup inside the behavior-preserving work item; it is its own work item through the
    repository's normal development workflow (`ADR-classify-performance-changes-by-observable-behavior`).

## 3. Run Contract

1. **Entry**: the playbook MUST run only when the user invoked or confirmed it; invocation, an external runner naming
   it and a clean measurement MUST NOT authorize a change, and IF the run is unattended, THEN it MUST stop at the
   decision round with nothing applied.
2. **Intake**: the playbook MUST record the run ID, a credential-free repository identity, HEAD, dirty paths, prior
   reports, the report destination and the environment (machine, operating system, runtime versions and the load at
   intake).
3. **Target selection**: each target MUST name an operation as an exact argument list with its working directory and
   environment, its metric (wall time, subprocess count or peak memory) and an optional goal; IF scope is missing,
   THEN the playbook MUST clarify it before any timed run.
4. **Modes**: the run MUST take one of two modes. In `survey` mode the run MUST end at the decision round with
   nothing applied; WHEN that round approves a change, the run MUST turn `targeted`, recorded in the report. In
   `targeted` mode the run MUST read every reference in phase order, each on its read condition, and end with a
   measured before and after per change. A `survey` run that applied nothing is complete with its decisions recorded
   and outcome `stopped at decision round`.
5. **Resolving `review-refactor`**: before the decision round, the playbook's agent MUST run
   `devkit playbook get maintenance/review-refactor` and read each cited file next to the returned `source.path`;
   WHERE that path is an override directory without the file, the agent MUST read the same relative path under the
   bundle's managed directory (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`).
   - **Reference reading**: reading that text MUST NOT start any of `review-refactor`'s intake, batches or decision
     rounds (`CAP-DIST-context-and-playbooks`).
   - **Citation form**: each citation MUST name the file and the heading text without its number, for example
     `review-refactor references/applying.md "Commits and verification"`; the `devkit-catalog` bundle test checks
     that each cited heading exists.
   - **Missing heading**: IF a cited heading is missing from the resolved file, THEN the run MUST stop with a report
     naming the missing section and MUST NOT improvise a procedure.
6. **Dispositions**: each candidate MUST receive one of apply with behavior preserved; contract change; defer
   (destination and restart condition); keep (reason). All candidates of the run MUST be decided in one decision
   round, and unanswered candidates MUST stay pending.
7. **Approval**: the decision-round approval MUST supply the routed work item's intent and MUST NOT supply its
   integration approval; invocation and a clean measurement MUST NOT authorize a change.
8. **Following edits**: the playbook's agent MUST NOT edit receipt-owned files, MUST record a correctness defect
   found on the way as a follow-up, and MUST NOT stash.
9. **Revalidation**: IF HEAD or a relevant dirty path moved since intake before agreed changes are applied, THEN the
   agent MUST re-run the baseline and revalidate the evidence first, and a change whose intent shifted MUST return to
   the decision round.

## 4. Measurement Contract

`ADR-measure-performance-unprofiled-and-interleaved-in-one-session` governs every timed run; `references/measurement.md`
states the procedure.

1. **No bundled script**: the playbook MUST ship no timing script; the agent SHOULD use an installed benchmark tool
   (for example `hyperfine`) and otherwise write a short loop.
2. **Loop requirements**: either way, the timing loop MUST run variants as argument lists, discard a warm-up run, run
   at least five interleaved repetitions per variant, check each run's exit code, compare its output digest against
   the other runs of the same variant and report median, minimum and range.
3. **Real process**: the agent MUST time the real process from outside with the target's exact argument list,
   working directory and environment, and MUST drop failed runs.
4. **Same input**: old and new MUST run against the same input and working directory, the old code by a runtime path
   override to an extracted copy or from a separate worktree prepared with the repository's documented setup; the
   agent MUST NOT stash or switch the working checkout.
5. **Run states**: each measurement MUST label its state, warm or cold; the first run after a code or cache-format
   change MUST count as a warm-up, and WHERE the operation keeps a persistent cache, both states MUST be measured.
6. **Noise floor**: the noise floor MUST be the larger of the two variants' ranges after dropping each variant's
   slowest run, and for a single variant (a baseline before any change) that variant's range after dropping its
   slowest run; a median difference below it MUST be reported as no measurable change, and IF one outlier decides,
   THEN five more repetitions per variant MUST run before concluding.
7. **Quiet machine**: WHILE an edit task, verification or other workload of the run is active, the agent MUST NOT
   take a timed run; it MUST record the load before and after each measurement, baselines included.
8. **Composite operations**: WHERE a target is composite, its components MUST be timed unprofiled and their sum
   checked against the total before ranking.
9. **Attribution**: profiling MUST only attribute cost and MUST NOT report a saving; a hotspot's share MUST be
   confirmed unprofiled before it becomes a candidate, and subprocesses MUST be counted and timed separately. WHERE a
   hotspot builds large object graphs, collector time and object counts SHOULD be measured; cold and warm runs SHOULD
   be profiled separately, and startup and import time SHOULD be measured on their own.
10. **Baseline record**: each baseline MUST record revision, environment, exact command, state, run count, median,
    minimum, range and the load before and after; every comparison, the final one included, MUST re-run the older revision in the same session,
    and numbers recorded in another session MUST count as context only.

## 5. Change Contract

1. **Candidates**: each candidate MUST record location, the mechanism of the cost, its measured share unprofiled,
   the proposed change, an expected saving derived from the share, risk, classification, planned differential inputs,
   route and edited paths. IF the expected saving is below the noise floor, THEN the candidate MUST be dropped and
   counted in the coverage; a measured cost no change can remove MUST be reported as kept with its reason. A
   candidate that removes repeated work (one scan instead of many, a memo within one run, fewer processes) SHOULD be
   preferred over micro-optimization of a single call.
2. **Behavior-preserving**: a change MUST count as behavior-preserving only when stdout, stderr, exit codes, written
   files and their bytes, persisted formats, error behavior and the order of observable side effects stay the same
   for every accepted input (`ADR-classify-performance-changes-by-observable-behavior`).
   - A private cache format change qualifies when a version or fingerprint invalidates old entries and outputs are
     identical with the cache off, cold and warm.
   - A memo within one run qualifies when its key covers every input that changes the answer and it never memoizes a
     failure.
3. **Contract change**: changed output, new state kept between runs, concurrency or parallelism, changed defaults,
   accuracy or error handling, and a removed option MUST each be classified as a contract change and MUST be its own
   work item through the repository's normal development workflow.
4. **Route**: the run's agreed behavior-preserving changes MUST form one work item that follows the repository's
   feature workflow at the depth its own classification gives (with `spec`, `session` when no contract or
   specification text changes), whether it edits one module or several; the decision round MUST state the route and
   the edited paths, which are the work item's write scope. `review-refactor`'s "Work items and route" MUST NOT be
   followed.
5. **Application**: the work item MUST follow the cited `review-refactor` sections: from `references/applying.md`,
   "Branch and edit tasks", "Subagent edits", "Commits and verification", "Review", "Report", "Integration" and
   "Contract removals"; from `references/criteria.md`, "Preservation evidence" with its differential comparison
   (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`).
   - **Branch and integration**: the work item's branch and integration path MUST be those of the feature workflow it
     was routed to, whatever the number of modules it edits; text of the cited sections naming the overall-refactor
     workflow's branch policy or integration path MUST NOT apply.
   - **Removals**: an approved removal of an option MUST be its own contract-change work item;
     `review-refactor`'s compatibility-policy exception MUST NOT apply.
6. **Found differences**: IF the differential comparison or the review finds any difference, THEN the agent MUST fix
   it or return the change to the decision round as its own contract-change work item; `review-refactor`'s approved
   behavior change inside the behavior-preserving work item MUST NOT apply.
7. **Parallel edits**: WHERE edit tasks run in parallel isolated checkouts, every timing run MUST wait until no edit
   task or verification runs.
8. **Per-change measurement**: each change MUST be measured by the measurement contract, old and new on the previous
   checkpoint, with the statistics recorded in its commit body beside the preservation evidence. IF a change shows no
   measurable change, THEN it MUST return to the decision round unless the user approved it for another measured
   reason (fewer subprocesses, lower peak memory).
9. **Differential inputs**: the differential inputs MUST include the input domain's error cases and unusual states
   (unreadable entries, symbolic link loops, differently spelled paths, a vanished working directory) besides the
   repository's corpus.
10. **Reviewer brief**: the fresh reviewer's brief MUST add each change's classification and claim of equal behavior,
    the error paths of replaced APIs, and cache invalidation and memo keys.
11. **Final measurement**: at the work item's final head, every target MUST be measured interleaved against the
    intake revision in one session.

## 6. Report Interface

The report is an ordinary local Markdown file under the owning unit's materials or the repository's materials
location. It records intake and environment, mode, targets and the baseline record per target; coverage (operations
measured, components attributed, candidates dropped below the noise floor, gaps); candidates and changes as separate
records, each change with its candidate, classification, differential inputs and count, verification, measured
before and after and commit; decisions with provenance, follow-ups, counts and the final interleaved measurement
against the intake revision; and the outcome (`stopped at decision round`, `applied` or `partially applied`) with the
work items' integration state; a report written before a work item integrates MUST have its outcome updated when
that work item integrates or stops. A run is complete when no decision is pending, every agreed change is committed or
routed and the final measurement is recorded; a `survey` run that applied nothing is complete with its decisions
recorded and outcome `stopped at decision round`.
