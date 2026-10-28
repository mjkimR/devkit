# Attributing cost

Read when the measurement does not already name the cost. A profile attributes cost to code; it never measures a
saving. Every share that becomes a candidate is confirmed unprofiled by the measurement protocol.

## 1. Choose the profiler

| Class | Use | Distortion |
| --- | --- | --- |
| Deterministic (tracing) | Call counts and the call graph of one process | Inflates wall time two to three times, call-heavy code more than I/O |
| Sampling | Shares of wall time with less distortion | Low; use one only when it is installed |
| Process tracing | Subprocess counts, their arguments and their time | Low per process; invisible to in-process profilers |
| Allocation and collector statistics | Object counts and garbage collection time | Varies; read counts, never timings, under a tracing profiler |
| Import-time trace | Startup and module import cost | Measures imports alone |

Name tools as examples only (for example a runtime's built-in tracing profiler, a sampling profiler, an import-time
trace). Use what is installed; install a tool only with the user's consent.

## 2. Traps and their checks

1. Profiler inflation. A deterministic profiler slows call-heavy code more than I/O, so its shares are skewed toward
   many small calls.
   - Check: confirm a hotspot's share unprofiled before it becomes a candidate. Time the function directly around its
     calls, or run a probe with the work removed or replaced by its cached answer and measure the difference by the
     protocol.
2. Child processes. An in-process profiler shows a subprocess only as time spent waiting.
   - Check: count and time subprocesses separately, by tracing process creation or by wrapping the spawning call
     to log each argument list and its duration. Look for repeated identical calls.
3. Allocation and garbage collection. Their cost lands on whatever code runs when the collector triggers, not on
   the code that built the objects.
   - Check: when a hotspot builds large object graphs (decoded caches, parsed trees, many small records), measure
     collector time and object counts, and compare a run with the collector's thresholds raised in a probe.
4. Cold against warm. The first run after a code or cache-format change rebuilds caches and attributes the rebuild
   to the wrong phase.
   - Check: profile cold and warm separately, each after its own warm-up rule, and label each profile.
5. Startup and imports. Interpreter startup, module imports and shutdown fall outside a profile started inside the
   program.
   - Check: measure startup and import time on their own (for example a runtime's import-time trace and the time
     of a no-op invocation), and time shutdown as the difference between the outside wall time and the in-process
     time.
6. One process standing for a composite. A single profile of a composite operation hides which component owns the
   time.
   - Check: use the per-component timing of the measurement protocol first; profile the component that owns the
     cost.

## 3. From profile to share

1. For each hotspot, write the mechanism of its cost: repeated work, per-item system calls, subprocesses,
   allocation or a slower algorithm.
2. Confirm the share unprofiled (trap 1) and record it as a share of the target's measured metric.
3. If the unprofiled share is below the noise floor, drop the hotspot and count it in the coverage.
4. Record what you profiled, in which state, and what you did not reach as coverage gaps.
