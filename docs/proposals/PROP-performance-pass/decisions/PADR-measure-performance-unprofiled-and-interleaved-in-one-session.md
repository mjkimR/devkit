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

- Time the real process from outside, with exact argument list, working directory and environment; check each run's
  exit code and output, and drop failed runs.
- Discard at least one warm-up run per variant, and every run after a code or cache-format change; label cold and warm
  states and measure both when the operation keeps a persistent cache.
- Run at least five repetitions per variant, interleaved; report median, minimum and range. A difference within the
  larger range is reported as no measurable change.
- Measure old and new on the same machine in the same session, the old revision from an extracted copy or a separate
  checkout, never by stashing or switching the working checkout; record the load before and after.
- Profile only to attribute cost; confirm a hotspot's share unprofiled before it becomes a candidate.
- Record each baseline with revision, environment, command, state, count, median, minimum and range; a later run
  re-measures the baseline rather than comparing with numbers from another session.

## 5. Consequences

- Positive: savings are comparable and reproducible; profiler artifacts never enter the report.
- Negative: each comparison takes at least ten timed runs plus warm-ups.
- Follow-up: none.

## 6. Confirmation

Review only (the playbook's `references/measurement.md` states the protocol; its report fields require the recorded
values).
