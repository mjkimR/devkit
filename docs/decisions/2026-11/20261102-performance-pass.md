---
id: ADR-performance-pass
title: Performance pass playbook, classification, measurement and reuse
summary: "For repeatable performance passes, we ship a separate maintenance playbook that classifies changes by observable behavior, measures unprofiled and interleaved in one session and reuses review-refactor application by exact retrieval, to keep savings honest, accepting more work items and runs."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-classify-performance-changes-by-observable-behavior
  - ADR-keep-performance-passes-in-a-separate-maintenance-playbook
  - ADR-measure-performance-unprofiled-and-interleaved-in-one-session
  - ADR-reuse-review-refactor-application-through-exact-playbook-retrieval
---

# [ADR-performance-pass] Performance pass playbook, classification, measurement and reuse

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `maintenance/performance-pass` and `maintenance/review-refactor` playbooks
  (`packages/devkit-catalog`), `CAP-DIST-context-and-playbooks`

---

## 1. Context & Problem Statement

A performance pass has its own goal (latency of user-selected operations) and its own evidence (a measured baseline,
attribution without profiler distortion, measured savings), unlike a maintenance-cost review. Folding it into
`review-refactor` as a fourth surface would put measurement and profiling text into a playbook that is already near
its size budget and whose criteria (a named maintenance cost, reduction grounds) do not apply to latency.

Faster code often changes behavior on inputs the corpus does not contain: a scan API that raises where the old call
returned `False` broke every listing on one symlink loop
(`docs/materials/2026-10/20261028-performance-pass/pass-evidence.md` §2). Some speedups change the contract outright:
state kept between runs can serve stale answers and occupies disk; concurrency changes ordering, error reporting and
resource use. `review-refactor` routes behavior-preserving changes as refactors and contract changes as their own
work items; performance changes need the same split with criteria of their own.

Reported savings must survive repetition. A deterministic profiler inflated wall time 2.7x in an earlier measurement
and distorts shares between call-heavy and I/O-bound code; in-process timers miss interpreter shutdown and work in
child processes; the first run after a code or cache-format change rebuilds caches; concurrent agents add noise; and
before/after numbers taken in different checkouts or sessions are not comparable
(`docs/materials/2026-10/20261028-performance-pass/pass-evidence.md` §3).

A performance pass applies agreed changes exactly as `review-refactor` does: one work item on its own branch, edit
tasks in disjoint scopes, one commit per change with verification before and after, differential old/new comparison,
a fresh adversarial review, report and integration. Copying those steps creates two copies that drift. A playbook's
relative body resources resolve against the parent of the effective `source.path` that exact retrieval returns, which
is an override path when the user overrode the playbook (`CAP-DIST-context-and-playbooks`). A file of another
playbook exists only when a selected preset deploys that playbook.

---

## 2. Decision Drivers

- Each playbook keeps one goal, one set of review criteria and one kind of evidence.
- The playbook fits the skill size budget with a router `SKILL.md` and references read per phase.
- Application, evidence and review rules shared with `review-refactor` exist once; one application and evidence
  procedure serves both playbooks.
- A consumer selects the playbook from the `maintenance` bundle like the other maintenance playbooks.
- A change routed as a refactor changes no observable behavior for any accepted input.
- Internal caches and memos stay usable when their invalidation is proved.
- The split matches `review-refactor`'s dispositions so application is shared.
- A saving is a difference larger than the measurement's own spread.
- The protocol is language-neutral and needs no installed benchmark tool.
- A development worker or a later run can reproduce the baseline.
- The reference follows the user's override of `review-refactor`.
- A missing or renamed target is caught before release, not during a run.
- No playbook requires running another.

---

## 3. Considered Options

- **Placement**:
  - A separate `performance-pass` playbook in `maintenance`, router-structured from the start (selected by `user`):
    focused criteria and evidence; a second asset whose shared steps are reused by reference. (Chosen.)
  - A `performance` surface of `review-refactor`: one asset; mixes latency criteria into maintenance-cost criteria and
    grows a playbook near its budget (rejected in `ADR-keep-performance-passes-in-a-separate-maintenance-playbook`).
  - A playbook in another bundle: no shared preset or retrieval path with `review-refactor` (rejected in
    `ADR-keep-performance-passes-in-a-separate-maintenance-playbook`).
- **Classification**:
  - Observable-behavior criteria with named contract-change classes: clear routing; more work items. (Chosen.)
  - Corpus-equivalence only: cheap; misses error paths, as the regression showed (rejected in
    `ADR-classify-performance-changes-by-observable-behavior`).
  - Every performance change as a contract change: safest; turns internal speedups into full feature work (rejected
    in `ADR-classify-performance-changes-by-observable-behavior`).
- **Measurement**:
  - Unprofiled real-process timing, variants interleaved in one session, median, minimum and range: reproducible and
    honest; costs several runs per variant. (Chosen.)
  - Profiler totals before and after: one run each; inflated and distorted (rejected in
    `ADR-measure-performance-unprofiled-and-interleaved-in-one-session`).
  - Single before and after runs: cheapest; noise exceeds small savings (rejected in
    `ADR-measure-performance-unprofiled-and-interleaved-in-one-session`).
- **Reuse of `review-refactor` application**:
  - Exact retrieval plus cited headings, co-deployed: one procedure; adds a preset constraint and a test. (Chosen.)
  - Relative link into the sibling directory: no constraint; ignores overrides and breaks silently when
    `review-refactor` is not deployed (rejected in
    `ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`).
  - Copy the shared steps: self-contained; two copies drift, against the settled reuse by reference (rejected in
    `ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`).

---

## 4. Decision Outcome

### Playbook placement

- `performance-pass` is a directory-form playbook asset of the `maintenance` catalog bundle beside `review-refactor`.
  (`ADR-keep-performance-passes-in-a-separate-maintenance-playbook`)
- It is authored by the `skill-authoring` playbook as a router: `SKILL.md` holds the entry condition, intake, mode
  selection, the decision round summary, the report and completion; each phase that only some runs need has its own
  reference. (`ADR-keep-performance-passes-in-a-separate-maintenance-playbook`)
- It reuses `review-refactor`'s application procedure and differential evidence by reference, as stated under Reuse
  of review-refactor application. (`ADR-keep-performance-passes-in-a-separate-maintenance-playbook`)

### Classification

- Behavior-preserving: stdout, stderr, exit codes, written files and their bytes, persisted formats other versions or
  tools read, error behavior (which inputs fail and how) and the order of observable side effects stay the same for
  every accepted input. (`ADR-classify-performance-changes-by-observable-behavior`)
  - A change to a private cache's format qualifies when a version or fingerprint invalidates old entries and outputs
    are identical with the cache off, cold and warm.
  - A memo within one run qualifies when its key covers every input that changes the answer and failures are never
    memoized.
- Contract change: changed output (content, order or format); new state that persists between runs where none
  existed (a cache file, a daemon); concurrency or parallelism that can change ordering, errors, locking or resource
  use; changed defaults, accuracy or error handling; a removed option. It is its own work item through the
  repository's normal development workflow, as in `review-refactor`.
  (`ADR-classify-performance-changes-by-observable-behavior`)
- Differential comparison runs old and new on the repository's corpus plus the input domain's edge and error cases
  (empty, malformed, unreadable, symbolic link loops, differently spelled paths, a vanished working directory).
  (`ADR-classify-performance-changes-by-observable-behavior`)
- Any difference the comparison or the review finds is fixed, or the change returns to the decision round as its own
  contract-change work item; unlike `review-refactor`, no approved behavior change stays in the behavior-preserving
  work item. (`ADR-classify-performance-changes-by-observable-behavior`)

### Measurement

- The playbook ships no timing script (`user`): an installed benchmark tool is used when available, otherwise the
  agent's own short loop, and either meets the requirements below.
  (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Time the real process from outside, with exact argument list, working directory and environment; check each run's
  exit code and its output digest against the other runs of the same variant (paths normalized between variants'
  directories), and drop failed runs. (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Run old and new against the same input and working directory: the old code by a runtime path override to an
  extracted copy, or from a separate worktree prepared with the repository's documented setup; never stash or switch
  the working checkout. (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Warm state: discard at least one warm-up run per variant; the first run after a code or cache-format change is a
  warm-up. Cold state: clear caches the documented way before every run. Measure both when the operation keeps a
  persistent cache. (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Run at least five repetitions per variant, interleaved; report median, minimum and range. The noise floor is the
  larger of the two variants' ranges after dropping each variant's slowest run; a median difference below it is no
  measurable change, and when one outlier decides, five more repetitions per variant run first.
  (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Measure on the same machine in one session while no edit task, verification or other workload of the run is
  active; record the load before and after. (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Profile only to attribute cost; confirm a hotspot's share unprofiled before it becomes a candidate.
  (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)
- Record each baseline with revision, environment, command, state, count, median, minimum and range. Every
  comparison, the final one at the work item's head included, re-runs the older revision in the same session;
  recorded numbers from another session are context only.
  (`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`)

### Reuse of review-refactor application

- `performance-pass`'s `SKILL.md`, before the decision round, tells the agent to run `devkit playbook get
  maintenance/review-refactor` and read `references/applying.md` and `references/criteria.md` next to the returned
  `source.path`, falling back to the managed copy when an override directory lacks the file.
  (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)
- Citations name the file and the heading text without its number, in one form a test parses (for example
  `review-refactor references/applying.md "Commits and verification"`).
  (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)
- Reading that text is reference reading, not an invocation: no intake, batch or decision round of `review-refactor`
  starts. `CAP-DIST-context-and-playbooks` states this for co-deployed playbooks.
  (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)
- Every preset that deploys `performance-pass` also deploys `review-refactor`.
  (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)
- Not followed: `review-refactor`'s "Work items and route"; the run's behavior-preserving work item follows the
  repository's feature workflow at its own depth, for one module or several (`user`), because the direct-mode
  overall-refactor route is granted to `review-refactor` runs only. Also not followed: its "approved behavior change"
  inside the behavior-preserving work item (every found difference is a contract change, as stated under
  Classification). (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)
- `performance-pass` states only what it adds or overrides: measurement per change on a quiet machine, its
  preservation criteria, the reviewer brief additions and its report fields.
  (`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`)

---

## 5. Consequences

- **Positive**:
  - Each playbook stays focused and within budget; latency evidence has its own criteria.
  - A speedup that changes a contract is visible in the decision round and gets its own review.
  - Savings are comparable and reproducible; profiler artifacts never enter the report.
  - One procedure; improvements to `review-refactor` application apply to both.
- **Negative / Risks**:
  - Two playbooks to keep aligned where they share steps.
  - Caching or concurrency proposals need a separate work item even when small.
  - Each comparison takes at least ten timed runs plus warm-ups.
  - A `performance` preset also deploys `review-refactor`; a heading rename in `review-refactor` needs a matching
    edit here.
  - A user override of `review-refactor` that drops a cited heading leaves the reference without a target; the
    playbook tells the agent to stop and report the missing section rather than improvise.
- **Follow-ups**:
  - If a later run shows the two playbooks share most of their procedure, merge them (the retirement criterion of
    `SPEC-performance-pass`).

---

## 6. Confirmation

- `devkit-catalog` bundle tests (asset kind and source, presets) and `uv run devkit rules check --phase hygiene` on
  the playbook directory (`RULE-skill-document-size`, `RULE-agent-asset-wording`).
- A `devkit-catalog` bundle test asserts that every preset containing `performance-pass` contains `review-refactor`
  and that each citation in `performance-pass` (parsed from the fixed form) names a heading, number removed, that
  exists in the named `review-refactor` file.
- Review only for classification (the playbook's `references/candidates.md` states the criteria; each change record
  names its classification and differential inputs).
- Review only for measurement (the playbook's `references/measurement.md` states the protocol; its report fields
  require the recorded values).
