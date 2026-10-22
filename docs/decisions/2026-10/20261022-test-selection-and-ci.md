---
id: ADR-test-selection-and-ci
title: Affected-Test Selection Locally and Complete CI Overnight and at Release
summary: "For a growing test suite, we verify locally with per-file affected-test selection and module-level devkit_spec nodes and run complete CI nightly on a changed head and at release, to cut repeated full runs, accepting that a selection miss can reach main until the next complete CI."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-nightly-ci-verification
  - ADR-select-tests-by-file-with-finer-spec-dependency-nodes
---

# [ADR-test-selection-and-ci] Affected-Test Selection Locally and Complete CI Overnight and at Release

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: not recorded in the members
- **Involved Components/Capabilities**: not listed in the members; topics: `just test-affected` and its selector, the
  nightly CI wrapper, manual and release CI

---

## 1. Context & Problem Statement

Repeated complete workspace runs delay development as the suite grows. Static affected-test selection covers most
local changes but cannot detect every dependency, subprocess or entry-point relationship; it is a local optimization,
not a complete runtime dependency proof. Area/package test groups combine unrelated imports, and devkit_spec had one
production node: the measured file-only split reduces excess tests but cannot narrow that package's internal changes.

---

## 2. Decision Drivers

- Avoid repeated costly complete runs during development, review and integration.
- Keep complete coverage before publication and retry a failed head until it passes.
- Reduce demonstrated false positives, preserve required consumers and full fallbacks, and keep the selector
  stateless.
- Avoid changing production architecture solely for test performance.

---

## 3. Considered Options

### Verification cadence (`ADR-nightly-ci-verification`)
- **Affected tests locally, complete CI nightly on a changed head and at release** (selected).
- **A mandatory full suite per integration** (rejected): discovers selection misses earlier but repeats costly work.
- **Nightly check of only the last 24 hours of commits** (rejected): could permanently miss a failed head; a
  successful-head baseline retries it.

### Selection granularity (`ADR-select-tests-by-file-with-finer-spec-dependency-nodes`)
- Keep broad groups (rejected).
- Split files alone (rejected: cannot narrow devkit_spec's internal changes).
- Split files and devkit_spec source modules (selected: addresses both observed causes with bounded implementation
  scope).
- Function-level or recorded runtime coverage analysis (rejected).

---

## 4. Decision Outcome

- Development, review and integration use `just test-affected` without a separate mandatory local full-suite run. Its
  existing full-suite fallback and frontend instructions still apply. Lint, type and governance checks remain.
  (ADR-nightly-ci-verification)
- The final integration content is verified after incorporating a moved base or resolving conflicts; merging the same
  verified content does not trigger another test run. (ADR-nightly-ci-verification)
- Full CI runs at 04:17 Asia/Seoul when the scheduled default-branch head differs from the latest successful nightly
  wrapper head, or no success exists. Failed and cancelled runs do not advance that baseline; API failures fail the
  gate. Manual wrapper runs always perform full CI. Existing manual CI and release CI always perform full checks, and
  publication still depends on release CI success. (ADR-nightly-ci-verification)
- The nightly wrapper reuses the existing complete CI rather than duplicating its checks. Repository-specific timing
  belongs in the repository docs; shipped delivery skills follow each consuming repository's verification policy.
  (ADR-nightly-ci-verification)
- Select per-file test groups and opt-in module-level devkit_spec nodes; keep other production owners coarse by
  default. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- Resolve helpers, applicable conftests, relative imports, initializers and re-exports conservatively. Use broad owner
  dependencies for static uncertainty and full fallback for unsafe/unknown change mapping or parse failure. Retain
  existing explicit data/structural/frontend checks and all full triggers. No implicit package edge on every fine spec
  test may defeat the new granularity; opaque consumers explicitly retain a broad dependency.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- Do not use deferred imports to conceal real dependencies, and do not add helper extraction or runtime coverage
  storage to this implementation. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- Validate reductions on same-revision before/after collection matrices alongside independent positive and negative
  dependency fixtures. Exact numerical reductions are evidence, not authority to omit required coverage.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)

---

## 5. Consequences

- **Positive**: local verification avoids repeated complete runs; a failed nightly head is retried until a success
  advances the baseline. (ADR-nightly-ci-verification)
- **Negative / Risks**:
  - An undetected failure can stay on main until a later complete CI; GitHub scheduling can be delayed or dropped.
    Release CI prevents publishing a head whose required full checks fail. (ADR-nightly-ci-verification)
  - The graph parser and selector tests gain complexity around Python package initialization and test helpers.
    Conservative cases still select large groups or the full suite; that is intentional: complete nightly and release
    CI remains necessary, and some changes inherently have broad consumers.
    (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- **Follow-ups**: future workspace packages use the existing broad default until explicit finer coverage is justified.
  The MCP packaging work may change inventory and baseline counts, requiring normal base refresh and measurement rather
  than concurrent blind edits to the selector. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)

---

## 6. Confirmation

- `packages/devkit/tests/e2e/package/test_affected_tests.py` tests `scripts/affected_tests.py`: per-file selection,
  dependency nodes and the `mode=full` fallback.
- `.github/workflows/nightly.yml` runs the full suite when the default branch changed since the last successful
  nightly, and `.github/scripts/nightly-ci.test.cjs` tests that gate; `.github/workflows/release.yml` runs it at
  release.
