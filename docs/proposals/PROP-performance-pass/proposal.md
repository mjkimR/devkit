---
id: PROP-performance-pass
title: Performance pass maintenance playbook
summary: Add a maintenance playbook that measures, profiles and applies behavior-preserving performance changes to user-selected commands with differential preservation evidence, separate from review-refactor.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-27
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-operations
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/README.md
    - docs/capabilities/delivery/
    - docs/capabilities/distribution/
    - docs/usecases/governance/
    - guides/install/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-performance-pass] Performance pass maintenance playbook

## 1. Background & Hypothesis

A performance pass over this repository on 2026-10-27 (rules check 3.0s to 1.7s, a one-file commit-gate check 0.92s
to 0.38s, `sync --dry-run` 1.25s to 1.14s) borrowed the `maintenance/review-refactor` procedure, but its goal is
latency, not a smaller surface, and it needed steps that playbook does not have: a measured baseline, profiling
without being misled by profiler inflation or child processes, per-component timing, and differential old/new
comparisons as preservation evidence. A fresh review still found a regression (a symlink loop breaking every file
listing) that tests missed (`materials/pass-evidence.md`).

Hypothesis: a separate, router-structured maintenance playbook that turns a user-selected set of slow operations into
measured, behavior-preserving changes with differential evidence makes such passes repeatable in any repository and
keeps `review-refactor` focused on maintenance cost.

## 2. Technical Spike Questions

- **Q1**: Which entry modes does the router need (a measurement-only survey, a targeted pass on named commands or
  checks, a regression investigation), and what does each load?
  - Answer: three modes (`materials/design-options.md` O1). `survey` loads measurement and profiling and stops at the
    decision round with nothing applied; `targeted` loads every reference in phase order; `regression` loads
    measurement (two-revision comparison and bisection) and profiling, then candidates and application only when a
    fix is agreed. Mode table in §3.
- **Q2**: What measurement protocol is portable: warm-up, repetitions and the statistic reported, cold versus warm
  caches, machine noise and concurrent load, and how a baseline is recorded so a later run can compare?
  - Answer: unprofiled real-process timing, variants interleaved in one session, at least one warm-up and five
    repetitions, median, minimum and range, cold and warm labeled, the old revision run side by side from an
    extracted copy (`PADR-measure-performance-unprofiled-and-interleaved-in-one-session`). A recorded baseline names
    revision, environment, command, state and statistics; a later run re-measures it instead of comparing across
    sessions. Evidence: `materials/pass-evidence.md` §3.
- **Q3**: How does profiling guidance stay language-neutral while naming the known traps (deterministic profiler
  inflation, work in child processes, garbage collection and allocation, caches rebuilt on the first run)?
  - Answer: the reference states each trap as a property of a profiler class (deterministic or sampling, in-process
    or system-wide) with the check that exposes it, and names tools only as examples ("for example `cProfile`,
    `py-spy`, `perf`"); the agent installs nothing without asking. Evidence: `materials/pass-evidence.md` §3.
- **Q4**: What does a decision round show (each candidate with its measured share, expected saving and risk), and
  which changes count as behavior-preserving versus contract changes (output, caching across runs, concurrency)?
  - Answer: §3 "Candidates and decision round" and
    `PADR-classify-performance-changes-by-observable-behavior`.
- **Q5**: Which parts are shared with `review-refactor` (parallel application in isolated checkouts, differential
  comparison, adversarial review, report) and how are they referenced rather than copied?
  - Answer: application, verification, differential comparison, review, report and integration are read from
    `review-refactor` through exact playbook retrieval and cited by heading, with co-deployment and a heading test
    (`PADR-reuse-review-refactor-application-through-exact-playbook-retrieval`). Measurement, attribution, candidate
    criteria, the reviewer brief additions and the report's performance fields stay in `performance-pass`.

## 3. Proposed Design & Impact

### Asset, packaging and authoring

- `performance-pass` is a directory-form playbook asset of the `maintenance` catalog bundle beside `review-refactor`
  (`PADR-keep-performance-passes-in-a-separate-maintenance-playbook`), authored with the `skill-authoring` playbook.
- Presets (`materials/design-options.md` O5): the implicit `all` includes it; a new preset `performance` deploys
  `performance-pass` and `review-refactor`; `upkeep` and `refactoring` are unchanged. Every preset that deploys
  `performance-pass` deploys `review-refactor`.
- Its `description` names one operation (a performance pass that measures user-selected slow operations and applies
  behavior-preserving speedups with measured and differential evidence) and its scope, so intake discovery offers it
  only for a performance request.
- Entry: it runs only when the user invoked or confirmed it (`devkit-playbook`, `devkit playbook get
  maintenance/performance-pass` or a confirmed intake offer). Invocation, an external runner naming it and a clean
  measurement authorize no change; only the decision round does, and an unattended run stops there with nothing
  applied.
- The body is self-contained apart from the cited `review-refactor` sections: it states its own criteria and cites no
  repository document ID.

### Router layout

| File | Holds | Read when |
| --- | --- | --- |
| `SKILL.md` | Header; entry condition; constraints for every run (no change without the decision round, behavior preservation, measurement honesty, receipt-owned files read-only, a correctness defect found on the way is a follow-up, never stash); intake; mode table; decision round dispositions; report fields; completion | Always |
| `references/measurement.md` | Metrics; command form; run states; warm-up, repetitions and statistics; noise; old/new side by side; per-component timing; baseline record; regression comparison and bisection | Every mode, before the first timed run |
| `references/profiling.md` | Attribution by profiler class; the traps and the check for each; confirming a share unprofiled | When measurement does not already name the cost |
| `references/candidates.md` | Candidate record; expected-saving estimate; noise floor; behavior-preserving versus contract-change criteria; decision round presentation; what is kept with a reason | Before the decision round |
| `references/applying.md` | Which `review-refactor` sections apply and how to resolve them; per-change measurement; performance additions to differential evidence and the reviewer brief; final measurement | After the round approved changes |

Each file stays below the 12288-byte budget, aiming at about 9.5 KB (`materials/design-options.md` O6). Every reference
is linked from `SKILL.md` with its read condition.

### Intake and modes

1. Intake records what the other maintenance playbooks record (run ID, credential-free repository identity, HEAD,
   dirty paths, prior reports, report destination) plus the environment: machine, operating system, runtime
   versions and the load at intake.
2. The user selects the targets: each operation as an exact argument list with its working directory and
   environment, the metric (wall time, subprocess count, peak memory) and, when they have one, a goal. Missing scope
   is clarified before any timed run.
3. Modes:

| Mode | Entry | Loads | Ends |
| --- | --- | --- | --- |
| `survey` | The user names candidate operations and wants a ranked list | `measurement.md`, `profiling.md`, `candidates.md` | Decision round; nothing applied in this mode. An approved change turns the run `targeted`, recorded in the report |
| `targeted` | The user names operations to speed up | All references in phase order | Report with measured before/after per change |
| `regression` | One operation got slower between two named revisions | `measurement.md` (two-revision comparison and bisection), `profiling.md`; `candidates.md` and `applying.md` only when a fix is agreed | Report naming the responsible change and the agreed disposition |

A regression against a stated contract (a documented budget) is a defect: the round routes its fix through the
repository's bugfix workflow as a contract repair, not as a refactor.

### Measurement protocol (`references/measurement.md`)

`PADR-measure-performance-unprofiled-and-interleaved-in-one-session`:

- Time the real process from outside; an in-process timer misses startup, shutdown and child processes.
- Run each command from an argument list or a script file, never from an unquoted shell variable (zsh does not split
  it); check each run's exit code and output digest against the expected and drop failed runs.
- Label the state: warm (caches filled by an earlier run of the same revision) or cold (caches cleared the
  documented way). Measure both when the operation keeps a persistent cache. Discard every run after a code or
  cache-format change.
- At least one discarded warm-up per variant, at least five repetitions, variants interleaved (old, new, old, new).
  Report median, minimum and range; a difference within the larger range is "no measurable change".
- Record the load before and after; repeat later when another workload runs or the range is wide.
- Run old and new on the same machine in the same session; run the old revision from an extracted copy
  (for example `git archive`) or a separate checkout, never by stashing or switching the working checkout. A
  language runtime may load the old source by path (for example `PYTHONPATH`).
- For a composite operation, time its components unprofiled and check that their sum explains the total before
  ranking.
- Baseline record: revision, environment, exact command, state, run count, median, minimum, range. A later run
  re-measures the baseline instead of comparing with another session's numbers.
- Regression: measure both revisions by the same protocol, then bisect between them on the same metric, recording
  each probe's revision and statistics.

### Attribution (`references/profiling.md`)

- Profile only to attribute cost, never to report savings.
- Deterministic (tracing) profilers inflate wall time two to three times and inflate call-heavy code more than I/O;
  confirm a hotspot's share unprofiled (time the function directly, or measure with the work removed in a probe)
  before it becomes a candidate. Sampling profilers distort less; use one only when installed.
- An in-process profiler shows a child process only as waiting: count and time subprocesses separately (for example
  by tracing process creation or wrapping the spawning call).
- Allocation and garbage collection are not attributed to the function that caused them: measure collector time and
  object counts when a hotspot builds large object graphs.
- Profile cold and warm separately; the first run after a change rebuilds caches.
- Startup and import time are measured on their own (for example a runtime's import-time trace).

### Candidates and decision round (`references/candidates.md`)

- Each candidate records: location; mechanism of the cost (repeated work, per-item system calls, subprocesses,
  allocation, a slower algorithm); measured share of the target metric, unprofiled; proposed change; expected saving
  as an estimate derived from the share; risk (which inputs or states could behave differently); classification
  (below); planned differential inputs; route, edited paths and write scope as `review-refactor` requires.
- A candidate whose expected saving is below the noise floor is dropped and counted in the coverage. A measured cost
  no change can remove (for example a probe whose answer is not known in advance) is reported as kept, with the reason.
- Prefer removing repeated work (one scan instead of many, a memo within one run, fewer processes) over
  micro-optimization.
- Classification (`PADR-classify-performance-changes-by-observable-behavior`):
  - Behavior-preserving: every observable result, error path and persisted format stays the same for every accepted
    input. A private cache format change with version or fingerprint invalidation and identical outputs cache off,
    cold and warm qualifies; so does a memo within one run whose key covers every input that changes the answer and
    which never memoizes a failure.
  - Contract change: changed output (content, order, format); new state kept between runs; concurrency or
    parallelism; changed defaults, accuracy or error handling; a removed option.
- Dispositions are `review-refactor`'s: apply with behavior preserved (joins the run's work item), contract change
  (its own work item through the normal workflow), defer (destination and restart condition), keep (reason). All
  candidates of the run are decided in one round; unanswered ones stay pending.

### Application and evidence (`references/applying.md`)

`PADR-reuse-review-refactor-application-through-exact-playbook-retrieval`:

- Resolve `devkit playbook get maintenance/review-refactor` and read `references/applying.md` and
  `references/criteria.md` relative to its `source.path`. Follow the application sections by heading (work items and
  route, branch and edit tasks, subagent edits, commits and verification, review, report, integration, contract
  removals) and the preservation evidence section of `criteria.md`, including its differential comparison. If a cited
  section is missing, stop and report it.
- Additions for performance changes:
  - Measure each change by the protocol, old and new on the previous checkpoint, and record the statistics in its
    commit body beside the preservation evidence.
  - Differential inputs include the input domain's error cases and unusual states (unreadable entries, symbolic link
    loops, differently spelled paths, a vanished working directory), not only the corpus.
  - The reviewer brief adds: each change's classification and its claim of equal behavior; error paths of replaced
    APIs; cache invalidation and memo keys.
  - At the work item's final head, measure every target again against the intake baseline.
- Development starts after the review-refactor lessons change on its development branch lands, because the cited
  sections (parallel isolated checkouts, differential comparison without stash, reviewer brief) come from it; the Host
  checks this before handoff.

### Report and completion (`SKILL.md`)

- Intake and environment, mode, targets and the baseline record per target.
- Coverage: operations measured, components attributed, candidates dropped below the noise floor, coverage gaps.
- Candidates and changes as separate records; each change names its candidate, classification, differential inputs
  and count, verification, measured before/after and commit.
- Decisions with provenance, follow-ups, counts, and the final measurement against the baseline.
- Outcome (`stopped at decision round`, `applied`, `partially applied`) with the work items' integration state.
- A run is complete with no pending decision, every agreed change committed or routed and the final measurement
  recorded. The report is an ordinary local file in the owning unit's materials or the repository's materials
  location.

### Living Spec targets

- New capability under `docs/capabilities/delivery/` for the performance pass, with the playbook as entrypoint.
- New use case under `docs/usecases/governance/`.
- `CAP-DIST-content-packages` §6: the `performance` preset, the co-deployment constraint and that `performance-pass`
  reads `review-refactor`'s application procedure without running it.
- `CAP-DLV-review-refactor`: its application and evidence section headings are cited by `performance-pass`.
- `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md`, the bundle manifest and the
  `devkit-catalog` bundle tests (presets, co-deployment, cited headings, self-containment and size).
- Handbook entries follow at the next release.

## 4. Lifecycle & Retirement Criteria

- Accepted when Planning answers Q1 to Q5 and the router layout passes the authoring playbook's size and structure
  rules.
- Retire or merge into `review-refactor` if a later run shows the two playbooks share most of their procedure.

## 5. Planning decisions

- Settled by `user` at intent: a separate maintenance playbook, router-structured, in the `maintenance` bundle beside
  `review-refactor`, reusing its parallel application and differential evidence by reference
  (`PADR-keep-performance-passes-in-a-separate-maintenance-playbook`).
- Settled in Planning: three modes (O1); exact retrieval with co-deployment (O2); report in `SKILL.md` (O3); preset
  `performance`, `upkeep` unchanged (O5); the measurement protocol and change classification PADRs.
- Open for the user: the milestone (`MS-maintenance-operations` is `done`) and the timing helper script (O4).
