# Development measurements for `SPEC-persistent-python-facts-cache`

## Reproduction and scope

Run from the staged Development checkout:

```bash
UV_CACHE_DIR=/tmp/devkit-uv-cache uv run python docs/materials/2026-10/20261022-persistent-python-facts-cache/benchmark.py --output /tmp/facts-results.json
```

CPython 3.12.3; the measured input tree is `56c88a4204c8fe7fc773302b8b10745c38ff326c` on HEAD `bcc65602a3156f5163b27a4c2fb7ace20e11f8bc`.
The staged tree identifies the uncommitted implementation measured before the build boundary commit.
Each of the nine scenario/mode combinations has five fresh subprocesses. Final samples ran without concurrent task
checks. `development-results.json` preserves every sample, counters, timing and CLI result. The preliminary artifact
is separate because early full-check samples overlapped type checks.

The worker invokes the real CLI through `CliRunner`; parent wall time includes process startup, imports, descriptor
loading, evaluation and rendering. Disabled mode forces the internal cache control off. Cold mode removes only the
three derived rule memos before each sample. Warm mode restores the same seeded memos before each sample.
The edit scenario appends a comment to one source file and restores its bytes in `finally`. Snapshot mode evaluates
the staged tree, including the staged receipt and rule source. No benchmark step changes the Git index.

## End-to-end results

Seconds, medians of five samples:

| Scenario | Disabled | Cold store | Warm store | Warm saving vs disabled |
| :--- | ---: | ---: | ---: | ---: |
| full | 5.902 | 6.733 | 3.301 | 44.1% |
| edit | 5.732 | 6.876 | 3.468 | 39.5% |
| snapshot | 5.131 | 6.427 | 3.013 | 41.3% |

The full warm saving is 44.1%, exceeding the accepted 20% threshold. Every mode's full JSON result, stderr
and exit status equal disabled execution within its scenario. All measured commands exited zero with no findings,
errors or notices.

Warm full and staged checks invoke no migrated extractor. Warm edit checks invoke each descriptor exactly once,
only for `packages/devkit/src/devkit_agt/features/rules/models/phases.py`. Cold/disabled full inputs consume 547
advisory files and 498 files each for architecture and usecase boundaries. Other rules may still parse sources;
this evidence makes no global zero-AST claim. The benchmark asserts the warm counters and source paths.

## Cost breakdown

Milliseconds, per-counter medians. Counters overlap; do not sum the columns to infer total latency.

| Scenario/mode | Source read/cache access | Source hashing | Fingerprint hashing | JSON load + entry validation | Extraction | Judgment + other rules | Atomic write |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full/disabled | 33.60 | 3.14 | 0.00 | 0.00 | 2622.88 | 2104.92 | 0.00 |
| full/cold | 31.82 | 3.02 | 0.35 | 0.71 | 2763.64 | 1810.32 | 17.54 |
| full/warm | 28.44 | 2.38 | 0.33 | 213.50 | 0.00 | 1788.20 | 0.00 |
| edit/disabled | 31.27 | 3.01 | 0.00 | 0.00 | 2550.09 | 2015.76 | 0.00 |
| edit/cold | 33.48 | 3.12 | 0.37 | 0.73 | 2805.93 | 1847.41 | 25.02 |
| edit/warm | 29.46 | 2.44 | 0.34 | 217.02 | 4.38 | 1772.39 | 18.62 |
| snapshot/disabled | 57.84 | 3.13 | 0.00 | 0.00 | 2692.07 | 1239.35 | 0.00 |
| snapshot/cold | 60.09 | 3.33 | 0.35 | 0.77 | 2608.41 | 1500.18 | 0.00 |
| snapshot/warm | 56.36 | 2.68 | 0.35 | 234.96 | 0.00 | 1390.35 | 0.00 |

Source provenance is captured during module imports and remains included in total process time; the fingerprint
counter measures hashing captured provenance. JSON time excludes descriptor decode; total facts lookup also includes
identity and reconstruction. Judgment is evaluator time minus facts pull time, so it includes unrelated rule work.
Atomic write time excludes encoding/serialization, which remain in total CLI time. Warm unchanged runs perform no
memo replacement. The separate roundtrip tests verify preserved memo mtimes.

## Memo size and tradeoffs

| Memo | Bytes |
| :--- | ---: |
| `RULE-architecture.json` | 1,383,736 |
| `RULE-advisory-unique-code.json` | 459,717 |
| `RULE-usecase-boundaries.json` | 4,430,998 |

The original implementation baseline in `development-baseline.json` was 4.393 s median across five uninstrumented
fresh CLI processes before production refactoring. It is a reference point, not the disabled mode of the final
benchmark. The richer rule-owned syntax extraction adds cold/disabled cost; cold-store runs also pay encoding and
persistence. The measured benefit applies to repeated warm execution. Original and final measurements use different
instrumentation, so their difference is not presented as a controlled speedup.

An initial recursive usecase payload was about 18.8 MB and produced a 9.98 s warm median. The revised codec shares
expression and execution-scope records through validated reference tables. Invalid semantic record roles cause
re-extraction, as demonstrated by warmed-memo corruption regressions and the independent review.

In-place and materialized staged snapshots, CI snapshots and divergent unstaged source/rule/helper inputs are
verified by `packages/devkit/tests/integration/features/rules/engine/test_project.py`. The timed snapshot scenario
covers the staged path only; the snapshot variants' timing is not separately characterized.
