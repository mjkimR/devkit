---
id: PADR-measure-performance-unprofiled-and-interleaved-in-one-session
title: Measure performance unprofiled and interleaved in one session
summary: For performance pass baselines and results, we time the real process unprofiled, interleave old and new variants on one machine in one session and report median, minimum and range, to keep savings honest against profiler inflation and noise, accepting longer measurement runs.
proposal: PROP-performance-pass
status: draft
created_at: 2026-10-27
---

# [PADR-measure-performance-unprofiled-and-interleaved-in-one-session] Measure performance unprofiled and interleaved in one session

- **Status**: Draft
- **Date**: 2026-10-27

---

## 1. Context & Problem Statement

Reported savings must survive repetition. A deterministic profiler inflated wall time 2.7x in an earlier measurement
and distorts shares between call-heavy and I/O-bound code; in-process timers miss interpreter shutdown and work in
child processes; the first run after a code or cache-format change rebuilds caches; concurrent agents add noise; and
before/after numbers taken in different checkouts or sessions are not comparable (`materials/pass-evidence.md` §3).

## 2. Decision Drivers

- A saving is a difference larger than the measurement's own spread.
- The protocol is language-neutral and needs no installed benchmark tool.
- A development worker or a later run can reproduce the baseline.

## 3. Considered Options

- **Unprofiled real-process timing, variants interleaved in one session, median, minimum and range** (selected):
  reproducible and honest; costs several runs per variant.
- **Profiler totals before and after**: one run each; inflated and distorted.
- **Single before and after runs**: cheapest; noise exceeds small savings.

## 4. Decision Outcome

- The playbook ships no timing script (`user`): an installed benchmark tool is used when available, otherwise the
  agent's own short loop, and either meets the requirements below.
- Time the real process from outside, with exact argument list, working directory and environment; check each run's
  exit code and its output digest against the other runs of the same variant (paths normalized between variants'
  directories), and drop failed runs.
- Run old and new against the same input and working directory: the old code by a runtime path override to an
  extracted copy, or from a separate worktree prepared with the repository's documented setup; never stash or switch
  the working checkout.
- Warm state: discard at least one warm-up run per variant; the first run after a code or cache-format change is a
  warm-up. Cold state: clear caches the documented way before every run. Measure both when the operation keeps a
  persistent cache.
- Run at least five repetitions per variant, interleaved; report median, minimum and range. The noise floor is the
  larger of the two variants' ranges after dropping each variant's slowest run; a median difference below it is no
  measurable change, and when one outlier decides, five more repetitions per variant run first.
- Measure on the same machine in one session while no edit task, verification or other workload of the run is
  active; record the load before and after.
- Profile only to attribute cost; confirm a hotspot's share unprofiled before it becomes a candidate.
- Record each baseline with revision, environment, command, state, count, median, minimum and range. Every
  comparison, the final one at the work item's head included, re-runs the older revision in the same session;
  recorded numbers from another session are context only.

## 5. Consequences

- Positive: savings are comparable and reproducible; profiler artifacts never enter the report.
- Negative: each comparison takes at least ten timed runs plus warm-ups.
- Follow-up: none.

## 6. Confirmation

Review only (the playbook's `references/measurement.md` states the protocol; its report fields require the recorded
values).
