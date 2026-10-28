---
id: PLAN-performance-pass
spec: SPEC-performance-pass
---

# Technical Plan: `SPEC-performance-pass` Performance pass maintenance playbook

## 1. Constitution & Invariant Review

None. The four accepted ADRs (`ADR-keep-performance-passes-in-a-separate-maintenance-playbook`,
`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`,
`ADR-measure-performance-unprofiled-and-interleaved-in-one-session`,
`ADR-classify-performance-changes-by-observable-behavior`) fix the design. `CAP-DIST-context-and-playbooks` §4
already resolves body resources against the parent of `source.path`; §5 gains a sentence that reading a co-deployed
playbook's resources is no invocation, which states an existing consequence of §4 and §5 rather than changing an
invariant. `ARCH-05-2-components` is untouched: the change adds content and a test, no code. The direct-mode
overall-refactor grant of `CAP-DLV-delivery-workflows` and `ARCH-04-delivery-strategy` stays with `review-refactor`
(spec Non-Goal 3).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass/` | New directory-form playbook: `SKILL.md` and `references/{measurement,profiling,candidates,changes}.md` (AC-04 to AC-10) |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/bundle.toml` | New asset `performance-pass` (`kind = "playbook"`, `source = "playbooks/performance-pass"`) and preset `performance = ["performance-pass", "review-refactor"]` (AC-01) |
| `packages/devkit-catalog/tests/integration/bundles/test_bundles.py` | Preset table, deployed files, co-deployment, citation headings, entry condition, self-containment and budget tests for `performance-pass` (AC-01 to AC-05) |
| `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md` | `performance` preset and four playbooks under `all` (AC-11) |
| Living Spec (`spec-sync`) | New CAP-DLV-performance-pass and UC-speed-up-selected-slow-operations; `CAP-DIST-context-and-playbooks` §5, `CAP-DIST-content-packages` §6, `CAP-DLV-review-refactor` (spec §6) |

No new dependency. `devkit-catalog` stays content-only; this repository does not select `maintenance`, so no
`devkit sync` output changes.

## 3. Component & Interface Design

### Playbook files

| File | Holds (spec §5 and AC) | Read when |
| --- | --- | --- |
| `SKILL.md` | Header (`name: performance-pass`, one-operation `description`); entry condition (AC-04); constraints for every run; intake with environment; mode table (AC-10); resolving `review-refactor` (AC-06); decision round dispositions and route summary; report fields and completion (AC-10) | Always |
| `references/measurement.md` | Protocol of AC-07 | Every mode, before the first timed run |
| `references/profiling.md` | Attribution by profiler class and its traps (spec §5) | When measurement does not already name the cost |
| `references/candidates.md` | Candidate record, expected saving, classification, presentation, route (AC-08) | Before the decision round |
| `references/changes.md` | Cited sections, overrides, additions, final measurement (AC-09) | After the round approved changes |

`SKILL.md` links each reference as `` `references/<name>.md` `` with its read condition, the form the existing
`review-refactor` test parses. References never link one another; a reference names a phase of `SKILL.md` instead.

### Citation form (normative for the test)

```text
review-refactor references/<file>.md "<heading text without its number>"
```

The test collects every match of `review-refactor (references/[a-z-]+\.md) "([^"]+)"` over the playbook's files,
after collapsing whitespace so a citation wrapped across lines still matches, requires the AC-03 set as a subset,
and checks each heading against the `^#+ ` lines of the named file with a leading `\d+(\.\d+)*\.? ` removed.

### Manifest

```toml
[[assets]]
id = "performance-pass"
kind = "playbook"
source = "playbooks/performance-pass"

[presets.performance]
assets = ["performance-pass", "review-refactor"]
```

## 4. Error Handling & Edge Cases

- A cited heading missing in a user override of `review-refactor`: the playbook stops the run with a report (AC-06);
  in this repository the test fails first (AC-03).
- An override directory without `references/<file>`: read the managed copy (AC-06).
- `review-refactor` not deployed: impossible through presets (AC-02); a hand-edited selection fails `devkit playbook
  get` with `SELECTION_INVALID`, and the playbook stops with a report.

## 5. Decisions Taken in Development

- Parallel authoring (Host direction): the playbook (Task 1.1) and the manifest, tests and catalog documentation
  (Task 1.2) have disjoint write scopes and are written concurrently in separate checkouts; Task 1.2's
  playbook-dependent tests run once Task 1.1's result is transferred. The Living Spec drafts are written concurrently
  and committed at `living-spec-draft`.
- Citation test over collapsed text rather than per line: Markdown wrapping must not hide a citation.
- Content tests assert stable phrases of the entry condition only, as for `review-refactor`; the protocol's detail is
  verified by review (ADR Confirmation sections: review only).

## 6. Verification & Test Plan

| Scenario | Proof |
| --- | --- |
| AC-01, AC-02, AC-03, AC-04, AC-05 | `just test devkit-catalog` (`tests/integration/bundles/test_bundles.py`) |
| AC-05 | `uv run devkit rules check --phase hygiene packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass` |
| AC-06 to AC-10 | `code-reviewer` against the spec and the ADRs |
| AC-11 | Review; `just rules-check` (links) |
| Whole change | `just test-affected`, `just lint-check`, `just rules-check`, `uv run devkit sync --check` |
