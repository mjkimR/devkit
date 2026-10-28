# Measurement protocol

Read before the first timed run of every mode. Every number the run reports comes from this protocol: baselines,
per-change savings and the final measurement. A profile never supplies one.

## 1. Metrics and command form

1. Measure the metric the user selected per target: wall time, subprocess count or peak memory. Record wall time
   beside any other metric.
2. Time the real process from outside. An in-process timer misses interpreter startup, shutdown and child processes.
3. Write each variant as an exact argument list with its working directory and environment, or as a script file.
   Never hold a command in an unquoted shell variable: zsh does not word-split it and runs the whole string as one
   word.
4. Count subprocesses by tracing process creation or by wrapping the spawning call; read peak memory from the
   operating system's resource accounting for the whole process tree.

## 2. Timing loop

Use an installed benchmark tool when one is available (for example `hyperfine`); otherwise write your own short loop.
Install nothing without asking the user. Either way the loop meets every requirement below:

1. Give the variants as argument lists.
2. Discard at least one warm-up run per variant.
3. Run at least five repetitions per variant, interleaved: old, new, old, new.
4. Check each run's exit code. Compare each run's output digest (stdout, stderr and written files the target
   produces) with the other runs of the same variant, after normalizing paths that differ between the variants'
   directories.
5. Drop a run that failed or whose output differs from its variant's other runs, and record the drop. If drops
   leave fewer than five runs, add runs until five succeed.
6. Report median, minimum and range per variant, with the run count.

A tool's own summary counts only when its configuration meets these requirements; add the exit-code and output
checks around it when it does not make them.

## 3. Run states

- Warm: caches filled by an earlier run of the same revision, after the discarded warm-up runs.
- Cold: caches cleared the documented way before every run.
- Label every measurement `warm` or `cold`. When the operation keeps a persistent cache, measure both.
- Treat the first run after a code or cache-format change as a warm-up, never a sample.

## 4. Noise floor

1. Per variant, drop the single slowest run and take the range of the rest.
2. The noise floor is the larger of the two variants' ranges.
   For a single variant, such as a baseline before any change exists, the noise floor is that variant's range after
   dropping its slowest run; candidate selection and attribution use this value.
3. A median difference below the noise floor is "no measurable change". Report it in those words, never as a saving.
4. If one outlier decides whether a difference clears the floor, run five more repetitions per variant before
   concluding.

## 5. Quiet machine

- Measure while no edit task, verification run or other workload of the run is active.
- Record the load before and after each measurement. If another workload ran in between or the load rose, repeat
  the measurement later.
- Measure both variants on the same machine in the same session.

## 6. Old and new against the same input

1. Run old and new against the same input and working directory.
2. Load the old code by a runtime path override (for example `PYTHONPATH` pointing at a copy of the previous revision
   extracted with `git archive`), or run it from a separate worktree prepared with the repository's documented setup.
3. Never stash or switch the working checkout to reach the old code; the stash list is shared by every worktree of
   the repository.
4. Confirm each variant loads the code you meant (for example print the module path once outside the timed runs).

## 7. Per-component timing

For a composite operation (a check that runs many rules, a command that runs several phases), time its components
unprofiled: each component on its own, or with a timer around each component in an instrumented copy. Check that the
components' sum explains the total before ranking candidates; record an unexplained remainder as its own component.

## 8. Baseline record

Record per target and state: revision, environment, exact command (argument list, working directory, environment),
state, run count, median, minimum and range.

Every comparison, the final one included, re-runs the older revision in the same session. A number recorded in
another session is context only; never subtract it from a number of this session.
