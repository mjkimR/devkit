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

A performance pass over this repository on 2026-10-27 (per commit, warm and unprofiled: file listing in a full rules
check 0.30 s to 0.05 s, a one-file rules check 0.44 s to 0.33 s, `sync --dry-run` 1.25 s to about 0.92 s with
subprocesses 29 to 14; `materials/pass-evidence.md` §1) borrowed the `maintenance/review-refactor` procedure, but its
goal is latency, not a smaller surface, and it needed steps that playbook does not have: a measured baseline,
profiling without being misled by profiler inflation or child processes, per-component timing, and differential
old/new comparisons as preservation evidence. A fresh review still found a regression (a symlink loop breaking every
file listing) that tests missed (`materials/pass-evidence.md` §2). The session totals in the original draft (rules
check 3.0 s to 1.7 s, a one-file commit-gate check 0.92 s to 0.38 s, `sync --dry-run` to 1.14 s) are session
observations from another measuring session; that they differ from the per-commit figures is the cross-session
noise the protocol below addresses.

Hypothesis: a separate, router-structured maintenance playbook that turns a user-selected set of slow operations into
measured, behavior-preserving changes with differential evidence makes such passes repeatable in any repository and
keeps `review-refactor` focused on maintenance cost.

## 2. Technical Spike Questions

- **Q1**: Which entry modes does the router need (a measurement-only survey, a targeted pass on named commands or
  checks, a regression investigation), and what does each load?
  - Answer: two modes (`materials/design-options.md` O1, revised after `challenger-01` finding 9). `survey` loads
    measurement, profiling and candidates and stops at the decision round with nothing applied; `targeted` loads every
    reference in phase order. A regression mode is left out: the pass gives no evidence for it, and bisection conflicts
    with the rule never to switch the working checkout. It is added when a real regression run shows the need.
- **Q2**: What measurement protocol is portable: warm-up, repetitions and the statistic reported, cold versus warm
  caches, machine noise and concurrent load, and how a baseline is recorded so a later run can compare?
  - Answer: unprofiled real-process timing, variants interleaved in one quiet session against the same input and
    working directory, at least one warm-up and five repetitions, median, minimum and range, a defined noise floor,
    cold and warm labeled (`PADR-measure-performance-unprofiled-and-interleaved-in-one-session`). A recorded baseline
    names revision, environment, command, state and statistics; every comparison, the final one included, re-runs the
    older revision in the same session instead of reusing recorded numbers. Evidence: `materials/pass-evidence.md` §3.
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
  - Answer: branch and edit tasks, parallel subagent edits in isolated checkouts, commits and verification,
    differential comparison, review, report, integration and contract removals are read from `review-refactor`
    through exact playbook retrieval and cited by heading, with co-deployment, an override fallback and a heading test
    (`PADR-reuse-review-refactor-application-through-exact-playbook-retrieval`). Measurement, attribution, candidate
    criteria, the route, the stricter difference rule, the reviewer brief additions and the report's performance fields
    stay in `performance-pass`.

## 3. Proposed Design & Impact

### Asset, packaging and authoring

- `performance-pass` is a directory-form playbook asset of the `maintenance` catalog bundle beside `review-refactor`
  (`PADR-keep-performance-passes-in-a-separate-maintenance-playbook`), authored with the `skill-authoring` playbook.
- Presets (`materials/design-options.md` O5): the implicit `all` includes it; a new preset `performance` deploys
  `performance-pass` and `review-refactor`; `upkeep` and `refactoring` are unchanged. Every preset that deploys
  `performance-pass` deploys `review-refactor`; selection is a union of presets with no per-asset selection, so a
  preset-membership test suffices.
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
| `SKILL.md` | Header; entry condition; constraints for every run (no change without the decision round, behavior preservation, measurement honesty, receipt-owned files read-only, a correctness defect found on the way is a follow-up, never stash); intake; mode table; resolving `review-refactor` (below); decision round dispositions and route; report fields; completion | Always |
| `references/measurement.md` | Metrics; command form; run states; warm-up, repetitions, statistics and the noise floor; quiet-machine rule; old/new against the same input; per-component timing; baseline record | Every mode, before the first timed run |
| `references/profiling.md` | Attribution by profiler class; the traps and the check for each; confirming a share unprofiled | When measurement does not already name the cost |
| `references/candidates.md` | Candidate record; expected-saving estimate; behavior-preserving versus contract-change criteria; decision round presentation; what is kept with a reason | Before the decision round |
| `references/changes.md` | Which `review-refactor` sections apply and the overrides to them; per-change measurement; performance additions to differential evidence and the reviewer brief; final measurement | After the round approved changes |

The application reference is named `changes.md`, not `applying.md`, so it is never confused with `review-refactor`'s
`references/applying.md` (`challenger-01` finding 10). Each file stays below the 12288-byte budget, aiming at about
9.5 KB (`materials/design-options.md` O6). Every reference is linked from `SKILL.md` with its read condition, and no
reference sends the agent to another of its own references.

### Resolving `review-refactor` (`SKILL.md`)

`PADR-reuse-review-refactor-application-through-exact-playbook-retrieval`:

- Before the decision round, run `devkit playbook get maintenance/review-refactor`. For each cited file, read
  `references/<file>` next to the returned `source.path`; when that path is an override directory without the file,
  read the managed copy, because files missing from an override directory are read from upstream.
- Reading that text is reference reading, not an invocation: none of `review-refactor`'s intake, batches or decision
  round starts.
- Citations use one form the bundle test parses: the file and the heading text without its number, for example
  `review-refactor references/applying.md "Commits and verification"`. A missing cited heading stops the run with a
  report, never an improvised procedure.

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

### Measurement protocol (`references/measurement.md`)

`PADR-measure-performance-unprofiled-and-interleaved-in-one-session`:

- Time the real process from outside; an in-process timer misses startup, shutdown and child processes.
- Run each command from an argument list or a script file, never from an unquoted shell variable (zsh does not split
  it). Check each run's exit code, and its output digest against the other runs of the same variant, normalizing
  paths that differ between variants' directories; drop failed runs.
- Run old and new against the same input and working directory: load the old code by a runtime path override (for
  example `PYTHONPATH` pointing at an extracted copy of the previous revision), or from a separate worktree prepared
  with the repository's documented setup. Never stash or switch the working checkout.
- Label the state. Warm: caches filled by an earlier run of the same revision, after at least one discarded warm-up
  run per variant. Cold: caches cleared the documented way before every run. Measure both when the operation keeps a
  persistent cache; the first run after a code or cache-format change is a warm-up, never a sample.
- At least five repetitions per variant, interleaved (old, new, old, new). Report median, minimum and range.
- Noise floor: the larger of the two variants' ranges after dropping each variant's single slowest run. A median
  difference below it is "no measurable change"; when one outlier decides, add five repetitions per variant before
  concluding.
- Measure on a quiet machine: no edit task, verification run or other workload of the run is active; record the load
  before and after and repeat later when another workload ran.
- For a composite operation, time its components unprofiled and check that their sum explains the total before
  ranking.
- Baseline record: revision, environment, exact command, state, run count, median, minimum, range. Any comparison,
  the final one included, re-runs the older revision in the same session; recorded numbers from another session are
  context only.

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
  (below); planned differential inputs; route, edited paths and write scope (below).
- A candidate whose expected saving is below the noise floor (`measurement.md`) is dropped and counted in the
  coverage. A measured cost no change can remove (for example a probe whose answer is not known in advance) is
  reported as kept, with the reason.
- Prefer removing repeated work (one scan instead of many, a memo within one run, fewer processes) over
  micro-optimization.
- Classification (`PADR-classify-performance-changes-by-observable-behavior`):
  - Behavior-preserving: every observable result, error path and persisted format stays the same for every accepted
    input. A private cache format change with version or fingerprint invalidation and identical outputs cache off,
    cold and warm qualifies; so does a memo within one run whose key covers every input that changes the answer and
    which never memoizes a failure.
  - Contract change: changed output (content, order, format); new state kept between runs; concurrency or
    parallelism; changed defaults, accuracy or error handling; a removed option.
- Dispositions follow `review-refactor`'s table: apply with behavior preserved (joins the run's work item), contract
  change (its own work item through the normal workflow), defer (destination and restart condition), keep (reason).
  All candidates of the run are decided in one round; unanswered ones stay pending.
- Route and write scope (pending question `q1`; recommended option shown): the run's agreed behavior-preserving
  changes form one work item that follows the repository's feature workflow at the depth its own classification gives
  (with the `spec` bundle, `session` when no contract or specification text changes), whether it edits one module or
  several. The decision round states the route and the edited paths, which are the write scope. `review-refactor`'s
  "Work items and route" section is not followed: the direct-mode overall-refactor route for several modules is
  granted to `review-refactor` runs only. If the user chooses the refactor route instead, the design adds a PADR
  extending that grant and the Living Spec and classification targets in `materials/design-options.md` O7.

### Application and evidence (`references/changes.md`)

- Follow the cited `review-refactor` sections: from `references/applying.md`, "Branch and edit tasks", "Subagent
  edits", "Commits and verification", "Review", "Report", "Integration" and "Contract removals"; from
  `references/criteria.md`, "Preservation evidence", including its differential comparison.
- Overrides to the cited text for performance changes:
  - Any difference the differential comparison or the review finds is a contract change: fix it, or return the change
    to the decision round as its own contract-change work item. `review-refactor`'s "approved behavior change" inside
    the behavior-preserving work item does not apply.
  - Edit tasks may run in parallel in isolated checkouts, but every timing run waits until no edit task or
    verification runs.
- Additions:
  - Measure each change by the protocol, old and new on the previous checkpoint, and record the statistics in its
    commit body beside the preservation evidence.
  - Differential inputs include the input domain's error cases and unusual states (unreadable entries, symbolic link
    loops, differently spelled paths, a vanished working directory), not only the corpus.
  - The reviewer brief adds: each change's classification and its claim of equal behavior; error paths of replaced
    APIs; cache invalidation and memo keys.
  - At the work item's final head, measure every target interleaved against the intake revision in one session.
- Base: the cited sections (parallel isolated checkouts, differential comparison without stash, reviewer brief) are on
  `main` from merge `dc3e07a2`, which this Planning branch predates. Development branches from a base containing it.

### Report and completion (`SKILL.md`)

- Intake and environment, mode, targets and the baseline record per target.
- Coverage: operations measured, components attributed, candidates dropped below the noise floor, coverage gaps.
- Candidates and changes as separate records; each change names its candidate, classification, differential inputs
  and count, verification, measured before/after and commit.
- Decisions with provenance, follow-ups, counts, and the final interleaved measurement against the intake revision.
- Outcome (`stopped at decision round`, `applied`, `partially applied`) with the work items' integration state.
- A run is complete with no pending decision, every agreed change committed or routed and the final measurement
  recorded. The report is an ordinary local file in the owning unit's materials or the repository's materials
  location.

### Living Spec targets

- New capability under `docs/capabilities/delivery/` for the performance pass, with the playbook as entrypoint.
- New use case under `docs/usecases/governance/`.
- `CAP-DIST-context-and-playbooks` §5: a playbook may read a co-deployed playbook's body resources as reference text;
  that is no invocation and starts none of its intake or decision rounds.
- `CAP-DIST-content-packages` §6: the `performance` preset, the co-deployment constraint, the reference reading
  without running, and the playbook count ("three independent playbooks").
- `CAP-DLV-review-refactor`: its application and evidence section headings are cited by `performance-pass`.
- `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md`, the bundle manifest and the
  `devkit-catalog` bundle tests (presets, co-deployment, cited headings in the citation form, self-containment, links
  and size).
- Handbook entries follow at the next release.

## 4. Lifecycle & Retirement Criteria

- Accepted when Planning answers Q1 to Q5 and the router layout passes the authoring playbook's size and structure
  rules.
- Retire or merge into `review-refactor` if a later run shows the two playbooks share most of their procedure.

## 5. Planning decisions

- Settled by `user` at intent: a separate maintenance playbook, router-structured, in the `maintenance` bundle beside
  `review-refactor`, reusing its parallel application and differential evidence by reference
  (`PADR-keep-performance-passes-in-a-separate-maintenance-playbook`).
- Settled in Planning: two modes, no regression mode (O1); exact retrieval with co-deployment, override fallback and
  a parseable citation form (O2); report in `SKILL.md` (O3); preset `performance`, `upkeep` unchanged (O5); the
  measurement protocol and change classification PADRs; for performance changes every found difference is a contract
  change.
- Open for the user (`worker` envelope questions): `q1` the route of the behavior-preserving work item, `q2` the
  milestone (`MS-maintenance-operations` is `done`), `q3` the timing helper script (O4).
