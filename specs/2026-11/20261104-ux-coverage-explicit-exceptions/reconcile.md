---
reconcile_id: REC-ux-coverage-explicit-exceptions
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-ux-screens.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-explicit-ux-coverage-exception-notation.md
    resolution: modified
---

# Reconciliation: `SPEC-ux-coverage-explicit-exceptions`

## Contract comparison

`CAP-GOV-spec-rules` 3.16 now states the two classifications `RULE-ux-coverage` honors (`global: <reason>` Step
cells, `off screen: <reason>` step phrases, presence-only reasons, no wording heuristic), the five report messages,
the MUST NOT for a classified item with a reason, and the use-case-first placement of step reports with the
UX-document fallback. The implementation in `features/governance/usecases/ux_coverage.py` emits exactly those five
messages (`_step_report` and the two row branches), skips a classified item only when its reason is non-empty, and
places step reports by `reportable()` on the use case first; the rule tests assert each message and placement
(AC-01 to AC-08, AC-10). 3.15 and the 3.1 rows name the classified cell as an accepted Step cell and a cell starting
with pairs and carrying `global:` later as invalid with its pairs still checked; `services/ux.py` returns
`((), True)` for a cell whose stripped text starts with `global:` and leaves every other cell's parse unchanged, and
the `RULE-ux-links` tests assert the mixed and misspelled cells, the unchanged link errors and the phrase's
invariance for the links.

`ADR-explicit-ux-coverage-exception-notation` and `ADR-ux-coverage-step-targeting` (promoted at handoff) carry the
decisions and their traces to 3.15 and 3.16; `ADR-ux-screens` gained the two "Superseded in part by" lines naming the
replaced clauses, so `RULE-decision-supersession` passes. The `docs` bundle's `ux_coverage` and `ux_links` guides,
the `ux-writing` and `usecase-writing` instructions and the `ux` template restate the notation with one complete
example each and cite no repository ID; `.devkit/managed/docs/` is the synced copy and `.devkit/installation.json`
the regenerated receipt.

No use case cites the UX rules (`devkit docs refs CAP-GOV-spec-rules --direction in` lists only
`UC-keep-the-living-spec-consistent` and `UC-adopt-in-an-existing-repository`, whose operations are unchanged: a
classification is written by the author like a citation and checked by the same rules run). No architecture or
steering document changes: the glossary's `UX document` row ("each interaction names the step it serves") stays
accurate for served steps, and the classified cell is a documented exception of the rule, not a new term. No screen
was drafted (the change has no interface), so there is no `docs/ux/` target.

## Deferred work and source feedback

The spec has no source feedback. `FB-proposal-scaffold-dirs-vanish-in-worktree` was recorded during Planning about
the proposal scaffold, is unrelated to this change and stays open. The only follow-up the ADR names (a spelling
check for near-miss step phrases) is conditional on consumer reports and not concrete work; nothing in the agreed
scope is deferred.

## Verification and retained work

`uv run devkit rules test RULE-ux-coverage RULE-ux-links` passed=2; `pytest packages/devkit-docs` 600 passed;
`just test-affected` 2171 passed at build; `uv run devkit rules check --ci --base 4f8cc732` errors=0 warnings=0;
`uv run devkit generated check` stale=0; `uv run devkit sync --check` clean. Code review round 1 passed with two P3
improvements, applied and closed in `reverify-01`.

Reconcile check round 1 (independent `reconcile-reviewer`, `reconcile-check-01`) confirmed the reflection and found
one P2 and one P3: the Decision Outcome traces of `ADR-explicit-ux-coverage-exception-notation` named `SHOULD` for
clauses 3.16 restates as `MUST NOT`, and the `ux` template's Interactions comment ran past the wrap. Both are wording
repairs (the ADR's decision is unchanged, a permitted ADR edit), applied by the implementer and self-verified in
`reconcile-check-02`: the three traces now carry the keyword 3.16 uses, the comment is rewrapped and the managed copy
regenerated.

## Entrypoints

`devkit spec entrypoints derive` proposes the bundle guides, tests, instructions, the template and the managed copies
for `CAP-GOV-spec-rules`; all rejected: they are content and receipt support, not where reading starts. The changed
source (`services/ux.py`, `usecases/ux_coverage.py`) is already inside the capability's listed entrypoint
`packages/devkit-docs/src/devkit_docs/features/governance/`. Entrypoints stay unchanged.
