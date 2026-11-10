---
id: ADR-test-selection-and-ci
title: Affected tests locally, one run after each batch, complete CI overnight and at release
summary: "For a growing test suite, we verify locally with per-file affected-test selection, test main once after each local-orchestrated batch and run complete CI nightly on a changed head and at release, to cut full runs, accepting that a selection miss can reach main until the next complete CI."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-nightly-ci-verification
  - ADR-select-tests-by-file-with-finer-spec-dependency-nodes
  - ADR-post-batch-test-run
---

# [ADR-test-selection-and-ci] Affected tests locally, one run after each batch, complete CI overnight and at release

Superseded in part by `ADR-post-merge-verification`: permission to leave non-batch integrated-head testing to a later batch or nightly run. Affected selection, full fallback and full nightly/release CI remain.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `just test-affected` and its selector, `spec-orchestrate` Completion, the
  nightly CI wrapper, manual and release CI

---

## 1. Context & Problem Statement

Repeated complete workspace runs delay development as the suite grows. Static affected-test selection covers most
local changes but cannot detect every dependency, subprocess or entry-point relationship; it is a local optimization,
not a complete runtime dependency proof. Area/package test groups combine unrelated imports, and devkit_spec had one
production node: the measured file-only split reduces excess tests but cannot narrow that package's internal changes.

With `ADR-local-and-pull-request-integration`, the integrating command merges a conflict-free moved target itself and runs only CI
rules on the merged result; tests and review ran on the source. Two units integrated one after the other can each pass
their own tests and still break together, and nothing runs the tests on the combined head until nightly CI. A
local-orchestrated run integrates several units in a row, so its end is the point where the combined head is known.

---

## 2. Decision Drivers

- Avoid repeated costly complete runs during development, review and integration. (ADR-test-selection-and-ci)
- Keep complete coverage before publication and retry a failed head until it passes. (ADR-test-selection-and-ci)
- Reduce demonstrated false positives, preserve required consumers and full fallbacks, and keep the selector
  stateless. (ADR-test-selection-and-ci)
- Avoid changing production architecture solely for test performance. (ADR-test-selection-and-ci)
- A semantic conflict may surface later, but not stay hidden (user direction). (ADR-post-batch-test-run)
- One run on the integrated head, not an aggregation of the units' earlier results (user direction).
  (ADR-post-batch-test-run)
- Shipped skills follow each consuming repository's verification policy; the bundle prescribes no command.
  (ADR-post-batch-test-run)
- No automatic revert; a failure becomes follow-up work. (ADR-post-batch-test-run)

---

## 3. Considered Options

### Verification cadence (`ADR-nightly-ci-verification`)

- **Affected tests locally, complete CI nightly on a changed head and at release** (selected).
- **A mandatory full suite per integration** (rejected in `ADR-nightly-ci-verification`): discovers selection misses
  earlier but repeats costly work.
- **Nightly check of only the last 24 hours of commits** (rejected in `ADR-nightly-ci-verification`): could
  permanently miss a failed head; a successful-head baseline retries it.

### Selection granularity (`ADR-select-tests-by-file-with-finer-spec-dependency-nodes`)

- Keep broad groups (rejected in `ADR-select-tests-by-file-with-finer-spec-dependency-nodes`).
- Split files alone (rejected in `ADR-select-tests-by-file-with-finer-spec-dependency-nodes`: cannot narrow
  devkit_spec's internal changes).
- Split files and devkit_spec source modules (selected: addresses both observed causes with bounded implementation
  scope).
- Function-level or recorded runtime coverage analysis (rejected in
  `ADR-select-tests-by-file-with-finer-spec-dependency-nodes`).

### Combined-head test after integration (`ADR-post-batch-test-run`)

- **Rely on nightly CI** (rejected in `ADR-post-batch-test-run`): the combined head stays untested for up to a day and
  a failure is not attributed to the batch.
- **Re-test each unit after its merge** (rejected in `ADR-post-batch-test-run`): repeats work per unit, the cost the
  light merge removes.
- **One run after the batch, in `spec-orchestrate` Completion** (selected): the Host runs the repository's
  integrated-content verification once on `main`, with no new CLI command.
- **A CLI helper that runs and records the batch tests** (rejected in `ADR-post-batch-test-run`): devkit would need to
  own the test command, which is repository policy, and the result is a conversation report, not a record.
- **The full suite once per batch** (rejected by the user in `ADR-post-batch-test-run`): also catches selection
  misses, but costs a full local run per batch that this decision leaves to nightly CI.
- **Wait until every unit the run started is integrated** (rejected by the user in `ADR-post-batch-test-run`): a
  blocked unit can stay open for long, leaving the integrated units untested on `main` until nightly CI.

---

## 4. Decision Outcome

Chosen: affected tests locally with per-file and module-level devkit_spec selection, one run on `main` after each
local-orchestrated batch, and complete CI nightly on a changed head and at release.

### Verification cadence

- Development, review and integration use `just test-affected` without a separate mandatory local full-suite run. Its
  existing full-suite fallback and frontend instructions still apply. Lint, type and governance checks remain.
  (ADR-nightly-ci-verification)
- Full CI runs at 04:17 Asia/Seoul when the scheduled default-branch head differs from the latest successful nightly
  wrapper head, or no success exists. Failed and cancelled runs do not advance that baseline; API failures fail the
  gate. Manual wrapper runs always perform full CI. Existing manual CI and release CI always perform full checks, and
  publication still depends on release CI success. (ADR-nightly-ci-verification)
- The nightly wrapper reuses the existing complete CI rather than duplicating its checks. Repository-specific timing
  belongs in the repository docs; shipped delivery skills follow each consuming repository's verification policy.
  (ADR-nightly-ci-verification)

### Selection granularity

- Select per-file test groups and opt-in module-level devkit_spec nodes; keep other production owners coarse by
  default. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- Selection resolves helpers, applicable conftests, relative imports, initializers and re-exports conservatively. Use
  broad owner dependencies for static uncertainty and full fallback for unsafe/unknown change mapping or parse failure.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes) → `ARCH-07-deployment` §1.3 (MUST)
- Selection retains existing explicit data/structural/frontend checks and all full triggers.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes) → `ARCH-07-deployment` §1.3 (MUST)
- An implicit package edge on every fine spec test does not defeat the new granularity; opaque consumers explicitly
  retain a broad dependency. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
  → `ARCH-07-deployment` §1.3 (MUST NOT)
- Deferred imports do not conceal real dependencies. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
  → `ARCH-07-deployment` §1.3 (MUST NOT)
- Do not add helper extraction or runtime coverage storage to this implementation.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
- Reductions are validated on same-revision before/after collection matrices alongside independent positive and
  negative dependency fixtures. Exact numerical reductions are evidence, not authority to omit required coverage.
  (ADR-select-tests-by-file-with-finer-spec-dependency-nodes) → `ARCH-07-deployment` §1.3 (SHOULD)

### Post-batch test run

- One run after the batch in `spec-orchestrate` Completion is chosen because it meets both user constraints with a
  skill change only. (ADR-post-batch-test-run)
- When a local-orchestrated run starts its first unit, the Host notes the base branch HEAD as the batch start.
  (ADR-post-batch-test-run)
- Once every unit the run started is finished and no worker turn of the run is still running, the Host runs the
  repository's verification for integrated content once on the base branch HEAD, scoped from the batch start when the
  repository's selector supports a base. In this repository that is `just test-affected --base <batch start>`,
  keeping its `mode=full` fallback; nightly CI still runs the full suite. (ADR-post-batch-test-run)
- A unit counts as finished when it is integrated, ends blocked with its problem recorded, waits for a user decision
  (its last `worker` envelope is `needs_input`), or continues in `direct` mode. The run thus tests what it integrated.
  (ADR-post-batch-test-run)
- Outside a batch run (a unit continued in `direct`, or any `direct`-mode integration), a conflict-free CLI-built
  merge is covered by its source verification plus the CI rules on the merged result; the combined head is tested by
  a later batch run or by nightly CI. The repository's verification policy states this in place of incorporating a
  moved base before integration. (ADR-post-batch-test-run)
- After a context loss the Host recovers the batch start as the first parent of the run's earliest
  `chore(merge): integrate <branch> into <base branch>` commit on the first-parent history; only when that fails it
  runs the selector's full fallback. (ADR-post-batch-test-run)
- The Host reports the result in the conversation with the tested head and the command. A failure is reported with
  its evidence and recorded as feedback for follow-up work; nothing is reverted automatically.
  (ADR-post-batch-test-run)
- A run that integrated no unit runs nothing. (ADR-post-batch-test-run)

---

## 5. Consequences

- **Positive**:
  - Local verification avoids repeated complete runs; a failed nightly head is retried until a success advances the
    baseline. (ADR-nightly-ci-verification)
  - Semantic conflicts between the batch's units surface before nightly CI and are attributed to the batch.
    (ADR-post-batch-test-run)
- **Negative / Risks**:
  - An undetected failure can stay on main until a later complete CI; GitHub scheduling can be delayed or dropped.
    Release CI prevents publishing a head whose required full checks fail. (ADR-nightly-ci-verification)
  - The graph parser and selector tests gain complexity around Python package initialization and test helpers.
    Conservative cases still select large groups or the full suite; that is intentional: complete nightly and release
    CI remains necessary, and some changes inherently have broad consumers.
    (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
  - One extra test run per batch; a selection miss the affected selector does not cover still waits for nightly CI.
    (ADR-post-batch-test-run)
- **Follow-ups**:
  - Future workspace packages use the existing broad default until explicit finer coverage is justified. The MCP
    packaging work may change inventory and baseline counts, requiring normal base refresh and measurement rather than
    concurrent blind edits to the selector. (ADR-select-tests-by-file-with-finer-spec-dependency-nodes)
  - Development states this repository's command and the coverage outside a batch run in `AGENTS.md`,
    `docs/development/ci-cd.md` and `docs/development/workflow.md`, and replaces "Integration incorporates a moved
    base" in `CAP-HARN-agent-guidance`. (ADR-post-batch-test-run)

---

## 6. Confirmation

- `packages/devkit/tests/e2e/package/test_affected_tests.py` tests `scripts/affected_tests.py`: per-file selection,
  dependency nodes and the `mode=full` fallback.
- `.github/workflows/nightly.yml` runs the full suite when the default branch changed since the last successful
  nightly, and `.github/scripts/nightly-ci.test.cjs` tests that gate; `.github/workflows/release.yml` runs it at
  release.
- Bundle asset tests check that `spec-orchestrate` Completion names the batch run and its finished-unit rule, and that
  `spec-integrate` step 1 is conditional (`packages/devkit-spec/tests/integration/bundles/spec/`).
- Review only for the Host's conversation report of the batch run.
